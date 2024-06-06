"""
These line assignment algorithms were adapted from the Python code provided at
https://github.com/jwcarr/drift which is licensed under a creative commons
attribution license. It is expected that these implementations will gradually
diverge from the original work.
"""

######################################################################
# CHAIN
#
# https://github.com/sascha2schroeder/popEye/
######################################################################


def chain(fixation_XY, text_block, x_thresh=192, y_thresh=32):
    """
    Chain consecutive fixations that are sufficiently close to each other, and
    then assign chains to their closest text lines. Default params:
    `x_thresh=192`, `y_thresh=32`. Requires NumPy. Original method
    implemented in [popEye](https://github.com/sascha2schroeder/popEye/).
    """
    try:
        import numpy as np
    except ModuleNotFoundError as e:
        e.msg = "The chain method requires NumPy."
        raise
    fixation_XY = np.array(fixation_XY, dtype=int)
    line_Y = np.array(text_block.midlines, dtype=int)
    dist_X = abs(np.diff(fixation_XY[:, 0]))
    dist_Y = abs(np.diff(fixation_XY[:, 1]))
    end_chain_indices = list(
        np.where(np.logical_or(dist_X > x_thresh, dist_Y > y_thresh))[0] + 1
    )
    end_chain_indices.append(len(fixation_XY))
    start_of_chain = 0
    for end_of_chain in end_chain_indices:
        mean_y = np.mean(fixation_XY[start_of_chain:end_of_chain, 1])
        line_i = np.argmin(abs(line_Y - mean_y))
        fixation_XY[start_of_chain:end_of_chain, 1] = line_Y[line_i]
        start_of_chain = end_of_chain
    return fixation_XY[:, 1]


######################################################################
# CLUSTER
#
# https://github.com/sascha2schroeder/popEye/
######################################################################


def cluster(fixation_XY, text_block):
    """
    Classify fixations into *m* clusters based on their Y-values, and then
    assign clusters to text lines in positional order. Requires SciPy.
    Original method implemented in [popEye](https://github.com/sascha2schroeder/popEye/).
    """
    try:
        import numpy as np
        from scipy.cluster.vq import kmeans2
    except ModuleNotFoundError as e:
        e.msg = "The cluster method requires SciPy."
        raise
    fixation_Y = np.array(fixation_XY, dtype=float)[:, 1]
    line_Y = np.array(text_block.midlines, dtype=int)
    _, clusters = kmeans2(fixation_Y, line_Y, iter=100, minit="matrix", missing="warn")
    return line_Y[clusters]


######################################################################
# MERGE
#
# Špakov, O., Istance, H., Hyrskykari, A., Siirtola, H., & Räihä,
#   K.-J. (2019). Improving the performance of eye trackers with
#   limited spatial accuracy and low sampling rates for reading
#   analysis by heuristic fixation-to-word mapping. Behavior Research
#   Methods, 51(6), 2661–2687.
#
# https://doi.org/10.3758/s13428-018-1120-x
# https://github.com/uta-gasp/sgwm
######################################################################


