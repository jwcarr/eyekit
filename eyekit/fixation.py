import numpy as _np

class Fixation:

	def __init__(self, x, y, duration):
		self.x = x
		self.y = y
		self.duration = duration
		self.discarded = False

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

	@property
	def discarded(self):
		return self._discarded

	@discarded.setter
	def discarded(self, discarded):
		self._discarded = bool(discarded)

	def discard(self):
		self._discarded = True

	def totuple(self):
		return (self.x, self.y, self.duration)

class FixationSequence:

	def __init__(self, sequence=[], min_duration=0):
		if not isinstance(min_duration, int) and not isinstance(min_duration, float):
			raise ValueError('min_duration should be int or float')
		self.min_duration = min_duration
		self.sequence = []
		for fixation in sequence:
			self.append(fixation)

	def __repr__(self):
		return 'FixationSequence[%s, ..., %s]' % (str(self.sequence[0]), str(self.sequence[-1]))

	def __len__(self):
		return len(self.sequence)

	def __getitem__(self, index):
		if isinstance(index, int):
			return self.sequence[index]
		if isinstance(index, slice):
			return FixationSequence(self.sequence[index.start:index.stop])
		raise IndexError('Index to FixationSequence must be integer or slice')

	def __iter__(self):
		for fixation in self.sequence:
			yield fixation

	def __add__(self, other):
		if not isinstance(other, FixationSequence):
			raise TypeError('Can only concatenate with another FixationSequence')
		return FixationSequence(self.sequence + other.sequence)

	def append(self, fixation):
		if not isinstance(fixation, Fixation):
			try:
				x, y, duration = fixation[0], fixation[1], fixation[2]
			except:
				raise ValueError('Cannot create FixationSequence, pass a list of (x, y, duration) for each fixation')
			fixation = Fixation(x, y, duration)
		if fixation.duration > self.min_duration:
			self.sequence.append(fixation)

	def tolist(self):
		'''
		Returns representation of the fixation sequence in simple list
		format for serialization.
		'''
		return [fixation.totuple() for fixation in self.sequence]

	def toarray(self):
		'''
		Returns representation of the fixation sequence as numpy array for
		processing.
		'''
		return _np.array(self.tolist(), dtype=float)
