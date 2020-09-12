'''

Functions for performing common procedures, such as discarding out of
bounds fixations and snapping fixations to the lines of text.

'''


from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock
from . import _drift

def snap_to_lines(fixation_sequence, text_block, method='warp', **kwargs):
	'''
	
	Given a `FixationSequence` and `TextBlock`, snap each fixation to the
	line that it most likely belongs to, eliminating any y-axis variation
	or drift. Returns a copy of the fixation sequence. Several methods
	are available, some of which take optional parameters. For a full
	description and evaluation of these methods, see [Carr et al. (2020)](https://osf.io/jg3nc/).

	- `chain` : Chain consecutive fixations that are sufficiently close to each other, and then assign chains to their closest text lines. Default params: `x_thresh=192`, `y_thresh=32`
	- `cluster` : Classify fixations into *m* clusters based on their Y-values, and then assign clusters to text lines in positional order.
	- `merge` : Form a set of progressive sequences and then reduce the set to *m* by repeatedly merging those that appear to be on the same line. Merged sequences are then assigned to text lines in positional order. Default params: `y_thresh=32`, `g_thresh=0.1`, `e_thresh=20`
	- `regress` : Find *m* regression lines that best fit the fixations and group fixations according to best fit regression lines, and then assign groups to text lines in positional order. Default params: `k_bounds=(-0.1, 0.1)`, `o_bounds=(-50, 50)`, `s_bounds=(1, 20)`
	- `segment` : Segment fixation sequence into *m* subsequences based on *m*–1 most-likely return sweeps, and then assign subsequences to text lines in chronological order.
	- `split` : Split fixation sequence into subsequences based on best candidate return sweeps, and then assign subsequences to closest text lines.
	- `warp` : Map fixations to word centers by finding a monotonically increasing mapping with minimal cost, effectively resulting in *m* subsequences, and then assign fixations to the lines that their mapped words belong to, effectively assigning subsequences to text lines in chronological order.

	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('fixation_sequence should be of type eyekit.FixationSequence')
	if not isinstance(text_block, _TextBlock):
		raise TypeError('text_block should be of type eyekit.Text')
	if method not in ['chain', 'cluster', 'merge', 'regress', 'segment', 'split', 'warp']:
		raise ValueError('Supported methods are "chain", "cluster", "merge", "regress", "segment", "split", and "warp"')
	fixation_XY = fixation_sequence.XYarray(include_discards=False)
	if text_block.n_rows == 1:
		fixation_XY[:, 1] = text_block.line_positions[0]
	else:
		if method == 'warp':
			fixation_XY = _drift.warp(fixation_XY, text_block.word_centers)
		else:
			fixation_XY = _drift.__dict__[method](fixation_XY, text_block.line_positions, **kwargs)
	return _FixationSequence([(x, y, f.duration) for f, (x, y) in zip(fixation_sequence, fixation_XY)])

def discard_out_of_bounds_fixations(fixation_sequence, text_block, in_bounds_threshold=128):
	'''
	Given a fixation sequence and text, discard all fixations that do
	not fall within some threshold of any character in the text.
	'''
	if not isinstance(fixation_sequence, _FixationSequence):
		raise TypeError('fixation_sequence should be of type eyekit.FixationSequence')
	if not isinstance(text_block, _TextBlock):
		raise TypeError('text_block should be of type eyekit.Text')
	fixation_sequence_copy = fixation_sequence.copy()
	for fixation in fixation_sequence_copy:
		if not text_block.in_bounds(fixation, in_bounds_threshold):
			fixation.discarded = True
	return fixation_sequence_copy

def fixation_sequence_distance(sequence1, sequence2):
	'''
	Returns Dynamic Time Warping distance between two fixation sequences.
	'''
	if not isinstance(sequence1, _FixationSequence) or not isinstance(sequence2, _FixationSequence):
		raise TypeError('sequence1 and sequence2 should be of type eyekit.FixationSequence')
	cost, _ = _drift._dynamic_time_warping(sequence1.XYarray(), sequence2.XYarray())
	return cost
