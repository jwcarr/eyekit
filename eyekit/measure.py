"""
Functions for calculating common reading measures, such as gaze duration or
initial landing position.
"""


from functools import wraps as _wraps
from .fixation import _is_FixationSequence
from .text import _is_InterestArea, _is_TextBlock, _fail


def _handle_collections(func):
    """
    Measure function decorator. If an measure function is given a collection
    of interest areas, the function is applied to each one and the results are
    returned as a dictionary.
    """
    func.__doc__ = (
        func.__doc__.strip()
        + " This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned."
    )

    @_wraps(func)
    def func_wrapper(interest_area, fixation_sequence):
        _is_FixationSequence(fixation_sequence)
        try:
            _is_InterestArea(interest_area)
        except TypeError:
            try:
                return {ia.id: func(ia, fixation_sequence) for ia in interest_area}
            except Exception:
                _fail(interest_area, "InterestArea or an iterable")
        return func(interest_area, fixation_sequence)

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
def first_of_many_duration(interest_area, fixation_sequence):
    """
    Given an interest area and fixation sequence, return the duration of the
    initial fixation on that interest area, but only if there was more than
    one fixation on the interest area (otherwise return `None`).
    """
    duration = None
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            if duration is not None:
                return duration
            duration = fixation.duration
    return None


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
def go_past_duration(interest_area, fixation_sequence):
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
    the right edge). Technically, the distance is measured from the text onset
    without including any padding. Returns `None` if no fixation landed on the
    interest area.
    """
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            for char in interest_area:
                if fixation in char:  # be sure not to find a fixation in the padding
                    return abs(interest_area.onset - fixation.x)
    return None


@_handle_collections
def landing_distances(interest_area, fixation_sequence):
    """
    Given an interest area and fixation sequence, return a list of landing
    distances on that interest area. Each landing distance is the pixel
    distance between the fixation and the left edge of the interest area
    (or, in the case of right-to-left text, the right edge). The distance is
    measured from the text onset without including any padding. Returns an
    empty list if no fixation landed on the interest area.
    """
    distances = []
    for fixation in fixation_sequence.iter_without_discards():
        if fixation in interest_area:
            for char in interest_area:
                if fixation in char:  # be sure not to find a fixation in the padding
                    distances.append(abs(interest_area.onset - fixation.x))
    return distances


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


def duration_mass(text_block, fixation_sequence, *, ngram_width=1, gamma=30):
    """
    Given a `eyekit.text.TextBlock` and `eyekit.fixation.FixationSequence`,
    distribute the durations of the fixations probabilistically across the
    `eyekit.text.TextBlock`. Specifically, the duration of fixation *f* is
    distributed over all characters *C* in its line according to the
    probability that the reader is "seeing" each character (see
    `p_characters_fixation()`), and this is summed over all fixations:

    $$\\sum_{f \\in F} p(C|f) \\cdot f_\\mathrm{dur}$$

    For a given fixation *f*, we compute a Gaussian distribution over all
    characters in the line according to:

    $$p(c|f) \\propto \\mathrm{exp} \\frac{ -\\mathrm{ED}(f_\\mathrm{pos}, c_\\mathrm{pos})^2 }{2\\gamma^2}$$

    where *γ* (`gamma`) is a free parameter controlling the rate at which
    probability decays with the Euclidean distance (ED) between the position
    of fixation *f* and the position of character *c*.

    Returns a 2D Numpy array, the sum of which is equal to the total duration
    of all fixations. This can be passed to `eyekit.vis.Image.draw_heatmap()`
    for visualization. Duration mass reveals the parts of the text that
    received the most attention. Optionally, this can be performed over
    higher-level ngrams by setting `ngram_width` > 1.
    """
    try:
        import numpy as np
    except ModuleNotFoundError as e:
        e.msg = "The duration_mass function requires NumPy."
        raise
    _is_TextBlock(text_block)
    _is_FixationSequence(fixation_sequence)
    shape = text_block.n_rows, text_block.n_cols - (ngram_width - 1)
    two_gamma_squared = 2 * gamma**2

    def p_characters_fixation(fixation):
        line_n = np.argmin(abs(np.array(text_block.midlines) - fixation.y))
        p_distribution = np.zeros(shape, dtype=float)
        fixation_xy = np.array(fixation.xy, dtype=int)
        for ngram in text_block.ngrams(
            ngram_width, line_n=line_n, alphabetical_only=False
        ):
            ngram_xy = np.array(ngram.center, dtype=int)
            r, s, _ = ngram.location
            p_distribution[(r, s)] = np.exp(
                -((fixation_xy - ngram_xy) ** 2).sum() / two_gamma_squared
            )
        return p_distribution / p_distribution.sum()

    distribution = np.zeros(shape, dtype=float)
    for fixation in fixation_sequence.iter_without_discards():
        distribution += p_characters_fixation(fixation) * fixation.duration
    return distribution
