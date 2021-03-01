"""

Functions for calculating common analysis measures, such as total fixation
duration or initial landing position.

"""


import numpy as _np
from .fixation import FixationSequence as _FixationSequence, Fixation as _Fixation
from .text import TextBlock as _TextBlock, InterestArea as _InterestArea


def number_of_fixations(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the total
    number of fixations on each interest area. Returns a dictionary in which the
    keys are interest area IDs and the values are counts.

    """
    if isinstance(interest_areas, _InterestArea):
        interest_areas = [interest_areas]
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    counts = {}
    for interest_area in interest_areas:
        if not isinstance(interest_area, _InterestArea):
            raise TypeError(f"{str(interest_area)} is not of type InterestArea")
        counts[interest_area.id] = 0
        for fixation in fixation_sequence.iter_without_discards():
            if fixation in interest_area:
                counts[interest_area.id] += 1
    return counts


def initial_fixation_duration(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the
    duration of the initial fixation on each interest area. Returns a
    dictionary in which the keys are interest area IDs and the values are
    initial fixation durations.

    """
    if isinstance(interest_areas, _InterestArea):
        interest_areas = [interest_areas]
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    durations = {}
    for interest_area in interest_areas:
        if not isinstance(interest_area, _InterestArea):
            raise TypeError(f"{str(interest_area)} is not of type InterestArea")
        durations[interest_area.id] = 0
        for fixation in fixation_sequence.iter_without_discards():
            if fixation in interest_area:
                durations[interest_area.id] = fixation.duration
                break
    return durations


def total_fixation_duration(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the total
    fixation duration on each interest area. Returns a dictionary in which the
    keys are interest area IDs and the values are total fixation durations.

    """
    if isinstance(interest_areas, _InterestArea):
        interest_areas = [interest_areas]
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    durations = {}
    for interest_area in interest_areas:
        if not isinstance(interest_area, _InterestArea):
            raise TypeError(f"{str(interest_area)} is not of type InterestArea")
        durations[interest_area.id] = 0
        for fixation in fixation_sequence.iter_without_discards():
            if fixation in interest_area:
                durations[interest_area.id] += fixation.duration
    return durations


def gaze_duration(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the gaze
    duration on each interest area. Gaze duration is the sum duration of all
    fixations inside an interest area until the area is exited for the first
    time. Returns a dictionary in which the keys are interest area IDs and the
    values are gaze durations.

    """
    if isinstance(interest_areas, _InterestArea):
        interest_areas = [interest_areas]
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    durations = {}
    for interest_area in interest_areas:
        if not isinstance(interest_area, _InterestArea):
            raise TypeError(f"{str(interest_area)} is not of type InterestArea")
        durations[interest_area.id] = 0
        for fixation in fixation_sequence.iter_without_discards():
            if fixation in interest_area:
                durations[interest_area.id] += fixation.duration
            elif durations[interest_area.id] > 0:
                break  # at least one previous fixation was inside the IA and this fixation is not, so break
    return durations


def initial_landing_position(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the initial
    landing position (expressed in character positions) on each interest area.
    Counting is from 1, so a 1 indicates that the fixation landed on the first
    character and so forth. If the interest area represents right-to-left
    text, the first character is the rightmost one. Returns a dictionary in
    which the keys are interest area IDs and the values are initial landing
    positions.

    """
    if isinstance(interest_areas, _InterestArea):
        interest_areas = [interest_areas]
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    positions = {}
    for interest_area in interest_areas:
        if not isinstance(interest_area, _InterestArea):
            raise TypeError(f"{str(interest_area)} is not of type InterestArea")
        positions[interest_area.id] = None
        for fixation in fixation_sequence.iter_without_discards():
            if fixation in interest_area:
                for position, char in enumerate(interest_area, 1):
                    if fixation in char:
                        positions[interest_area.id] = position
                        break
                break
    return positions


def initial_landing_distance(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the initial
    landing distance on each interest area. The initial landing distance is
    the pixel distance between the first fixation to land in an interest area
    and the left edge of that interest area (or, in the case of right-to-left
    text, the right edge). Returns a dictionary in which the keys are interest
    area IDs and the values are initial landing distances.

    """
    if isinstance(interest_areas, _InterestArea):
        interest_areas = [interest_areas]
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    positions = {}
    for interest_area in interest_areas:
        if not isinstance(interest_area, _InterestArea):
            raise TypeError(f"{str(interest_area)} is not of type InterestArea")
        positions[interest_area.id] = None
        for fixation in fixation_sequence.iter_without_discards():
            if fixation in interest_area:
                if interest_area.right_to_left:
                    positions[interest_area.id] = interest_area.onset - fixation.x
                else:
                    positions[interest_area.id] = fixation.x - interest_area.onset
                break
    return positions


def number_of_regressions(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the number
    of regressions back to each interest area after the interest area was read
    for the first time. In other words, find the first fixation to exit the
    interest area and then count how many times the reader returns to the
    interest area from the right (or from the left in the case of
    right-to-left text). Returns a dictionary in which the keys are interest
    area IDs and the values are counts.

    """
    if isinstance(interest_areas, _InterestArea):
        interest_areas = [interest_areas]
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    regression_counts = {}
    for interest_area in interest_areas:
        if not isinstance(interest_area, _InterestArea):
            raise TypeError(f"{str(interest_area)} is not of type InterestArea")
        regression_counts[interest_area.id] = 0
        entered_interest_area = False
        first_exit_index = None
        for fixation in fixation_sequence.iter_without_discards():
            if fixation in interest_area:
                entered_interest_area = True
            elif entered_interest_area:
                first_exit_index = fixation.index
                break
        if first_exit_index is None:
            continue  # IA was never exited, so there can't be any regressions back to it
        for prev_fix, curr_fix in fixation_sequence.iter_pairs(include_discards=False):
            if prev_fix.index < first_exit_index:
                continue
            if prev_fix not in interest_area and curr_fix in interest_area:
                if interest_area.right_to_left:
                    if curr_fix.x > prev_fix.x:
                        regression_counts[interest_area.id] += 1
                else:
                    if curr_fix.x < prev_fix.x:
                        regression_counts[interest_area.id] += 1
    return regression_counts


def duration_mass(text_block, fixation_sequence, n=1, gamma=30):
    """

    Given a `eyekit.text.TextBlock` and `eyekit.fixation.FixationSequence`,
    distribute the durations of the fixations probabilistically across the
    `eyekit.text.TextBlock`. Specifically, the duration of fixation *f* is
    distributed over all characters *C* in its line according to the
    probability that the reader is "seeing" each character (see
    `p_characters_fixation()`), and this is summed over all fixations:

    $$\\sum_{f \\in F} p(C|f) \\cdot f_\\mathrm{dur}$$

    Returns a 2D Numpy array, the sum of which is equal to the total duration
    of all fixations. This can be passed to `eyekit.vis.Image.draw_text_block_heatmap()`
    for visualization. Duration mass reveals the parts of the text that
    received the most attention. Optionally, this can be performed over
    higher-level ngrams by setting `n` > 1.

    """
    if not isinstance(text_block, _TextBlock):
        raise TypeError("text_block should be of type TextBlock")
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type FixationSequence")
    shape = text_block.n_rows, text_block.n_cols - (n - 1)
    distribution = _np.zeros(shape, dtype=float)
    for fixation in fixation_sequence.iter_without_discards():
        distribution += (
            p_characters_fixation(text_block, fixation, n=n, gamma=gamma)
            * fixation.duration
        )
    return distribution


def p_characters_fixation(text_block, fixation, n=1, gamma=30):
    """

    Given a `eyekit.text.TextBlock` and `eyekit.fixation.Fixation`, calculate
    the probability that the reader is "seeing" each character in the text. We
    assume that the closer a character is to the fixation point, the greater
    the probability that the participant is "seeing" (i.e., processing) that
    character. Specifically, for a given fixation *f*, we compute a Gaussian
    distribution over all characters in the line according to:

    $$p(c|f) \\propto \\mathrm{exp} \\frac{ -\\mathrm{ED}(f_\\mathrm{pos}, c_\\mathrm{pos})^2 }{2\\gamma^2}$$

    where *γ* (`gamma`) is a free parameter controlling the rate at which
    probability decays with the Euclidean distance (ED) between the position
    of fixation *f* and the position of character *c*.

    Returns a 2D Numpy array representing a probability distribution over all
    characters, with all its mass confined to the line that the fixation
    occurred inside, and with greater mass closer to fixation points. This
    array can be passed to `eyekit.vis.Image.draw_text_block_heatmap()` for
    visualization. Optionally, this calculation can be performed over
    higher-level ngrams by setting `n` > 1.

    """
    if not isinstance(fixation, _Fixation):
        raise TypeError("fixation should be of type Fixation")
    line_n = _np.argmin(abs(_np.array(text_block.midlines) - fixation.y))
    shape = text_block.n_rows, text_block.n_cols - (n - 1)
    distribution = _np.zeros(shape, dtype=float)
    fixation_xy = _np.array(fixation.xy, dtype=int)
    two_gamma_squared = 2 * gamma ** 2
    for ngram in text_block.ngrams(n, line_n=line_n, alphabetical_only=False):
        ngram_xy = _np.array(ngram.center, dtype=int)
        r, s, _ = ngram.location
        distribution[(r, s)] = _np.exp(
            -((fixation_xy - ngram_xy) ** 2).sum() / two_gamma_squared
        )
    return distribution / distribution.sum()
