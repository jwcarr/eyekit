class Fixation:

	def __init__(self, x, y, duration):
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

	@property
	def xy(self):
		return self.x, self.y

	def replace_y(self, revised_y):
		return Fixation(self.x, revised_y, self.duration)


class FixationSequence:

	def __init__(self, sequence, min_duration=0):
		self.sequence = []
		for fixation in sequence:
			try:
				x, y, duration = float(fixation[0]), float(fixation[1]), float(fixation[2])
			except:
				raise ValueError('To create a fixation sequence, pass a list of (x, y, duration) for each fixation')
			if duration > min_duration:
				self.sequence.append(Fixation(x, y, duration))

	def __repr__(self):
		return 'FixationSequence[%s, ..., %s]' % (str(self.sequence[0]), str(self.sequence[-1]))

	def __len__(self):
		return len(self.sequence)

	def __getitem__(self, index):
		if isinstance(index, int):
			return self.sequence[index]
		if isinstance(index, slice):
			return FixationSequence(self.sequence[index.start:index.stop])

	def __iter__(self):
		for fixation in self.sequence:
			yield fixation
