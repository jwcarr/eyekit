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
    "\u003c": "\u003e",  # LESS-THAN SIGN
    "\u003e": "\u003c",  # GREATER-THAN SIGN
    "\u005b": "\u005d",  # LEFT SQUARE BRACKET
    "\u005d": "\u005b",  # RIGHT SQUARE BRACKET
    "\u007b": "\u007d",  # LEFT CURLY BRACKET
    "\u007d": "\u007b",  # RIGHT CURLY BRACKET
    "\u00ab": "\u00bb",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\u00bb": "\u00ab",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\u0f3a": "\u0f3b",  # TIBETAN MARK GUG RTAGS GYON
    "\u0f3b": "\u0f3a",  # TIBETAN MARK GUG RTAGS GYAS
    "\u0f3c": "\u0f3d",  # TIBETAN MARK ANG KHANG GYON
    "\u0f3d": "\u0f3c",  # TIBETAN MARK ANG KHANG GYAS
    "\u169b": "\u169c",  # OGHAM FEATHER MARK
    "\u169c": "\u169b",  # OGHAM REVERSED FEATHER MARK
    "\u2039": "\u203a",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    "\u203a": "\u2039",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    "\u2045": "\u2046",  # LEFT SQUARE BRACKET WITH QUILL
    "\u2046": "\u2045",  # RIGHT SQUARE BRACKET WITH QUILL
    "\u207d": "\u207e",  # SUPERSCRIPT LEFT PARENTHESIS
    "\u207e": "\u207d",  # SUPERSCRIPT RIGHT PARENTHESIS
    "\u208d": "\u208e",  # SUBSCRIPT LEFT PARENTHESIS
    "\u208e": "\u208d",  # SUBSCRIPT RIGHT PARENTHESIS
    "\u2208": "\u220b",  # ELEMENT OF
    "\u2209": "\u220c",  # NOT AN ELEMENT OF
    "\u220a": "\u220d",  # SMALL ELEMENT OF
    "\u220b": "\u2208",  # CONTAINS AS MEMBER
    "\u220c": "\u2209",  # DOES NOT CONTAIN AS MEMBER
    "\u220d": "\u220a",  # SMALL CONTAINS AS MEMBER
    "\u2215": "\u29f5",  # DIVISION SLASH
    "\u221f": "\u2bfe",  # RIGHT ANGLE
    "\u2220": "\u29a3",  # ANGLE
    "\u2221": "\u299b",  # MEASURED ANGLE
    "\u2222": "\u29a0",  # SPHERICAL ANGLE
    "\u2224": "\u2aee",  # DOES NOT DIVIDE
    "\u223c": "\u223d",  # TILDE OPERATOR
    "\u223d": "\u223c",  # REVERSED TILDE
    "\u2243": "\u22cd",  # ASYMPTOTICALLY EQUAL TO
    "\u2245": "\u224c",  # APPROXIMATELY EQUAL TO
    "\u224c": "\u2245",  # ALL EQUAL TO
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
    "\u226a": "\u226b",  # MUCH LESS-THAN
    "\u226b": "\u226a",  # MUCH GREATER-THAN
    "\u226e": "\u226f",  # [BEST FIT] NOT LESS-THAN
    "\u226f": "\u226e",  # [BEST FIT] NOT GREATER-THAN
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
    "\u227a": "\u227b",  # PRECEDES
    "\u227b": "\u227a",  # SUCCEEDS
    "\u227c": "\u227d",  # PRECEDES OR EQUAL TO
    "\u227d": "\u227c",  # SUCCEEDS OR EQUAL TO
    "\u227e": "\u227f",  # [BEST FIT] PRECEDES OR EQUIVALENT TO
    "\u227f": "\u227e",  # [BEST FIT] SUCCEEDS OR EQUIVALENT TO
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
    "\u228a": "\u228b",  # [BEST FIT] SUBSET OF WITH NOT EQUAL TO
    "\u228b": "\u228a",  # [BEST FIT] SUPERSET OF WITH NOT EQUAL TO
    "\u228f": "\u2290",  # SQUARE IMAGE OF
    "\u2290": "\u228f",  # SQUARE ORIGINAL OF
    "\u2291": "\u2292",  # SQUARE IMAGE OF OR EQUAL TO
    "\u2292": "\u2291",  # SQUARE ORIGINAL OF OR EQUAL TO
    "\u2298": "\u29b8",  # CIRCLED DIVISION SLASH
    "\u22a2": "\u22a3",  # RIGHT TACK
    "\u22a3": "\u22a2",  # LEFT TACK
    "\u22a6": "\u2ade",  # ASSERTION
    "\u22a8": "\u2ae4",  # TRUE
    "\u22a9": "\u2ae3",  # FORCES
    "\u22ab": "\u2ae5",  # DOUBLE VERTICAL BAR DOUBLE RIGHT TURNSTILE
    "\u22b0": "\u22b1",  # PRECEDES UNDER RELATION
    "\u22b1": "\u22b0",  # SUCCEEDS UNDER RELATION
    "\u22b2": "\u22b3",  # NORMAL SUBGROUP OF
    "\u22b3": "\u22b2",  # CONTAINS AS NORMAL SUBGROUP
    "\u22b4": "\u22b5",  # NORMAL SUBGROUP OF OR EQUAL TO
    "\u22b5": "\u22b4",  # CONTAINS AS NORMAL SUBGROUP OR EQUAL TO
    "\u22b6": "\u22b7",  # ORIGINAL OF
    "\u22b7": "\u22b6",  # IMAGE OF
    "\u22b8": "\u27dc",  # MULTIMAP
    "\u22c9": "\u22ca",  # LEFT NORMAL FACTOR SEMIDIRECT PRODUCT
    "\u22ca": "\u22c9",  # RIGHT NORMAL FACTOR SEMIDIRECT PRODUCT
    "\u22cb": "\u22cc",  # LEFT SEMIDIRECT PRODUCT
    "\u22cc": "\u22cb",  # RIGHT SEMIDIRECT PRODUCT
    "\u22cd": "\u2243",  # REVERSED TILDE EQUALS
    "\u22d0": "\u22d1",  # DOUBLE SUBSET
    "\u22d1": "\u22d0",  # DOUBLE SUPERSET
    "\u22d6": "\u22d7",  # LESS-THAN WITH DOT
    "\u22d7": "\u22d6",  # GREATER-THAN WITH DOT
    "\u22d8": "\u22d9",  # VERY MUCH LESS-THAN
    "\u22d9": "\u22d8",  # VERY MUCH GREATER-THAN
    "\u22da": "\u22db",  # LESS-THAN EQUAL TO OR GREATER-THAN
    "\u22db": "\u22da",  # GREATER-THAN EQUAL TO OR LESS-THAN
    "\u22dc": "\u22dd",  # EQUAL TO OR LESS-THAN
    "\u22dd": "\u22dc",  # EQUAL TO OR GREATER-THAN
    "\u22de": "\u22df",  # EQUAL TO OR PRECEDES
    "\u22df": "\u22de",  # EQUAL TO OR SUCCEEDS
    "\u22e0": "\u22e1",  # [BEST FIT] DOES NOT PRECEDE OR EQUAL
    "\u22e1": "\u22e0",  # [BEST FIT] DOES NOT SUCCEED OR EQUAL
    "\u22e2": "\u22e3",  # [BEST FIT] NOT SQUARE IMAGE OF OR EQUAL TO
    "\u22e3": "\u22e2",  # [BEST FIT] NOT SQUARE ORIGINAL OF OR EQUAL TO
    "\u22e4": "\u22e5",  # [BEST FIT] SQUARE IMAGE OF OR NOT EQUAL TO
    "\u22e5": "\u22e4",  # [BEST FIT] SQUARE ORIGINAL OF OR NOT EQUAL TO
    "\u22e6": "\u22e7",  # [BEST FIT] LESS-THAN BUT NOT EQUIVALENT TO
    "\u22e7": "\u22e6",  # [BEST FIT] GREATER-THAN BUT NOT EQUIVALENT TO
    "\u22e8": "\u22e9",  # [BEST FIT] PRECEDES BUT NOT EQUIVALENT TO
    "\u22e9": "\u22e8",  # [BEST FIT] SUCCEEDS BUT NOT EQUIVALENT TO
    "\u22ea": "\u22eb",  # [BEST FIT] NOT NORMAL SUBGROUP OF
    "\u22eb": "\u22ea",  # [BEST FIT] DOES NOT CONTAIN AS NORMAL SUBGROUP
    "\u22ec": "\u22ed",  # [BEST FIT] NOT NORMAL SUBGROUP OF OR EQUAL TO
    "\u22ed": "\u22ec",  # [BEST FIT] DOES NOT CONTAIN AS NORMAL SUBGROUP OR EQUAL
    "\u22f0": "\u22f1",  # UP RIGHT DIAGONAL ELLIPSIS
    "\u22f1": "\u22f0",  # DOWN RIGHT DIAGONAL ELLIPSIS
    "\u22f2": "\u22fa",  # ELEMENT OF WITH LONG HORIZONTAL STROKE
    "\u22f3": "\u22fb",  # ELEMENT OF WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22f4": "\u22fc",  # SMALL ELEMENT OF WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22f6": "\u22fd",  # ELEMENT OF WITH OVERBAR
    "\u22f7": "\u22fe",  # SMALL ELEMENT OF WITH OVERBAR
    "\u22fa": "\u22f2",  # CONTAINS WITH LONG HORIZONTAL STROKE
    "\u22fb": "\u22f3",  # CONTAINS WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22fc": "\u22f4",  # SMALL CONTAINS WITH VERTICAL BAR AT END OF HORIZONTAL STROKE
    "\u22fd": "\u22f6",  # CONTAINS WITH OVERBAR
    "\u22fe": "\u22f7",  # SMALL CONTAINS WITH OVERBAR
    "\u2308": "\u2309",  # LEFT CEILING
    "\u2309": "\u2308",  # RIGHT CEILING
    "\u230a": "\u230b",  # LEFT FLOOR
    "\u230b": "\u230a",  # RIGHT FLOOR
    "\u2329": "\u232a",  # LEFT-POINTING ANGLE BRACKET
    "\u232a": "\u2329",  # RIGHT-POINTING ANGLE BRACKET
    "\u2768": "\u2769",  # MEDIUM LEFT PARENTHESIS ORNAMENT
    "\u2769": "\u2768",  # MEDIUM RIGHT PARENTHESIS ORNAMENT
    "\u276a": "\u276b",  # MEDIUM FLATTENED LEFT PARENTHESIS ORNAMENT
    "\u276b": "\u276a",  # MEDIUM FLATTENED RIGHT PARENTHESIS ORNAMENT
    "\u276c": "\u276d",  # MEDIUM LEFT-POINTING ANGLE BRACKET ORNAMENT
    "\u276d": "\u276c",  # MEDIUM RIGHT-POINTING ANGLE BRACKET ORNAMENT
    "\u276e": "\u276f",  # HEAVY LEFT-POINTING ANGLE QUOTATION MARK ORNAMENT
    "\u276f": "\u276e",  # HEAVY RIGHT-POINTING ANGLE QUOTATION MARK ORNAMENT
    "\u2770": "\u2771",  # HEAVY LEFT-POINTING ANGLE BRACKET ORNAMENT
    "\u2771": "\u2770",  # HEAVY RIGHT-POINTING ANGLE BRACKET ORNAMENT
    "\u2772": "\u2773",  # LIGHT LEFT TORTOISE SHELL BRACKET ORNAMENT
    "\u2773": "\u2772",  # LIGHT RIGHT TORTOISE SHELL BRACKET ORNAMENT
    "\u2774": "\u2775",  # MEDIUM LEFT CURLY BRACKET ORNAMENT
    "\u2775": "\u2774",  # MEDIUM RIGHT CURLY BRACKET ORNAMENT
    "\u27c3": "\u27c4",  # OPEN SUBSET
    "\u27c4": "\u27c3",  # OPEN SUPERSET
    "\u27c5": "\u27c6",  # LEFT S-SHAPED BAG DELIMITER
    "\u27c6": "\u27c5",  # RIGHT S-SHAPED BAG DELIMITER
    "\u27c8": "\u27c9",  # REVERSE SOLIDUS PRECEDING SUBSET
    "\u27c9": "\u27c8",  # SUPERSET PRECEDING SOLIDUS
    "\u27cb": "\u27cd",  # MATHEMATICAL RISING DIAGONAL
    "\u27cd": "\u27cb",  # MATHEMATICAL FALLING DIAGONAL
    "\u27d5": "\u27d6",  # LEFT OUTER JOIN
    "\u27d6": "\u27d5",  # RIGHT OUTER JOIN
    "\u27dc": "\u22b8",  # LEFT MULTIMAP
    "\u27dd": "\u27de",  # LONG RIGHT TACK
    "\u27de": "\u27dd",  # LONG LEFT TACK
    "\u27e2": "\u27e3",  # WHITE CONCAVE-SIDED DIAMOND WITH LEFTWARDS TICK
    "\u27e3": "\u27e2",  # WHITE CONCAVE-SIDED DIAMOND WITH RIGHTWARDS TICK
    "\u27e4": "\u27e5",  # WHITE SQUARE WITH LEFTWARDS TICK
    "\u27e5": "\u27e4",  # WHITE SQUARE WITH RIGHTWARDS TICK
    "\u27e6": "\u27e7",  # MATHEMATICAL LEFT WHITE SQUARE BRACKET
    "\u27e7": "\u27e6",  # MATHEMATICAL RIGHT WHITE SQUARE BRACKET
    "\u27e8": "\u27e9",  # MATHEMATICAL LEFT ANGLE BRACKET
    "\u27e9": "\u27e8",  # MATHEMATICAL RIGHT ANGLE BRACKET
    "\u27ea": "\u27eb",  # MATHEMATICAL LEFT DOUBLE ANGLE BRACKET
    "\u27eb": "\u27ea",  # MATHEMATICAL RIGHT DOUBLE ANGLE BRACKET
    "\u27ec": "\u27ed",  # MATHEMATICAL LEFT WHITE TORTOISE SHELL BRACKET
    "\u27ed": "\u27ec",  # MATHEMATICAL RIGHT WHITE TORTOISE SHELL BRACKET
    "\u27ee": "\u27ef",  # MATHEMATICAL LEFT FLATTENED PARENTHESIS
    "\u27ef": "\u27ee",  # MATHEMATICAL RIGHT FLATTENED PARENTHESIS
    "\u2983": "\u2984",  # LEFT WHITE CURLY BRACKET
    "\u2984": "\u2983",  # RIGHT WHITE CURLY BRACKET
    "\u2985": "\u2986",  # LEFT WHITE PARENTHESIS
    "\u2986": "\u2985",  # RIGHT WHITE PARENTHESIS
    "\u2987": "\u2988",  # Z NOTATION LEFT IMAGE BRACKET
    "\u2988": "\u2987",  # Z NOTATION RIGHT IMAGE BRACKET
    "\u2989": "\u298a",  # Z NOTATION LEFT BINDING BRACKET
    "\u298a": "\u2989",  # Z NOTATION RIGHT BINDING BRACKET
    "\u298b": "\u298c",  # LEFT SQUARE BRACKET WITH UNDERBAR
    "\u298c": "\u298b",  # RIGHT SQUARE BRACKET WITH UNDERBAR
    "\u298d": "\u2990",  # LEFT SQUARE BRACKET WITH TICK IN TOP CORNER
    "\u298e": "\u298f",  # RIGHT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    "\u298f": "\u298e",  # LEFT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    "\u2990": "\u298d",  # RIGHT SQUARE BRACKET WITH TICK IN TOP CORNER
    "\u2991": "\u2992",  # LEFT ANGLE BRACKET WITH DOT
    "\u2992": "\u2991",  # RIGHT ANGLE BRACKET WITH DOT
    "\u2993": "\u2994",  # LEFT ARC LESS-THAN BRACKET
    "\u2994": "\u2993",  # RIGHT ARC GREATER-THAN BRACKET
    "\u2995": "\u2996",  # DOUBLE LEFT ARC GREATER-THAN BRACKET
    "\u2996": "\u2995",  # DOUBLE RIGHT ARC LESS-THAN BRACKET
    "\u2997": "\u2998",  # LEFT BLACK TORTOISE SHELL BRACKET
    "\u2998": "\u2997",  # RIGHT BLACK TORTOISE SHELL BRACKET
    "\u299b": "\u2221",  # MEASURED ANGLE OPENING LEFT
    "\u29a0": "\u2222",  # SPHERICAL ANGLE OPENING LEFT
    "\u29a3": "\u2220",  # REVERSED ANGLE
    "\u29a4": "\u29a5",  # ANGLE WITH UNDERBAR
    "\u29a5": "\u29a4",  # REVERSED ANGLE WITH UNDERBAR
    "\u29a8": "\u29a9",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING UP AND RIGHT
    "\u29a9": "\u29a8",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING UP AND LEFT
    "\u29aa": "\u29ab",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING DOWN AND RIGHT
    "\u29ab": "\u29aa",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING DOWN AND LEFT
    "\u29ac": "\u29ad",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING RIGHT AND UP
    "\u29ad": "\u29ac",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING LEFT AND UP
    "\u29ae": "\u29af",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING RIGHT AND DOWN
    "\u29af": "\u29ae",  # MEASURED ANGLE WITH OPEN ARM ENDING IN ARROW POINTING LEFT AND DOWN
    "\u29b8": "\u2298",  # CIRCLED REVERSE SOLIDUS
    "\u29c0": "\u29c1",  # CIRCLED LESS-THAN
    "\u29c1": "\u29c0",  # CIRCLED GREATER-THAN
    "\u29c4": "\u29c5",  # SQUARED RISING DIAGONAL SLASH
    "\u29c5": "\u29c4",  # SQUARED FALLING DIAGONAL SLASH
    "\u29cf": "\u29d0",  # LEFT TRIANGLE BESIDE VERTICAL BAR
    "\u29d0": "\u29cf",  # VERTICAL BAR BESIDE RIGHT TRIANGLE
    "\u29d1": "\u29d2",  # BOWTIE WITH LEFT HALF BLACK
    "\u29d2": "\u29d1",  # BOWTIE WITH RIGHT HALF BLACK
    "\u29d4": "\u29d5",  # TIMES WITH LEFT HALF BLACK
    "\u29d5": "\u29d4",  # TIMES WITH RIGHT HALF BLACK
    "\u29d8": "\u29d9",  # LEFT WIGGLY FENCE
    "\u29d9": "\u29d8",  # RIGHT WIGGLY FENCE
    "\u29da": "\u29db",  # LEFT DOUBLE WIGGLY FENCE
    "\u29db": "\u29da",  # RIGHT DOUBLE WIGGLY FENCE
    "\u29e8": "\u29e9",  # DOWN-POINTING TRIANGLE WITH LEFT HALF BLACK
    "\u29e9": "\u29e8",  # DOWN-POINTING TRIANGLE WITH RIGHT HALF BLACK
    "\u29f5": "\u2215",  # REVERSE SOLIDUS OPERATOR
    "\u29f8": "\u29f9",  # BIG SOLIDUS
    "\u29f9": "\u29f8",  # BIG REVERSE SOLIDUS
    "\u29fc": "\u29fd",  # LEFT-POINTING CURVED ANGLE BRACKET
    "\u29fd": "\u29fc",  # RIGHT-POINTING CURVED ANGLE BRACKET
    "\u2a2b": "\u2a2c",  # MINUS SIGN WITH FALLING DOTS
    "\u2a2c": "\u2a2b",  # MINUS SIGN WITH RISING DOTS
    "\u2a2d": "\u2a2e",  # PLUS SIGN IN LEFT HALF CIRCLE
    "\u2a2e": "\u2a2d",  # PLUS SIGN IN RIGHT HALF CIRCLE
    "\u2a34": "\u2a35",  # MULTIPLICATION SIGN IN LEFT HALF CIRCLE
    "\u2a35": "\u2a34",  # MULTIPLICATION SIGN IN RIGHT HALF CIRCLE
    "\u2a3c": "\u2a3d",  # INTERIOR PRODUCT
    "\u2a3d": "\u2a3c",  # RIGHTHAND INTERIOR PRODUCT
    "\u2a64": "\u2a65",  # Z NOTATION DOMAIN ANTIRESTRICTION
    "\u2a65": "\u2a64",  # Z NOTATION RANGE ANTIRESTRICTION
    "\u2a79": "\u2a7a",  # LESS-THAN WITH CIRCLE INSIDE
    "\u2a7a": "\u2a79",  # GREATER-THAN WITH CIRCLE INSIDE
    "\u2a7b": "\u2a7c",  # [BEST FIT] LESS-THAN WITH QUESTION MARK ABOVE
    "\u2a7c": "\u2a7b",  # [BEST FIT] GREATER-THAN WITH QUESTION MARK ABOVE
    "\u2a7d": "\u2a7e",  # LESS-THAN OR SLANTED EQUAL TO
    "\u2a7e": "\u2a7d",  # GREATER-THAN OR SLANTED EQUAL TO
    "\u2a7f": "\u2a80",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT INSIDE
    "\u2a80": "\u2a7f",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT INSIDE
    "\u2a81": "\u2a82",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT ABOVE
    "\u2a82": "\u2a81",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT ABOVE
    "\u2a83": "\u2a84",  # LESS-THAN OR SLANTED EQUAL TO WITH DOT ABOVE RIGHT
    "\u2a84": "\u2a83",  # GREATER-THAN OR SLANTED EQUAL TO WITH DOT ABOVE LEFT
    "\u2a85": "\u2a86",  # [BEST FIT] LESS-THAN OR APPROXIMATE
    "\u2a86": "\u2a85",  # [BEST FIT] GREATER-THAN OR APPROXIMATE
    "\u2a87": "\u2a88",  # [BEST FIT] LESS-THAN AND SINGLE-LINE NOT EQUAL TO
    "\u2a88": "\u2a87",  # [BEST FIT] GREATER-THAN AND SINGLE-LINE NOT EQUAL TO
    "\u2a89": "\u2a8a",  # [BEST FIT] LESS-THAN AND NOT APPROXIMATE
    "\u2a8a": "\u2a89",  # [BEST FIT] GREATER-THAN AND NOT APPROXIMATE
    "\u2a8b": "\u2a8c",  # LESS-THAN ABOVE DOUBLE-LINE EQUAL ABOVE GREATER-THAN
    "\u2a8c": "\u2a8b",  # GREATER-THAN ABOVE DOUBLE-LINE EQUAL ABOVE LESS-THAN
    "\u2a8d": "\u2a8e",  # [BEST FIT] LESS-THAN ABOVE SIMILAR OR EQUAL
    "\u2a8e": "\u2a8d",  # [BEST FIT] GREATER-THAN ABOVE SIMILAR OR EQUAL
    "\u2a8f": "\u2a90",  # [BEST FIT] LESS-THAN ABOVE SIMILAR ABOVE GREATER-THAN
    "\u2a90": "\u2a8f",  # [BEST FIT] GREATER-THAN ABOVE SIMILAR ABOVE LESS-THAN
    "\u2a91": "\u2a92",  # LESS-THAN ABOVE GREATER-THAN ABOVE DOUBLE-LINE EQUAL
    "\u2a92": "\u2a91",  # GREATER-THAN ABOVE LESS-THAN ABOVE DOUBLE-LINE EQUAL
    "\u2a93": "\u2a94",  # LESS-THAN ABOVE SLANTED EQUAL ABOVE GREATER-THAN ABOVE SLANTED EQUAL
    "\u2a94": "\u2a93",  # GREATER-THAN ABOVE SLANTED EQUAL ABOVE LESS-THAN ABOVE SLANTED EQUAL
    "\u2a95": "\u2a96",  # SLANTED EQUAL TO OR LESS-THAN
    "\u2a96": "\u2a95",  # SLANTED EQUAL TO OR GREATER-THAN
    "\u2a97": "\u2a98",  # SLANTED EQUAL TO OR LESS-THAN WITH DOT INSIDE
    "\u2a98": "\u2a97",  # SLANTED EQUAL TO OR GREATER-THAN WITH DOT INSIDE
    "\u2a99": "\u2a9a",  # DOUBLE-LINE EQUAL TO OR LESS-THAN
    "\u2a9a": "\u2a99",  # DOUBLE-LINE EQUAL TO OR GREATER-THAN
    "\u2a9b": "\u2a9c",  # DOUBLE-LINE SLANTED EQUAL TO OR LESS-THAN
    "\u2a9c": "\u2a9b",  # DOUBLE-LINE SLANTED EQUAL TO OR GREATER-THAN
    "\u2a9d": "\u2a9e",  # [BEST FIT] SIMILAR OR LESS-THAN
    "\u2a9e": "\u2a9d",  # [BEST FIT] SIMILAR OR GREATER-THAN
    "\u2a9f": "\u2aa0",  # [BEST FIT] SIMILAR ABOVE LESS-THAN ABOVE EQUALS SIGN
    "\u2aa0": "\u2a9f",  # [BEST FIT] SIMILAR ABOVE GREATER-THAN ABOVE EQUALS SIGN
    "\u2aa1": "\u2aa2",  # DOUBLE NESTED LESS-THAN
    "\u2aa2": "\u2aa1",  # DOUBLE NESTED GREATER-THAN
    "\u2aa6": "\u2aa7",  # LESS-THAN CLOSED BY CURVE
    "\u2aa7": "\u2aa6",  # GREATER-THAN CLOSED BY CURVE
    "\u2aa8": "\u2aa9",  # LESS-THAN CLOSED BY CURVE ABOVE SLANTED EQUAL
    "\u2aa9": "\u2aa8",  # GREATER-THAN CLOSED BY CURVE ABOVE SLANTED EQUAL
    "\u2aaa": "\u2aab",  # SMALLER THAN
    "\u2aab": "\u2aaa",  # LARGER THAN
    "\u2aac": "\u2aad",  # SMALLER THAN OR EQUAL TO
    "\u2aad": "\u2aac",  # LARGER THAN OR EQUAL TO
    "\u2aaf": "\u2ab0",  # PRECEDES ABOVE SINGLE-LINE EQUALS SIGN
    "\u2ab0": "\u2aaf",  # SUCCEEDS ABOVE SINGLE-LINE EQUALS SIGN
    "\u2ab1": "\u2ab2",  # [BEST FIT] PRECEDES ABOVE SINGLE-LINE NOT EQUAL TO
    "\u2ab2": "\u2ab1",  # [BEST FIT] SUCCEEDS ABOVE SINGLE-LINE NOT EQUAL TO
    "\u2ab3": "\u2ab4",  # PRECEDES ABOVE EQUALS SIGN
    "\u2ab4": "\u2ab3",  # SUCCEEDS ABOVE EQUALS SIGN
    "\u2ab5": "\u2ab6",  # [BEST FIT] PRECEDES ABOVE NOT EQUAL TO
    "\u2ab6": "\u2ab5",  # [BEST FIT] SUCCEEDS ABOVE NOT EQUAL TO
    "\u2ab7": "\u2ab8",  # [BEST FIT] PRECEDES ABOVE ALMOST EQUAL TO
    "\u2ab8": "\u2ab7",  # [BEST FIT] SUCCEEDS ABOVE ALMOST EQUAL TO
    "\u2ab9": "\u2aba",  # [BEST FIT] PRECEDES ABOVE NOT ALMOST EQUAL TO
    "\u2aba": "\u2ab9",  # [BEST FIT] SUCCEEDS ABOVE NOT ALMOST EQUAL TO
    "\u2abb": "\u2abc",  # DOUBLE PRECEDES
    "\u2abc": "\u2abb",  # DOUBLE SUCCEEDS
    "\u2abd": "\u2abe",  # SUBSET WITH DOT
    "\u2abe": "\u2abd",  # SUPERSET WITH DOT
    "\u2abf": "\u2ac0",  # SUBSET WITH PLUS SIGN BELOW
    "\u2ac0": "\u2abf",  # SUPERSET WITH PLUS SIGN BELOW
    "\u2ac1": "\u2ac2",  # SUBSET WITH MULTIPLICATION SIGN BELOW
    "\u2ac2": "\u2ac1",  # SUPERSET WITH MULTIPLICATION SIGN BELOW
    "\u2ac3": "\u2ac4",  # SUBSET OF OR EQUAL TO WITH DOT ABOVE
    "\u2ac4": "\u2ac3",  # SUPERSET OF OR EQUAL TO WITH DOT ABOVE
    "\u2ac5": "\u2ac6",  # SUBSET OF ABOVE EQUALS SIGN
    "\u2ac6": "\u2ac5",  # SUPERSET OF ABOVE EQUALS SIGN
    "\u2ac7": "\u2ac8",  # [BEST FIT] SUBSET OF ABOVE TILDE OPERATOR
    "\u2ac8": "\u2ac7",  # [BEST FIT] SUPERSET OF ABOVE TILDE OPERATOR
    "\u2ac9": "\u2aca",  # [BEST FIT] SUBSET OF ABOVE ALMOST EQUAL TO
    "\u2aca": "\u2ac9",  # [BEST FIT] SUPERSET OF ABOVE ALMOST EQUAL TO
    "\u2acb": "\u2acc",  # [BEST FIT] SUBSET OF ABOVE NOT EQUAL TO
    "\u2acc": "\u2acb",  # [BEST FIT] SUPERSET OF ABOVE NOT EQUAL TO
    "\u2acd": "\u2ace",  # SQUARE LEFT OPEN BOX OPERATOR
    "\u2ace": "\u2acd",  # SQUARE RIGHT OPEN BOX OPERATOR
    "\u2acf": "\u2ad0",  # CLOSED SUBSET
    "\u2ad0": "\u2acf",  # CLOSED SUPERSET
    "\u2ad1": "\u2ad2",  # CLOSED SUBSET OR EQUAL TO
    "\u2ad2": "\u2ad1",  # CLOSED SUPERSET OR EQUAL TO
    "\u2ad3": "\u2ad4",  # SUBSET ABOVE SUPERSET
    "\u2ad4": "\u2ad3",  # SUPERSET ABOVE SUBSET
    "\u2ad5": "\u2ad6",  # SUBSET ABOVE SUBSET
    "\u2ad6": "\u2ad5",  # SUPERSET ABOVE SUPERSET
    "\u2ade": "\u22a6",  # SHORT LEFT TACK
    "\u2ae3": "\u22a9",  # DOUBLE VERTICAL BAR LEFT TURNSTILE
    "\u2ae4": "\u22a8",  # VERTICAL BAR DOUBLE LEFT TURNSTILE
    "\u2ae5": "\u22ab",  # DOUBLE VERTICAL BAR DOUBLE LEFT TURNSTILE
    "\u2aec": "\u2aed",  # DOUBLE STROKE NOT SIGN
    "\u2aed": "\u2aec",  # REVERSED DOUBLE STROKE NOT SIGN
    "\u2aee": "\u2224",  # DOES NOT DIVIDE WITH REVERSED NEGATION SLASH
    "\u2af7": "\u2af8",  # TRIPLE NESTED LESS-THAN
    "\u2af8": "\u2af7",  # TRIPLE NESTED GREATER-THAN
    "\u2af9": "\u2afa",  # DOUBLE-LINE SLANTED LESS-THAN OR EQUAL TO
    "\u2afa": "\u2af9",  # DOUBLE-LINE SLANTED GREATER-THAN OR EQUAL TO
    "\u2bfe": "\u221f",  # REVERSED RIGHT ANGLE
    "\u2e02": "\u2e03",  # LEFT SUBSTITUTION BRACKET
    "\u2e03": "\u2e02",  # RIGHT SUBSTITUTION BRACKET
    "\u2e04": "\u2e05",  # LEFT DOTTED SUBSTITUTION BRACKET
    "\u2e05": "\u2e04",  # RIGHT DOTTED SUBSTITUTION BRACKET
    "\u2e09": "\u2e0a",  # LEFT TRANSPOSITION BRACKET
    "\u2e0a": "\u2e09",  # RIGHT TRANSPOSITION BRACKET
    "\u2e0c": "\u2e0d",  # LEFT RAISED OMISSION BRACKET
    "\u2e0d": "\u2e0c",  # RIGHT RAISED OMISSION BRACKET
    "\u2e1c": "\u2e1d",  # LEFT LOW PARAPHRASE BRACKET
    "\u2e1d": "\u2e1c",  # RIGHT LOW PARAPHRASE BRACKET
    "\u2e20": "\u2e21",  # LEFT VERTICAL BAR WITH QUILL
    "\u2e21": "\u2e20",  # RIGHT VERTICAL BAR WITH QUILL
    "\u2e22": "\u2e23",  # TOP LEFT HALF BRACKET
    "\u2e23": "\u2e22",  # TOP RIGHT HALF BRACKET
    "\u2e24": "\u2e25",  # BOTTOM LEFT HALF BRACKET
    "\u2e25": "\u2e24",  # BOTTOM RIGHT HALF BRACKET
    "\u2e26": "\u2e27",  # LEFT SIDEWAYS U BRACKET
    "\u2e27": "\u2e26",  # RIGHT SIDEWAYS U BRACKET
    "\u2e28": "\u2e29",  # LEFT DOUBLE PARENTHESIS
    "\u2e29": "\u2e28",  # RIGHT DOUBLE PARENTHESIS
    "\u3008": "\u3009",  # LEFT ANGLE BRACKET
    "\u3009": "\u3008",  # RIGHT ANGLE BRACKET
    "\u300a": "\u300b",  # LEFT DOUBLE ANGLE BRACKET
    "\u300b": "\u300a",  # RIGHT DOUBLE ANGLE BRACKET
    "\u300c": "\u300d",  # [BEST FIT] LEFT CORNER BRACKET
    "\u300d": "\u300c",  # [BEST FIT] RIGHT CORNER BRACKET
    "\u300e": "\u300f",  # [BEST FIT] LEFT WHITE CORNER BRACKET
    "\u300f": "\u300e",  # [BEST FIT] RIGHT WHITE CORNER BRACKET
    "\u3010": "\u3011",  # LEFT BLACK LENTICULAR BRACKET
    "\u3011": "\u3010",  # RIGHT BLACK LENTICULAR BRACKET
    "\u3014": "\u3015",  # LEFT TORTOISE SHELL BRACKET
    "\u3015": "\u3014",  # RIGHT TORTOISE SHELL BRACKET
    "\u3016": "\u3017",  # LEFT WHITE LENTICULAR BRACKET
    "\u3017": "\u3016",  # RIGHT WHITE LENTICULAR BRACKET
    "\u3018": "\u3019",  # LEFT WHITE TORTOISE SHELL BRACKET
    "\u3019": "\u3018",  # RIGHT WHITE TORTOISE SHELL BRACKET
    "\u301a": "\u301b",  # LEFT WHITE SQUARE BRACKET
    "\u301b": "\u301a",  # RIGHT WHITE SQUARE BRACKET
    "\ufe59": "\ufe5a",  # SMALL LEFT PARENTHESIS
    "\ufe5a": "\ufe59",  # SMALL RIGHT PARENTHESIS
    "\ufe5b": "\ufe5c",  # SMALL LEFT CURLY BRACKET
    "\ufe5c": "\ufe5b",  # SMALL RIGHT CURLY BRACKET
    "\ufe5d": "\ufe5e",  # SMALL LEFT TORTOISE SHELL BRACKET
    "\ufe5e": "\ufe5d",  # SMALL RIGHT TORTOISE SHELL BRACKET
    "\ufe64": "\ufe65",  # SMALL LESS-THAN SIGN
    "\ufe65": "\ufe64",  # SMALL GREATER-THAN SIGN
    "\uff08": "\uff09",  # FULLWIDTH LEFT PARENTHESIS
    "\uff09": "\uff08",  # FULLWIDTH RIGHT PARENTHESIS
    "\uff1c": "\uff1e",  # FULLWIDTH LESS-THAN SIGN
    "\uff1e": "\uff1c",  # FULLWIDTH GREATER-THAN SIGN
    "\uff3b": "\uff3d",  # FULLWIDTH LEFT SQUARE BRACKET
    "\uff3d": "\uff3b",  # FULLWIDTH RIGHT SQUARE BRACKET
    "\uff5b": "\uff5d",  # FULLWIDTH LEFT CURLY BRACKET
    "\uff5d": "\uff5b",  # FULLWIDTH RIGHT CURLY BRACKET
    "\uff5f": "\uff60",  # FULLWIDTH LEFT WHITE PARENTHESIS
    "\uff60": "\uff5f",  # FULLWIDTH RIGHT WHITE PARENTHESIS
    "\uff62": "\uff63",  # [BEST FIT] HALFWIDTH LEFT CORNER BRACKET
    "\uff63": "\uff62",  # [BEST FIT] HALFWIDTH RIGHT CORNER BRACKET
}
