"""

These implementations of seven vertical drift algorithms were adapted from the
Python code provided at https://github.com/jwcarr/drift which is licensed
under a creative commons attribution license.

"""

import numpy as np

######################################################################
# CHAIN
#
# https://github.com/sascha2schroeder/popEye/
######################################################################


def chain(fixation_XY, text_block, x_thresh=192, y_thresh=32):
    line_Y = np.array(text_block.line_positions, dtype=int)
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
    try:
        from scipy.cluster.vq import kmeans2
    except ImportError:
        raise ImportError(
            'The cluster method requires SciPy. Run "pip install scipy" to use this method.'
        )
    line_Y = np.array(text_block.line_positions, dtype=int)
    fixation_Y = np.array(fixation_XY[:, 1], dtype=float)
    _, clusters = kmeans2(fixation_Y, line_Y, iter=100, minit="matrix", missing="raise")
    for fixation_i, cluster_i in enumerate(clusters):
        fixation_XY[fixation_i, 1] = line_Y[cluster_i]
    return fixation_XY[:, 1]


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

phases = [
    {"min_i": 3, "min_j": 3, "no_constraints": False},  # Phase 1
    {"min_i": 1, "min_j": 3, "no_constraints": False},  # Phase 2
    {"min_i": 1, "min_j": 1, "no_constraints": False},  # Phase 3
    {"min_i": 1, "min_j": 1, "no_constraints": True},  # Phase 4
]


def merge(fixation_XY, text_block, y_thresh=32, gradient_thresh=0.1, error_thresh=20):
    line_Y = np.array(text_block.line_positions, dtype=int)
    diff_X = np.diff(fixation_XY[:, 0])
    dist_Y = abs(np.diff(fixation_XY[:, 1]))
    sequence_boundaries = list(
        np.where(np.logical_or(diff_X < 0, dist_Y > y_thresh))[0] + 1
    )
    sequence_starts = [0] + sequence_boundaries
    sequence_ends = sequence_boundaries + [len(fixation_XY)]
    sequences = [
        list(range(start, end)) for start, end in zip(sequence_starts, sequence_ends)
    ]
    for phase in phases:
        while len(sequences) > len(line_Y):
            best_merger = None
            best_error = np.inf
            for i in range(len(sequences) - 1):
                if len(sequences[i]) < phase["min_i"]:
                    continue  # first sequence too short, skip to next i
                for j in range(i + 1, len(sequences)):
                    if len(sequences[j]) < phase["min_j"]:
                        continue  # second sequence too short, skip to next j
                    candidate_XY = fixation_XY[sequences[i] + sequences[j]]
                    gradient, intercept = np.polyfit(
                        candidate_XY[:, 0], candidate_XY[:, 1], 1
                    )
                    residuals = candidate_XY[:, 1] - (
                        gradient * candidate_XY[:, 0] + intercept
                    )
                    error = np.sqrt(sum(residuals ** 2) / len(candidate_XY))
                    if phase["no_constraints"] or (
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
    try:
        from scipy.optimize import minimize
        from scipy.stats import norm
    except ImportError:
        raise ImportError(
            'The regress method requires SciPy. Run "pip install scipy" to use this method.'
        )
    line_Y = np.array(text_block.line_positions, dtype=int)
    density = np.zeros((len(fixation_XY), len(line_Y)))

    def fit_lines(params, return_line_assignments=False):
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
        if return_line_assignments:
            return density.argmax(axis=1)
        return -sum(density.max(axis=1))

    best_fit = minimize(fit_lines, [0, 0, 0], method="powell")
    line_assignments = fit_lines(best_fit.x, True)
    for fixation_i, line_i in enumerate(line_assignments):
        fixation_XY[fixation_i, 1] = line_Y[line_i]
    return fixation_XY[:, 1]


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
    line_Y = np.array(text_block.line_positions, dtype=int)
    diff_X = np.diff(fixation_XY[:, 0])
    saccades_ordered_by_length = np.argsort(diff_X)
    line_change_indices = saccades_ordered_by_length[: len(line_Y) - 1]
    current_line_i = 0
    for fixation_i in range(len(fixation_XY)):
        fixation_XY[fixation_i, 1] = line_Y[current_line_i]
        if fixation_i in line_change_indices:
            current_line_i += 1
    return fixation_XY[:, 1]


######################################################################
# SPLIT
######################################################################


def split(fixation_XY, text_block):
    try:
        from scipy.cluster.vq import kmeans2
    except ImportError:
        raise ImportError(
            'The split method requires SciPy. Run "pip install scipy" to use this method.'
        )
    line_Y = np.array(text_block.line_positions, dtype=int)
    diff_X = np.array(np.diff(fixation_XY[:, 0]), dtype=float).reshape(-1, 1)
    centers, clusters = kmeans2(diff_X, 2, iter=100, minit="++", missing="raise")
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
    try:
        from scipy.optimize import minimize
    except ImportError:
        raise ImportError(
            'The stretch method requires SciPy. Run "pip install scipy" to use this method.'
        )
    line_Y = np.array(text_block.line_positions, dtype=int)
    n = len(fixation_XY)
    fixation_Y = fixation_XY[:, 1]
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
# Python implementation of the Dynamic Time Warping algorithm adapted
# from: https://github.com/talcs/simpledtw (MIT License)
######################################################################


def warp(fixation_XY, text_block):
    word_XY = np.array(text_block.word_centers, dtype=int)
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
    "split": split,
    "stretch": stretch,
    "warp": warp,
}
