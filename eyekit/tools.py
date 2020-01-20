from .fixation import FixationSequence
import numpy as np

def correct_vertical_drift(passage, fixation_sequence, bounce_threshold=100, in_bounds_threshold=50):
	'''
	Given a passage and fixation sequence, snap each fixation's y-axis
	coordinate to the line in the passage that it most likely belongs to,
	removing any vertical variation other than movements from one line to
	the next. If a fixation's revised y-axis coordinate falls more than
	(bounce_threshold) pixels away from its original position, it is
	eliminated.
	'''
	fixn_xy = fixation_sequence.toarray()[:, :2]
	alignment, cost = _dynamic_time_warping(fixn_xy, passage.char_xy)
	corrected_fixation_sequence = []
	for fixn_index, char_indices in enumerate(alignment):
		line_y = _mode([int(passage.char_xy[char_index][1]) for char_index in char_indices])
		if abs(fixation_sequence[fixn_index].y - line_y) < bounce_threshold:
			corrected_fixation = fixation_sequence[fixn_index].update_y(line_y)
			if passage._in_bounds(corrected_fixation, in_bounds_threshold):
				corrected_fixation_sequence.append(corrected_fixation)
	return FixationSequence(corrected_fixation_sequence)

def initial_landing_positions(passage, fixation_sequence):
	matrix, words = passage.word_identity_matrix()
	landing_positions, already_seen_words = [], []
	for fixation in fixation_sequence:
		rc = passage.xy_to_rc(fixation.xy)
		word_i = matrix[rc][0]
		if word_i > 0 and word_i not in already_seen_words:
			already_seen_words.append(word_i)
			landing_positions.append((words[word_i], matrix[rc][1]))
	return landing_positions

def spread_duration_mass(passage, fixation_sequence, n=1, gamma=30, in_bounds_threshold=None, line_only=True):
	'''
	Iterate over a sequence of fixations and, for each fixation,
	distribute its duration across the passage (or, optionally, just the
	line) according to the probability that the participant is "seeing"
	each ngram.
	'''
	if in_bounds_threshold is not None:
		fixation_sequence = [fixation for fixation in fixation_sequence if passage._in_bounds(fixation, in_bounds_threshold)]
	return sum([fixation.duration * passage.p_ngrams_fixation(fixation, n, gamma, line_only) for fixation in fixation_sequence])


def _mode(lst):
	'''
	Returns modal value from a list of values.
	'''
	return max(set(lst), key=lst.count)

def _dynamic_time_warping(series1, series2):
	'''
	Returns the best alignment between two time series and the resulting
	cost using the Dynamic Time Warping algorithm. Adapted from
	https://github.com/talcs/simpledtw - Copyright (c) 2018 talcs (MIT
	License)
	'''
	matrix = np.zeros((len(series1) + 1, len(series2) + 1))
	matrix[0,:] = np.inf
	matrix[:,0] = np.inf
	matrix[0,0] = 0
	for i, vec1 in enumerate(series1):
		for j, vec2 in enumerate(series2):
			cost = np.linalg.norm(vec1 - vec2)
			matrix[i + 1, j + 1] = cost + min(matrix[i, j + 1], matrix[i + 1, j], matrix[i, j])
	matrix = matrix[1:,1:]
	i = matrix.shape[0] - 1
	j = matrix.shape[1] - 1
	alignment = [list() for v in range(matrix.shape[0])]
	while i > 0 or j > 0:
		alignment[i].append(j)
		option_diag = matrix[i - 1, j - 1] if i > 0 and j > 0 else np.inf
		option_up = matrix[i - 1, j] if i > 0 else np.inf
		option_left = matrix[i, j - 1] if j > 0 else np.inf
		move = np.argmin([option_diag, option_up, option_left])
		if move == 0:
			i -= 1
			j -= 1
		elif move == 1:
			i -= 1
		else:
			j -= 1
	alignment[0].append(0)
	return alignment, matrix[-1, -1]
