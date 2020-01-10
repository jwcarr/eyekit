class Fixation:

	def __init__(self, x, y, duration):
		self.x, self.y = x, y
		self.duration = duration

	def __repr__(self):
		return 'Fixation[%i,%i]' % self.xy

	@property
	def xy(self):
		return self.x, self.y

	def replace_y(self, revised_y):
		return Fixation(self.x, revised_y, self.duration)
