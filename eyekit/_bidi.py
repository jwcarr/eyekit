# An adaptation of python-bidi: https://github.com/MeirKriheli/python-bidi
# Python 2 compatibility and debugging have been stripped out, and a new
# option has been added to return the original logical position of each
# character after conversion to display form.


# THE ORIGINAL PYTHON-BIDI LICENSE FOLLOWS:

# python-bidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2008-2010 Yaacov Zamir <kzamir_a_walla.co.il>,
# Copyright (C) 2010-2015 Meir kriheli <mkriheli@gmail.com>.


from collections import deque
from unicodedata import bidirectional, mirrored


def _LEAST_GREATER_ODD(x):
    return (x + 1) | 1


def _LEAST_GREATER_EVEN(x):
    return (x + 2) & ~1


def _embedding_direction(x):
    return ("L", "R")[x % 2]


EXPLICIT_LEVEL_LIMIT = 62

X2_X5_MAPPINGS = {
    "RLE": (_LEAST_GREATER_ODD, "N"),
    "LRE": (_LEAST_GREATER_EVEN, "N"),
    "RLO": (_LEAST_GREATER_ODD, "R"),
    "LRO": (_LEAST_GREATER_EVEN, "L"),
}

X6_IGNORED = list(X2_X5_MAPPINGS.keys()) + ["BN", "PDF", "B"]
X9_REMOVED = list(X2_X5_MAPPINGS.keys()) + ["BN", "PDF"]


def get_embedding_levels(text, storage, upper_is_rtl=False):
    """

    Setup the storage with the array of chars

    """
    base_level = storage["base_level"]
    for log_pos, char in enumerate(text):
        if upper_is_rtl and char.isupper():
            bidi_type = "R"
        else:
            bidi_type = bidirectional(char)
        storage["chars"].append(
            {
                "ch": char,
                "level": base_level,
                "type": bidi_type,
                "orig": bidi_type,
                "log_pos": log_pos,
            }
        )


def explicit_embed_and_overrides(storage):
    """

    Apply X1 to X9 rules of the unicode algorithm.

    See http://unicode.org/reports/tr9/#Explicit_Levels_and_Directions

    """
    overflow_counter = almost_overflow_counter = 0
    directional_override = "N"
    levels = deque()

    # X1
    embedding_level = storage["base_level"]

    for char in storage["chars"]:
        bidi_type = char["type"]

        level_func, override = X2_X5_MAPPINGS.get(bidi_type, (None, None))

        if level_func:
            # So this is X2 to X5
            # if we've past EXPLICIT_LEVEL_LIMIT, note it and do nothing

            if overflow_counter != 0:
                overflow_counter += 1
                continue

            new_level = level_func(embedding_level)
            if new_level < EXPLICIT_LEVEL_LIMIT:
                levels.append((embedding_level, directional_override))
                embedding_level, directional_override = new_level, override

            elif embedding_level == EXPLICIT_LEVEL_LIMIT - 2:
                # The new level is invalid, but a valid level can still be
                # achieved if this level is 60 and we encounter an RLE or
                # RLO further on.  So record that we 'almost' overflowed.
                almost_overflow_counter += 1

            else:
                overflow_counter += 1
        else:
            # X6
            if bidi_type not in X6_IGNORED:
                char["level"] = embedding_level
                if directional_override != "N":
                    char["type"] = directional_override

            # X7
            elif bidi_type == "PDF":
                if overflow_counter:
                    overflow_counter -= 1
                elif (
                    almost_overflow_counter
                    and embedding_level != EXPLICIT_LEVEL_LIMIT - 1
                ):
                    almost_overflow_counter -= 1
                elif levels:
                    embedding_level, directional_override = levels.pop()

            # X8
            elif bidi_type == "B":
                levels.clear()
                overflow_counter = almost_overflow_counter = 0
                embedding_level = char["level"] = storage["base_level"]
                directional_override = "N"

    # Removes the explicit embeds and overrides of types
    # RLE, LRE, RLO, LRO, PDF, and BN. Adjusts extended chars
    # next and prev as well

    # Applies X9. See http://unicode.org/reports/tr9/#X9
    storage["chars"] = [
        char for char in storage["chars"] if char["type"] not in X9_REMOVED
    ]

    calc_level_runs(storage)


def calc_level_runs(storage):
    """

    Split the storage to run of char types at the same level.

    Applies X10. See http://unicode.org/reports/tr9/#X10

    """
    # run level depends on the higher of the two levels on either side of
    # the boundary If the higher level is odd, the type is R; otherwise,
    # it is L

    storage["runs"].clear()
    chars = storage["chars"]

    # empty string ?
    if not chars:
        return

    def calc_level_run(b_l, b_r):
        return ["L", "R"][max(b_l, b_r) % 2]

    first_char = chars[0]

    sor = calc_level_run(storage["base_level"], first_char["level"])
    eor = None

    run_start = run_length = 0

    prev_level, prev_type = first_char["level"], first_char["type"]

    for char in chars:
        curr_level, curr_type = char["level"], char["type"]

        if curr_level == prev_level:
            run_length += 1
        else:
            eor = calc_level_run(prev_level, curr_level)
            storage["runs"].append(
                {
                    "sor": sor,
                    "eor": eor,
                    "start": run_start,
                    "type": prev_type,
                    "length": run_length,
                }
            )
            sor = eor
            run_start += run_length
            run_length = 1

        prev_level, prev_type = curr_level, curr_type

    # for the last char/runlevel
    eor = calc_level_run(curr_level, storage["base_level"])
    storage["runs"].append(
        {
            "sor": sor,
            "eor": eor,
            "start": run_start,
            "type": curr_type,
            "length": run_length,
        }
    )


