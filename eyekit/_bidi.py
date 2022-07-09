# This file contains a modified verision of python-bidi
# (https://github.com/MeirKriheli/python-bidi), which has an LGPLv3 license.
# Python 2 compatibility and debugging have been removed, and a new option has
# been added to return the original logical position of each character after
# conversion to display form. The original python-bidi license follows:

# python-bidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2008-2010 Yaacov Zamir <kzamir_a_walla.co.il>,
# Copyright (C) 2010-2015 Meir kriheli <mkriheli@gmail.com>,
# Copyright (C) 2021 Jon Carr.

"""
Module to handle bidirectional text and support for right-to-left scripts.
"""

from collections import deque
from unicodedata import bidirectional, mirrored


def least_greater_odd(x):
    return (x + 1) | 1


def least_greater_even(x):
    return (x + 2) & ~1


def embedding_direction(x):
    return ("L", "R")[x % 2]


def calc_level_run(b_l, b_r):
    return ("L", "R")[max(b_l, b_r) % 2]


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

    if not chars:
        return

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
                            chars[seq_idx]["type"] = embedding_direction(
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

            if embedding_direction(char["level"]) == "L":
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
        start = end = None

        for run_idx in range(line_start, line_end + 1):
            run_ch = chars[run_idx]

            if run_ch["level"] >= level:
                if start is None:
                    start = end = run_idx
                else:
                    end = run_idx
            else:
                if end is not None:
                    chars[start : +end + 1] = reversed(chars[start : +end + 1])
                    start = end = None

        if start is not None:
            chars[start : +end + 1] = reversed(chars[start : +end + 1])


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
        if mirrored(unichar) and embedding_direction(char["level"]) == "R":
            char["ch"] = MIRRORED_CHARACTER_PAIRS.get(unichar, unichar)


def display(text, right_to_left=False, return_log_pos=False, upper_is_rtl=False):
    """
    Returns `text` in display form. `right_to_left` determines the base
    direction. If `return_log_pos` is `True`, the original logical positions
    of the characters will also be returned, which is useful if you need to
    retain logical order but calculate display metrics.
    """
    base_level = 1 if right_to_left else 0
    base_direction = "R" if right_to_left else "L"
    storage = {
        "base_level": base_level,
        "base_dir": base_direction,
        "chars": [],
        "runs": deque(),
    }
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

    explicit_embed_and_overrides(storage)
    resolve_weak_types(storage)
    resolve_neutral_types(storage)
    resolve_implicit_levels(storage)
    reorder_resolved_levels(storage)

    if return_log_pos:
        return [(char["ch"], char["log_pos"]) for char in storage["chars"]]

    apply_mirroring(storage)
    return "".join([char["ch"] for char in storage["chars"]])


EXPLICIT_LEVEL_LIMIT = 62

X2_X5_MAPPINGS = {
    "RLE": (least_greater_odd, "N"),
    "LRE": (least_greater_even, "N"),
    "RLO": (least_greater_odd, "R"),
    "LRO": (least_greater_even, "L"),
}

X6_IGNORED = list(X2_X5_MAPPINGS.keys()) + ["BN", "PDF", "B"]
X9_REMOVED = list(X2_X5_MAPPINGS.keys()) + ["BN", "PDF"]

# http://www.unicode.org/Public/UNIDATA/BidiMirroring.txt
MIRRORED_CHARACTER_PAIRS = {
    "\u0028": "\u0029",  # LEFT PARENTHESIS
    "\u0029": "\u0028",  # RIGHT PARENTHESIS
    "\u003C": "\u003E",  # LESS-THAN SIGN
    "\u003E": "\u003C",  # GREATER-THAN SIGN
    "\u005B": "\u005D",  # LEFT SQUARE BRACKET
    "\u005D": "\u005B",  # RIGHT SQUARE BRACKET
    "\u007B": "\u007D",  # LEFT CURLY BRACKET
    "\u007D": "\u007B",  # RIGHT CURLY BRACKET
    "\u00AB": "\u00BB",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\u00BB": "\u00AB",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\u0F3A": "\u0F3B",  # TIBETAN MARK GUG RTAGS GYON
    "\u0F3B": "\u0F3A",  # TIBETAN MARK GUG RTAGS GYAS
    "\u0F3C": "\u0F3D",  # TIBETAN MARK ANG KHANG GYON
    "\u0F3D": "\u0F3C",  # TIBETAN MARK ANG KHANG GYAS
    "\u169B": "\u169C",  # OGHAM FEATHER MARK
    "\u169C": "\u169B",  # OGHAM REVERSED FEATHER MARK
    "\u2039": "\u203A",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    "\u203A": "\u2039",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    "\u2045": "\u2046",  # LEFT SQUARE BRACKET WITH QUILL
    "\u2046": "\u2045",  # RIGHT SQUARE BRACKET WITH QUILL
    "\u207D": "\u207E",  # SUPERSCRIPT LEFT PARENTHESIS
    "\u207E": "\u207D",  # SUPERSCRIPT RIGHT PARENTHESIS
    "\u208D": "\u208E",  # SUBSCRIPT LEFT PARENTHESIS
    "\u208E": "\u208D",  # SUBSCRIPT RIGHT PARENTHESIS
    "\u2208": "\u220B",  # ELEMENT OF
    "\u2209": "\u220C",  # NOT AN ELEMENT OF
    "\u220A": "\u220D",  # SMALL ELEMENT OF
    "\u220B": "\u2208",  # CONTAINS AS MEMBER
    "\u220C": "\u2209",  # DOES NOT CONTAIN AS MEMBER
    "\u220D": "\u220A",  # SMALL CONTAINS AS MEMBER
    "\u2215": "\u29F5",  # DIVISION SLASH
    "\u221F": "\u2BFE",  # RIGHT ANGLE
    "\u2220": "\u29A3",  # ANGLE
    "\u2221": "\u299B",  # MEASURED ANGLE
    "\u2222": "\u29A0",  # SPHERICAL ANGLE
    "\u2224": "\u2AEE",  # DOES NOT DIVIDE
    "\u223C": "\u223D",  # TILDE OPERATOR
    "\u223D": "\u223C",  # REVERSED TILDE
    "\u2243": "\u22CD",  # ASYMPTOTICALLY EQUAL TO
    "\u2245": "\u224C",  # APPROXIMATELY EQUAL TO
    "\u224C": "\u2245",  # ALL EQUAL TO
    "\u2252": "\u2253",  # APPROXIMATELY EQUAL TO OR THE IMAGE OF
    "\u2253": "\u2252",  # IMAGE OF OR APPROXIMATELY EQUAL TO
    "\u2254": "\u2255",  # COLON EQUALS
    "\u2255": "\u2254",  # EQUALS COLON
    "\u2264": "\u2265",  # LESS-THAN OR EQUAL TO
    "\u2265": "\u2264",  # GREATER-THAN OR EQUAL TO
    "\u2266": "\u2267",  # LESS-THAN OVER EQUAL TO
    "\u2267": "\u2266",  # GREATER-THAN OVER EQUAL TO
    "\u2268": "\u2269",  # [BEST FIT] LESS-THAN BUT NOT EQUAL TO
    "\u2269": "\u2268",  # [BEST FIT] GREATER-THAN BUT NOT EQUAL TO
    "\u226A": "\u226B",  # MUCH LESS-THAN
    "\u226B": "\u226A",  # MUCH GREATER-THAN
    "\u226E": "\u226F",  # [BEST FIT] NOT LESS-THAN
    "\u226F": "\u226E",  # [BEST FIT] NOT GREATER-THAN
    "\u2270": "\u2271",  # [BEST FIT] NEITHER LESS-THAN NOR EQUAL TO
    "\u2271": "\u2270",  # [BEST FIT] NEITHER GREATER-THAN NOR EQUAL TO
    "\u2272": "\u2273",  # [BEST FIT] LESS-THAN OR EQUIVALENT TO
    "\u2273": "\u2272",  # [BEST FIT] GREATER-THAN OR EQUIVALENT TO
    "\u2274": "\u2275",  # [BEST FIT] NEITHER LESS-THAN NOR EQUIVALENT TO
    "\u2275": "\u2274",  # [BEST FIT] NEITHER GREATER-THAN NOR EQUIVALENT TO
    "\u2276": "\u2277",  # LESS-THAN OR GREATER-THAN
    "\u2277": "\u2276",  # GREATER-THAN OR LESS-THAN
    "\u2278": "\u2279",  # [BEST FIT] NEITHER LESS-THAN NOR GREATER-THAN
    "\u2279": "\u2278",  # [BEST FIT] NEITHER GREATER-THAN NOR LESS-THAN
    "\u227A": "\u227B",  # PRECEDES
    "\u227B": "\u227A",  # SUCCEEDS
    "\u227C": "\u227D",  # PRECEDES OR EQUAL TO
    "\u227D": "\u227C",  # SUCCEEDS OR EQUAL TO
    "\u227E": "\u227F",  # [BEST FIT] PRECEDES OR EQUIVALENT TO
    "\u227F": "\u227E",  # [BEST FIT] SUCCEEDS OR EQUIVALENT TO
    "\u2280": "\u2281",  # [BEST FIT] DOES NOT PRECEDE
    "\u2281": "\u2280",  # [BEST FIT] DOES NOT SUCCEED
    "\u2282": "\u2283",  # SUBSET OF
    "\u2283": "\u2282",  # SUPERSET OF
    "\u2284": "\u2285",  # [BEST FIT] NOT A SUBSET OF
    "\u2285": "\u2284",  # [BEST FIT] NOT A SUPERSET OF
    "\u2286": "\u2287",  # SUBSET OF OR EQUAL TO
    "\u2287": "\u2286",  # SUPERSET OF OR EQUAL TO
    "\u2288": "\u2289",  # [BEST FIT] NEITHER A SUBSET OF NOR EQUAL TO
    "\u2289": "\u2288",  # [BEST FIT] NEITHER A SUPERSET OF NOR EQUAL TO
    "\u228A": "\u228B",  # [BEST FIT] SUBSET OF WITH NOT EQUAL TO
    "\u228B": "\u228A",  # [BEST FIT] SUPERSET OF WITH NOT EQUAL TO
    "\u228F": "\u2290",  # SQUARE IMAGE OF
    "\u2290": "\u228F",  # SQUARE ORIGINAL OF
    "\u2291": "\u2292",  # SQUARE IMAGE OF OR EQUAL TO
    "\u2292": "\u2291",  # SQUARE ORIGINAL OF OR EQUAL TO
    "\u2298": "\u29B8",  # CIRCLED DIVISION SLASH
    "\u22A2": "\u22A3",  # RIGHT TACK
    "\u22A3": "\u22A2",  # LEFT TACK
    "\u22A6": "\u2ADE",  # ASSERTION
    "\u22A8": "\u2AE4",  # TRUE
    "\u22A9": "\u2AE3",  # FORCES
    "\u22AB": "\u2AE5",  # DOUBLE VERTICAL BAR DOUBLE RIGHT TURNSTILE
    "\u22B0": "\u22B1",  # PRECEDES UNDER RELATION
    "\u22B1": "\u22B0",  # SUCCEEDS UNDER RELATION
    "\u22B2": "\u22B3",  # NORMAL SUBGROUP OF
    "\u22B3": "\u22B2",  # CONTAINS AS NORMAL SUBGROUP
    "\u22B4": "\u22B5",  # NORMAL SUBGROUP OF OR EQUAL TO
    "\u22B5": "\u22B4",  # CONTAINS AS NORMAL SUBGROUP OR EQUAL TO
    "\u22B6": "\u22B7",  # ORIGINAL OF
    "\u22B7": "\u22B6",  # IMAGE OF
    "\u22B8": "\u27DC",  # MULTIMAP
    "\u22C9": "\u22CA",  # LEFT NORMAL FACTOR SEMIDIRECT PRODUCT
    "\u22CA": "\u22C9",  # RIGHT NORMAL FACTOR SEMIDIRECT PRODUCT
    "\u22CB": "\u22CC",  # LEFT SEMIDIRECT PRODUCT
    "\u22CC": "\u22CB",  # RIGHT SEMIDIRECT PRODUCT
    "\u22CD": "\u2243",  # REVERSED TILDE EQUALS
    "\u22D0": "\u22D1",  # DOUBLE SUBSET
    "\u22D1": "\u22D0",  # DOUBLE SUPERSET
    "\u22D6": "\u22D7",  # LESS-THAN WITH DOT
    "\u22D7": "\u22D6",  # GREATER-THAN WITH DOT
    "\u22D8": "\u22D9",  # VERY MUCH LESS-THAN
    "\u22D9": "\u22D8",  # VERY MUCH GREATER-THAN
    "\u22DA": "\u22DB",  # LESS-THAN EQUAL TO OR GREATER-THAN
    "\u22DB": "\u22DA",  # GREATER-THAN EQUAL TO OR LESS-THAN
    "\u22DC": "\u22DD",  # EQUAL TO OR LESS-THAN
    "\u22DD": "\u22DC",  # EQUAL TO OR GREATER-THAN
    "\u22DE": "\u22DF",  # EQUAL TO OR PRECEDES
    "\u22DF": "\u22DE",  # EQUAL TO OR SUCCEEDS
    "\u22E0": "\u22E1",  # [BEST FIT] DOES NOT PRECEDE OR EQUAL
    "\u22E1": "\u22E0",  # [BEST FIT] DOES NOT SUCCEED OR EQUAL
    "\u22E2": "\u22E3",  # [BEST FIT] NOT SQUARE IMAGE OF OR EQUAL TO
    "\u22E3": "\u22E2",  # [BEST FIT] NOT SQUARE ORIGINAL OF OR EQUAL TO
    "\u22E4": "\u22E5",  # [BEST FIT] SQUARE IMAGE OF OR NOT EQUAL TO
    "\u22E5": "\u22E4",  # [BEST FIT] SQUARE ORIGINAL OF OR NOT EQUAL TO
    "\u22E6": "\u22E7",  # [BEST FIT] LESS-THAN BUT NOT EQUIVALENT TO
    "\u22E7": "\u22E6",  # [BEST FIT] GREATER-THAN BUT NOT EQUIVALENT TO
    "\u22E8": "\u22E9",  # [BEST FIT] PRECEDES BUT NOT EQUIVALENT TO
    "\u22E9": "\u22E8",  # [BEST FIT] SUCCEEDS BUT NOT EQUIVALENT TO
    "\u22EA": "\u22EB",  # [BEST FIT] NOT NORMAL SUBGROUP OF
    "\u22EB": "\u22EA",  # [BEST FIT] DOES NOT CONTAIN AS NORMAL SUBGROUP
    "\u22EC": "\u22ED",  # [BEST FIT] NOT NORMAL SUBGROUP OF OR EQUAL TO
    "\u22ED": "\u22EC",  # [BEST FIT] DOES NOT CONTAIN AS NORMAL SUBGROUP OR EQUAL
    "\u22F0": "\u22F1",  # UP RIGHT DIAGONAL ELLIPSIS
    "\u22F1": "\u22F0",  # DOWN RIGHT DIAGONAL ELLIPSIS
    "\u22F2": "\u22FA",  # ELEMENT OF WITH LONG HORIZONTAL STROKE
    "\u22F3": "\u22FB",  # ELEMENT OF WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22F4": "\u22FC",  # SMALL ELEMENT OF WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22F6": "\u22FD",  # ELEMENT OF WITH OVERBAR
    "\u22F7": "\u22FE",  # SMALL ELEMENT OF WITH OVERBAR
    "\u22FA": "\u22F2",  # CONTAINS WITH LONG HORIZONTAL STROKE
    "\u22FB": "\u22F3",  # CONTAINS WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22FC": "\u22F4",  # SMALL CONTAINS WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22FD": "\u22F6",  # CONTAINS WITH OVERBAR
    "\u22FE": "\u22F7",  # SMALL CONTAINS WITH OVERBAR
    "\u2308": "\u2309",  # LEFT CEILING
    "\u2309": "\u2308",  # RIGHT CEILING
    "\u230A": "\u230B",  # LEFT FLOOR
    "\u230B": "\u230A",  # RIGHT FLOOR
    "\u2329": "\u232A",  # LEFT-POINTING ANGLE BRACKET
    "\u232A": "\u2329",  # RIGHT-POINTING ANGLE BRACKET
    "\u2768": "\u2769",  # MEDIUM LEFT PARENTHESIS ORNAMENT
    "\u2769": "\u2768",  # MEDIUM RIGHT PARENTHESIS ORNAMENT
    "\u276A": "\u276B",  # MEDIUM FLATTENED LEFT PARENTHESIS ORNAMENT
    "\u276B": "\u276A",  # MEDIUM FLATTENED RIGHT PARENTHESIS ORNAMENT
    "\u276C": "\u276D",  # MEDIUM LEFT-POINTING ANGLE BRACKET ORNAMENT
    "\u276D": "\u276C",  # MEDIUM RIGHT-POINTING ANGLE BRACKET ORNAMENT
    "\u276E": "\u276F",  # HEAVY LEFT-POINTING ANGLE QUOTATION MARK ORNAMENT
    "\u276F": "\u276E",  # HEAVY RIGHT-POINTING ANGLE QUOTATION MARK ORNAMENT
    "\u2770": "\u2771",  # HEAVY LEFT-POINTING ANGLE BRACKET ORNAMENT
    "\u2771": "\u2770",  # HEAVY RIGHT-POINTING ANGLE BRACKET ORNAMENT
    "\u2772": "\u2773",  # LIGHT LEFT TORTOISE SHELL BRACKET ORNAMENT
    "\u2773": "\u2772",  # LIGHT RIGHT TORTOISE SHELL BRACKET ORNAMENT
    "\u2774": "\u2775",  # MEDIUM LEFT CURLY BRACKET ORNAMENT
    "\u2775": "\u2774",  # MEDIUM RIGHT CURLY BRACKET ORNAMENT
    "\u27C3": "\u27C4",  # OPEN SUBSET
    "\u27C4": "\u27C3",  # OPEN SUPERSET
    "\u27C5": "\u27C6",  # LEFT S-SHAPED BAG DELIMITER
    "\u27C6": "\u27C5",  # RIGHT S-SHAPED BAG DELIMITER
    "\u27C8": "\u27C9",  # REVERSE SOLIDUS PRECEDING SUBSET
    "\u27C9": "\u27C8",  # SUPERSET PRECEDING SOLIDUS
    "\u27CB": "\u27CD",  # MATHEMATICAL RISING DIAGONAL
    "\u27CD": "\u27CB",  # MATHEMATICAL FALLING DIAGONAL
    "\u27D5": "\u27D6",  # LEFT OUTER JOIN
    "\u27D6": "\u27D5",  # RIGHT OUTER JOIN
    "\u27DC": "\u22B8",  # LEFT MULTIMAP
    "\u27DD": "\u27DE",  # LONG RIGHT TACK
    "\u27DE": "\u27DD",  # LONG LEFT TACK
    "\u27E2": "\u27E3",  # WHITE CONCAVE-SIDED DIAMOND WITH LEFTWARDS TICK
    "\u27E3": "\u27E2",  # WHITE CONCAVE-SIDED DIAMOND WITH RIGHTWARDS TICK
    "\u27E4": "\u27E5",  # WHITE SQUARE WITH LEFTWARDS TICK
    "\u27E5": "\u27E4",  # WHITE SQUARE WITH RIGHTWARDS TICK
    "\u27E6": "\u27E7",  # MATHEMATICAL LEFT WHITE SQUARE BRACKET
    "\u27E7": "\u27E6",  # MATHEMATICAL RIGHT WHITE SQUARE BRACKET
    "\u27E8": "\u27E9",  # MATHEMATICAL LEFT ANGLE BRACKET
    "\u27E9": "\u27E8",  # MATHEMATICAL RIGHT ANGLE BRACKET
    "\u27EA": "\u27EB",  # MATHEMATICAL LEFT DOUBLE ANGLE BRACKET
    "\u27EB": "\u27EA",  # MATHEMATICAL RIGHT DOUBLE ANGLE BRACKET
    "\u27EC": "\u27ED",  # MATHEMATICAL LEFT WHITE TORTOISE SHELL BRACKET
    "\u27ED": "\u27EC",  # MATHEMATICAL RIGHT WHITE TORTOISE SHELL BRACKET
    "\u27EE": "\u27EF",  # MATHEMATICAL LEFT FLATTENED PARENTHESIS
    "\u27EF": "\u27EE",  # MATHEMATICAL RIGHT FLATTENED PARENTHESIS
    "\u2983": "\u2984",  # LEFT WHITE CURLY BRACKET
    "\u2984": "\u2983",  # RIGHT WHITE CURLY BRACKET
    "\u2985": "\u2986",  # LEFT WHITE PARENTHESIS
    "\u2986": "\u2985",  # RIGHT WHITE PARENTHESIS
    "\u2987": "\u2988",  # Z NOTATION LEFT IMAGE BRACKET
    "\u2988": "\u2987",  # Z NOTATION RIGHT IMAGE BRACKET
    "\u2989": "\u298A",  # Z NOTATION LEFT BINDING BRACKET
    "\u298A": "\u2989",  # Z NOTATION RIGHT BINDING BRACKET
    "\u298B": "\u298C",  # LEFT SQUARE BRACKET WITH UNDERBAR
    "\u298C": "\u298B",  # RIGHT SQUARE BRACKET WITH UNDERBAR
    "\u298D": "\u2990",  # LEFT SQUARE BRACKET WITH TICK IN TOP CORNER
    "\u298E": "\u298F",  # RIGHT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    "\u298F": "\u298E",  # LEFT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    "\u2990": "\u298D",  # RIGHT SQUARE BRACKET WITH TICK IN TOP CORNER
    "\u2991": "\u2992",  # LEFT ANGLE BRACKET WITH DOT
    "\u2992": "\u2991",  # RIGHT ANGLE BRACKET WITH DOT
    "\u2993": "\u2994",  # LEFT ARC LESS-THAN BRACKET
    "\u2994": "\u2993",  # RIGHT ARC GREATER-THAN BRACKET
    "\u2995": "\u2996",  # DOUBLE LEFT ARC GREATER-THAN BRACKET
    "\u2996": "\u2995",  # DOUBLE RIGHT ARC LESS-THAN BRACKET
    "\u2997": "\u2998",  # LEFT BLACK TORTOISE SHELL BRACKET
    "\u2998": "\u2997",  # RIGHT BLACK TORTOISE SHELL BRACKET
    "\u299B": "\u2221",  # MEASURED ANGLE OPENING LEFT
    "\u29A0": "\u2222",  # SPHERICAL ANGLE OPENING LEFT
    "\u29A3": "\u2220",  # REVERSED ANGLE
    "\u29A4": "\u29A5",  # ANGLE WITH UNDERBAR
    "\u29A5": "\u29A4",  # REVERSED ANGLE WITH UNDERBAR
    "\u29A8": "\u29A9",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING UP AND RIGHT
    "\u29A9": "\u29A8",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING UP AND LEFT
    "\u29AA": "\u29AB",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING DOWN AND RIGHT
    "\u29AB": "\u29AA",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING DOWN AND LEFT
    "\u29AC": "\u29AD",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING RIGHT AND UP
    "\u29AD": "\u29AC",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING LEFT AND UP
    "\u29AE": "\u29AF",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING RIGHT AND DOWN
    "\u29AF": "\u29AE",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING LEFT AND DOWN
    "\u29B8": "\u2298",  # CIRCLED REVERSE SOLIDUS
    "\u29C0": "\u29C1",  # CIRCLED LESS-THAN
    "\u29C1": "\u29C0",  # CIRCLED GREATER-THAN
    "\u29C4": "\u29C5",  # SQUARED RISING DIAGONAL SLASH
    "\u29C5": "\u29C4",  # SQUARED FALLING DIAGONAL SLASH
    "\u29CF": "\u29D0",  # LEFT TRIANGLE BESIDE VERTICAL BAR
    "\u29D0": "\u29CF",  # VERTICAL BAR BESIDE RIGHT TRIANGLE
    "\u29D1": "\u29D2",  # BOWTIE WITH LEFT HALF BLACK
    "\u29D2": "\u29D1",  # BOWTIE WITH RIGHT HALF BLACK
    "\u29D4": "\u29D5",  # TIMES WITH LEFT HALF BLACK
    "\u29D5": "\u29D4",  # TIMES WITH RIGHT HALF BLACK
    "\u29D8": "\u29D9",  # LEFT WIGGLY FENCE
    "\u29D9": "\u29D8",  # RIGHT WIGGLY FENCE
    "\u29DA": "\u29DB",  # LEFT DOUBLE WIGGLY FENCE
    "\u29DB": "\u29DA",  # RIGHT DOUBLE WIGGLY FENCE
    "\u29E8": "\u29E9",  # DOWN-POINTING TRIANGLE WITH LEFT HALF BLACK
    "\u29E9": "\u29E8",  # DOWN-POINTING TRIANGLE WITH RIGHT HALF BLACK
    "\u29F5": "\u2215",  # REVERSE SOLIDUS OPERATOR
    "\u29F8": "\u29F9",  # BIG SOLIDUS
    "\u29F9": "\u29F8",  # BIG REVERSE SOLIDUS
    "\u29FC": "\u29FD",  # LEFT-POINTING CURVED ANGLE BRACKET
    "\u29FD": "\u29FC",  # RIGHT-POINTING CURVED ANGLE BRACKET
    "\u2A2B": "\u2A2C",  # MINUS SIGN WITH FALLING DOTS
    "\u2A2C": "\u2A2B",  # MINUS SIGN WITH RISING DOTS
    "\u2A2D": "\u2A2E",  # PLUS SIGN IN LEFT HALF CIRCLE
    "\u2A2E": "\u2A2D",  # PLUS SIGN IN RIGHT HALF CIRCLE
    "\u2A34": "\u2A35",  # MULTIPLICATION SIGN IN LEFT HALF CIRCLE
    "\u2A35": "\u2A34",  # MULTIPLICATION SIGN IN RIGHT HALF CIRCLE
    "\u2A3C": "\u2A3D",  # INTERIOR PRODUCT
    "\u2A3D": "\u2A3C",  # RIGHTHAND INTERIOR PRODUCT
    "\u2A64": "\u2A65",  # Z NOTATION DOMAIN ANTIRESTRICTION
    "\u2A65": "\u2A64",  # Z NOTATION RANGE ANTIRESTRICTION
    "\u2A79": "\u2A7A",  # LESS-THAN WITH CIRCLE INSIDE
    "\u2A7A": "\u2A79",  # GREATER-THAN WITH CIRCLE INSIDE
    "\u2A7B": "\u2A7C",  # [BEST FIT] LESS-THAN WITH QUESTION MARK ABOVE
    "\u2A7C": "\u2A7B",  # [BEST FIT] GREATER-THAN WITH QUESTION MARK ABOVE
    "\u2A7D": "\u2A7E",  # LESS-THAN OR SLANTED EQUAL TO
    "\u2A7E": "\u2A7D",  # GREATER-THAN OR SLANTED EQUAL TO
    "\u2A7F": "\u2A80",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT INSIDE
    "\u2A80": "\u2A7F",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT INSIDE
    "\u2A81": "\u2A82",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT ABOVE
    "\u2A82": "\u2A81",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT ABOVE
    "\u2A83": "\u2A84",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT ABOVE RIGHT
    "\u2A84": "\u2A83",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT ABOVE LEFT
    "\u2A85": "\u2A86",  # [BEST FIT] LESS-THAN OR APPROXIMATE
    "\u2A86": "\u2A85",  # [BEST FIT] GREATER-THAN OR APPROXIMATE
    "\u2A87": "\u2A88",  # [BEST FIT] LESS-THAN AND SINGLE-LINE NOT EQUAL TO
    "\u2A88": "\u2A87",  # [BEST FIT] GREATER-THAN AND SINGLE-LINE NOT EQUAL TO
    "\u2A89": "\u2A8A",  # [BEST FIT] LESS-THAN AND NOT APPROXIMATE
    "\u2A8A": "\u2A89",  # [BEST FIT] GREATER-THAN AND NOT APPROXIMATE
    "\u2A8B": "\u2A8C",  # LESS-THAN ABOVE DOUBLE-LINE EQUAL ABOVE GREATER-THAN
    "\u2A8C": "\u2A8B",  # GREATER-THAN ABOVE DOUBLE-LINE EQUAL ABOVE LESS-THAN
    "\u2A8D": "\u2A8E",  # [BEST FIT] LESS-THAN ABOVE SIMILAR OR EQUAL
    "\u2A8E": "\u2A8D",  # [BEST FIT] GREATER-THAN ABOVE SIMILAR OR EQUAL
    "\u2A8F": "\u2A90",  # [BEST FIT] LESS-THAN ABOVE SIMILAR ABOVE GREATER-THAN
    "\u2A90": "\u2A8F",  # [BEST FIT] GREATER-THAN ABOVE SIMILAR ABOVE LESS-THAN
    "\u2A91": "\u2A92",  # LESS-THAN ABOVE GREATER-THAN ABOVE DOUBLE-LINE EQUAL
    "\u2A92": "\u2A91",  # GREATER-THAN ABOVE LESS-THAN ABOVE DOUBLE-LINE EQUAL
    "\u2A93": "\u2A94",  # LESS-THAN ABOVE SLANTED EQUAL ABOVE GREATER-THAN ABOVE SLANTED EQUAL
    "\u2A94": "\u2A93",  # GREATER-THAN ABOVE SLANTED EQUAL ABOVE LESS-THAN ABOVE SLANTED EQUAL
    "\u2A95": "\u2A96",  # SLANTED EQUAL TO OR LESS-THAN
    "\u2A96": "\u2A95",  # SLANTED EQUAL TO OR GREATER-THAN
    "\u2A97": "\u2A98",  # SLANTED EQUAL TO OR LESS-THAN WITH DOT INSIDE
    "\u2A98": "\u2A97",  # SLANTED EQUAL TO OR GREATER-THAN WITH DOT INSIDE
    "\u2A99": "\u2A9A",  # DOUBLE-LINE EQUAL TO OR LESS-THAN
    "\u2A9A": "\u2A99",  # DOUBLE-LINE EQUAL TO OR GREATER-THAN
    "\u2A9B": "\u2A9C",  # DOUBLE-LINE SLANTED EQUAL TO OR LESS-THAN
    "\u2A9C": "\u2A9B",  # DOUBLE-LINE SLANTED EQUAL TO OR GREATER-THAN
    "\u2A9D": "\u2A9E",  # [BEST FIT] SIMILAR OR LESS-THAN
    "\u2A9E": "\u2A9D",  # [BEST FIT] SIMILAR OR GREATER-THAN
    "\u2A9F": "\u2AA0",  # [BEST FIT] SIMILAR ABOVE LESS-THAN ABOVE EQUALS SIGN
    "\u2AA0": "\u2A9F",  # [BEST FIT] SIMILAR ABOVE GREATER-THAN ABOVE EQUALS SIGN
    "\u2AA1": "\u2AA2",  # DOUBLE NESTED LESS-THAN
    "\u2AA2": "\u2AA1",  # DOUBLE NESTED GREATER-THAN
    "\u2AA6": "\u2AA7",  # LESS-THAN CLOSED BY CURVE
    "\u2AA7": "\u2AA6",  # GREATER-THAN CLOSED BY CURVE
    "\u2AA8": "\u2AA9",  # LESS-THAN CLOSED BY CURVE ABOVE SLANTED EQUAL
    "\u2AA9": "\u2AA8",  # GREATER-THAN CLOSED BY CURVE ABOVE SLANTED EQUAL
    "\u2AAA": "\u2AAB",  # SMALLER THAN
    "\u2AAB": "\u2AAA",  # LARGER THAN
    "\u2AAC": "\u2AAD",  # SMALLER THAN OR EQUAL TO
    "\u2AAD": "\u2AAC",  # LARGER THAN OR EQUAL TO
    "\u2AAF": "\u2AB0",  # PRECEDES ABOVE SINGLE-LINE EQUALS SIGN
    "\u2AB0": "\u2AAF",  # SUCCEEDS ABOVE SINGLE-LINE EQUALS SIGN
    "\u2AB1": "\u2AB2",  # [BEST FIT] PRECEDES ABOVE SINGLE-LINE NOT EQUAL TO
    "\u2AB2": "\u2AB1",  # [BEST FIT] SUCCEEDS ABOVE SINGLE-LINE NOT EQUAL TO
    "\u2AB3": "\u2AB4",  # PRECEDES ABOVE EQUALS SIGN
    "\u2AB4": "\u2AB3",  # SUCCEEDS ABOVE EQUALS SIGN
    "\u2AB5": "\u2AB6",  # [BEST FIT] PRECEDES ABOVE NOT EQUAL TO
    "\u2AB6": "\u2AB5",  # [BEST FIT] SUCCEEDS ABOVE NOT EQUAL TO
    "\u2AB7": "\u2AB8",  # [BEST FIT] PRECEDES ABOVE ALMOST EQUAL TO
    "\u2AB8": "\u2AB7",  # [BEST FIT] SUCCEEDS ABOVE ALMOST EQUAL TO
    "\u2AB9": "\u2ABA",  # [BEST FIT] PRECEDES ABOVE NOT ALMOST EQUAL TO
    "\u2ABA": "\u2AB9",  # [BEST FIT] SUCCEEDS ABOVE NOT ALMOST EQUAL TO
    "\u2ABB": "\u2ABC",  # DOUBLE PRECEDES
    "\u2ABC": "\u2ABB",  # DOUBLE SUCCEEDS
    "\u2ABD": "\u2ABE",  # SUBSET WITH DOT
    "\u2ABE": "\u2ABD",  # SUPERSET WITH DOT
    "\u2ABF": "\u2AC0",  # SUBSET WITH PLUS SIGN BELOW
    "\u2AC0": "\u2ABF",  # SUPERSET WITH PLUS SIGN BELOW
    "\u2AC1": "\u2AC2",  # SUBSET WITH MULTIPLICATION SIGN BELOW
    "\u2AC2": "\u2AC1",  # SUPERSET WITH MULTIPLICATION SIGN BELOW
    "\u2AC3": "\u2AC4",  # SUBSET OF OR EQUAL TO WITH DOT ABOVE
    "\u2AC4": "\u2AC3",  # SUPERSET OF OR EQUAL TO WITH DOT ABOVE
    "\u2AC5": "\u2AC6",  # SUBSET OF ABOVE EQUALS SIGN
    "\u2AC6": "\u2AC5",  # SUPERSET OF ABOVE EQUALS SIGN
    "\u2AC7": "\u2AC8",  # [BEST FIT] SUBSET OF ABOVE TILDE OPERATOR
    "\u2AC8": "\u2AC7",  # [BEST FIT] SUPERSET OF ABOVE TILDE OPERATOR
    "\u2AC9": "\u2ACA",  # [BEST FIT] SUBSET OF ABOVE ALMOST EQUAL TO
    "\u2ACA": "\u2AC9",  # [BEST FIT] SUPERSET OF ABOVE ALMOST EQUAL TO
    "\u2ACB": "\u2ACC",  # [BEST FIT] SUBSET OF ABOVE NOT EQUAL TO
    "\u2ACC": "\u2ACB",  # [BEST FIT] SUPERSET OF ABOVE NOT EQUAL TO
    "\u2ACD": "\u2ACE",  # SQUARE LEFT OPEN BOX OPERATOR
    "\u2ACE": "\u2ACD",  # SQUARE RIGHT OPEN BOX OPERATOR
    "\u2ACF": "\u2AD0",  # CLOSED SUBSET
    "\u2AD0": "\u2ACF",  # CLOSED SUPERSET
    "\u2AD1": "\u2AD2",  # CLOSED SUBSET OR EQUAL TO
    "\u2AD2": "\u2AD1",  # CLOSED SUPERSET OR EQUAL TO
    "\u2AD3": "\u2AD4",  # SUBSET ABOVE SUPERSET
    "\u2AD4": "\u2AD3",  # SUPERSET ABOVE SUBSET
    "\u2AD5": "\u2AD6",  # SUBSET ABOVE SUBSET
    "\u2AD6": "\u2AD5",  # SUPERSET ABOVE SUPERSET
    "\u2ADE": "\u22A6",  # SHORT LEFT TACK
    "\u2AE3": "\u22A9",  # DOUBLE VERTICAL BAR LEFT TURNSTILE
    "\u2AE4": "\u22A8",  # VERTICAL BAR DOUBLE LEFT TURNSTILE
    "\u2AE5": "\u22AB",  # DOUBLE VERTICAL BAR DOUBLE LEFT TURNSTILE
    "\u2AEC": "\u2AED",  # DOUBLE STROKE NOT SIGN
    "\u2AED": "\u2AEC",  # REVERSED DOUBLE STROKE NOT SIGN
    "\u2AEE": "\u2224",  # DOES NOT DIVIDE WITH REVERSED NEGATION SLASH
    "\u2AF7": "\u2AF8",  # TRIPLE NESTED LESS-THAN
    "\u2AF8": "\u2AF7",  # TRIPLE NESTED GREATER-THAN
    "\u2AF9": "\u2AFA",  # DOUBLE-LINE SLANTED LESS-THAN OR EQUAL TO
    "\u2AFA": "\u2AF9",  # DOUBLE-LINE SLANTED GREATER-THAN OR EQUAL TO
    "\u2BFE": "\u221F",  # REVERSED RIGHT ANGLE
    "\u2E02": "\u2E03",  # LEFT SUBSTITUTION BRACKET
    "\u2E03": "\u2E02",  # RIGHT SUBSTITUTION BRACKET
    "\u2E04": "\u2E05",  # LEFT DOTTED SUBSTITUTION BRACKET
    "\u2E05": "\u2E04",  # RIGHT DOTTED SUBSTITUTION BRACKET
    "\u2E09": "\u2E0A",  # LEFT TRANSPOSITION BRACKET
    "\u2E0A": "\u2E09",  # RIGHT TRANSPOSITION BRACKET
    "\u2E0C": "\u2E0D",  # LEFT RAISED OMISSION BRACKET
    "\u2E0D": "\u2E0C",  # RIGHT RAISED OMISSION BRACKET
    "\u2E1C": "\u2E1D",  # LEFT LOW PARAPHRASE BRACKET
    "\u2E1D": "\u2E1C",  # RIGHT LOW PARAPHRASE BRACKET
    "\u2E20": "\u2E21",  # LEFT VERTICAL BAR WITH QUILL
    "\u2E21": "\u2E20",  # RIGHT VERTICAL BAR WITH QUILL
    "\u2E22": "\u2E23",  # TOP LEFT HALF BRACKET
    "\u2E23": "\u2E22",  # TOP RIGHT HALF BRACKET
    "\u2E24": "\u2E25",  # BOTTOM LEFT HALF BRACKET
    "\u2E25": "\u2E24",  # BOTTOM RIGHT HALF BRACKET
    "\u2E26": "\u2E27",  # LEFT SIDEWAYS U BRACKET
    "\u2E27": "\u2E26",  # RIGHT SIDEWAYS U BRACKET
    "\u2E28": "\u2E29",  # LEFT DOUBLE PARENTHESIS
    "\u2E29": "\u2E28",  # RIGHT DOUBLE PARENTHESIS
    "\u3008": "\u3009",  # LEFT ANGLE BRACKET
    "\u3009": "\u3008",  # RIGHT ANGLE BRACKET
    "\u300A": "\u300B",  # LEFT DOUBLE ANGLE BRACKET
    "\u300B": "\u300A",  # RIGHT DOUBLE ANGLE BRACKET
    "\u300C": "\u300D",  # [BEST FIT] LEFT CORNER BRACKET
    "\u300D": "\u300C",  # [BEST FIT] RIGHT CORNER BRACKET
    "\u300E": "\u300F",  # [BEST FIT] LEFT WHITE CORNER BRACKET
    "\u300F": "\u300E",  # [BEST FIT] RIGHT WHITE CORNER BRACKET
    "\u3010": "\u3011",  # LEFT BLACK LENTICULAR BRACKET
    "\u3011": "\u3010",  # RIGHT BLACK LENTICULAR BRACKET
    "\u3014": "\u3015",  # LEFT TORTOISE SHELL BRACKET
    "\u3015": "\u3014",  # RIGHT TORTOISE SHELL BRACKET
    "\u3016": "\u3017",  # LEFT WHITE LENTICULAR BRACKET
    "\u3017": "\u3016",  # RIGHT WHITE LENTICULAR BRACKET
    "\u3018": "\u3019",  # LEFT WHITE TORTOISE SHELL BRACKET
    "\u3019": "\u3018",  # RIGHT WHITE TORTOISE SHELL BRACKET
    "\u301A": "\u301B",  # LEFT WHITE SQUARE BRACKET
    "\u301B": "\u301A",  # RIGHT WHITE SQUARE BRACKET
    "\uFE59": "\uFE5A",  # SMALL LEFT PARENTHESIS
    "\uFE5A": "\uFE59",  # SMALL RIGHT PARENTHESIS
    "\uFE5B": "\uFE5C",  # SMALL LEFT CURLY BRACKET
    "\uFE5C": "\uFE5B",  # SMALL RIGHT CURLY BRACKET
    "\uFE5D": "\uFE5E",  # SMALL LEFT TORTOISE SHELL BRACKET
    "\uFE5E": "\uFE5D",  # SMALL RIGHT TORTOISE SHELL BRACKET
    "\uFE64": "\uFE65",  # SMALL LESS-THAN SIGN
    "\uFE65": "\uFE64",  # SMALL GREATER-THAN SIGN
    "\uFF08": "\uFF09",  # FULLWIDTH LEFT PARENTHESIS
    "\uFF09": "\uFF08",  # FULLWIDTH RIGHT PARENTHESIS
    "\uFF1C": "\uFF1E",  # FULLWIDTH LESS-THAN SIGN
    "\uFF1E": "\uFF1C",  # FULLWIDTH GREATER-THAN SIGN
    "\uFF3B": "\uFF3D",  # FULLWIDTH LEFT SQUARE BRACKET
    "\uFF3D": "\uFF3B",  # FULLWIDTH RIGHT SQUARE BRACKET
    "\uFF5B": "\uFF5D",  # FULLWIDTH LEFT CURLY BRACKET
    "\uFF5D": "\uFF5B",  # FULLWIDTH RIGHT CURLY BRACKET
    "\uFF5F": "\uFF60",  # FULLWIDTH LEFT WHITE PARENTHESIS
    "\uFF60": "\uFF5F",  # FULLWIDTH RIGHT WHITE PARENTHESIS
    "\uFF62": "\uFF63",  # [BEST FIT] HALFWIDTH LEFT CORNER BRACKET
    "\uFF63": "\uFF62",  # [BEST FIT] HALFWIDTH RIGHT CORNER BRACKET
}
