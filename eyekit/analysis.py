"""

Functions for calculating common reading measures, such as gaze duration or
initial landing position.

"""


from functools import wraps as _wraps
import numpy as _np
from .fixation import FixationSequence as _FixationSequence, Fixation as _Fixation
from .text import TextBlock as _TextBlock, InterestArea as _InterestArea


def _handle_collections(func):
    """

    Analysis function decorator. If an analysis function is given a collection
    of interest areas, the function is applied to each one and the results are
    returned as a dictionary.

    """

    func.__doc__ = (
        func.__doc__.strip()
        + " This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned."
    )

    @_wraps(func)
    def func_wrapper(interest_area, fixation_sequence):
        if not isinstance(fixation_sequence, _FixationSequence):
            raise TypeError(
                f"Expected object of type FixationSequence, not {type(fixation_sequence)}"
            )
        if isinstance(interest_area, _InterestArea):
            return func(interest_area, fixation_sequence)
        try:
            return {ia.id: func(ia, fixation_sequence) for ia in interest_area}
        except Exception:
            raise TypeError(
                f"Expected object of type InterestArea or an iterable, not {type(interest_area)}"
            )

    return func_wrapper


@_handle_collections
def number_of_fixations(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the number of
    fixations on that interest area.

    """
    count = 0
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            count += 1
    return count


@_handle_collections
def initial_fixation_duration(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the duration of the
    initial fixation on that interest area.

    """
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            return fixation.duration
    return 0


@_handle_collections
def total_fixation_duration(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the sum duration of
    all fixations on that interest area.

    """
    duration = 0
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            duration += fixation.duration
    return duration


@_handle_collections
def gaze_duration(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the gaze duration on
    that interest area. Gaze duration is the sum duration of all fixations
    inside an interest area until the area is exited for the first time.

    """
    duration = 0
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            duration += fixation.duration
        elif duration > 0:
            break  # at least one previous fixation was inside the IA and this fixation is not, so break
    return duration


@_handle_collections
def go_past_time(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the go-past time on
    that interest area. Go-past time is the sum duration of all fixations from
    when the interest area is first entered until when it is first exited to
    the right, including any regressions to the left that occur during that
    time period (and vice versa in the case of right-to-left text).

    """
    duration = 0
    entered = False
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            entered = True
            duration += fixation.duration
        elif entered:
            if interest_area.is_before(fixation):
                break  # IA has previously been entered and has now been exited
            duration += fixation.duration
    return duration


@_handle_collections
def second_pass_duration(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the second pass
    duration on that interest area. Second pass duration is the sum duration
    of all fixations inside an interest area during the second pass over that
    interest area.

    """
    duration = 0
    current_pass = None
    next_pass = 1
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            if current_pass is None:  # first fixation in a new pass
                current_pass = next_pass
            if current_pass == 2:
                duration += fixation.duration
        elif current_pass == 1:  # first fixation to exit the first pass
            current_pass = None
            next_pass += 1
        elif current_pass == 2:  # first fixation to exit the second pass
            break
    return duration


@_handle_collections
def initial_landing_position(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the initial landing
    position (expressed in character positions) on that interest area.
    Counting is from 1. If the interest area represents right-to-left text,
    the first character is the rightmost one. Returns `None` if no fixation
    landed on the interest area.

    """
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            for position, char in enumerate(interest_area, 1):
                if fixation in char:
                    return position
    return None


@_handle_collections
def initial_landing_distance(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the initial landing
    distance on that interest area. The initial landing distance is the pixel
    distance between the first fixation to land in an interest area and the
    left edge of that interest area (or, in the case of right-to-left text,
    the right edge). Returns `None` if no fixation landed on the interest
    area.

    """
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            return abs(interest_area.onset - fixation.x)
    return None


@_handle_collections
def number_of_regressions_in(interest_area, fixation_sequence):
    """

    Given an interest area and fixation sequence, return the number of
    regressions back to that interest area after the interest area was read
    for the first time. In other words, find the first fixation to exit the
    interest area and then count how many times the reader returns to the
    interest area from the right (or from the left in the case of
    right-to-left text).

    """
    entered_interest_area = False
    first_exit_index = None
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            entered_interest_area = True
        elif entered_interest_area:
            first_exit_index = fixation.index
            break
    if first_exit_index is None:
        return 0  # IA was never exited, so there can't be any regressions back to it
    count = 0
    for prev_fix, curr_fix in fixation_sequence.iter_pairs(include_discards=False):
        if prev_fix.index < first_exit_index:
            continue
        if prev_fix not in interest_area and curr_fix in interest_area:
            if interest_area.right_to_left:
                if curr_fix.x > prev_fix.x:
                    count += 1
            else:
                if curr_fix.x < prev_fix.x:
                    count += 1
    return count


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
