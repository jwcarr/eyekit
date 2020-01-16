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

	def __init__(self, passage_text, fontsize, first_character_position, character_spacing, line_spacing, pad_lines_with_spaces=False):

		if not isinstance(pad_lines_with_spaces, bool):
			raise ValueError('pad_lines_with_spaces should be boolean')
		self.pad_lines_with_spaces = pad_lines_with_spaces

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
		if self.pad_lines_with_spaces:
			self.first_character_position = first_character_position[0]-character_spacing, first_character_position[1]
		else:
			self.first_character_position = first_character_position[0], first_character_position[1]

		if isinstance(passage_text, str):
			with open(passage_text, mode='r') as file:
				if self.pad_lines_with_spaces:
					self.text = [list(' %s ' % line.strip()) for line in file]
				else:
					self.text = [list(line.strip()) for line in file]
		else:
			if self.pad_lines_with_spaces:
				self.text = [list(' %s ' % line.strip()) for line in passage_text]
			else:
				self.text = [list(line.strip()) for line in passage_text]

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
		any character in the passage. Returns False otherwise.
		'''
		for line in self.characters:
			for char in line:
				if distance(fixation.xy, char.xy) <= in_bounds_threshold:
					return True
		return False

	def _p_ngram_fixation(self, ngram, fixation, gamma, line_only):
		'''
		Returns the unnormalized probability that the participant is
		"seeing" an ngram given a fixation.
		'''
		if line_only:
			distances = [abs(fixation.x - char.x) for char in ngram]
		else:
			distances = [distance(fixation.xy, char.xy) for char in ngram]
		averagedistance = sum(distances) / len(distances)
		return np.exp(-averagedistance**2 / (2 * gamma**2))

	# PUBLIC METHODS

	def rc_to_xy(self, rc, rc2=None):
		'''
		Returns x and y coordinates from row and column indices.
		'''
		if rc2 is None:
			if isinstance(rc, tuple):
				r, c = rc
			else:
				r, c = rc.rc
		else:
			r, c = rc, rc2
		x = self.first_character_position[0] + c*self.character_spacing
		y = self.first_character_position[1] + r*self.line_spacing
		return float(x), float(y)

	def xy_to_rc(self, xy, xy2=None):
		'''
		Returns row and column indices from x and y coordinates.
		'''
		if xy2 is None:
			if isinstance(xy, tuple):
				x, y = xy
			else:
				x, y = xy.xy
		else:
			x, y = xy, xy2
		row = round(y - (self.first_character_position[1] - self.line_spacing//2)) // self.line_spacing
		col = round(x - (self.first_character_position[0] - self.character_spacing//2)) // self.character_spacing
		return int(row), int(col)

	def iter_words(self, filter_func=None, line_n=None):
		'''
		Iterate over words in the passage, optionally of a given
		length.
		'''
		word = []
		for i, line in enumerate(self.characters):
			if line_n is not None and i != line_n:
				continue
			if self.pad_lines_with_spaces:
				line = line[1:-1]
			for char in line:
				if str(char) == '_':
					if filter_func is None or filter_func(word):
						yield word
					word = []
				else:
					word.append(char)
			if filter_func is None or filter_func(word):
				yield word
			word = []

	def iter_chars(self, filter_func=None, line_n=None):
		'''
		Iterate over characters in the passage.
		'''
		for i, line in enumerate(self.characters):
			if line_n is not None and i != line_n:
				continue
			for char in line:
				if filter_func is None or filter_func(char):
					yield char

	def iter_ngrams(self, n, filter_func=None, line_n=None):
		'''
		Iterate over ngrams in the passage, optionally on a given line.
		'''
		for i, line in enumerate(self.characters):
			if line_n is not None and i != line_n:
				continue
			for j in range(len(line)-(n-1)):
				ngram = line[j:j+n]
				if filter_func is None or filter_func(ngram):
					yield ngram

	def nearest_word(self, fixation):
		'''
		Return the nearest word to a given fixation.
		'''
		best_dist = np.inf
		best_word = None
		for word in self.iter_words():
			dist = np.min([distance(fixation.xy, char.xy) for char in word])
			if dist < best_dist:
				best_dist = dist
				best_word = word
		return best_word

	def nearest_char(self, fixation):
		'''
		Return the nearest character to a given fixation. Only valid
		characters are considered (i.e. characters that are specified in the
		alphabet).
		'''
		best_dist = np.inf
		best_char = None
		for char in self.iter_chars():
			dist = distance(fixation.xy, char.xy)
			if dist < best_dist:
				best_dist = dist
				best_char = char
		return best_char

	def nearest_ngram(self, fixation, n):
		'''
		Return the nearest ngram to a given fixation.
		'''
		best_dist = np.inf
		best_ngram = None
		for ngram in self.iter_ngrams(n):
			dist = np.mean([distance(fixation.xy, char.xy) for char in ngram])
			if dist < best_dist:
				best_dist = dist
				best_ngram = ngram
		return best_ngram

	def p_ngrams_fixation(self, fixation, n, gamma=30, line_only=True):
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
			distribution[ngram[0].rc] = self._p_ngram_fixation(ngram, fixation, gamma, line_only)
		return distribution / distribution.sum()

	def sum_duration_mass(self, fixation_sequence, n, gamma=30, in_bounds_threshold=None, line_only=True):
		'''
		Iterate over a sequence of fixations and, for each fixation,
		distribute its duration across the passage (or, optionally, just the
		line) according to the probability that the participant is "seeing"
		each ngram.
		'''
		if in_bounds_threshold is not None:
			fixation_sequence = [fixation for fixation in fixation_sequence if self._in_bounds(fixation, in_bounds_threshold)]
		return sum([fixation.duration * self.p_ngrams_fixation(fixation, n, gamma, line_only) for fixation in fixation_sequence])


def distance(point1, point2):
	'''
	Returns the Euclidean distance between two points.
	'''
	return np.sqrt(sum([(a - b)**2 for a, b in zip(point1, point2)]))
