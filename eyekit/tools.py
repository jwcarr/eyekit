from .fixation import FixationSequence
from . import drift

def correct_vertical_drift(fixation_sequence, passage, method='dtw', **kwargs):
	if method not in ['dtw', 'saccades', 'chain', 'cluster', 'match', 'regression']:
		raise ValueError('method should be dtw, saccades, chain, cluster, match, or regression')
	return drift.__dict__[method](fixation_sequence, passage, **kwargs)

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