def merge(fixation_XY, text_block, y_thresh=32, gradient_thresh=0.1, error_thresh=20):
    """
    Form a set of progressive sequences and then reduce the set to *m* by
    repeatedly merging those that appear to be on the same line. Merged
    sequences are then assigned to text lines in positional order. Default
    params: `y_thresh=32`, `gradient_thresh=0.1`, `error_thresh=20`. Requires
    NumPy. Original method by [Špakov et al. (2019)](https://doi.org/10.3758/s13428-018-1120-x).
    """
    try:
        import numpy as np
    except ModuleNotFoundError as e:
        e.msg = "The merge method requires NumPy."
        raise
    fixation_XY = np.array(fixation_XY, dtype=int)
    line_Y = np.array(text_block.midlines, dtype=int)
    diff_X = np.diff(fixation_XY[:, 0])
    dist_Y = abs(np.diff(fixation_XY[:, 1]))
    if text_block.right_to_left:
        sequence_boundaries = list(
            np.where(np.logical_or(diff_X > 0, dist_Y > y_thresh))[0] + 1
        )
    else:
        sequence_boundaries = list(
            np.where(np.logical_or(diff_X < 0, dist_Y > y_thresh))[0] + 1
        )
    sequence_starts = [0] + sequence_boundaries
    sequence_ends = sequence_boundaries + [len(fixation_XY)]
    sequences = [
        list(range(start, end)) for start, end in zip(sequence_starts, sequence_ends)
    ]
    for min_i, min_j, remove_constraints in [
        (3, 3, False),  # Phase 1
        (1, 3, False),  # Phase 2
        (1, 1, False),  # Phase 3
        (1, 1, True),  # Phase 4
    ]:
        while len(sequences) > len(line_Y):
            best_merger = None
            best_error = np.inf
            for i in range(len(sequences) - 1):
                if len(sequences[i]) < min_i:
                    continue  # first sequence too short, skip to next i
                for j in range(i + 1, len(sequences)):
                    if len(sequences[j]) < min_j:
                        continue  # second sequence too short, skip to next j
                    candidate_XY = fixation_XY[sequences[i] + sequences[j]]
                    gradient, intercept = np.polyfit(
                        candidate_XY[:, 0], candidate_XY[:, 1], 1
                    )
                    residuals = candidate_XY[:, 1] - (
                        gradient * candidate_XY[:, 0] + intercept
                    )
                    error = np.sqrt(sum(residuals**2) / len(candidate_XY))
                    if remove_constraints or (
                        abs(gradient) < gradient_thresh and error < error_thresh
                    ):
                        if error < best_error:
                            best_merger = (i, j)
                            best_error = error
            if best_merger is None:
                break  # no possible mergers, break while and move to next phase
            merge_i, merge_j = best_merger
            merged_sequence = sequences[merge_i] + sequences[merge_j]
            sequences.append(merged_sequence)
            del sequences[merge_j], sequences[merge_i]
    mean_Y = [fixation_XY[sequence, 1].mean() for sequence in sequences]
    ordered_sequence_indices = np.argsort(mean_Y)
    for line_i, sequence_i in enumerate(ordered_sequence_indices):
        fixation_XY[sequences[sequence_i], 1] = line_Y[line_i]
    return fixation_XY[:, 1]


######################################################################
# REGRESS
#
# Cohen, A. L. (2013). Software for the automatic correction of
#   recorded eye fixation locations in reading experiments. Behavior
#   Research Methods, 45(3), 679–683.
#
# https://doi.org/10.3758/s13428-012-0280-3
# https://blogs.umass.edu/rdcl/resources/
######################################################################


def regress(
    fixation_XY,
    text_block,
    slope_bounds=(-0.1, 0.1),
    offset_bounds=(-50, 50),
    std_bounds=(1, 20),
):
    """
    Find *m* regression lines that best fit the fixations and group fixations
    according to best fit regression lines, and then assign groups to text
    lines in positional order. Default params: `slope_bounds=(-0.1, 0.1)`,
    `offset_bounds=(-50, 50)`, `std_bounds=(1, 20)`. Requires SciPy.
    Original method by [Cohen (2013)](https://doi.org/10.3758/s13428-012-0280-3).
    """
    try:
        import numpy as np
        from scipy.optimize import minimize
        from scipy.stats import norm
    except ModuleNotFoundError as e:
        e.msg = "The regress method requires SciPy."
        raise
    fixation_XY = np.array(fixation_XY, dtype=int)
    line_Y = np.array(text_block.midlines, dtype=int)
    density = np.zeros((len(fixation_XY), len(line_Y)))

    def fit_lines(params):
        k = slope_bounds[0] + (slope_bounds[1] - slope_bounds[0]) * norm.cdf(params[0])
        o = offset_bounds[0] + (offset_bounds[1] - offset_bounds[0]) * norm.cdf(
            params[1]
        )
        s = std_bounds[0] + (std_bounds[1] - std_bounds[0]) * norm.cdf(params[2])
        predicted_Y_from_slope = fixation_XY[:, 0] * k
        line_Y_plus_offset = line_Y + o
        for line_i in range(len(line_Y)):
            fit_Y = predicted_Y_from_slope + line_Y_plus_offset[line_i]
            density[:, line_i] = norm.logpdf(fixation_XY[:, 1], fit_Y, s)
        return -sum(density.max(axis=1))

    best_fit = minimize(fit_lines, [0, 0, 0], method="powell")
    fit_lines(best_fit.x)
    return line_Y[density.argmax(axis=1)]


