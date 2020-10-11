"""

Functions for calculating common analysis measures, such as total fixation
duration or initial landing position.

"""


import numpy as _np
from ._core import distance as _distance
from .fixation import FixationSequence as _FixationSequence, Fixation as _Fixation
from .text import TextBlock as _TextBlock, InterestArea as _InterestArea


def initial_fixation_duration(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the
    duration of the initial fixation on each interest area.

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
    fixation duration on each interest area.

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
    time.

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
    Counting is from 1, so a 1 indicates the initial fixation landed on the
    first character and so forth.

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


def initial_landing_x(interest_areas, fixation_sequence):
    """

    Given an interest area or collection of interest areas, return the initial
    landing position (expressed in pixel distance from the start of the
    interest area) on each interest area.

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
                for char in interest_area:
                    if fixation in char:
                        positions[interest_area.id] = fixation.x - interest_area.x_tl
                        break
                break
    return positions


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
    line_positions = _np.array(text_block.line_positions, dtype=int)
    line_n = _np.argmin(abs(line_positions - fixation.y))
    shape = text_block.n_rows, text_block.n_cols - (n - 1)
    distribution = _np.zeros(shape, dtype=float)
    for ngram in text_block.ngrams(n, line_n=line_n):
        r, s, e = ngram.id.split(":")
        distance = _distance(fixation.xy, ngram.center)
        distribution[(int(r), int(s))] = _np.exp(-(distance ** 2) / (2 * gamma ** 2))
    return distribution / distribution.sum()
