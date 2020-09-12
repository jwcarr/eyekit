'''

Functions for calculating common analysis measures, such as total
fixation duration or initial landing position.

'''


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
		durations[interest_area.label] = 0
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
		durations[interest_area.label] = 0
		for fixation in fixation_sequence.iter_without_discards():
			if fixation in interest_area:
				durations[interest_area.label] += fixation.duration
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
		positions[interest_area.label] = None
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
	positions = {}
	for interest_area in interest_areas:
		if not isinstance(interest_area, _InterestArea):
			raise TypeError('%s is not of type InterestArea' % str(interest_area))
		positions[interest_area.label] = None
		for fixation in fixation_sequence.iter_without_discards():
			if fixation in interest_area:
				for char in interest_area:
					if fixation in char:
						positions[interest_area.label] = fixation.x - interest_area.x_tl
						break
				break
	return positions

def duration_mass(text_block, fixation_sequence, n=1, gamma=30):
	'''

	Iterate over a sequence of fixations and, for each fixation,
	distribute its duration across the line of text it is located inside
	and return the sum of these distributions.

	More specifically, we assume that the closer a character is to the
	fixation point, the greater the probability that the participant is
	"looking at" (i.e., processing) that character. Specifically, for a
	given fixation *f*, we compute a Gaussian distribution over all
	characters in the line according to:

	$$p(c|f) \\propto \\mathrm{exp} \\frac{ -\\mathrm{ED}(f_\\mathrm{pos}, c_\\mathrm{pos})^2 }{2\\gamma^2}$$

	where *γ* is a free parameter controlling the rate at which
	probability decays with the Euclidean distance (ED) between the
	position of fixation *f* and the position of character *c*. The
	duration of fixation *f* is then distributed across the entire line
	probabilistically and summed over all fixations in the fixation
	sequence *F*, yielding what we refer to as "duration mass".

	$$\\sum_{f \\in F} P(c|f) \\cdot f_\\mathrm{dur}$$

	'''
	distributions = []
	for fixation in fixation_sequence.iter_without_discards():
		distribution = text_block.p_ngrams_fixation(fixation, n, gamma) * fixation.duration
		distributions.append(distribution)
	return sum(distributions)
