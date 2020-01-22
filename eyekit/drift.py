from .fixation import FixationSequence as _FixationSequence
import numpy as _np

def dtw(fixation_sequence, passage, bounce_threshold=100):
	'''
	Given a fixation sequence and passage, snap each fixation's y-axis
	coordinate to the line in the passage that it most likely belongs to,
	removing any vertical variation other than movements from one line to
	the next. If a fixation's revised y-axis coordinate falls more than
	(bounce_threshold) pixels away from its original position, it is
	eliminated.
	'''
	fixation_xy = fixation_sequence.toarray()[:, :2]
	alignment, cost = _dynamic_time_warping(fixation_xy, passage.char_xy)
	corrected_fixation_sequence = []
	for fixn_index, char_indices in enumerate(alignment):
		line_y = _mode([int(passage.char_xy[char_index][1]) for char_index in char_indices])
		if abs(fixation_sequence[fixn_index].y - line_y) < bounce_threshold:
			corrected_fixation = fixation_sequence[fixn_index].update_y(line_y)
			corrected_fixation_sequence.append(corrected_fixation)
	return _FixationSequence(corrected_fixation_sequence)

def saccades(fixation_sequence, passage, bounce_threshold=100):
	'''
	Identify N-1 biggest backward saccades, where N is the number of
	lines in the passage, and use these to segment the fixation sequence
	into lines. Update the y-axis coordinates of the fixations
	accordingly.
	'''
	fixation_x = fixation_sequence.toarray()[:, 0]
	x_dists = fixation_x[1:] - fixation_x[:-1]
	sorted_x_dists = sorted(zip(x_dists, range(len(x_dists))))
	line_change_indices = [i for _, i in sorted_x_dists[:passage.n_rows-1]]
	corrected_fixation_sequence, curr_line_index = [], 0
	for index, fixation in enumerate(fixation_sequence):
		line_y = passage.line_positions[curr_line_index]
		if abs(fixation.y - line_y) < bounce_threshold:
			corrected_fixation = fixation.update_y(line_y)
			corrected_fixation_sequence.append(corrected_fixation)
		if index in line_change_indices:
			curr_line_index += 1
	return _FixationSequence(corrected_fixation_sequence)

def chain(fixation_sequence, passage, x_thresh=128, y_thresh=32):
	'''
	Identify runs of fixations (a sequence of fixations that only change
	by small amounts on x or y), and then snap the run of fixations to
	the closest line.
	'''
	run = [fixation_sequence[0]]
	corrected_fixation_sequence = []
	for fixation in fixation_sequence[1:]:
		x_dist = abs(fixation.x - run[-1].x)
		y_dist = abs(fixation.y - run[-1].y)
		if not (x_dist > x_thresh) and not (y_dist > y_thresh):
			run.append(fixation)
		else:
			mean_y = _np.mean([run_fixation.y for run_fixation in run])
			line_i = _np.argmin(abs(passage.line_positions - mean_y))
			line_y = passage.line_positions[line_i]
			for run_fixation in run:
				corrected_fixation = run_fixation.update_y(line_y)
				corrected_fixation_sequence.append(corrected_fixation)
			run = [fixation]
	return _FixationSequence(corrected_fixation_sequence)

def cluster(fixation_sequence, passage):
	'''
	Perform k-means clustering on the y-coordinates of the fixations to
	group them into likely lines, then update the y-coordinate of each
	fixation according to the cluster it is assigned to.
	'''
	try:
		from sklearn.cluster import KMeans
	except ImportError:
		print('scikit-learn is required to perform kmeans clustering: pip install sklearn')
	fixation_y = fixation_sequence.toarray()[:, 1].reshape(-1, 1)
	cluster_indices = KMeans(passage.n_rows).fit_predict(fixation_y)
	sorted_cluster_indices = sorted([(fixation_y[cluster_indices == i].mean(), i) for i in range(passage.n_rows)])
	cluster_index_to_line_y = dict([(sorted_cluster_indices[i][1], passage.line_positions[i]) for i in range(passage.n_rows)])
	corrected_fixation_sequence = []
	for cluster_i, fixation in zip(cluster_indices, fixation_sequence):
		line_y = cluster_index_to_line_y[cluster_i]
		corrected_fixation = fixation.update_y(line_y)
		corrected_fixation_sequence.append(corrected_fixation)
	return _FixationSequence(corrected_fixation_sequence)

def match(fixation_sequence, passage):
	'''
	For each fixation in the fixation sequence, update the fixation's
	y-coordinate to that of the nearest line.
	'''
	corrected_fixation_sequence = []
	for fixation in fixation_sequence:
		line_i = _np.argmin(abs(passage.line_positions - fixation.y))
		line_y = passage.line_positions[line_i]
		corrected_fixation = fixation.update_y(line_y)
		corrected_fixation_sequence.append(corrected_fixation)
	return _FixationSequence(corrected_fixation_sequence)

def regression(fixation_sequence, passage):
	'''
	Fit N regression lines to the fixations, where N is the number of lines in the passage.
	'''
	return _FixationSequence([])

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
	matrix = _np.zeros((len(series1) + 1, len(series2) + 1))
	matrix[0,:] = _np.inf
	matrix[:,0] = _np.inf
	matrix[0,0] = 0
	for i, vec1 in enumerate(series1):
		for j, vec2 in enumerate(series2):
			cost = _np.linalg.norm(vec1 - vec2)
			matrix[i + 1, j + 1] = cost + min(matrix[i, j + 1], matrix[i + 1, j], matrix[i, j])
	matrix = matrix[1:,1:]
	i = matrix.shape[0] - 1
	j = matrix.shape[1] - 1
	alignment = [list() for v in range(matrix.shape[0])]
	while i > 0 or j > 0:
		alignment[i].append(j)
		option_diag = matrix[i - 1, j - 1] if i > 0 and j > 0 else _np.inf
		option_up = matrix[i - 1, j] if i > 0 else _np.inf
		option_left = matrix[i, j - 1] if j > 0 else _np.inf
		move = _np.argmin([option_diag, option_up, option_left])
		if move == 0:
			i -= 1
			j -= 1
		elif move == 1:
			i -= 1
		else:
			j -= 1
	alignment[0].append(0)
	return alignment, matrix[-1, -1]