######################################################################
# SEGMENT
#
# Abdulin, E. R., & Komogortsev, O. V. (2015). Person verification via
#   eye movement-driven text reading model, In 2015 IEEE 7th
#   International Conference on Biometrics Theory, Applications and
#   Systems. IEEE.
#
# https://doi.org/10.1109/BTAS.2015.7358786
######################################################################


def segment(fixation_XY, text_block):
    """
    Segment fixation sequence into *m* subsequences based on *m*–1 most-likely
    return sweeps, and then assign subsequences to text lines in chronological
    order. Requires NumPy. Original method by
    [Abdulin & Komogortsev (2015)](https://doi.org/10.1109/BTAS.2015.7358786).
    """
    try:
        import numpy as np
    except ModuleNotFoundError as e:
        e.msg = "The segment method requires NumPy."
        raise
    fixation_XY = np.array(fixation_XY, dtype=int)
    line_Y = np.array(text_block.midlines, dtype=int)
    diff_X = np.diff(fixation_XY[:, 0])
    saccades_ordered_by_length = np.argsort(diff_X)
    if text_block.right_to_left:
        line_change_indices = saccades_ordered_by_length[-(len(line_Y) - 1) :]
    else:
        line_change_indices = saccades_ordered_by_length[: len(line_Y) - 1]
    current_line_i = 0
    for fixation_i in range(len(fixation_XY)):
        fixation_XY[fixation_i, 1] = line_Y[current_line_i]
        if fixation_i in line_change_indices:
            current_line_i += 1
    return fixation_XY[:, 1]


######################################################################
# SLICE
#
# Glandorf, D., & Schroeder, S. (2021). Slice: An algorithm to assign
#   fixations in multi-line texts. Procedia Computer Science, 192,
#   2971–2979.
#
# https://doi.org/10.1016/j.procs.2021.09.069
######################################################################


