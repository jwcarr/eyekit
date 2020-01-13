class Fixation:

	def __init__(self, x, y, duration):
		try:
			x, y, duration = float(x), float(y), float(duration)
		except:
			raise ValueError('Cannot create Fixation; invalid values')
		self.x, self.y = x, y
		self.duration = duration

	def __repr__(self):
		return 'Fixation[%i,%i]' % self.xy

	def __getitem__(self, index):
		if index == 0:
			return self.x
		if index == 1:
			return self.y
		if index == 2:
			return self.duration
		raise IndexError('Index can only be 0 (x), 1 (y), or 2 (duration)')

	@property
	def xy(self):
		return self.x, self.y

	def replace_y(self, revised_y):
		'''
		Returns copy of the fixation with a revised y-coordinate
		'''
		return Fixation(self.x, revised_y, self.duration)


class FixationSequence:

	def __init__(self, sequence, min_duration=0):
		if not isinstance(min_duration, int) and not isinstance(min_duration, float):
			raise ValueError('min_duration should be int or float')
		self.sequence = []
		for fixation in sequence:
			if not isinstance(fixation, Fixation):
				try:
					x, y, duration = fixation[0], fixation[1], fixation[2]
				except:
					raise ValueError('Cannot create FixationSequence, pass a list of (x, y, duration) for each fixation')
				fixation = Fixation(x, y, duration)
			if fixation.duration > min_duration:
				self.sequence.append(fixation)

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