def resolve_weak_types(storage):
    """

    Resolve weak type rules W1 - W3.

    See: http://unicode.org/reports/tr9/#Resolving_Weak_Types

    """

    for run in storage["runs"]:
        prev_strong = prev_type = run["sor"]
        start, length = run["start"], run["length"]
        chars = storage["chars"][start : start + length]
        for char in chars:
            # W1. Examine each nonspacing mark (NSM) in the level run, and
            # change the type of the NSM to the type of the previous character.
            # If the NSM is at the start of the level run, it will get the type
            # of sor.
            bidi_type = char["type"]

            if bidi_type == "NSM":
                char["type"] = bidi_type = prev_type

            # W2. Search backward from each instance of a European number until
            # the first strong type (R, L, AL, or sor) is found. If an AL is
            # found, change the type of the European number to Arabic number.
            if bidi_type == "EN" and prev_strong == "AL":
                char["type"] = "AN"

            # update prev_strong if needed
            if bidi_type in ("R", "L", "AL"):
                prev_strong = bidi_type

            prev_type = char["type"]

        # W3. Change all ALs to R
        for char in chars:
            if char["type"] == "AL":
                char["type"] = "R"

        # W4. A single European separator between two European numbers changes
        # to a European number. A single common separator between two numbers of
        # the same type changes to that type.
        for idx in range(1, len(chars) - 1):
            bidi_type = chars[idx]["type"]
            prev_type = chars[idx - 1]["type"]
            next_type = chars[idx + 1]["type"]

            if bidi_type == "ES" and (prev_type == next_type == "EN"):
                chars[idx]["type"] = "EN"

            if (
                bidi_type == "CS"
                and prev_type == next_type
                and prev_type in ("AN", "EN")
            ):
                chars[idx]["type"] = prev_type

        # W5. A sequence of European terminators adjacent to European numbers
        # changes to all European numbers.
        for idx in range(len(chars)):
            if chars[idx]["type"] == "EN":
                for et_idx in range(idx - 1, -1, -1):
                    if chars[et_idx]["type"] == "ET":
                        chars[et_idx]["type"] = "EN"
                    else:
                        break
                for et_idx in range(idx + 1, len(chars)):
                    if chars[et_idx]["type"] == "ET":
                        chars[et_idx]["type"] = "EN"
                    else:
                        break

        # W6. Otherwise, separators and terminators change to Other Neutral.
        for char in chars:
            if char["type"] in ("ET", "ES", "CS"):
                char["type"] = "ON"

        # W7. Search backward from each instance of a European number until the
        # first strong type (R, L, or sor) is found. If an L is found, then
        # change the type of the European number to L.
        prev_strong = run["sor"]
        for char in chars:
            if char["type"] == "EN" and prev_strong == "L":
                char["type"] = "L"

            if char["type"] in ("L", "R"):
                prev_strong = char["type"]


def resolve_neutral_types(storage):
    """

    Resolving neutral types. Implements N1 and N2

    See: http://unicode.org/reports/tr9/#Resolving_Neutral_Types

    """

    for run in storage["runs"]:
        start, length = run["start"], run["length"]
        # use sor and eor
        chars = (
            [{"type": run["sor"]}]
            + storage["chars"][start : start + length]
            + [{"type": run["eor"]}]
        )
        total_chars = len(chars)

        seq_start = None
        for idx in range(total_chars):
            char = chars[idx]
            if char["type"] in ("B", "S", "WS", "ON"):
                # N1. A sequence of neutrals takes the direction of the
                # surrounding strong text if the text on both sides has the same
                # direction. European and Arabic numbers act as if they were R
                # in terms of their influence on neutrals. Start-of-level-run
                # (sor) and end-of-level-run (eor) are used at level run
                # boundaries.
                if seq_start is None:
                    seq_start = idx
                    prev_bidi_type = chars[idx - 1]["type"]
            else:
                if seq_start is not None:
                    next_bidi_type = chars[idx]["type"]

                    if prev_bidi_type in ("AN", "EN"):
                        prev_bidi_type = "R"

                    if next_bidi_type in ("AN", "EN"):
                        next_bidi_type = "R"

                    for seq_idx in range(seq_start, idx):
                        if prev_bidi_type == next_bidi_type:
                            chars[seq_idx]["type"] = prev_bidi_type
                        else:
                            # N2. Any remaining neutrals take the embedding
                            # direction. The embedding direction for the given
                            # neutral character is derived from its embedding
                            # level: L if the character is set to an even level,
                            # and R if the level is odd.
                            chars[seq_idx]["type"] = _embedding_direction(
                                chars[seq_idx]["level"]
                            )

                    seq_start = None


def resolve_implicit_levels(storage):
    """

    Resolving implicit levels (I1, I2)

    See: http://unicode.org/reports/tr9/#Resolving_Implicit_Levels

    """
    for run in storage["runs"]:
        start, length = run["start"], run["length"]
        chars = storage["chars"][start : start + length]

        for char in chars:
            # only those types are allowed at this stage
            assert char["type"] in ("L", "R", "EN", "AN"), (
                "%s not allowed here" % char["type"]
            )

            if _embedding_direction(char["level"]) == "L":
                # I1. For all characters with an even (left-to-right) embedding
                # direction, those of type R go up one level and those of type
                # AN or EN go up two levels.
                if char["type"] == "R":
                    char["level"] += 1
                elif char["type"] != "L":
                    char["level"] += 2
            else:
                # I2. For all characters with an odd (right-to-left) embedding
                # direction, those of type L, EN or AN  go up one level.
                if char["type"] != "R":
                    char["level"] += 1


def reverse_contiguous_sequence(
    chars, line_start, line_end, highest_level, lowest_odd_level
):
    """

    L2. From the highest level found in the text to the lowest odd
    level on each line, including intermediate levels not actually
    present in the text, reverse any contiguous sequence of characters
    that are at that level or higher.

    """
    for level in range(highest_level, lowest_odd_level - 1, -1):
        _start = _end = None

        for run_idx in range(line_start, line_end + 1):
            run_ch = chars[run_idx]

            if run_ch["level"] >= level:
                if _start is None:
                    _start = _end = run_idx
                else:
                    _end = run_idx
            else:
                if _end is not None:
                    chars[_start : +_end + 1] = reversed(chars[_start : +_end + 1])
                    _start = _end = None

        # anything remaining ?
        if _start is not None:
            chars[_start : +_end + 1] = reversed(chars[_start : +_end + 1])