def slice(fixation_XY, text_block, x_thresh=192, y_thresh=32, w_thresh=32, n_thresh=90):
    """
    Form a set of runs and then reduce the set to *m* by repeatedly merging
    those that appear to be on the same line. Merged sequences are then
    assigned to text lines in positional order. Default params:
    `x_thresh=192`, `y_thresh=32`, `w_thresh=32`, `n_thresh=90`. Requires
    NumPy. Original method by [Glandorf & Schroeder (2021)](https://doi.org/10.1016/j.procs.2021.09.069).
    """
    try:
        import numpy as np
    except ModuleNotFoundError as e:
        e.msg = "The slice method requires NumPy."
        raise
    fixation_XY = np.array(fixation_XY, dtype=int)
    line_Y = np.array(text_block.midlines, dtype=int)
    proto_lines, phantom_proto_lines = {}, {}
    # 1. Segment runs
    dist_X = abs(np.diff(fixation_XY[:, 0]))
    dist_Y = abs(np.diff(fixation_XY[:, 1]))
    end_run_indices = list(
        np.where(np.logical_or(dist_X > x_thresh, dist_Y > y_thresh))[0] + 1
    )
    run_starts = [0] + end_run_indices
    run_ends = end_run_indices + [len(fixation_XY)]
    runs = [list(range(start, end)) for start, end in zip(run_starts, run_ends)]
    # 2. Determine starting run
    longest_run_i = np.argmax(
        [fixation_XY[run[-1], 0] - fixation_XY[run[0], 0] for run in runs]
    )
    proto_lines[0] = runs.pop(longest_run_i)
    # 3. Group runs into proto lines
    while runs:
        merger_on_this_iteration = False
        for proto_line_i, direction in [(min(proto_lines), -1), (max(proto_lines), 1)]:
            # Create new proto line above or below (depending on direction)
            proto_lines[proto_line_i + direction] = []
            # Get current proto line XY coordinates (if proto line is empty, get phanton coordinates)
            if proto_lines[proto_line_i]:
                proto_line_XY = fixation_XY[proto_lines[proto_line_i]]
            else:
                proto_line_XY = phantom_proto_lines[proto_line_i]
            # Compute differences between current proto line and all runs
            run_differences = np.zeros(len(runs))
            for run_i, run in enumerate(runs):
                y_diffs = [
                    y - proto_line_XY[np.argmin(abs(proto_line_XY[:, 0] - x)), 1]
                    for x, y in fixation_XY[run]
                ]
                run_differences[run_i] = np.mean(y_diffs)
            # Find runs that can be merged into this proto line
            merge_into_current = list(np.where(abs(run_differences) < w_thresh)[0])
            # Find runs that can be merged into the adjacent proto line
            merge_into_adjacent = list(
                np.where(
                    np.logical_and(
                        run_differences * direction >= w_thresh,
                        run_differences * direction < n_thresh,
                    )
                )[0]
            )
            # Perform mergers
            for index in merge_into_current:
                proto_lines[proto_line_i].extend(runs[index])
            for index in merge_into_adjacent:
                proto_lines[proto_line_i + direction].extend(runs[index])
            # If no, mergers to the adjacent, create phantom line for the adjacent
            if not merge_into_adjacent:
                average_x, average_y = np.mean(proto_line_XY, axis=0)
                adjacent_y = average_y + text_block.line_height * direction
                phantom_proto_lines[proto_line_i + direction] = np.array(
                    [[average_x, adjacent_y]]
                )
            # Remove all runs that were merged on this iteration
            for index in sorted(merge_into_current + merge_into_adjacent, reverse=True):
                del runs[index]
                merger_on_this_iteration = True
        # If no mergers were made, break the while loop
        if not merger_on_this_iteration:
            break
    # 4. Assign any leftover runs to the closest proto lines
    for run in runs:
        best_pl_distance = np.inf
        best_pl_assignemnt = None
        for proto_line_i in proto_lines:
            if proto_lines[proto_line_i]:
                proto_line_XY = fixation_XY[proto_lines[proto_line_i]]
            else:
                proto_line_XY = phantom_proto_lines[proto_line_i]
            y_diffs = [
                y - proto_line_XY[np.argmin(abs(proto_line_XY[:, 0] - x)), 1]
                for x, y in fixation_XY[run]
            ]
            pl_distance = abs(np.mean(y_diffs))
            if pl_distance < best_pl_distance:
                best_pl_distance = pl_distance
                best_pl_assignemnt = proto_line_i
        proto_lines[best_pl_assignemnt].extend(run)
    # 5. Prune proto lines
    while len(proto_lines) > len(line_Y):
        top, bot = min(proto_lines), max(proto_lines)
        if len(proto_lines[top]) < len(proto_lines[bot]):
            proto_lines[top + 1].extend(proto_lines[top])
            del proto_lines[top]
        else:
            proto_lines[bot - 1].extend(proto_lines[bot])
            del proto_lines[bot]
    # 6. Map proto lines to text lines
    for line_i, proto_line_i in enumerate(sorted(proto_lines)):
        fixation_XY[proto_lines[proto_line_i], 1] = line_Y[line_i]
    return fixation_XY[:, 1]


######################################################################
# SPLIT
#
# Carr, J. W., Pescuma, V. N., Furlan, M., Ktori, M., & Crepaldi, D.
#   (2021). Algorithms for the automated correction of vertical drift
#   in eye tracking data. Behavior Research Methods.
#
# https://doi.org/10.3758/s13428-021-01554-0
# https://github.com/jwcarr/drift
######################################################################


