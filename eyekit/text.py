import re as _re
import numpy as _np


CASE_SENSITIVE = False
ALPHABET = list('ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÈÉÌÍÒÓÙÚabcdefghijklmnopqrstuvwxyzàáèéìíòóùú’ ')
SPECIAL_CHARACTERS = {'’':' ', 'À':'A', 'Á':'A', 'È':'E', 'É':'E', 'Ì':'I', 'Í':'I', 'Ò':'O', 'Ó':'O', 'Ù':'U', 'Ú':'U', 'à':'a', 'á':'a', 'è':'e', 'é':'e', 'ì':'i', 'í':'i', 'ò':'o', 'ó':'o', 'ù':'u', 'ú':'u'}
IA_REGEX = _re.compile(r'(\[(.+?)\]\{(.+?)\})')


class Character:

	def __init__(self, char, r, c, x, y):
		self.char = char
		if self.char in SPECIAL_CHARACTERS:
			self.underlying_char = SPECIAL_CHARACTERS[char]
		else:
			self.underlying_char = char
		if not CASE_SENSITIVE:
			self.underlying_char = self.underlying_char.lower()
		self.x, self.y = x, y
		self.r, self.c = r, c

	def __str__(self):
		return self.char

	def __repr__(self):
		return self.char

	def __eq__(self, other):
		'''
		Special characters are treated as equal to their nonspecial
		counterparts.
		'''
		if other in SPECIAL_CHARACTERS:
			other = SPECIAL_CHARACTERS[other]
		if CASE_SENSITIVE:
			return self.underlying_char == other
		return self.underlying_char == other.lower()

	@property
	def xy(self):
		return self.x, self.y
	
	@property
	def rc(self):
		return self.r, self.c

	@property
	def ignore(self):
		return self.char not in ALPHABET


class InterestArea:

	def __init__(self, label, text, x_tl, y_tl, width, height):
		self.label = label
		self.text = text
		self.x_tl, self.y_tl = x_tl, y_tl
		self.x_br, self.y_br = x_tl + width, y_tl + height
		self.width, self.height = width, height

	def __repr__(self):
		return 'InterestArea[%s]' % self.label

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

	@property
	def rectangle(self):
		return self.x_tl, self.y_tl, self.width, self.height


