import numpy as _np
try:
	from sklearn.cluster import KMeans as _KMeans
except ImportError:
	_KMeans = None
try:
	from scipy.optimize import minimize as _minimize
except ImportError:
	_minimize = None
try:
	from scipy.stats import norm as _norm
except ImportError:
	_norm = None


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
	alignment = _dynamic_time_warping(fixation_xy, passage.char_xy)
	for fixn_index, char_indices in enumerate(alignment):
		char_y = [passage.char_xy[char_index][1] for char_index in char_indices]
		line_y = max(set(char_y), key=char_y.count) # modal character y value
		if abs(fixation_sequence[fixn_index].y - line_y) < bounce_threshold:
			fixation_sequence[fixn_index].y = line_y
		else:
			fixation_sequence[fixn_index].discard()
	return fixation_sequence

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
	return alignment

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
	curr_line_index = 0
	for index, fixation in enumerate(fixation_sequence):
		line_y = passage.line_positions[curr_line_index]
		if abs(fixation.y - line_y) < bounce_threshold:
			fixation.y = line_y
		if index in line_change_indices:
			curr_line_index += 1
	return fixation_sequence

def chain(fixation_sequence, passage, x_thresh=128, y_thresh=32):
	'''
	Identify runs of fixations (a sequence of fixations that only change
	by small amounts on x or y), and then snap the run of fixations to
	the closest line. This is a Python port of popEye's chain method:
	https://github.com/sascha2schroeder/popEye
	'''
	fixation_xy = fixation_sequence.toarray()[:, :2]
	x_dists = abs(fixation_xy[1:, 0] - fixation_xy[:-1, 0])
	y_dists = abs(fixation_xy[1:, 1] - fixation_xy[:-1, 1])
	run_indices = list(_np.where(_np.logical_or(x_dists > x_thresh, y_dists > y_thresh))[0] + 1)
	run_indices.append(len(fixation_sequence))
	start_index = 0
	for end_index in run_indices:
		mean_y = fixation_xy[start_index:end_index, 1].mean()
		line_i = _np.argmin(abs(passage.line_positions - mean_y))
		line_y = passage.line_positions[line_i]
		for fixation_i in range(start_index, end_index):
			fixation_sequence[fixation_i].y = line_y
		start_index = end_index
	return fixation_sequence

def cluster(fixation_sequence, passage):
	'''
	Perform k-means clustering on the y-coordinates of the fixations to
	group them into likely lines, then update the y-coordinate of each
	fixation according to the cluster it is assigned to. This is a Python
	port of popEye's cluster method:
	https://github.com/sascha2schroeder/popEye
	'''
	if _KMeans is None:
		raise ValueError('scikit-learn is required for the cluster method. Install sklearn or use another method.')
	fixation_y = fixation_sequence.toarray()[:, 1].reshape(-1, 1)
	cluster_indices = _KMeans(passage.n_rows).fit_predict(fixation_y)
	sorted_cluster_indices = sorted([(fixation_y[cluster_indices == i].mean(), i) for i in range(passage.n_rows)])
	cluster_index_to_line_y = dict([(sorted_cluster_indices[i][1], passage.line_positions[i]) for i in range(passage.n_rows)])
	for cluster_i, fixation in zip(cluster_indices, fixation_sequence):
		line_y = cluster_index_to_line_y[cluster_i]
		fixation.y = line_y
	return fixation_sequence

def match(fixation_sequence, passage):
	'''
	For each fixation in the fixation sequence, update the fixation's
	y-coordinate to that of the nearest line. This is a Python port of
	popEye's match method: https://github.com/sascha2schroeder/popEye
	'''
	for fixation in fixation_sequence:
		line_i = _np.argmin(abs(passage.line_positions - fixation.y))
		line_y = passage.line_positions[line_i]
		fixation.y = line_y
	return fixation_sequence

def regression(fixation_sequence, passage, k_bounds=(-0.1, 0.1), o_bounds=(-50, 50), s_bounds=(1, 20)):
	'''
	The regression method proposed by Cohen (2013; Behav Res Methods 45).
	Fit N regression lines to the fixations, where N is the number of
	lines in the passage. Each fixation is then assigned to the text line
	associated with the highest-likelihood regression line. This is a
	simplified Python port of Cohen's R implementation:
	https://blogs.umass.edu/rdcl/resources/
	'''
	if _minimize is None or _norm is None:
		raise ValueError('scipy is required for the regression method. Install scipy or use another method.')
	fixation_xy = fixation_sequence.toarray()[:, :2]
	start_points = _np.column_stack(([passage.first_character_position[0]]*passage.n_rows, passage.line_positions))
	best_params = _minimize(_fit_lines, [0, 0, 0], args=(fixation_xy, start_points, True, k_bounds, o_bounds, s_bounds), method='nelder-mead').x
	line_categories = _fit_lines(best_params, fixation_xy, start_points, False, k_bounds, o_bounds, s_bounds)
	for line_i, fixation in zip(line_categories, fixation_sequence):
		line_y = passage.line_positions[line_i]
		fixation.y = line_y
	return fixation_sequence

def _fit_lines(params, fixation_xy, start_points, return_goodness_of_fit, k_bounds, o_bounds, s_bounds):
	'''
	Fit regression lines to the fixations and return the overall goodness
	of fit. This is the objective function to be optimzied. Again, this
	is ported from Cohen's R implementation.
	'''
	line_y = start_points[:, 1]
	n_clusters, n_fixations = len(line_y), len(fixation_xy)
	data_density = _np.zeros((n_fixations, n_clusters))
	y_difference = _np.zeros((n_fixations, n_clusters))
	k = k_bounds[0] + (k_bounds[1] - k_bounds[0]) * _norm.cdf(params[0])
	o = o_bounds[0] + (o_bounds[1] - o_bounds[0]) * _norm.cdf(params[1])
	s = s_bounds[0] + (s_bounds[1] - s_bounds[0]) * _norm.cdf(params[2])
	for line_i in range(n_clusters):
		y_on_line = o + k * (fixation_xy[:, 0] - start_points[line_i, 0]) + start_points[line_i, 1]
		data_density[:, line_i] = _norm.logpdf(fixation_xy[:, 1], y_on_line, s)
		y_difference[:, line_i] = fixation_xy[:, 1] - y_on_line
	data_density_max = data_density.max(axis=1)
	goodness_of_fit = -sum(data_density_max)
	if return_goodness_of_fit:
		return goodness_of_fit
	return data_density.argmax(axis=1)
