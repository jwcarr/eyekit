"""
Functions for calculating common reading measures, such as gaze duration or
initial landing position.
"""

from functools import wraps as _wraps
from .fixation import _is_FixationSequence
from .text import _is_InterestArea, _is_TextBlock, _fail, InterestArea as _InterestArea


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


def interest_area_report(trials, measures):
    """
    Given one or more trials and one or more measures, apply each measure to
    all interest areas associated with each trial and return a Pandas
    dataframe with the collated results. The `trials` argument should be a
    list of dictionaries, where each dictionary contains minimally a
    `fixations` key that maps to a `eyekit.fixation.FixationSequence` and an
    `interest_areas` key that maps to a list of interest areas extracted from
    a `eyekit.text.TextBlock`. Any other keys in the dictionary
    (e.g., trial/subject identifiers) will be included as separate columns
    in the resulting dataframe. The `measures` argument should be a list of
    built-in measures from the `eyekit.measure` module or your own custom
    measurement functions. For example:

    ```
    trials = [
        {
            'trial_id': 'trial1',
            'fixations': FixationSequence(...),
            'interest_areas': text_block.words()
        }
    ]
    measures = ['total_fixation_duration', 'gaze_duration']
    dataframe = eyekit.measure.interest_area_report(trials, measures)
    dataframe.to_csv('path/to/output.csv') # write dateframe to CSV
    ```
    """
    try:
        import pandas as pd
    except ModuleNotFoundError as e:
        e.msg = "The collate function requires Pandas."
        raise

    if (
        isinstance(trials, dict)
        and "fixations" in trials
        and "interest_areas" in trials
    ):
        trials = [trials]
    if isinstance(trials, list):
        trials = {i: trial for i, trial in enumerate(trials)}

    data_keys = []
    for trial_i, trial in trials.items():
        if "fixations" not in trial:
            raise ValueError(
                f'Trial {trial_i} does not contain a "fixations" key. Each trial should contain "fixations" and "interest_areas".'
            )
        if "interest_areas" not in trial:
            raise ValueError(
                f'Trial {trial_i} does not contain a "interest_areas" key. Each trial should contain "fixations" and "interest_areas".'
            )
        data_keys.extend(trial.keys())
    data_keys = sorted(list(set(data_keys) - set(["fixations", "interest_areas"])))

    measure_funcs = []
    if callable(measures):
        measure_funcs.append(measures)
    else:
        if isinstance(measures, str):
            measures = [measures]
        for measure in measures:
            if callable(measure):
                measure_funcs.append(measure)
            elif measure in _MEASURE_FUNCS:
                measure_funcs.append(_MEASURE_FUNCS[measure])
            else:
                raise ValueError(f"Measure {measure} not recognized")

    df = {key: [] for key in data_keys}
    df.update({"interest_area_id": [], "interest_area_text": []})
    df.update({measure_func.__name__: [] for measure_func in measure_funcs})

    for _, trial in trials.items():
        fixation_sequence = trial["fixations"]
        interest_areas = list(trial["interest_areas"])
        for key in data_keys:
            df[key].extend([trial.get(key, None)] * len(interest_areas))
        for interest_area in interest_areas:
            df["interest_area_id"].append(interest_area.id)
            df["interest_area_text"].append(interest_area.text)
            for measure_func in measure_funcs:
                df[measure_func.__name__].append(
                    measure_func(interest_area, fixation_sequence)
                )

    return pd.DataFrame(df)


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
    Deprecated in 0.5.4. Given an interest area and fixation sequence, return
    a list of landing distances on that interest area. Each landing distance
    is the pixel distance between the fixation and the left edge of the
    interest area(or, in the case of right-to-left text, the right edge). The
    distance is measured from the text onset without including any padding.
    Returns an empty list if no fixation landed on the interest area.
    """
    import warnings as _warnings

    _warnings.warn("eyekit.measure.landing_distances() is deprecated", FutureWarning)
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


_MEASURE_FUNCS = {
    "number_of_fixations": number_of_fixations,
    "initial_fixation_duration": initial_fixation_duration,
    "first_of_many_duration": first_of_many_duration,
    "total_fixation_duration": total_fixation_duration,
    "gaze_duration": gaze_duration,
    "go_past_duration": go_past_duration,
    "second_pass_duration": second_pass_duration,
    "initial_landing_position": initial_landing_position,
    "initial_landing_distance": initial_landing_distance,
    "number_of_regressions_in": number_of_regressions_in,
}
