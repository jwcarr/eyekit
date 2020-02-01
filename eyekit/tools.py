from .fixation import FixationSequence as _FixationSequence
from .passage import Passage as _Passage
from . import drift

def correct_vertical_drift(fixation_sequence, passage, method='warp', **kwargs):
	'''
	Pass a fixation sequence, passage, and other arguments to the
	relevant drift correction algorithm.
	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise ValueError('Invalid fixation sequence')
	if not isinstance(passage, _Passage):
		raise ValueError('Invalid passage')
	if method not in ['warp', 'saccades', 'chain', 'cluster', 'match', 'regression']:
		raise ValueError('method should be warp, saccades, chain, cluster, match, or regression')
	drift.__dict__[method](fixation_sequence, passage, **kwargs)

def discard_out_of_bounds_fixations(fixation_sequence, passage, in_bounds_threshold=128):
	'''
	Given a fixation sequence and passage, discard all fixations that do
	not fall within some threshold of any character in the passage.
	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise ValueError('Invalid fixation sequence')
	if not isinstance(passage, _Passage):
		raise ValueError('Invalid passage')
	for fixation in fixation_sequence:
		if not passage.in_bounds(fixation, in_bounds_threshold):
			fixation.discarded = True

def fixation_sequence_distance(sequence1, sequence2):
	'''
	Return Dynamic Time Warping distance between two fixation sequences.
	'''
	if not isinstance(sequence1, _FixationSequence) or not isinstance(sequence2, _FixationSequence):
		raise ValueError('Invalid fixation sequence')
	_, cost = drift._dynamic_time_warping(sequence1.XYarray(), sequence2.XYarray())
	return cost

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
