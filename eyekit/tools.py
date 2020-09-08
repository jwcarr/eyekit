from .fixation import FixationSequence as _FixationSequence
from .text import Text as _Text
from . import drift

def correct_vertical_drift(fixation_sequence, text, method='warp', **kwargs):
	'''
	Correct vertical drift using the specified algorithm.
	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise ValueError('Invalid fixation sequence')
	if not isinstance(text, _Text):
		raise ValueError('Invalid text')
	if method not in ['attach', 'chain', 'cluster', 'merge', 'regress', 'segment', 'split', 'warp']:
		raise ValueError('method should be attach, chain, cluster, merge, regress, segment, split, or warp')
	fixation_XY = fixation_sequence.XYarray(include_discards=False)
	if method == 'warp':
		fixation_XY = drift.warp(fixation_XY, text.word_centers())
	else:
		fixation_XY = drift.__dict__[method](fixation_XY, text.line_positions, **kwargs)
	return _FixationSequence([(x, y, f.duration) for f, (x, y) in zip(fixation_sequence, fixation_XY)])

def discard_out_of_bounds_fixations(fixation_sequence, text, in_bounds_threshold=128):
	'''
	Given a fixation sequence and text, discard all fixations that do
	not fall within some threshold of any character in the text.
	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise ValueError('Invalid fixation sequence')
	if not isinstance(text, _Text):
		raise ValueError('Invalid text')
	fixation_sequence_copy = fixation_sequence.copy()
	for fixation in fixation_sequence_copy:
		if not text.in_bounds(fixation, in_bounds_threshold):
			fixation.discarded = True
	return fixation_sequence_copy

def fixation_sequence_distance(sequence1, sequence2):
	'''
	Return Dynamic Time Warping distance between two fixation sequences.
	'''
	if not isinstance(sequence1, _FixationSequence) or not isinstance(sequence2, _FixationSequence):
		raise ValueError('Invalid fixation sequence')
	cost, _ = drift._dynamic_time_warping(sequence1.XYarray(), sequence2.XYarray())
	return cost

def initial_landing_positions(text, fixation_sequence):
	matrix, words = text.word_identity_matrix()
	landing_positions, already_seen_words = [], []
	for fixation in fixation_sequence:
		rc = text.xy_to_rc(fixation.xy)
		word_i = matrix[rc][0]
		if word_i > 0 and word_i not in already_seen_words:
			already_seen_words.append(word_i)
			landing_positions.append((words[word_i], matrix[rc][1]))
	return landing_positions

def spread_duration_mass(text, fixation_sequence, n=1, gamma=30, in_bounds_threshold=None, line_only=True):
	'''
	Iterate over a sequence of fixations and, for each fixation,
	distribute its duration across the text (or, optionally, just the
	line) according to the probability that the participant is "seeing"
	each ngram.
	'''
	if in_bounds_threshold is not None:
		fixation_sequence = [fixation for fixation in fixation_sequence if text._in_bounds(fixation, in_bounds_threshold)]
	return sum([fixation.duration * text.p_ngrams_fixation(fixation, n, gamma, line_only) for fixation in fixation_sequence])
