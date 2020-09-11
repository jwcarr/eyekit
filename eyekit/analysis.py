from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock, InterestArea as _InterestArea


def initial_fixation_duration(interest_areas, fixation_sequence):
	'''

	Given an interest area or collection of interest areas, return the
	duration of the initial fixation on each interest area.

	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('Fixation sequence should be of type FixationSequence')
	try:
		iter(interest_areas)
	except TypeError:
		interest_areas = [interest_areas]
	durations = {}
	for interest_area in interest_areas:
		if not isinstance(interest_area, _InterestArea):
			raise TypeError('Interest area should be of type InterestArea')
		for fixation in fixation_sequence.iter_without_discards():
			if fixation in interest_area:
				durations[interest_area.label] = fixation.duration
				break
	return durations

def total_fixation_duration(interest_areas, fixation_sequence):
	'''

	Given an interest area or collection of interest areas, return the
	total fixation duration on each interest area.

	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('Fixation sequence should be of type FixationSequence')
	try:
		iter(interest_areas)
	except TypeError:
		interest_areas = [interest_areas]
	durations = {}
	for interest_area in interest_areas:
		if not isinstance(interest_area, _InterestArea):
			raise TypeError('Interest area should be of type InterestArea')
		for fixation in fixation_sequence.iter_without_discards():
			if fixation in interest_area:
				if interest_area.label in durations:
					durations[interest_area.label] += fixation.duration
				else:
					durations[interest_area.label] = fixation.duration
	return durations

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