class Text:

	def __init__(self, text, first_character_position, character_spacing, line_spacing, fontsize):
		
		if not isinstance(first_character_position, tuple) or len(first_character_position) != 2:
			raise ValueError('first_character_position should be tuple representing the xy coordinates of the first character')
		self.first_character_position = first_character_position

		if not isinstance(character_spacing, int) or character_spacing < 0:
			raise ValueError('character_spacing should be positive integer')
		self.character_spacing = character_spacing
		
		if not isinstance(line_spacing, int) or line_spacing < 0:
			raise ValueError('line_spacing should be positive integer')
		self.line_spacing = line_spacing

		if not isinstance(fontsize, int) or fontsize < 0:
			raise ValueError('fontsize should be positive integer')
		self.fontsize = fontsize

		if isinstance(text, str):
			with open(text, mode='r') as file:
				text = [line for line in file]
		self.text = text

		self.characters = self._extract_characters()
		self.n_rows = len(self.characters)
		self.n_cols = max([len(row) for row in self.characters])
		self.line_positions = _np.array([line[0].y for line in self.characters], dtype=int)
		self._interest_areas = self._parse_interest_areas()

	def __repr__(self):
		return 'Text[%s...]' % ''.join(self.text[0][:16])

	def __getitem__(self, key):
		'''
		Subsetting a Text object with a row,column index returns
		the character and its xy coordinates.
		'''
		r, c = key
		if r >= self.n_rows or c >= self.n_cols:
			raise ValueError('Out of bounds')
		x = self.first_character_position[0] + c*self.character_spacing
		y = self.first_character_position[1] + r*self.line_spacing
		try:
			return self.characters[r][c], (x, y)
		except IndexError:
			return None, (x, y)

	def __iter__(self):
		'''
		Iterating over a Text object yields each character in the
		text along with its row-column index and pixel coordinates.
		'''
		for r in range(self.n_rows):
			for c in range(self.n_cols):
				char, xy = self[r,c]
				if char is not None:
					yield char, (r, c), xy

	# PRIVATE METHODS

	def _parse_interest_areas(self):
		interest_areas = {}
		for r in range(len(self.text)):
			for IA_markup, IA_text, IA_label in IA_REGEX.findall(self.text[r]):
				c = self.text[r].find(IA_markup)
				x = (self.first_character_position[0] + c*self.character_spacing) - self.character_spacing // 2
				y = (self.first_character_position[1] + r*self.line_spacing) - self.line_spacing // 2
				width = len(IA_text) * self.character_spacing
				height = self.line_spacing
				interest_areas[IA_label] = InterestArea(IA_label, IA_text, x, y, width, height)
				self.text[r] = self.text[r].replace(IA_markup, IA_text)
		return interest_areas

	def _extract_characters(self):
		'''
		Create a 2D grid that stores all valid characters from the text as
		Character objects. This grid can then be iterated over to extract
		ngrams of given size.
		'''
		characters = []
		for r, line in enumerate(self.text):
			characters_line = []
			for c, char in enumerate(line):
				x = self.first_character_position[0] + c*self.character_spacing
				y = self.first_character_position[1] + r*self.line_spacing
				character = Character(char, r, c, x, y)
				characters_line.append(character)
			characters.append(characters_line)
		return characters

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
		return _np.exp(-averagedistance**2 / (2 * gamma**2))

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
		return int(x), int(y)

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

	def in_bounds(self, fixation, in_bounds_threshold):
		'''
		Returns True if the given fixation is within a certain threshold of
		any character in the text. Returns False otherwise.
		'''
		for line in self.characters:
			for char in line:
				if distance(fixation.xy, char.xy) <= in_bounds_threshold:
					return True
		return False

	def iter_lines(self):
		'''
		Iterate over lines in the text.
		'''
		for line in self.characters:
			yield line

	def iter_words(self, filter_func=None, line_n=None):
		'''
		Iterate over words in the text, optionally on a given line.
		'''
		word = []
		for i, line in enumerate(self.characters):
			if line_n is not None and i != line_n:
				continue
			for char in line:
				if char.ignore:
					continue
				if str(char) == ' ':
					if filter_func is None or filter_func(word):
						yield word
					word = []
				else:
					word.append(char)
			if filter_func is None or filter_func(word):
				yield word
			word = []

	def get_word(self, label):
		for word in self.words():
			if word.label == label:
				return word
		raise KeyError('There is no word with the label %s' % label)

	def iter_chars(self, filter_func=None, line_n=None):
		'''
		Iterate over characters in the text, optionally on a given line.
		'''
		for i, line in enumerate(self.characters):
			if line_n is not None and i != line_n:
				continue
			for char in line:
				if char.ignore:
					continue
				if filter_func is None or filter_func(char):
					yield char

	def iter_ngrams(self, n, filter_func=None, line_n=None):
		'''
		Iterate over ngrams in the text, optionally on a given line.
		'''
		for i, line in enumerate(self.characters):
			if line_n is not None and i != line_n:
				continue
			for j in range(len(line)-(n-1)):
				ngram = line[j:j+n]
				if filter_func is None or filter_func(ngram):
					yield ngram

	def interest_areas(self):
		for _, interest_area in self._interest_areas.items():
			yield interest_area

	def get_interest_area(self, label):
		if label not in self._interest_areas:
			raise KeyError('There is no interest area with the label %s' % label)
		return self._interest_areas[label]

	def word_centers(self):
		'''
		Returns the center points of every word in the text.
		'''
		return _np.array([((word[-1].x - word[0].x) // 2 + word[0].x, word[0].y) for word in self.iter_words()], dtype=int)

	def bounding_box(self, word):
		'''
		Given a word, return the bounding box around that word (x, y, width,
		height).
		'''
		x = word[0].x - self.character_spacing // 2
		y = word[0].y - self.line_spacing // 2
		width = len(word) * self.character_spacing
		height = self.line_spacing
		return x, y, width, height

	def nearest_word(self, fixation):
		'''
		Return the nearest word to a given fixation.
		'''
		best_dist = _np.inf
		best_word = None
		for word in self.iter_words():
			dist = _np.min([distance(fixation.xy, char.xy) for char in word])
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
		best_dist = _np.inf
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
		best_dist = _np.inf
		best_ngram = None
		for ngram in self.iter_ngrams(n):
			dist = _np.mean([distance(fixation.xy, char.xy) for char in ngram])
			if dist < best_dist:
				best_dist = dist
				best_ngram = ngram
		return best_ngram

	def which_interest_area(self, fixation):
		for interest_area in self.interest_areas():
			if fixation in interest_area:
				return interest_area
		return None

	def which_word(self, fixation):
		for word in self.words():
			if fixation in word:
				return word
		return None

	def p_ngrams_fixation(self, fixation, n, gamma=30, line_only=True):
		'''
		Given a fixation, return probability distribution over ngrams in the
		text (or, optionally, just the line), representing the
		probability that each ngram is being "seen".
		'''
		if line_only:
			target_line = _np.argmin(abs(self.line_positions - fixation.y))
		else:
			target_line = None
		distribution = _np.zeros((self.n_rows, self.n_cols-(n-1)), dtype=float)
		for ngram in self.iter_ngrams(n, line_n=target_line):
			distribution[ngram[0].rc] = self._p_ngram_fixation(ngram, fixation, gamma, line_only)
		return distribution / distribution.sum()

	def word_identity_matrix(self):
		matrix = _np.full((self.n_rows, self.n_cols, 2), -1, dtype=int)
		words = []
		for word_i, word in enumerate(self.iter_words()):
			words.append(word)
			for char_i, char in enumerate(word):
				matrix[char.rc][0] = word_i
				matrix[char.rc][1] = char_i
		return matrix, words


def distance(point1, point2):
	'''
	Returns the Euclidean distance between two points.
	'''
	return _np.sqrt(sum([(a - b)**2 for a, b in zip(point1, point2)]))
