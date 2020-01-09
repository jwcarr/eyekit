import numpy as np


CASE_SENSITIVE = False
ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'à', 'á', 'è', 'é', 'ì', 'í', 'ò', 'ó', 'ù', 'ú', ' ', '’']
SPECIAL_CHARACTERS = {'à':'a', 'á':'a', 'è':'e', 'é':'e', 'ì':'i', 'í':'i', 'ò':'o', 'ó':'o', 'ù':'u', 'ú':'u', ' ':'_', '’':'_'}


class Character:

	def __init__(self, char, r, c, x, y):
		self.char = char
		self.x, self.y = x, y
		self.r, self.c = r, c

	def __str__(self):
		if self.char in SPECIAL_CHARACTERS:
			return SPECIAL_CHARACTERS[self.char]
		return self.char

	def __repr__(self):
		return self.char

	def __eq__(self, other):
		'''
		Special characters are treated as equal to their nonspecial
		counterparts.
		'''
		char = self.char
		if char in SPECIAL_CHARACTERS:
			char = SPECIAL_CHARACTERS[char]
		if other in SPECIAL_CHARACTERS:
			other = SPECIAL_CHARACTERS[other]
		return char == other

	@property
	def xy(self):
		return self.x, self.y
	
	@property
	def rc(self):
		return self.r, self.c


class Passage:

	def __init__(self, passage_text, fontsize, first_character_position, character_spacing, line_spacing):

		if not isinstance(fontsize, int) or fontsize < 0:
			raise ValueError('fontsize should be positive integer')
		self.fontsize = fontsize
		
		if not isinstance(character_spacing, int) or character_spacing < 0:
			raise ValueError('character_spacing should be positive integer')
		self.character_spacing = character_spacing
		
		if not isinstance(line_spacing, int) or line_spacing < 0:
			raise ValueError('line_spacing should be positive integer')
		self.line_spacing = line_spacing

		if not isinstance(first_character_position, tuple) or len(first_character_position) != 2:
			raise ValueError('first_character_position should be tuple representing the xy coordinates of the first character')
		self.first_character_position = first_character_position[0]-character_spacing, first_character_position[1]

		if isinstance(passage_text, str):
			with open(passage_text, mode='r') as file:
				self.text = [list(' %s ' % line.strip()) for line in file]
		else:
			self.text = [list(' %s ' % line.strip()) for line in passage_text]

		self.n_rows = len(self.text)
		self.n_cols = max([len(row) for row in self.text])

		self.characters, self.char_xy = self._extract_characters()
		self.line_positions = np.array([line[0].y for line in self.characters])

	def __repr__(self):
		return 'Passage[%s...]' % ''.join(self.text[0][1:17])

	def __getitem__(self, key):
		'''
		Subsetting a Passage object with a row,column index returns
		the character and its xy coordinates.
		'''
		r, c = key
		if r >= self.n_rows or c >= self.n_cols:
			raise ValueError('Out of bounds')
		x = self.first_character_position[0] + c*self.character_spacing
		y = self.first_character_position[1] + r*self.line_spacing
		try:
			return self.text[r][c], (x, y)
		except IndexError:
			return None, (x, y)

	def __iter__(self):
		'''
		Iterating over a Passage object yields each character in the
		passage along with its row-column index and pixel coordinates.
		'''
		for r in range(self.n_rows):
			for c in range(self.n_cols):
				char, xy = self[r,c]
				if char is not None:
					yield char, (r, c), xy

	# PRIVATE METHODS

	def _extract_characters(self):
		'''
		Create a 2D grid that stores all valid characters from the text as
		Character objects. This grid can then be iterated over to extract
		ngrams of given size.
		'''
		characters, char_xy = [], []
		for r, line in enumerate(self.text):
			characters_line = []
			for c, char in enumerate(line):
				if not CASE_SENSITIVE:
					char = char.lower()
				if char in ALPHABET:
					x = self.first_character_position[0] + c*self.character_spacing
					y = self.first_character_position[1] + r*self.line_spacing
					characters_line.append(Character(char, r, c, x, y))
					char_xy.append((x, y))
			characters.append(characters_line)
		return characters, np.array(char_xy, dtype=float)

	def _in_bounds(self, fixation, in_bounds_threshold):
		'''
		Returns True if the given fixation is within a certain threshold of
		any character in the passage. Returns False otherwise. The threshold
		is set at init time.
		'''
		for line in self.characters:
			for char in line:
				if distance(fixation.xy, char.xy) <= in_bounds_threshold:
					return True
		return False

	def _p_ngram_fixation(self, ngram, fixation, line_only):
		'''
		Returns the unnormalized probability that the participant is
		"seeing" an ngram given a fixation.
		'''
		if line_only:
			distances = [abs(fixation.x - char.x) for char in ngram]
		else:
			distances = [distance(fixation.xy, char.xy) for char in ngram]
		averagedistance = sum(distances) / len(distances)
		return np.exp(-averagedistance**2 / (2 * fixation.gamma**2))

	# PUBLIC METHODS

	def iter_words(self, length=None):
		'''
		Iterate over words in the passage, optionally of a given
		length.
		'''
		word = []
		for line in self.characters:
			for char in line[1:-1]:
				if str(char) == '_':
					if length is None or len(word) == length:
						yield word
					word = []
				else:
					word.append(char)
			if length is None or len(word) == length:
				yield word
			word = []

	def iter_chars(self):
		'''
		Iterate over characters in the passage.
		'''
		for line in self.characters:
			for char in line:
				yield char

	def iter_ngrams(self, n, line_n=None):
		'''
		Iterate over ngrams in the passage, optionally on a given line.
		'''
		for i, line in enumerate(self.characters):
			if line_n is not None and i != line_n:
				continue
			for j in range(len(line)-(n-1)):
				yield line[j:j+n]

	def word_from_fixation(self):
		pass

	def p_ngrams_fixation(self, fixation, n, line_only=True):
		'''
		Given a fixation, return probability distribution over ngrams in the
		passage (or, optionally, just the line), representing the
		probability that each ngram is being "seen".
		'''
		if line_only:
			target_line = np.argmin(abs(self.line_positions - fixation.y))
		else:
			target_line = None
		distribution = np.zeros((self.n_rows, self.n_cols-(n-1)), dtype=float)
		for ngram in self.iter_ngrams(n, line_n=target_line):
			distribution[ngram[0].rc] = self._p_ngram_fixation(ngram, fixation, line_only)
		return distribution / distribution.sum()

	def snap_fixation_sequence_to_lines(self, fixation_sequence, bounce_threshold=100, in_bounds_threshold=50):
		'''
		Given a fixation sequence, snap each fixation's y-axis coordinate to
		the line it most likely belongs to, removing any vertical variation
		other than movements from one line to the next. If a fixation's
		revised y-axis coordinate falls more than (bounce_threshold) pixels
		away from its original position, it is eliminated.
		'''
		fixn_xy = np.array([fixn.xy for fixn in fixation_sequence], dtype=float)
		alignment, cost = dtw(fixn_xy, self.char_xy)
		snapped_fixation_sequence = []
		for fixn_index, char_indices in enumerate(alignment):
			line_y = mode([int(self.char_xy[char_index][1]) for char_index in char_indices])
			if abs(fixation_sequence[fixn_index].y - line_y) < bounce_threshold:
				snapped_fixation = fixation_sequence[fixn_index].replace_y(line_y)
				if self._in_bounds(snapped_fixation, in_bounds_threshold):
					snapped_fixation_sequence.append(snapped_fixation)
		return snapped_fixation_sequence

	def sum_duration_mass(self, fixation_sequence, n, in_bounds_threshold=None, line_only=True):
		'''
		Iterate over a sequence of fixations and, for each fixation,
		distribute its duration across the passage (or, optionally, just the
		line) according to the probability that the participant is "seeing"
		each ngram.
		'''
		if in_bounds_threshold is not None:
			fixation_sequence = [fixation for fixation in fixation_sequence if self._in_bounds(fixation, in_bounds_threshold)]
		return sum([fixation.duration * self.p_ngrams_fixation(fixation, n, line_only) for fixation in fixation_sequence])