def reorder_resolved_levels(storage):
    """

    L1 and L2 rules

    """

    # Applies L1.

    should_reset = True
    chars = storage["chars"]

    for char in chars[::-1]:
        # L1. On each line, reset the embedding level of the following
        # characters to the paragraph embedding level:
        if char["orig"] in ("B", "S"):
            # 1. Segment separators,
            # 2. Paragraph separators,
            char["level"] = storage["base_level"]
            should_reset = True
        elif should_reset and char["orig"] in ("BN", "WS"):
            # 3. Any sequence of whitespace characters preceding a segment
            # separator or paragraph separator
            # 4. Any sequence of white space characters at the end of the
            # line.
            char["level"] = storage["base_level"]
        else:
            should_reset = False

    max_len = len(chars)

    # L2 should be per line
    # Calculates highest level and lowest odd level on the fly.

    line_start = line_end = 0
    highest_level = 0
    lowest_odd_level = EXPLICIT_LEVEL_LIMIT

    for idx in range(max_len):
        char = chars[idx]

        # calc the levels
        char_level = char["level"]
        if char_level > highest_level:
            highest_level = char_level

        if char_level % 2 and char_level < lowest_odd_level:
            lowest_odd_level = char_level

        if char["orig"] == "B" or idx == max_len - 1:
            line_end = idx
            # omit line breaks
            if char["orig"] == "B":
                line_end -= 1

            reverse_contiguous_sequence(
                chars, line_start, line_end, highest_level, lowest_odd_level
            )

            # reset for next line run
            line_start = idx + 1
            highest_level = 0
            lowest_odd_level = EXPLICIT_LEVEL_LIMIT


def apply_mirroring(storage):
    """

    Applies L4: mirroring: A character is depicted by a mirrored glyph if and
    only if (a) the resolved directionality of that character is R, and (b)
    the Bidi_Mirrored property value of that character is true.

    See: http://unicode.org/reports/tr9/#L4

    """
    for char in storage["chars"]:
        unichar = char["ch"]
        if mirrored(unichar) and _embedding_direction(char["level"]) == "R":
            char["ch"] = MIRRORED.get(unichar, unichar)


def display(text, right_to_left=False, return_log_pos=False, upper_is_rtl=False):
    """

    Returns `text` in display form. `right_to_left` determines the base
    direction. If `return_log_pos` is `True`, the original logical positions
    of the characters will also be returned, which is useful if you need to
    retain logical order but calculate display metrics. If `upper_is_rtl` is
    `True`, upper case characters will be treated as right-to-left for testing
    purposes.

    """
    storage = {
        "base_level": int(right_to_left),
        "base_dir": "R" if right_to_left else "L",
        "chars": [],
        "runs": deque(),
    }

    get_embedding_levels(text, storage, upper_is_rtl)
    explicit_embed_and_overrides(storage)
    resolve_weak_types(storage)
    resolve_neutral_types(storage)
    resolve_implicit_levels(storage)
    reorder_resolved_levels(storage)

    if return_log_pos:
        return [(char["ch"], char["log_pos"]) for char in storage["chars"]]

    apply_mirroring(storage)
    return "".join([char["ch"] for char in storage["chars"]])