def split(fixation_XY, text_block):
    """
    Split fixation sequence into subsequences based on best candidate return
    sweeps, and then assign subsequences to closest text lines. Requires
    SciPy. Original method by [Carr et al. (2022)](https://doi.org/10.3758/s13428-021-01554-0).
    """
    try:
        import numpy as np
        from scipy.cluster.vq import kmeans2
    except ModuleNotFoundError as e:
        e.msg = "The split method requires SciPy."
        raise
    fixation_XY = np.array(fixation_XY, dtype=int)
    line_Y = np.array(text_block.midlines, dtype=int)
    diff_X = np.array(np.diff(fixation_XY[:, 0]), dtype=float).reshape(-1, 1)
    centers, clusters = kmeans2(diff_X, 2, iter=100, minit="++", missing="raise")
    if text_block.right_to_left:
        sweep_marker = np.argmax(centers)
    else:
        sweep_marker = np.argmin(centers)
    end_line_indices = list(np.where(clusters == sweep_marker)[0] + 1)
    end_line_indices.append(len(fixation_XY))
    start_of_line = 0
    for end_of_line in end_line_indices:
        mean_y = np.mean(fixation_XY[start_of_line:end_of_line, 1])
        line_i = np.argmin(abs(line_Y - mean_y))
        fixation_XY[start_of_line:end_of_line] = line_Y[line_i]
        start_of_line = end_of_line
    return fixation_XY[:, 1]


######################################################################
# STRETCH
#
# Lohmeier, S. (2015). Experimental evaluation and modelling of the
#   comprehension of indirect anaphors in a programming language
#   (Master’s thesis). Technische Universität Berlin.
#
# http://www.monochromata.de/master_thesis/ma1.3.pdf
######################################################################


def stretch(
    fixation_XY, text_block, stretch_bounds=(0.9, 1.1), offset_bounds=(-50, 50)
):
    """
    Find a stretch factor and offset that results in a good alignment between
    the fixations and lines of text, and then assign the transformed fixations
    to the closest text lines. Default params: `stretch_bounds=(0.9, 1.1)`,
    `offset_bounds=(-50, 50)`. Requires SciPy.
    Original method by [Lohmeier (2015)](http://www.monochromata.de/master_thesis/ma1.3.pdf).
    """
    try:
        import numpy as np
        from scipy.optimize import minimize
    except ModuleNotFoundError as e:
        e.msg = "The stretch method requires SciPy."
        raise
    fixation_Y = np.array(fixation_XY, dtype=int)[:, 1]
    line_Y = np.array(text_block.midlines, dtype=int)
    n = len(fixation_Y)
    corrected_Y = np.zeros(n)

    def fit_lines(params):
        candidate_Y = fixation_Y * params[0] + params[1]
        for fixation_i in range(n):
            line_i = np.argmin(abs(line_Y - candidate_Y[fixation_i]))
            corrected_Y[fixation_i] = line_Y[line_i]
        return sum(abs(candidate_Y - corrected_Y))

    best_fit = minimize(
        fit_lines, [1, 0], method="powell", bounds=[stretch_bounds, offset_bounds]
    )
    fit_lines(best_fit.x)
    return corrected_Y


######################################################################
# WARP
#
# Carr, J. W., Pescuma, V. N., Furlan, M., Ktori, M., & Crepaldi, D.
#   (2021). Algorithms for the automated correction of vertical drift
#   in eye tracking data. Behavior Research Methods.
#
# https://doi.org/10.3758/s13428-021-01554-0
# https://github.com/jwcarr/drift
#
# Python implementation of the Dynamic Time Warping algorithm adapted
# from: https://github.com/talcs/simpledtw (MIT License)
######################################################################


