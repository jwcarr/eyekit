'''

Defines the `Fixation` and `FixationSequence` objects, which are used to
represent fixation data.

'''


import numpy as _np


class Fixation:

	'''

	Representation of a single fixation event. It is not usually necessary to
	create `Fixation` objects manually; they are created automatically during the
	instantiation of a `FixationSequence`.

	'''

	def __init__(self, x: int, y: int, duration: int, discarded: bool=False):
		self.x = x
		self.y = y
		self.duration = duration
		self.discarded = discarded

	def __repr__(self):
		return 'Fixation[%i,%i]' % self.xy

	@property
	def x(self) -> int:
		'''X-coordinate of the fixation.'''
		return self._x

	@x.setter
	def x(self, x):
		self._x = int(x)

	@property
	def y(self) -> int:
		'''Y-coordinate of the fixation.'''
		return self._y

	@y.setter
	def y(self, y):
		self._y = int(y)

	@property
	def xy(self) -> tuple:
		'''XY-coordinates of the fixation.'''
		return self._x, self._y

	@xy.setter
	def xy(self, xy):
		self._x = int(xy[0])
		self._y = int(xy[1])

	@property
	def duration(self) -> int:
		'''Duration of the fixation in milliseconds.'''
		return self._duration

	@duration.setter
	def duration(self, duration):
		self._duration = int(duration)

	@property
	def discarded(self) -> bool:
		'''`True` if the fixation has been discarded, `False` otherwise.'''
		return self._discarded

	@discarded.setter
	def discarded(self, discarded):
		self._discarded = bool(discarded)

	@property
	def tuple(self) -> tuple:
		'''Tuple representation of the fixation.'''
		if self.discarded:
			return (self._x, self._y, self._duration, True)
		return (self._x, self._y, self._duration)


class FixationSequence:

	'''

	Representation of a sequence of consecutive fixations, typically from a
	single trial.

	'''

	def __init__(self, sequence: list=[]):
		'''Initialized with:

		- `sequence` List of tuples of ints, or something similar, that conforms to
		the following structure: `[(106, 540, 100), (190, 536, 100), ..., (763, 529,
		100)]`, where each tuple contains the X-coordinate, Y-coordinate, and
		duration of a fixation

		'''
		self._sequence = []
		for fixation in sequence:
			self.append(fixation)

	def __repr__(self):
		if len(self) > 2:
			return f'FixationSequence[{str(self._sequence[0])}, ..., {str(self._sequence[-1])}]'
		elif len(self) == 2:
			return f'FixationSequence[{str(self._sequence[0])}, {str(self._sequence[1])}]'
		elif len(self) == 1:
			return f'FixationSequence[{str(self._sequence[0])}]'
		return 'FixationSequence[]'

	def __len__(self):
		return len(self._sequence)

	def __getitem__(self, index):
		if isinstance(index, int):
			return self._sequence[index]
		if isinstance(index, slice):
			return FixationSequence(self._sequence[index.start:index.stop])
		raise IndexError('Index to FixationSequence must be integer or slice')

	def __iter__(self):
		for fixation in self._sequence:
			yield fixation

	def __add__(self, other):
		if not isinstance(other, FixationSequence):
			raise TypeError('Can only concatenate with another FixationSequence')
		return FixationSequence(self._sequence + other._sequence)

	def append(self, fixation):
		if not isinstance(fixation, Fixation):
			try:
				fixation = Fixation(*fixation)
			except:
				raise ValueError('Cannot create FixationSequence, pass a list of (x, y, duration) for each fixation')
		self._sequence.append(fixation)

	def copy(self, include_discards=False):
		'''
		
		Returns a copy of the fixation sequence. Does not include any discarded
		fixations by default, so this can be useful if you want to permanently
		remove all discarded fixations.
		
		'''
		if include_discards:
			return FixationSequence([fixation.tuple for fixation in self.iter_with_discards()])
		return FixationSequence([fixation.tuple for fixation in self.iter_without_discards()])

	def iter_with_discards(self):
		'''

		Iterates over the fixation sequence including any discarded fixations. This
		is also the default behavior when iterating over a `FixationSequence`
		directly.
		
		'''
		for fixation in self._sequence:
			yield fixation

	def iter_without_discards(self):
		'''
		
		Iterates over the fixation sequence without any discarded fixations.
		
		'''
		for fixation in self._sequence:
			if not fixation.discarded:
				yield fixation

	def XYarray(self, include_discards=False):
		'''

		Returns a Numpy array containing the XY-coordinates of the fixations.

		'''
		if include_discards:
			return _np.array([fixation.xy for fixation in self.iter_with_discards()], dtype=int)
		return _np.array([fixation.xy for fixation in self.iter_without_discards()], dtype=int)

	def Xarray(self, include_discards=False):
		'''

		Returns a Numpy array containing the X-coordinates of the fixations.

		'''
		if include_discards:
			return _np.array([fixation.x for fixation in self.iter_with_discards()], dtype=int)
		return _np.array([fixation.x for fixation in self.iter_without_discards()], dtype=int)

	def Yarray(self, include_discards=False):
		'''

		Returns a Numpy array containing the Y-coordinates of the fixations.

		'''
		if include_discards:
			return _np.array([fixation.y for fixation in self.iter_with_discards()], dtype=int)
		return _np.array([fixation.y for fixation in self.iter_without_discards()], dtype=int)

	def _serialize(self):
		'''
		
		Returns representation of the fixation sequence in simple list format for
		serialization.
		
		'''
		return [fixation.tuple for fixation in self.iter_with_discards()]
