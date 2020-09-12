'''

Defines classes for dealing with texts, most notably the
`TextBlock` and `InterestArea` objects.

'''


import re as _re
import numpy as _np


_CASE_SENSITIVE = False
_ALPHABET = list('ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÈÉÌÍÒÓÙÚabcdefghijklmnopqrstuvwxyzàáèéìíòóùú')
_SPECIAL_CHARACTERS = {'À':'A', 'Á':'A', 'È':'E', 'É':'E', 'Ì':'I', 'Í':'I', 'Ò':'O', 'Ó':'O', 'Ù':'U', 'Ú':'U', 'à':'a', 'á':'a', 'è':'e', 'é':'e', 'ì':'i', 'í':'i', 'ò':'o', 'ó':'o', 'ù':'u', 'ú':'u'}
_IA_REGEX = _re.compile(r'(\[(.+?)\]\{(.+?)\})')


class Character:

	'''

	Representation of a single character of text. It is not usually
	necessary to create `Character` objects manually; they are created
	automatically during the instantiation of a `TextBlock`.

	'''

	def __init__(self, parent_text_block, char, r, c):
		self._parent_text_block = parent_text_block
		self.char = char
		self.r, self.c = r, c
		if self.char in _SPECIAL_CHARACTERS:
			self.underlying_char = _SPECIAL_CHARACTERS[char]
		else:
			self.underlying_char = char
		if not _CASE_SENSITIVE:
			self.underlying_char = self.underlying_char.lower()

	def __str__(self):
		return self.char

	def __repr__(self):
		return self.char

	def __eq__(self, other):
		'''

		Special characters are treated as equal to their nonspecial
		counterparts.
		
		'''
		if other in _SPECIAL_CHARACTERS:
			other = _SPECIAL_CHARACTERS[other]
		if _CASE_SENSITIVE:
			return self.underlying_char == other
		return self.underlying_char == other.lower()

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

	@property
	def x(self):
		'''*int* X-coordinate of the character'''
		return self._parent_text_block.first_character_position[0] + self.c * self._parent_text_block.character_spacing

	@property
	def y(self):
		'''*int* Y-coordinate of the character'''
		return self._parent_text_block.first_character_position[1] + self.r * self._parent_text_block.line_spacing

	@property
	def xy(self):
		'''*tuple* XY-coordinates of the character'''
		return self.x, self.y
	
	@property
	def rc(self):
		'''*tuple* Row,column index of the character'''
		return self.r, self.c

	@property
	def non_word_character(self):
		'''*bool* True if the character is non-alphabetical'''
		return self.char not in _ALPHABET

	@property
	def x_tl(self):
		'''X-coordinate of top-left corner of bounding box'''
		return (self._parent_text_block.first_character_position[0] + self.c * self._parent_text_block.character_spacing) - self._parent_text_block.character_spacing // 2
	
	@property
	def y_tl(self):
		'''Y-coordinate of top-left corner of bounding box'''
		return (self._parent_text_block.first_character_position[1] + self.r * self._parent_text_block.line_spacing) - self._parent_text_block.line_spacing // 2

	@property
	def x_br(self):
		'''X-coordinate of bottom-right corner of bounding box'''
		return self.x_tl + self._parent_text_block.character_spacing
	
	@property
	def y_br(self):
		'''Y-coordinate of bottom-right corner of bounding box'''
		return self.y_tl + self._parent_text_block.line_spacing

	@property
	def bounding_box(self):
		'''

		Bounding box around the character; x, y, width, and height.
		`Fixation in Character` returns `True` if the fixation is inside
		this bounding box.

		'''
		return self.x_tl, self.y_tl, self._parent_text_block.character_spacing, self._parent_text_block.line_spacing


class InterestArea:

	'''

	Representation of an interest area – a portion of a `TextBlock` object that
	is of potenital interest. It is not usually necessary to create
	`InterestArea` objects manually; they are created automatically when
	you slice a `TextBlock` object or when you iterate over lines, words,
	characters, ngrams, or parsed interest areas.

	'''

	def __init__(self, parent_text_block, r, c, length, label=None):
		self._parent_text_block = parent_text_block
		self.r, self.c = r, c
		self.length = length
		self.label = label

	def __repr__(self):
		return 'InterestArea[%s]' % self.label

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

	def __getitem__(self, key):
		if key < 0:
			return self._parent_text_block._characters[self.r][self.c+self.length+key]
		return self._parent_text_block._characters[self.r][self.c+key]

	def __iter__(self):
		for char in self.chars:
			yield char

	@property
	def x_tl(self):
		'''X-coordinate of top-left corner of bounding box'''
		return (self._parent_text_block.first_character_position[0] + self.c * self._parent_text_block.character_spacing) - self._parent_text_block.character_spacing // 2
	
	@property
	def y_tl(self):
		'''Y-coordinate of top-left corner of bounding box'''
		return (self._parent_text_block.first_character_position[1] + self.r * self._parent_text_block.line_spacing) - self._parent_text_block.line_spacing // 2

	@property
	def x_br(self):
		'''X-coordinate of bottom-right corner of bounding box'''
		return self.x_tl + self.width
	
	@property
	def y_br(self):
		'''Y-coordinate of bottom-right corner of bounding box'''
		return self.y_tl + self.height

	@property
	def width(self):
		'''Width of the `text.InterestArea`'''
		return self.length * self._parent_text_block.character_spacing
	
	@property
	def height(self):
		'''Height of the interest area'''
		return self._parent_text_block.line_spacing

	@property
	def chars(self):
		'''Characters in the interest area'''
		return self._parent_text_block._characters[self.r][self.c : self.c+self.length]

	@property
	def text(self):
		'''String represention of the interest area'''
		return ''.join(map(str, self.chars))

	@property
	def bounding_box(self):
		'''

		Bounding box around the interest area; x, y, width, and height.
		`Fixation in InterestArea` returns `True` if the fixation is inside
		this bounding box.

		'''
		return self.x_tl, self.y_tl, self.width, self.height

	@property
	def center(self):
		'''XY-coordinates of center of interest area'''
		return self.x_tl + self.width // 2, self.y_tl + self.height // 2

	@property
	def label(self):
		'''Arbitrary label for the interest area'''
		return self._label

	@label.setter
	def label(self, label):
		if label is None:
			self._label = 'slice'
		else:
			self._label = str(label)


