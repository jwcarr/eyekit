import numpy as _np

class Fixation:

	def __init__(self, x, y, duration, discarded=False):
		self.x = x
		self.y = y
		self.duration = duration
		self.discarded = discarded

	def __repr__(self):
		return 'Fixation[%i,%i]' % self.xy

	@property
	def x(self):
		return self._x

	@x.setter
	def x(self, x):
		self._x = int(x)

	@property
	def y(self):
		return self._y

	@y.setter
	def y(self, y):
		self._y = int(y)

	@property
	def xy(self):
		return self._x, self._y

	@xy.setter
	def xy(self, xy):
		self._x = int(xy[0])
		self._y = int(xy[1])

	@property
	def duration(self):
		return self._duration

	@duration.setter
	def duration(self, duration):
		self._duration = int(duration)

	@property
	def discarded(self):
		return self._discarded

	@discarded.setter
	def discarded(self, discarded):
		self._discarded = bool(discarded)

	def totuple(self):
		return (self._x, self._y, self._duration, self._discarded)

	def copy(self):
		return Fixation(self._x, self._y, self._duration, self._discarded)


class FixationSequence:

	def __init__(self, sequence=[]):
		self._sequence = []
		for fixation in sequence:
			self.append(fixation)

	def __repr__(self):
		return 'FixationSequence[%s, ..., %s]' % (str(self._sequence[0]), str(self._sequence[-1]))

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
			if not fixation.discarded:
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

	def iter_with_discards(self):
		'''
		Iterate over fixation sequence including discarded fixations.
		'''
		for fixation in self._sequence:
			yield fixation

	def copy(self, include_discards=False):
		'''
		Retuns a copy of the fixation sequence.
		'''
		if include_discards:
			return FixationSequence([fixation.totuple() for fixation in self.iter_with_discards()])
		return FixationSequence([fixation.totuple() for fixation in self])

	def tolist(self, include_discards=False):
		'''
		Returns representation of the fixation sequence in simple list
		format for serialization.
		'''
		if include_discards:
			return [fixation.totuple() for fixation in self.iter_with_discards()]
		return [fixation.totuple() for fixation in self]

	def toarray(self, include_discards=False):
		'''
		Returns representation of the fixation sequence as numpy array for
		processing.
		'''
		return _np.array(self.tolist(include_discards), dtype=int)