def mode(lst):
	'''
	Returns modal value from a list of values.
	'''
	return max(set(lst), key=lst.count)

def distance(point1, point2):
	'''
	Returns the Euclidean distance between two points.
	'''
	return np.sqrt(sum([(a - b)**2 for a, b in zip(point1, point2)]))

def dtw(series1, series2):
	'''
	Returns the best alignment between two time series and the resulting
	cost using the Dynamic Time Warping algorithm. Adapted from
	https://github.com/talcs/simpledtw - Copyright (c) 2018 talcs (MIT
	License)
	'''
	matrix = np.zeros((len(series1) + 1, len(series2) + 1))
	matrix[0,:] = np.inf
	matrix[:,0] = np.inf
	matrix[0,0] = 0
	for i, vec1 in enumerate(series1):
		for j, vec2 in enumerate(series2):
			cost = np.linalg.norm(vec1 - vec2)
			matrix[i + 1, j + 1] = cost + min(matrix[i, j + 1], matrix[i + 1, j], matrix[i, j])
	matrix = matrix[1:,1:]
	i = matrix.shape[0] - 1
	j = matrix.shape[1] - 1
	alignment = [list() for v in range(matrix.shape[0])]
	while i > 0 or j > 0:
		alignment[i].append(j)
		option_diag = matrix[i - 1, j - 1] if i > 0 and j > 0 else np.inf
		option_up = matrix[i - 1, j] if i > 0 else np.inf
		option_left = matrix[i, j - 1] if j > 0 else np.inf
		move = np.argmin([option_diag, option_up, option_left])
		if move == 0:
			i -= 1
			j -= 1
		elif move == 1:
			i -= 1
		else:
			j -= 1
	alignment[0].append(0)
	return alignment, matrix[-1, -1]
