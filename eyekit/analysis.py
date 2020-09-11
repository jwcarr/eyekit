from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock, InterestArea as _InterestArea


def initial_fixation_duration(interest_areas, fixation_sequence):
	'''

	Given an interest area or collection of interest areas, return the
	duration of the initial fixation on each interest area.

	'''
	if isinstance(interest_areas, _InterestArea):
		interest_areas = [interest_areas]
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('fixation_sequence should be of type FixationSequence')
	durations = {}
	for interest_area in interest_areas:
		if not isinstance(interest_area, _InterestArea):
			raise TypeError('%s is not of type InterestArea' % str(interest_area))
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
	if isinstance(interest_areas, _InterestArea):
		interest_areas = [interest_areas]
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('fixation_sequence should be of type FixationSequence')
	durations = {}
	for interest_area in interest_areas:
		if not isinstance(interest_area, _InterestArea):
			raise TypeError('%s is not of type InterestArea' % str(interest_area))
		for fixation in fixation_sequence.iter_without_discards():
			if fixation in interest_area:
				if interest_area.label in durations:
					durations[interest_area.label] += fixation.duration
				else:
					durations[interest_area.label] = fixation.duration
	return durations

def initial_landing_position(interest_areas, fixation_sequence):
	'''

	Given an interest area or collection of interest areas, return the
	initial landing position (expressed in character positions) on each
	interest area. Counting is from 1, so a 1 indicates the initial
	fixation landed on the first character and so forth.

	'''
	if isinstance(interest_areas, _InterestArea):
		interest_areas = [interest_areas]
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('fixation_sequence should be of type FixationSequence')
	positions = {}
	for interest_area in interest_areas:
		if not isinstance(interest_area, _InterestArea):
			raise TypeError('%s is not of type InterestArea' % str(interest_area))
		for fixation in fixation_sequence.iter_without_discards():
			if fixation in interest_area:
				for position, char in enumerate(interest_area, 1):
					if fixation in char:
						positions[interest_area.label] = position
						break
				break
	return positions

def initial_landing_x(interest_areas, fixation_sequence):
	'''

	Given an interest area or collection of interest areas, return the
	initial landing position (expressed in pixel distance from the start
	of the interest area) on each interest area.

	'''
	if isinstance(interest_areas, _InterestArea):
		interest_areas = [interest_areas]
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('fixation_sequence should be of type FixationSequence')
	x_positions = {}
	for interest_area in interest_areas:
		if not isinstance(interest_area, _InterestArea):
			raise TypeError('%s is not of type InterestArea' % str(interest_area))
		for fixation in fixation_sequence.iter_without_discards():
			if fixation in interest_area:
				for position, char in enumerate(interest_area, 1):
					if fixation in char:
						x_positions[interest_area.label] = fixation.x - interest_area.x_tl
						break
				break
	return x_positions

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