def warp(fixation_XY, text_block):
    """
    Map fixations to word centers using [Dynamic Time
    Warping](https://en.wikipedia.org/wiki/Dynamic_time_warping). This finds a
    monotonically increasing mapping between fixations and words with the
    shortest overall distance, effectively resulting in *m* subsequences.
    Fixations are then assigned to the lines that their mapped words belong
    to, effectively assigning subsequences to text lines in chronological
    order. Requires NumPy.
    Original method by [Carr et al. (2022)](https://doi.org/10.3758/s13428-021-01554-0).
    """
    try:
        import numpy as np
    except ModuleNotFoundError as e:
        e.msg = "The warp method requires NumPy."
        raise
    fixation_XY = np.array(fixation_XY, dtype=int)
    word_XY = np.array([word.center for word in text_block.words()], dtype=int)
    n1 = len(fixation_XY)
    n2 = len(word_XY)
    cost = np.zeros((n1 + 1, n2 + 1))
    cost[0, :] = np.inf
    cost[:, 0] = np.inf
    cost[0, 0] = 0
    for fixation_i in range(n1):
        for word_i in range(n2):
            distance = np.sqrt(sum((fixation_XY[fixation_i] - word_XY[word_i]) ** 2))
            cost[fixation_i + 1, word_i + 1] = distance + min(
                cost[fixation_i, word_i + 1],
                cost[fixation_i + 1, word_i],
                cost[fixation_i, word_i],
            )
    cost = cost[1:, 1:]
    warping_path = [[] for _ in range(n1)]
    while fixation_i > 0 or word_i > 0:
        warping_path[fixation_i].append(word_i)
        possible_moves = [np.inf, np.inf, np.inf]
        if fixation_i > 0 and word_i > 0:
            possible_moves[0] = cost[fixation_i - 1, word_i - 1]
        if fixation_i > 0:
            possible_moves[1] = cost[fixation_i - 1, word_i]
        if word_i > 0:
            possible_moves[2] = cost[fixation_i, word_i - 1]
        best_move = np.argmin(possible_moves)
        if best_move == 0:
            fixation_i -= 1
            word_i -= 1
        elif best_move == 1:
            fixation_i -= 1
        else:
            word_i -= 1
    warping_path[0].append(0)
    for fixation_i, words_mapped_to_fixation_i in enumerate(warping_path):
        candidate_Y = list(word_XY[words_mapped_to_fixation_i, 1])
        fixation_XY[fixation_i, 1] = max(set(candidate_Y), key=candidate_Y.count)
    return fixation_XY[:, 1]


methods = {
    "chain": chain,
    "cluster": cluster,
    "merge": merge,
    "regress": regress,
    "segment": segment,
    "slice": slice,
    "split": split,
    "stretch": stretch,
    "warp": warp,
}


def wisdom_of_the_crowd(assignments):
    """
    For each fixation, choose the y-value with the most votes across multiple
    algorithms. In the event of a tie, the left-most algorithm is given
    priority.
    """
    import numpy as np

    def fleiss_kappa(assignments):
        """
        Calculate Fleiss's kappa on a set of line assignments.
        https://en.wikipedia.org/wiki/Fleiss%27_kappa
        """
        n_fixations, n_methods = assignments.shape
        categories = list(np.unique(assignments))
        ratings = np.zeros((n_fixations, len(categories)), dtype=int)
        for i, row in enumerate(assignments):
            for val in row:
                ratings[i, categories.index(val)] += 1
        p_bar = (
            sum(((ratings**2).sum(axis=1) - n_methods) / (n_methods * (n_methods - 1)))
            / n_fixations
        )
        p_bar_e = sum((ratings.sum(axis=0) / (n_fixations * n_methods)) ** 2)
        return (p_bar - p_bar_e) / (1 - p_bar_e)

    assignments = np.column_stack(assignments)
    correction = []
    for row in assignments:
        candidates = list(row)
        candidate_counts = {y: candidates.count(y) for y in set(candidates)}
        best_count = max(candidate_counts.values())
        best_candidates = [y for y, c in candidate_counts.items() if c == best_count]
        if len(best_candidates) == 1:
            correction.append(best_candidates[0])
        else:
            for y in row:
                if y in best_candidates:
                    correction.append(y)
                    break
    return correction, fleiss_kappa(assignments)