# http://www.unicode.org/Public/UNIDATA/BidiMirroring.txt
MIRRORED = {
    u"\u0028": u"\u0029",  # LEFT PARENTHESIS
    u"\u0029": u"\u0028",  # RIGHT PARENTHESIS
    u"\u003C": u"\u003E",  # LESS-THAN SIGN
    u"\u003E": u"\u003C",  # GREATER-THAN SIGN
    u"\u005B": u"\u005D",  # LEFT SQUARE BRACKET
    u"\u005D": u"\u005B",  # RIGHT SQUARE BRACKET
    u"\u007B": u"\u007D",  # LEFT CURLY BRACKET
    u"\u007D": u"\u007B",  # RIGHT CURLY BRACKET
    u"\u00AB": u"\u00BB",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    u"\u00BB": u"\u00AB",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    u"\u0F3A": u"\u0F3B",  # TIBETAN MARK GUG RTAGS GYON
    u"\u0F3B": u"\u0F3A",  # TIBETAN MARK GUG RTAGS GYAS
    u"\u0F3C": u"\u0F3D",  # TIBETAN MARK ANG KHANG GYON
    u"\u0F3D": u"\u0F3C",  # TIBETAN MARK ANG KHANG GYAS
    u"\u169B": u"\u169C",  # OGHAM FEATHER MARK
    u"\u169C": u"\u169B",  # OGHAM REVERSED FEATHER MARK
    u"\u2039": u"\u203A",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    u"\u203A": u"\u2039",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    u"\u2045": u"\u2046",  # LEFT SQUARE BRACKET WITH QUILL
    u"\u2046": u"\u2045",  # RIGHT SQUARE BRACKET WITH QUILL
    u"\u207D": u"\u207E",  # SUPERSCRIPT LEFT PARENTHESIS
    u"\u207E": u"\u207D",  # SUPERSCRIPT RIGHT PARENTHESIS
    u"\u208D": u"\u208E",  # SUBSCRIPT LEFT PARENTHESIS
    u"\u208E": u"\u208D",  # SUBSCRIPT RIGHT PARENTHESIS
    u"\u2208": u"\u220B",  # ELEMENT OF
    u"\u2209": u"\u220C",  # NOT AN ELEMENT OF
    u"\u220A": u"\u220D",  # SMALL ELEMENT OF
    u"\u220B": u"\u2208",  # CONTAINS AS MEMBER
    u"\u220C": u"\u2209",  # DOES NOT CONTAIN AS MEMBER
    u"\u220D": u"\u220A",  # SMALL CONTAINS AS MEMBER
    u"\u2215": u"\u29F5",  # DIVISION SLASH
    u"\u223C": u"\u223D",  # TILDE OPERATOR
    u"\u223D": u"\u223C",  # REVERSED TILDE
    u"\u2243": u"\u22CD",  # ASYMPTOTICALLY EQUAL TO
    u"\u2252": u"\u2253",  # APPROXIMATELY EQUAL TO OR THE IMAGE OF
    u"\u2253": u"\u2252",  # IMAGE OF OR APPROXIMATELY EQUAL TO
    u"\u2254": u"\u2255",  # COLON EQUALS
    u"\u2255": u"\u2254",  # EQUALS COLON
    u"\u2264": u"\u2265",  # LESS-THAN OR EQUAL TO
    u"\u2265": u"\u2264",  # GREATER-THAN OR EQUAL TO
    u"\u2266": u"\u2267",  # LESS-THAN OVER EQUAL TO
    u"\u2267": u"\u2266",  # GREATER-THAN OVER EQUAL TO
    u"\u2268": u"\u2269",  # [BEST FIT] LESS-THAN BUT NOT EQUAL TO
    u"\u2269": u"\u2268",  # [BEST FIT] GREATER-THAN BUT NOT EQUAL TO
    u"\u226A": u"\u226B",  # MUCH LESS-THAN
    u"\u226B": u"\u226A",  # MUCH GREATER-THAN
    u"\u226E": u"\u226F",  # [BEST FIT] NOT LESS-THAN
    u"\u226F": u"\u226E",  # [BEST FIT] NOT GREATER-THAN
    u"\u2270": u"\u2271",  # [BEST FIT] NEITHER LESS-THAN NOR EQUAL TO
    u"\u2271": u"\u2270",  # [BEST FIT] NEITHER GREATER-THAN NOR EQUAL TO
    u"\u2272": u"\u2273",  # [BEST FIT] LESS-THAN OR EQUIVALENT TO
    u"\u2273": u"\u2272",  # [BEST FIT] GREATER-THAN OR EQUIVALENT TO
    u"\u2274": u"\u2275",  # [BEST FIT] NEITHER LESS-THAN NOR EQUIVALENT TO
    u"\u2275": u"\u2274",  # [BEST FIT] NEITHER GREATER-THAN NOR EQUIVALENT TO
    u"\u2276": u"\u2277",  # LESS-THAN OR GREATER-THAN
    u"\u2277": u"\u2276",  # GREATER-THAN OR LESS-THAN
    u"\u2278": u"\u2279",  # [BEST FIT] NEITHER LESS-THAN NOR GREATER-THAN
    u"\u2279": u"\u2278",  # [BEST FIT] NEITHER GREATER-THAN NOR LESS-THAN
    u"\u227A": u"\u227B",  # PRECEDES
    u"\u227B": u"\u227A",  # SUCCEEDS
    u"\u227C": u"\u227D",  # PRECEDES OR EQUAL TO
    u"\u227D": u"\u227C",  # SUCCEEDS OR EQUAL TO
    u"\u227E": u"\u227F",  # [BEST FIT] PRECEDES OR EQUIVALENT TO
    u"\u227F": u"\u227E",  # [BEST FIT] SUCCEEDS OR EQUIVALENT TO
    u"\u2280": u"\u2281",  # [BEST FIT] DOES NOT PRECEDE
    u"\u2281": u"\u2280",  # [BEST FIT] DOES NOT SUCCEED
    u"\u2282": u"\u2283",  # SUBSET OF
    u"\u2283": u"\u2282",  # SUPERSET OF
    u"\u2284": u"\u2285",  # [BEST FIT] NOT A SUBSET OF
    u"\u2285": u"\u2284",  # [BEST FIT] NOT A SUPERSET OF
    u"\u2286": u"\u2287",  # SUBSET OF OR EQUAL TO
    u"\u2287": u"\u2286",  # SUPERSET OF OR EQUAL TO
    u"\u2288": u"\u2289",  # [BEST FIT] NEITHER A SUBSET OF NOR EQUAL TO
    u"\u2289": u"\u2288",  # [BEST FIT] NEITHER A SUPERSET OF NOR EQUAL TO
    u"\u228A": u"\u228B",  # [BEST FIT] SUBSET OF WITH NOT EQUAL TO
    u"\u228B": u"\u228A",  # [BEST FIT] SUPERSET OF WITH NOT EQUAL TO
    u"\u228F": u"\u2290",  # SQUARE IMAGE OF
    u"\u2290": u"\u228F",  # SQUARE ORIGINAL OF
    u"\u2291": u"\u2292",  # SQUARE IMAGE OF OR EQUAL TO
    u"\u2292": u"\u2291",  # SQUARE ORIGINAL OF OR EQUAL TO
    u"\u2298": u"\u29B8",  # CIRCLED DIVISION SLASH
    u"\u22A2": u"\u22A3",  # RIGHT TACK
    u"\u22A3": u"\u22A2",  # LEFT TACK
    u"\u22A6": u"\u2ADE",  # ASSERTION
    u"\u22A8": u"\u2AE4",  # TRUE
    u"\u22A9": u"\u2AE3",  # FORCES
    u"\u22AB": u"\u2AE5",  # DOUBLE VERTICAL BAR DOUBLE RIGHT TURNSTILE
    u"\u22B0": u"\u22B1",  # PRECEDES UNDER RELATION
    u"\u22B1": u"\u22B0",  # SUCCEEDS UNDER RELATION
    u"\u22B2": u"\u22B3",  # NORMAL SUBGROUP OF
    u"\u22B3": u"\u22B2",  # CONTAINS AS NORMAL SUBGROUP
    u"\u22B4": u"\u22B5",  # NORMAL SUBGROUP OF OR EQUAL TO
    u"\u22B5": u"\u22B4",  # CONTAINS AS NORMAL SUBGROUP OR EQUAL TO
    u"\u22B6": u"\u22B7",  # ORIGINAL OF
    u"\u22B7": u"\u22B6",  # IMAGE OF
    u"\u22C9": u"\u22CA",  # LEFT NORMAL FACTOR SEMIDIRECT PRODUCT
    u"\u22CA": u"\u22C9",  # RIGHT NORMAL FACTOR SEMIDIRECT PRODUCT
    u"\u22CB": u"\u22CC",  # LEFT SEMIDIRECT PRODUCT
    u"\u22CC": u"\u22CB",  # RIGHT SEMIDIRECT PRODUCT
    u"\u22CD": u"\u2243",  # REVERSED TILDE EQUALS
    u"\u22D0": u"\u22D1",  # DOUBLE SUBSET
    u"\u22D1": u"\u22D0",  # DOUBLE SUPERSET
    u"\u22D6": u"\u22D7",  # LESS-THAN WITH DOT
    u"\u22D7": u"\u22D6",  # GREATER-THAN WITH DOT
    u"\u22D8": u"\u22D9",  # VERY MUCH LESS-THAN
    u"\u22D9": u"\u22D8",  # VERY MUCH GREATER-THAN
    u"\u22DA": u"\u22DB",  # LESS-THAN EQUAL TO OR GREATER-THAN
    u"\u22DB": u"\u22DA",  # GREATER-THAN EQUAL TO OR LESS-THAN
    u"\u22DC": u"\u22DD",  # EQUAL TO OR LESS-THAN
    u"\u22DD": u"\u22DC",  # EQUAL TO OR GREATER-THAN
    u"\u22DE": u"\u22DF",  # EQUAL TO OR PRECEDES
    u"\u22DF": u"\u22DE",  # EQUAL TO OR SUCCEEDS
    u"\u22E0": u"\u22E1",  # [BEST FIT] DOES NOT PRECEDE OR EQUAL
    u"\u22E1": u"\u22E0",  # [BEST FIT] DOES NOT SUCCEED OR EQUAL
    u"\u22E2": u"\u22E3",  # [BEST FIT] NOT SQUARE IMAGE OF OR EQUAL TO
    u"\u22E3": u"\u22E2",  # [BEST FIT] NOT SQUARE ORIGINAL OF OR EQUAL TO
    u"\u22E4": u"\u22E5",  # [BEST FIT] SQUARE IMAGE OF OR NOT EQUAL TO
    u"\u22E5": u"\u22E4",  # [BEST FIT] SQUARE ORIGINAL OF OR NOT EQUAL TO
    u"\u22E6": u"\u22E7",  # [BEST FIT] LESS-THAN BUT NOT EQUIVALENT TO
    u"\u22E7": u"\u22E6",  # [BEST FIT] GREATER-THAN BUT NOT EQUIVALENT TO
    u"\u22E8": u"\u22E9",  # [BEST FIT] PRECEDES BUT NOT EQUIVALENT TO
    u"\u22E9": u"\u22E8",  # [BEST FIT] SUCCEEDS BUT NOT EQUIVALENT TO
    u"\u22EA": u"\u22EB",  # [BEST FIT] NOT NORMAL SUBGROUP OF
    u"\u22EB": u"\u22EA",  # [BEST FIT] DOES NOT CONTAIN AS NORMAL SUBGROUP
    u"\u22EC": u"\u22ED",  # [BEST FIT] NOT NORMAL SUBGROUP OF OR EQUAL TO
    # [BEST FIT] DOES NOT CONTAIN AS NORMAL SUBGROUP OR EQUAL
    u"\u22ED": u"\u22EC",
    u"\u22F0": u"\u22F1",  # UP RIGHT DIAGONAL ELLIPSIS
    u"\u22F1": u"\u22F0",  # DOWN RIGHT DIAGONAL ELLIPSIS
    u"\u22F2": u"\u22FA",  # ELEMENT OF WITH LONG HORIZONTAL STROKE
    u"\u22F3": u"\u22FB",  # ELEMENT OF WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    u"\u22F4": u"\u22FC",  # SMALL ELEMENT OF WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    u"\u22F6": u"\u22FD",  # ELEMENT OF WITH OVERBAR
    u"\u22F7": u"\u22FE",  # SMALL ELEMENT OF WITH OVERBAR
    u"\u22FA": u"\u22F2",  # CONTAINS WITH LONG HORIZONTAL STROKE
    u"\u22FB": u"\u22F3",  # CONTAINS WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    u"\u22FC": u"\u22F4",  # SMALL CONTAINS WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    u"\u22FD": u"\u22F6",  # CONTAINS WITH OVERBAR
    u"\u22FE": u"\u22F7",  # SMALL CONTAINS WITH OVERBAR
    u"\u2308": u"\u2309",  # LEFT CEILING
    u"\u2309": u"\u2308",  # RIGHT CEILING
    u"\u230A": u"\u230B",  # LEFT FLOOR
    u"\u230B": u"\u230A",  # RIGHT FLOOR
    u"\u2329": u"\u232A",  # LEFT-POINTING ANGLE BRACKET
    u"\u232A": u"\u2329",  # RIGHT-POINTING ANGLE BRACKET
    u"\u2768": u"\u2769",  # MEDIUM LEFT PARENTHESIS ORNAMENT
    u"\u2769": u"\u2768",  # MEDIUM RIGHT PARENTHESIS ORNAMENT
    u"\u276A": u"\u276B",  # MEDIUM FLATTENED LEFT PARENTHESIS ORNAMENT
    u"\u276B": u"\u276A",  # MEDIUM FLATTENED RIGHT PARENTHESIS ORNAMENT
    u"\u276C": u"\u276D",  # MEDIUM LEFT-POINTING ANGLE BRACKET ORNAMENT
    u"\u276D": u"\u276C",  # MEDIUM RIGHT-POINTING ANGLE BRACKET ORNAMENT
    u"\u276E": u"\u276F",  # HEAVY LEFT-POINTING ANGLE QUOTATION MARK ORNAMENT
    u"\u276F": u"\u276E",  # HEAVY RIGHT-POINTING ANGLE QUOTATION MARK ORNAMENT
    u"\u2770": u"\u2771",  # HEAVY LEFT-POINTING ANGLE BRACKET ORNAMENT
    u"\u2771": u"\u2770",  # HEAVY RIGHT-POINTING ANGLE BRACKET ORNAMENT
    u"\u2772": u"\u2773",  # LIGHT LEFT TORTOISE SHELL BRACKET
    u"\u2773": u"\u2772",  # LIGHT RIGHT TORTOISE SHELL BRACKET
    u"\u2774": u"\u2775",  # MEDIUM LEFT CURLY BRACKET ORNAMENT
    u"\u2775": u"\u2774",  # MEDIUM RIGHT CURLY BRACKET ORNAMENT
    u"\u27C3": u"\u27C4",  # OPEN SUBSET
    u"\u27C4": u"\u27C3",  # OPEN SUPERSET
    u"\u27C5": u"\u27C6",  # LEFT S-SHAPED BAG DELIMITER
    u"\u27C6": u"\u27C5",  # RIGHT S-SHAPED BAG DELIMITER
    u"\u27C8": u"\u27C9",  # REVERSE SOLIDUS PRECEDING SUBSET
    u"\u27C9": u"\u27C8",  # SUPERSET PRECEDING SOLIDUS
    u"\u27D5": u"\u27D6",  # LEFT OUTER JOIN
    u"\u27D6": u"\u27D5",  # RIGHT OUTER JOIN
    u"\u27DD": u"\u27DE",  # LONG RIGHT TACK
    u"\u27DE": u"\u27DD",  # LONG LEFT TACK
    u"\u27E2": u"\u27E3",  # WHITE CONCAVE-SIDED DIAMOND WITH LEFTWARDS TICK
    u"\u27E3": u"\u27E2",  # WHITE CONCAVE-SIDED DIAMOND WITH RIGHTWARDS TICK
    u"\u27E4": u"\u27E5",  # WHITE SQUARE WITH LEFTWARDS TICK
    u"\u27E5": u"\u27E4",  # WHITE SQUARE WITH RIGHTWARDS TICK
    u"\u27E6": u"\u27E7",  # MATHEMATICAL LEFT WHITE SQUARE BRACKET
    u"\u27E7": u"\u27E6",  # MATHEMATICAL RIGHT WHITE SQUARE BRACKET
    u"\u27E8": u"\u27E9",  # MATHEMATICAL LEFT ANGLE BRACKET
    u"\u27E9": u"\u27E8",  # MATHEMATICAL RIGHT ANGLE BRACKET
    u"\u27EA": u"\u27EB",  # MATHEMATICAL LEFT DOUBLE ANGLE BRACKET
    u"\u27EB": u"\u27EA",  # MATHEMATICAL RIGHT DOUBLE ANGLE BRACKET
    u"\u27EC": u"\u27ED",  # MATHEMATICAL LEFT WHITE TORTOISE SHELL BRACKET
    u"\u27ED": u"\u27EC",  # MATHEMATICAL RIGHT WHITE TORTOISE SHELL BRACKET
    u"\u27EE": u"\u27EF",  # MATHEMATICAL LEFT FLATTENED PARENTHESIS
    u"\u27EF": u"\u27EE",  # MATHEMATICAL RIGHT FLATTENED PARENTHESIS
    u"\u2983": u"\u2984",  # LEFT WHITE CURLY BRACKET
    u"\u2984": u"\u2983",  # RIGHT WHITE CURLY BRACKET
    u"\u2985": u"\u2986",  # LEFT WHITE PARENTHESIS
    u"\u2986": u"\u2985",  # RIGHT WHITE PARENTHESIS
    u"\u2987": u"\u2988",  # Z NOTATION LEFT IMAGE BRACKET
    u"\u2988": u"\u2987",  # Z NOTATION RIGHT IMAGE BRACKET
    u"\u2989": u"\u298A",  # Z NOTATION LEFT BINDING BRACKET
    u"\u298A": u"\u2989",  # Z NOTATION RIGHT BINDING BRACKET
    u"\u298B": u"\u298C",  # LEFT SQUARE BRACKET WITH UNDERBAR
    u"\u298C": u"\u298B",  # RIGHT SQUARE BRACKET WITH UNDERBAR
    u"\u298D": u"\u2990",  # LEFT SQUARE BRACKET WITH TICK IN TOP CORNER
    u"\u298E": u"\u298F",  # RIGHT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    u"\u298F": u"\u298E",  # LEFT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    u"\u2990": u"\u298D",  # RIGHT SQUARE BRACKET WITH TICK IN TOP CORNER
    u"\u2991": u"\u2992",  # LEFT ANGLE BRACKET WITH DOT
    u"\u2992": u"\u2991",  # RIGHT ANGLE BRACKET WITH DOT
    u"\u2993": u"\u2994",  # LEFT ARC LESS-THAN BRACKET
    u"\u2994": u"\u2993",  # RIGHT ARC GREATER-THAN BRACKET
    u"\u2995": u"\u2996",  # DOUBLE LEFT ARC GREATER-THAN BRACKET
    u"\u2996": u"\u2995",  # DOUBLE RIGHT ARC LESS-THAN BRACKET
    u"\u2997": u"\u2998",  # LEFT BLACK TORTOISE SHELL BRACKET
    u"\u2998": u"\u2997",  # RIGHT BLACK TORTOISE SHELL BRACKET
    u"\u29B8": u"\u2298",  # CIRCLED REVERSE SOLIDUS
    u"\u29C0": u"\u29C1",  # CIRCLED LESS-THAN
    u"\u29C1": u"\u29C0",  # CIRCLED GREATER-THAN
    u"\u29C4": u"\u29C5",  # SQUARED RISING DIAGONAL SLASH
    u"\u29C5": u"\u29C4",  # SQUARED FALLING DIAGONAL SLASH
    u"\u29CF": u"\u29D0",  # LEFT TRIANGLE BESIDE VERTICAL BAR
    u"\u29D0": u"\u29CF",  # VERTICAL BAR BESIDE RIGHT TRIANGLE
    u"\u29D1": u"\u29D2",  # BOWTIE WITH LEFT HALF BLACK
    u"\u29D2": u"\u29D1",  # BOWTIE WITH RIGHT HALF BLACK
    u"\u29D4": u"\u29D5",  # TIMES WITH LEFT HALF BLACK
    u"\u29D5": u"\u29D4",  # TIMES WITH RIGHT HALF BLACK
    u"\u29D8": u"\u29D9",  # LEFT WIGGLY FENCE
    u"\u29D9": u"\u29D8",  # RIGHT WIGGLY FENCE
    u"\u29DA": u"\u29DB",  # LEFT DOUBLE WIGGLY FENCE
    u"\u29DB": u"\u29DA",  # RIGHT DOUBLE WIGGLY FENCE
    u"\u29F5": u"\u2215",  # REVERSE SOLIDUS OPERATOR
    u"\u29F8": u"\u29F9",  # BIG SOLIDUS
    u"\u29F9": u"\u29F8",  # BIG REVERSE SOLIDUS
    u"\u29FC": u"\u29FD",  # LEFT-POINTING CURVED ANGLE BRACKET
    u"\u29FD": u"\u29FC",  # RIGHT-POINTING CURVED ANGLE BRACKET
    u"\u2A2B": u"\u2A2C",  # MINUS SIGN WITH FALLING DOTS
    u"\u2A2C": u"\u2A2B",  # MINUS SIGN WITH RISING DOTS
    u"\u2A2D": u"\u2A2E",  # PLUS SIGN IN LEFT HALF CIRCLE
    u"\u2A2E": u"\u2A2D",  # PLUS SIGN IN RIGHT HALF CIRCLE
    u"\u2A34": u"\u2A35",  # MULTIPLICATION SIGN IN LEFT HALF CIRCLE
    u"\u2A35": u"\u2A34",  # MULTIPLICATION SIGN IN RIGHT HALF CIRCLE
    u"\u2A3C": u"\u2A3D",  # INTERIOR PRODUCT
    u"\u2A3D": u"\u2A3C",  # RIGHTHAND INTERIOR PRODUCT
    u"\u2A64": u"\u2A65",  # Z NOTATION DOMAIN ANTIRESTRICTION
    u"\u2A65": u"\u2A64",  # Z NOTATION RANGE ANTIRESTRICTION
    u"\u2A79": u"\u2A7A",  # LESS-THAN WITH CIRCLE INSIDE
    u"\u2A7A": u"\u2A79",  # GREATER-THAN WITH CIRCLE INSIDE
    u"\u2A7D": u"\u2A7E",  # LESS-THAN OR SLANTED EQUAL TO
    u"\u2A7E": u"\u2A7D",  # GREATER-THAN OR SLANTED EQUAL TO
    u"\u2A7F": u"\u2A80",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT INSIDE
    u"\u2A80": u"\u2A7F",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT INSIDE
    u"\u2A81": u"\u2A82",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT ABOVE
    u"\u2A82": u"\u2A81",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT ABOVE
    u"\u2A83": u"\u2A84",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT ABOVE RIGHT
    u"\u2A84": u"\u2A83",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT ABOVE LEFT
    u"\u2A8B": u"\u2A8C",  # LESS-THAN ABOVE DOUBLE-LINE EQUAL ABOVE GREATER-THAN
    u"\u2A8C": u"\u2A8B",  # GREATER-THAN ABOVE DOUBLE-LINE EQUAL ABOVE LESS-THAN
    u"\u2A91": u"\u2A92",  # LESS-THAN ABOVE GREATER-THAN ABOVE DOUBLE-LINE EQUAL
    u"\u2A92": u"\u2A91",  # GREATER-THAN ABOVE LESS-THAN ABOVE DOUBLE-LINE EQUAL
    # LESS-THAN ABOVE SLANTED EQUAL ABOVE GREATER-THAN ABOVE SLANTED EQUAL
    u"\u2A93": u"\u2A94",
    # GREATER-THAN ABOVE SLANTED EQUAL ABOVE LESS-THAN ABOVE SLANTED EQUAL
    u"\u2A94": u"\u2A93",
    u"\u2A95": u"\u2A96",  # SLANTED EQUAL TO OR LESS-THAN
    u"\u2A96": u"\u2A95",  # SLANTED EQUAL TO OR GREATER-THAN
    u"\u2A97": u"\u2A98",  # SLANTED EQUAL TO OR LESS-THAN WITH DOT INSIDE
    u"\u2A98": u"\u2A97",  # SLANTED EQUAL TO OR GREATER-THAN WITH DOT INSIDE
    u"\u2A99": u"\u2A9A",  # DOUBLE-LINE EQUAL TO OR LESS-THAN
    u"\u2A9A": u"\u2A99",  # DOUBLE-LINE EQUAL TO OR GREATER-THAN
    u"\u2A9B": u"\u2A9C",  # DOUBLE-LINE SLANTED EQUAL TO OR LESS-THAN
    u"\u2A9C": u"\u2A9B",  # DOUBLE-LINE SLANTED EQUAL TO OR GREATER-THAN
    u"\u2AA1": u"\u2AA2",  # DOUBLE NESTED LESS-THAN
    u"\u2AA2": u"\u2AA1",  # DOUBLE NESTED GREATER-THAN
    u"\u2AA6": u"\u2AA7",  # LESS-THAN CLOSED BY CURVE
    u"\u2AA7": u"\u2AA6",  # GREATER-THAN CLOSED BY CURVE
    u"\u2AA8": u"\u2AA9",  # LESS-THAN CLOSED BY CURVE ABOVE SLANTED EQUAL
    u"\u2AA9": u"\u2AA8",  # GREATER-THAN CLOSED BY CURVE ABOVE SLANTED EQUAL
    u"\u2AAA": u"\u2AAB",  # SMALLER THAN
    u"\u2AAB": u"\u2AAA",  # LARGER THAN
    u"\u2AAC": u"\u2AAD",  # SMALLER THAN OR EQUAL TO
    u"\u2AAD": u"\u2AAC",  # LARGER THAN OR EQUAL TO
    u"\u2AAF": u"\u2AB0",  # PRECEDES ABOVE SINGLE-LINE EQUALS SIGN
    u"\u2AB0": u"\u2AAF",  # SUCCEEDS ABOVE SINGLE-LINE EQUALS SIGN
    u"\u2AB3": u"\u2AB4",  # PRECEDES ABOVE EQUALS SIGN
    u"\u2AB4": u"\u2AB3",  # SUCCEEDS ABOVE EQUALS SIGN
    u"\u2ABB": u"\u2ABC",  # DOUBLE PRECEDES
    u"\u2ABC": u"\u2ABB",  # DOUBLE SUCCEEDS
    u"\u2ABD": u"\u2ABE",  # SUBSET WITH DOT
    u"\u2ABE": u"\u2ABD",  # SUPERSET WITH DOT
    u"\u2ABF": u"\u2AC0",  # SUBSET WITH PLUS SIGN BELOW
    u"\u2AC0": u"\u2ABF",  # SUPERSET WITH PLUS SIGN BELOW
    u"\u2AC1": u"\u2AC2",  # SUBSET WITH MULTIPLICATION SIGN BELOW
    u"\u2AC2": u"\u2AC1",  # SUPERSET WITH MULTIPLICATION SIGN BELOW
    u"\u2AC3": u"\u2AC4",  # SUBSET OF OR EQUAL TO WITH DOT ABOVE
    u"\u2AC4": u"\u2AC3",  # SUPERSET OF OR EQUAL TO WITH DOT ABOVE
    u"\u2AC5": u"\u2AC6",  # SUBSET OF ABOVE EQUALS SIGN
    u"\u2AC6": u"\u2AC5",  # SUPERSET OF ABOVE EQUALS SIGN
    u"\u2ACD": u"\u2ACE",  # SQUARE LEFT OPEN BOX OPERATOR
    u"\u2ACE": u"\u2ACD",  # SQUARE RIGHT OPEN BOX OPERATOR
    u"\u2ACF": u"\u2AD0",  # CLOSED SUBSET
    u"\u2AD0": u"\u2ACF",  # CLOSED SUPERSET
    u"\u2AD1": u"\u2AD2",  # CLOSED SUBSET OR EQUAL TO
    u"\u2AD2": u"\u2AD1",  # CLOSED SUPERSET OR EQUAL TO
    u"\u2AD3": u"\u2AD4",  # SUBSET ABOVE SUPERSET
    u"\u2AD4": u"\u2AD3",  # SUPERSET ABOVE SUBSET
    u"\u2AD5": u"\u2AD6",  # SUBSET ABOVE SUBSET
    u"\u2AD6": u"\u2AD5",  # SUPERSET ABOVE SUPERSET
    u"\u2ADE": u"\u22A6",  # SHORT LEFT TACK
    u"\u2AE3": u"\u22A9",  # DOUBLE VERTICAL BAR LEFT TURNSTILE
    u"\u2AE4": u"\u22A8",  # VERTICAL BAR DOUBLE LEFT TURNSTILE
    u"\u2AE5": u"\u22AB",  # DOUBLE VERTICAL BAR DOUBLE LEFT TURNSTILE
    u"\u2AEC": u"\u2AED",  # DOUBLE STROKE NOT SIGN
    u"\u2AED": u"\u2AEC",  # REVERSED DOUBLE STROKE NOT SIGN
    u"\u2AF7": u"\u2AF8",  # TRIPLE NESTED LESS-THAN
    u"\u2AF8": u"\u2AF7",  # TRIPLE NESTED GREATER-THAN
    u"\u2AF9": u"\u2AFA",  # DOUBLE-LINE SLANTED LESS-THAN OR EQUAL TO
    u"\u2AFA": u"\u2AF9",  # DOUBLE-LINE SLANTED GREATER-THAN OR EQUAL TO
    u"\u2E02": u"\u2E03",  # LEFT SUBSTITUTION BRACKET
    u"\u2E03": u"\u2E02",  # RIGHT SUBSTITUTION BRACKET
    u"\u2E04": u"\u2E05",  # LEFT DOTTED SUBSTITUTION BRACKET
    u"\u2E05": u"\u2E04",  # RIGHT DOTTED SUBSTITUTION BRACKET
    u"\u2E09": u"\u2E0A",  # LEFT TRANSPOSITION BRACKET
    u"\u2E0A": u"\u2E09",  # RIGHT TRANSPOSITION BRACKET
    u"\u2E0C": u"\u2E0D",  # LEFT RAISED OMISSION BRACKET
    u"\u2E0D": u"\u2E0C",  # RIGHT RAISED OMISSION BRACKET
    u"\u2E1C": u"\u2E1D",  # LEFT LOW PARAPHRASE BRACKET
    u"\u2E1D": u"\u2E1C",  # RIGHT LOW PARAPHRASE BRACKET
    u"\u2E20": u"\u2E21",  # LEFT VERTICAL BAR WITH QUILL
    u"\u2E21": u"\u2E20",  # RIGHT VERTICAL BAR WITH QUILL
    u"\u2E22": u"\u2E23",  # TOP LEFT HALF BRACKET
    u"\u2E23": u"\u2E22",  # TOP RIGHT HALF BRACKET
    u"\u2E24": u"\u2E25",  # BOTTOM LEFT HALF BRACKET
    u"\u2E25": u"\u2E24",  # BOTTOM RIGHT HALF BRACKET
    u"\u2E26": u"\u2E27",  # LEFT SIDEWAYS U BRACKET
    u"\u2E27": u"\u2E26",  # RIGHT SIDEWAYS U BRACKET
    u"\u2E28": u"\u2E29",  # LEFT DOUBLE PARENTHESIS
    u"\u2E29": u"\u2E28",  # RIGHT DOUBLE PARENTHESIS
    u"\u3008": u"\u3009",  # LEFT ANGLE BRACKET
    u"\u3009": u"\u3008",  # RIGHT ANGLE BRACKET
    u"\u300A": u"\u300B",  # LEFT DOUBLE ANGLE BRACKET
    u"\u300B": u"\u300A",  # RIGHT DOUBLE ANGLE BRACKET
    u"\u300C": u"\u300D",  # [BEST FIT] LEFT CORNER BRACKET
    u"\u300D": u"\u300C",  # [BEST FIT] RIGHT CORNER BRACKET
    u"\u300E": u"\u300F",  # [BEST FIT] LEFT WHITE CORNER BRACKET
    u"\u300F": u"\u300E",  # [BEST FIT] RIGHT WHITE CORNER BRACKET
    u"\u3010": u"\u3011",  # LEFT BLACK LENTICULAR BRACKET
    u"\u3011": u"\u3010",  # RIGHT BLACK LENTICULAR BRACKET
    u"\u3014": u"\u3015",  # LEFT TORTOISE SHELL BRACKET
    u"\u3015": u"\u3014",  # RIGHT TORTOISE SHELL BRACKET
    u"\u3016": u"\u3017",  # LEFT WHITE LENTICULAR BRACKET
    u"\u3017": u"\u3016",  # RIGHT WHITE LENTICULAR BRACKET
    u"\u3018": u"\u3019",  # LEFT WHITE TORTOISE SHELL BRACKET
    u"\u3019": u"\u3018",  # RIGHT WHITE TORTOISE SHELL BRACKET
    u"\u301A": u"\u301B",  # LEFT WHITE SQUARE BRACKET
    u"\u301B": u"\u301A",  # RIGHT WHITE SQUARE BRACKET
    u"\uFE59": u"\uFE5A",  # SMALL LEFT PARENTHESIS
    u"\uFE5A": u"\uFE59",  # SMALL RIGHT PARENTHESIS
    u"\uFE5B": u"\uFE5C",  # SMALL LEFT CURLY BRACKET
    u"\uFE5C": u"\uFE5B",  # SMALL RIGHT CURLY BRACKET
    u"\uFE5D": u"\uFE5E",  # SMALL LEFT TORTOISE SHELL BRACKET
    u"\uFE5E": u"\uFE5D",  # SMALL RIGHT TORTOISE SHELL BRACKET
    u"\uFE64": u"\uFE65",  # SMALL LESS-THAN SIGN
    u"\uFE65": u"\uFE64",  # SMALL GREATER-THAN SIGN
    u"\uFF08": u"\uFF09",  # FULLWIDTH LEFT PARENTHESIS
    u"\uFF09": u"\uFF08",  # FULLWIDTH RIGHT PARENTHESIS
    u"\uFF1C": u"\uFF1E",  # FULLWIDTH LESS-THAN SIGN
    u"\uFF1E": u"\uFF1C",  # FULLWIDTH GREATER-THAN SIGN
    u"\uFF3B": u"\uFF3D",  # FULLWIDTH LEFT SQUARE BRACKET
    u"\uFF3D": u"\uFF3B",  # FULLWIDTH RIGHT SQUARE BRACKET
    u"\uFF5B": u"\uFF5D",  # FULLWIDTH LEFT CURLY BRACKET
    u"\uFF5D": u"\uFF5B",  # FULLWIDTH RIGHT CURLY BRACKET
    u"\uFF5F": u"\uFF60",  # FULLWIDTH LEFT WHITE PARENTHESIS
    u"\uFF60": u"\uFF5F",  # FULLWIDTH RIGHT WHITE PARENTHESIS
    u"\uFF62": u"\uFF63",  # [BEST FIT] HALFWIDTH LEFT CORNER BRACKET
    u"\uFF63": u"\uFF62",  # [BEST FIT] HALFWIDTH RIGHT CORNER BRACKET
}