class TextBlock:

	'''

	Representation of a piece of text, which may be a word, sentence, or
	entire multiline passage.

	'''

	def __init__(self, text, first_character_position, character_spacing, line_spacing, fontsize):
		'''Initialized with:

		- ```text``` : *str* (single line) or *list* of *str* (multiline) representing the text
		- `first_character_position` : *tuple* providing the XY-coordinates of the center of the first character in the text
		- `character_spacing` : *int* Pixel distance between characters
		- `line_spacing` : *int* Pixel distance between lines
		- `fontsize` : *int* Fontsize (this only affects how images are rendered and is not used in any internal calculations)
		'''
		self.first_character_position = first_character_position
		self.character_spacing = character_spacing
		self.line_spacing = line_spacing
		self.fontsize = fontsize
		if isinstance(text, str):
			self._text = [text]
		elif isinstance(text, list):
			self._text = [str(line) for line in text]
		else:
			raise ValueError('text should be a string or a list of strings')
		self._interest_areas = self._parse_interest_areas()
		self._characters = self._extract_characters()
		self._n_rows = len(self._characters)
		self._n_cols = max([len(row) for row in self._characters])

	def __repr__(self):
		return 'TextBlock[%s...]' % ''.join(self._text[0][:16])

	def __getitem__(self, key):
		'''
		Subsetting a TextBlock object with a row,column index returns
		the indexed characters as an InterestArea.
		'''
		if self.n_rows == 1 and (isinstance(key, int) or isinstance(key, slice)):
			key = 0, key
		if not isinstance(key, tuple) or not len(key) == 2:
			raise IndexError('Index to multiline text should specify both the row and column')
		r, c = key
		if not isinstance(r, int) or r >= self.n_rows or r < 0:
			raise IndexError('Invalid row index')
		if isinstance(c, int):
			if c < 0 or c >= self.n_cols:
				raise IndexError('Invalid column index')
			return InterestArea(self, r, c, 1)
		if isinstance(c, slice):
			c_start = c.start if c.start is not None else 0
			c_stop = c.stop if c.stop is not None else self.n_cols
			if c_start < 0 or c_stop > self.n_cols or c_start >= c_stop:
				raise IndexError('Invalid column slice')
			return InterestArea(self, r, c_start, c_stop-c_start)
		raise IndexError('Invalid index to TextBlock object')

	def __iter__(self):
		'''
		Iterating over a TextBlock object yields each character in the
		text.
		'''
		for line in self._characters:
			for char in line:
				yield char

	# PROPERTIES

	@property
	def first_character_position(self):
		'''*tuple* XY-coordinates of the center of the first character in the text'''
		return self._first_character_position

	@first_character_position.setter
	def first_character_position(self, first_character_position):
		try:
			self._first_character_position = (int(first_character_position[0]), int(first_character_position[1]))
		except:
			raise ValueError('first_character_position should be tuple representing the xy coordinates of the first character')

	@property
	def character_spacing(self):
		'''*int* Pixel distance between characters'''
		return self._character_spacing

	@character_spacing.setter
	def character_spacing(self, character_spacing):
		if not isinstance(character_spacing, int) or character_spacing < 0:
			raise ValueError('character_spacing should be positive integer')
		self._character_spacing = character_spacing

	@property
	def line_spacing(self):
		'''*int* Pixel distance between lines'''
		return self._line_spacing

	@line_spacing.setter
	def line_spacing(self, line_spacing):
		if not isinstance(line_spacing, int) or line_spacing < 0:
			raise ValueError('line_spacing should be positive integer')
		self._line_spacing = line_spacing

	@property
	def fontsize(self):
		'''*int* Fontsize'''
		return self._fontsize

	@fontsize.setter
	def fontsize(self, fontsize):
		if not isinstance(fontsize, int) or fontsize < 0:
			raise ValueError('fontsize should be positive integer')
		self._fontsize = fontsize

	@property
	def n_rows(self):
		'''*int* Number of rows in the text (i.e. the number of lines)'''
		return self._n_rows
	
	@property
	def n_cols(self):
		'''*int* Number of columns in the text (i.e. the number of characters in the widest line)'''
		return self._n_cols

	@property
	def line_positions(self):
		'''*int-array* Y-coordinates of the center of each line of text'''
		return _np.array([line[0].y for line in self._characters], dtype=int)

	@property
	def word_centers(self):
		'''*int-array* XY-coordinates of the center of each word'''
		return _np.array([word.center for word in self.words()], dtype=int)

	
	# PUBLIC METHODS


	def interest_areas(self):
		'''

		Iterate over each `text.InterestArea` parsed from the raw text during
		initialization.
		
		'''
		for _, interest_area in self._interest_areas.items():
			yield interest_area

	def which_interest_area(self, fixation):
		'''

		Returns the parsed `text.InterestArea` that the fixation falls inside

		'''
		for interest_area in self.interest_areas():
			if fixation in interest_area:
				return interest_area
		return None

	def get_interest_area(self, label):
		'''

		Retrieve a parsed `text.InterestArea` by its label.
		
		'''
		if label not in self._interest_areas:
			raise KeyError('There is no interest area with the label %s' % label)
		return self._interest_areas[label]

	def lines(self):
		'''

		Iterate over each line as an `text.InterestArea`.

		'''
		for r, line in enumerate(self._characters):
			yield InterestArea(self, r, 0, len(line), 'line_%i'%r)

	def which_line(self, fixation):
		'''

		Returns the line `text.InterestArea` that the fixation falls inside

		'''
		for line in self.lines():
			if fixation in line:
				return line
		return None

	def words(self):
		'''

		Iterate over each word as an `text.InterestArea`.

		'''
		word_i = 0
		word = []
		for r, line in enumerate(self._characters):
			for char in line:
				if char.non_word_character:
					if word:
						yield InterestArea(self, word[0].r, word[0].c, len(word), 'word_%i'%word_i)
						word_i += 1
					word = []
				else:
					word.append(char)
			if word:
				yield InterestArea(self, word[0].r, word[0].c, len(word), 'word_%i'%word_i)
				word_i += 1
			word = []

	def which_word(self, fixation):
		'''

		Returns the word `text.InterestArea` that the fixation falls inside

		'''
		for word in self.words():
			if fixation in word:
				return word
		return None

	def characters(self, include_non_word_characters=False):
		'''

		Iterate over each character as an `text.InterestArea`.

		'''
		char_i = 0
		for r, line in enumerate(self._characters):
			for c, char in enumerate(line):
				if not include_non_word_characters and char.non_word_character:
					char_i += 1
					continue
				yield InterestArea(self, r, c, 1, 'character_%i'%char_i)
				char_i += 1

	def which_character(self, fixation, include_non_word_characters=False):
		'''

		Returns the character `text.InterestArea` that the fixation falls inside

		'''
		for character in self.characters(include_non_word_characters):
			if fixation in character:
				return character
		return None

	def ngrams(self, n):
		'''

		Iterate over each ngram, for given n, as an `text.InterestArea`.

		'''
		ngram_i = 0
		for r, line in enumerate(self._characters):
			for c in range(len(line)-(n-1)):
				yield InterestArea(self, r, c, n, '%igram_%i'%(n, ngram_i))
				ngram_i += 1

	# No which_ngram() method because, by definition, a fixation is
	# inside multiple ngrams.

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

	def in_bounds(self, fixation, threshold):
		'''
		Returns `True` if the given fixation is within a certain threshold of
		any character in the text. Returns `False` otherwise.
		'''
		for char in self:
			if _distance(fixation.xy, char.xy) <= threshold:
				return True
		return False

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

	# PRIVATE METHODS

	def _parse_interest_areas(self):
		interest_areas = {}
		for r in range(len(self._text)):
			for IA_markup, IA_text, IA_label in _IA_REGEX.findall(self._text[r]):
				if IA_label in interest_areas:
					raise ValueError('The interest area label %s has been used more than once.' % IA_label)
				c = self._text[r].find(IA_markup)
				interest_areas[IA_label] = InterestArea(self, r, c, len(IA_text), IA_label)
				self._text[r] = self._text[r].replace(IA_markup, IA_text)
		return interest_areas

	def _extract_characters(self):
		'''
		Create a 2D grid that stores all valid characters from the text as
		Character objects. This grid can then be iterated over to extract
		ngrams of given size.
		'''
		characters = []
		for r, line in enumerate(self._text):
			characters_line = []
			for c, char in enumerate(line):
				character = Character(self, char, r, c)
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
			distances = [_distance(fixation.xy, char.xy) for char in ngram]
		averagedistance = sum(distances) / len(distances)
		return _np.exp(-averagedistance**2 / (2 * gamma**2))

def _distance(point1, point2):
	'''
	Returns the Euclidean distance between two points.
	'''
	return _np.sqrt(sum([(a - b)**2 for a, b in zip(point1, point2)]))
