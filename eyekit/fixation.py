from copy import deepcopy as _deepcopy
import numpy as _np

class Fixation:

	def __init__(self, x, y, duration):
		self.x = x
		self.y = y
		self.duration = duration

	def __repr__(self):
		return 'Fixation[%i,%i]' % self.xy

	@property
	def x(self):
		return self._x

	@x.setter
	def x(self, x):
		self._x = float(x)

	@property
	def y(self):
		return self._y

	@y.setter
	def y(self, y):
		self._y = float(y)

	@property
	def xy(self):
		return self._x, self._y

	@xy.setter
	def xy(self, xy):
		self._x = float(xy[0])
		self._y = float(xy[1])

	@property
	def duration(self):
		return self._duration

	@duration.setter
	def duration(self, duration):
		self._duration = float(duration)

	def totuple(self):
		return (self._x, self._y, self._duration)

	def copy(self):
		return Fixation(self._x, self._y, self._duration)

	def replace_y(self, y):
		return Fixation(self._x, y, self._duration)


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
			yield fixation

	def __add__(self, other):
		if not isinstance(other, FixationSequence):
			raise TypeError('Can only concatenate with another FixationSequence')
		return FixationSequence(self._sequence + other._sequence)

	def append(self, fixation):
		if not isinstance(fixation, Fixation):
			try:
				x, y, duration = fixation[0], fixation[1], fixation[2]
			except:
				raise ValueError('Cannot create FixationSequence, pass a list of (x, y, duration) for each fixation')
			fixation = Fixation(x, y, duration)
		self._sequence.append(fixation)

	def copy(self):
		'''
		Retuns a copy of the fixation sequence.
		'''
		fixation_sequence = FixationSequence(self._sequence)
		fixation_sequence._sequence = _deepcopy(self._sequence)
		return fixation_sequence

	def tolist(self):
		'''
		Returns representation of the fixation sequence in simple list
		format for serialization.
		'''
		return [fixation.totuple() for fixation in self._sequence]

	def toarray(self):
		'''
		Returns representation of the fixation sequence as numpy array for
		processing.
		'''
		return _np.array(self.tolist(), dtype=float)
