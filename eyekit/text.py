'''

Defines classes for dealing with texts, most notably the
`TextBlock` and `InterestArea` objects.

'''


import re as _re
import numpy as _np
from fontTools.ttLib import TTFont as _TTFont
from matplotlib import font_manager as _font_manager


_CASE_SENSITIVE = False
_ALPHABET = list('ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÈÉÌÍÒÓÙÚabcdefghijklmnopqrstuvwxyzàáèéìíòóùú')
_SPECIAL_CHARACTERS = {'À':'A', 'Á':'A', 'È':'E', 'É':'E', 'Ì':'I', 'Í':'I', 'Ò':'O', 'Ó':'O', 'Ù':'U', 'Ú':'U', 'à':'a', 'á':'a', 'è':'e', 'é':'e', 'ì':'i', 'í':'i', 'ò':'o', 'ó':'o', 'ù':'u', 'ú':'u'}
_IA_REGEX = _re.compile(r'(\[(.+?)\]\{(.+?)\})')


class Character:

	'''

	Representation of a single character of text. A `Character` object is
	essentially a one-letter string that occupies a position in space and
	has a bounding box. It is not usually necessary to create `Character`
	objects manually; they are created automatically during the
	instantiation of a `TextBlock`.

	'''

	def __init__(self, char, x_tl, y_tl, width, height):
		if isinstance(char, str) and len(char) == 1:
			self._char = char
		else:
			raise ValueError('char must be one-letter string')
		self._x_tl, self._y_tl = float(x_tl), float(y_tl)
		self._width, self._height = float(width), float(height)

	def __repr__(self):
		return self._char

	def __str__(self):
		return self._char

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

	# IMMUTABLE POSITIONAL PROPERTIES

	@property
	def x(self):
		'''*float* X-coordinate of the center of the character'''
		return self.x_tl + self.width / 2

	@property
	def y(self):
		'''*float* Y-coordinate of the center of the character'''
		return self.y_tl + self.height / 2

	@property
	def x_tl(self):
		'''*float* X-coordinate of the top-left corner of character's bounding box'''
		return self._x_tl
	
	@property
	def y_tl(self):
		'''*float* Y-coordinate of the top-left corner of character's bounding box'''
		return self._y_tl

	@property
	def x_br(self):
		'''*float* X-coordinate of the bottom-right corner of character's bounding box'''
		return self._x_tl + self._width
	
	@property
	def y_br(self):
		'''*float* Y-coordinate of the bottom-right corner of character's bounding box'''
		return self._y_tl + self._height

	@property
	def width(self):
		'''*float* Width of the character'''
		return self.x_br - self.x_tl
	
	@property
	def height(self):
		'''*float* Height of the character (i.e., the line height inherited from the `TextBlock`)'''
		return self.y_br - self.y_tl

	@property
	def box(self):
		'''*tuple* The character's bounding box: x, y, width, and height'''
		return self._x_tl, self._y_tl, self._width, self._height

	@property
	def center(self):
		'''*tuple* XY-coordinates of center of character'''
		return self.x, self.y

	# OTHER PROPERTIES

	@property
	def non_word_character(self):
		'''*bool* True if the character is non-alphabetical'''
		return self._char not in _ALPHABET


class InterestArea:

	'''

	Representation of an interest area – a portion of a `TextBlock` object that
	is of potenital interest. It is not usually necessary to create
	`InterestArea` objects manually; they are created automatically when
	you slice a `TextBlock` object or when you iterate over lines, words,
	characters, ngrams, or parsed interest areas.

	'''

	def __init__(self, chars, label=None, padding=0):
		for char in chars:
			if not isinstance(char, Character):
				raise ValueError('chars must only contain Character objects')
		self._chars = chars
		self.label = label
		self._padding = padding

	def __repr__(self):
		return 'InterestArea[%s]' % self.label

	def __str__(self):
		return self.text

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

	def __getitem__(self, key):
		self._chars[key]

	def __len__(self):
		return len(self._chars)

	def __iter__(self):
		for char in self._chars:
			yield char

	# IMMUTABLE POSITIONAL PROPERTIES

	@property
	def x(self):
		'''*float* X-coordinate of the center of the interest area'''
		return self.x_tl + self.width / 2

	@property
	def y(self):
		'''*float* Y-coordinate of the center of the interest area'''
		return self.y_tl + self.height / 2

	@property
	def x_tl(self):
		'''*float* X-coordinate of the top-left corner of the interest area's bounding box'''
		return self._chars[0].x_tl - self._padding
	
	@property
	def y_tl(self):
		'''*float* Y-coordinate of the top-left corner of the interest area's bounding box'''
		return self._chars[0].y_tl

	@property
	def x_br(self):
		'''*float* X-coordinate of the bottom-right corner of the interest area's bounding box'''
		return self._chars[-1].x_br + self._padding
	
	@property
	def y_br(self):
		'''*float* Y-coordinate of the bottom-right corner of the interest area's bounding box'''
		return self._chars[-1].y_br

	@property
	def width(self):
		'''*float* Width of the interest area'''
		return self.x_br - self.x_tl
	
	@property
	def height(self):
		'''*float* Height of the interest area'''
		return self.y_br - self.y_tl

	@property
	def box(self):
		'''*tuple* The interest area's bounding box: x, y, width, and height'''
		return self.x_tl, self.y_tl, self.width, self.height

	@property
	def center(self):
		'''*tuple* XY-coordinates of center of interest area'''
		return self.x, self.y

	# OTHER PROPERTIES

	@property
	def text(self):
		'''*str* String represention of the interest area. Same as calling `str()` on an `InterestArea`.'''
		return ''.join(map(str, self._chars))

	@property
	def label(self):
		'''*str* Arbitrary label for the interest area'''
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

	def __init__(self, text, position, font_name, font_size, line_spacing=1.0):
		'''Initialized with:

		- ```text``` *str* (single line) | *list* of *str* (multiline) : The line or lines of text
		- `position` *tuple*[*float*, *float*] : XY-coordinates of the top left corner of the `TextBlock`'s bounding box
		- `font_name` *str* : Name of a font available on your system. Matplotlib's FontManager is used to discover available fonts.
		- `font_size` *float* : Font size in points.
		- `line_spacing` *float* : Amount of line spacing (1 for single line spacing, 2 for double line spacing, etc.)
		'''
		if isinstance(text, str):
			self._text = [text]
		elif isinstance(text, list):
			self._text = [str(line) for line in text]
		else:
			raise ValueError('text should be a string or a list of strings')
		
		try:
			self._x_tl = float(position[0])
			self._y_tl = float(position[1])
		except:
			raise ValueError('position should be tuple representing the XY coordinates of the top left corner of the TextBlock')

		if not isinstance(font_name, str):
			raise ValueError('font_name shoud be a string')
		self._font = _load_font(font_name)
		self._font_name = font_name

		try:
			self._font_size = float(font_size)
		except:
			raise ValueError('font_size should be numeric')
		if self._font_size < 1:
			raise ValueError('font_size should be at least 1pt')

		try:
			self._line_spacing = float(line_spacing)
		except:
			raise ValueError('line_spacing should be numeric')
		if self._line_spacing < 0.5:
			raise ValueError('line_spacing should be at least 0.5')
		self._line_height = self._font_size * self._line_spacing

		self._characters, self._interest_areas = self._initialize_text_block()

	def __repr__(self):
		return 'TextBlock[%s...]' % ''.join(map(str, self._characters[0][:16]))

	def __str__(self):
		return ' '.join([''.join(map(str, line)) for line in self._characters])

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

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
			return InterestArea([self._characters[r][c]])
		if isinstance(c, slice):
			try:
				return InterestArea(self._characters[r][c])
			except IndexError as exception:
				exception.args = ('Invalid column slice',)
				raise
		raise IndexError('Invalid index to TextBlock object')

	def __len__(self):
		return sum([len(line) for line in self._characters])

	def __iter__(self):
		'''
		Iterating over a TextBlock object yields each character in the
		text.
		'''
		for line in self._characters:
			for char in line:
				yield char

	# IMMUTABLE POSITIONAL PROPERTIES

	@property
	def x(self):
		'''*float* X-coordinate of the center of the TextBlock'''
		return self._x_tl + self.width / 2

	@property
	def y(self):
		'''*float* Y-coordinate of the center of the TextBlock'''
		return self._y_tl + self.height / 2

	@property
	def x_tl(self):
		'''*float* X-coordinate of the top-left corner of the TextBlock'''
		return self._x_tl

	@property
	def y_tl(self):
		'''*float* Y-coordinate of the top-left corner of the TextBlock'''
		return self._y_tl

	@property
	def x_br(self):
		'''*float* X-coordinate of the bottom-right corner of TextBlock'''
		return self._x_tl + self.width
	
	@property
	def y_br(self):
		'''*float* Y-coordinate of the bottom-right corner of TextBlock'''
		return self._y_tl + self.height

	@property
	def width(self):
		'''*float* Width of the TextBlock (i.e. the width of the widest line)'''
		max_width = 0.0
		for line in self._characters:
			line_width = sum([char.width for char in line])
			if line_width > max_width:
				max_width = line_width
		return max_width

	@property
	def height(self):
		'''*float* Height of the TextBlock'''
		return self.n_rows * self._line_height

	@property
	def box(self):
		'''*tuple* The interest area's bounding box: x, y, width, and height'''
		return self._x_tl, self._y_tl, self.width, self.height

	@property
	def center(self):
		'''*tuple* XY-coordinates of center of interest area'''
		return self.x, self.y

	# FONT PROPERTIES

	@property
	def font_name(self):
		'''*str* Name of the font'''
		return self._font_name

	@property
	def font_size(self):
		'''*float* Font size in points'''
		return self._font_size

	@property
	def line_spacing(self):
		'''*float* Line spacing (single, double, etc.)'''
		return self._line_spacing

	@property
	def line_height(self):
		'''*float* Pixel distance between lines'''
		return self._line_height

	# OTHER PROPERTIES

	@property
	def n_rows(self):
		'''*int* Number of rows in the text (i.e. the number of lines)'''
		return len(self._characters)
	
	@property
	def n_cols(self):
		'''*int* Number of columns in the text (i.e. the number of characters in the widest line)'''
		return max([len(row) for row in self._characters])

	@property
	def line_positions(self):
		'''*int-array* Y-coordinates of the center of each line of text'''
		return _np.array([line[0].y for line in self._characters], dtype=int)

	@property
	def word_centers(self):
		'''*int-array* XY-coordinates of the center of each word'''
		return _np.array([word.center for word in self.words()], dtype=int)

	################
	# PUBLIC METHODS
	################

	def interest_areas(self):
		'''

		Iterate over each `InterestArea` parsed from the raw text during
		initialization.
		
		'''
		for _, interest_area in self._interest_areas.items():
			yield interest_area

	def which_interest_area(self, fixation):
		'''

		Returns the parsed `InterestArea` that the fixation falls inside

		'''
		for interest_area in self.interest_areas():
			if fixation in interest_area:
				return interest_area
		return None

	def get_interest_area(self, label):
		'''

		Retrieve a parsed `InterestArea` by its label.
		
		'''
		if label not in self._interest_areas:
			raise KeyError('There is no interest area with the label %s' % label)
		return self._interest_areas[label]

	def lines(self):
		'''

		Iterate over each line as an `InterestArea`.

		'''
		for r, line in enumerate(self._characters):
			yield InterestArea(line, 'line_%i'%r)

	def which_line(self, fixation):
		'''

		Returns the line `InterestArea` that the fixation falls inside

		'''
		for line in self.lines():
			if fixation in line:
				return line
		return None

	def words(self, add_padding=True):
		'''

		Iterate over each word as an `InterestArea`. `add_padding` adds a
		little extra width to each word's bounding box, so that they cover
		the adjoining spaces or punctuation.

		'''
		if add_padding:
			half_space_width = self._get_character_width(' ') / 2
		word_i = 0
		word = []
		for r, line in enumerate(self._characters):
			for char in line:
				if char.non_word_character:
					if word:
						yield InterestArea(word, 'word_%i'%word_i, padding=half_space_width)
						word_i += 1
					word = []
				else:
					word.append(char)
			if word:
				yield InterestArea(word, 'word_%i'%word_i, padding=half_space_width)
				word_i += 1
			word = []

	def which_word(self, fixation, add_padding=True):
		'''

		Returns the word `InterestArea` that the fixation falls inside.
		`add_padding` adds a little extra width to each word's bounding
		box, so that they cover the adjoining spaces or punctuation.

		'''
		for word in self.words(add_padding):
			if fixation in word:
				return word
		return None

	def characters(self, include_non_word_characters=False):
		'''

		Iterate over each character as an `InterestArea`.

		'''
		char_i = 0
		for r, line in enumerate(self._characters):
			for char in line:
				if not include_non_word_characters and char.non_word_character:
					char_i += 1
					continue
				yield InterestArea([char], 'character_%i'%char_i)
				char_i += 1

	def which_character(self, fixation, include_non_word_characters=False):
		'''

		Returns the character `InterestArea` that the fixation falls inside

		'''
		for character in self.characters(include_non_word_characters):
			if fixation in character:
				return character
		return None

	def ngrams(self, n):
		'''

		Iterate over each ngram, for given n, as an `InterestArea`.

		'''
		ngram_i = 0
		for r, line in enumerate(self._characters):
			for c in range(len(line)-(n-1)):
				yield InterestArea(line[c:c+n], '%igram_%i'%(n, ngram_i))
				ngram_i += 1

	# No which_ngram() method because, by definition, a fixation is
	# inside multiple ngrams.

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

	def todict(self):
		'''
		
		Returns the `TextBlock`'s ininialization arguments as a dictionary
		for serialization.
		
		'''
		dic = {}
		dic['position'] = self.x_tl, self.y_tl
		dic['font_name'] = self.font_name
		dic['font_size'] = self.font_size
		dic['line_spacing'] = self.line_spacing
		dic['text'] = self._text
		return dic

	#################
	# PRIVATE METHODS
	#################

	def _initialize_text_block(self):
		'''

		Parses out any marked up interest areas from the text and then
		converts and stores every character as a Character object with the
		appropriate character width.

		'''
		characters = []
		interest_areas = {}
		y_tl = self.y_tl
		for r, line in enumerate(self._text):
			for IA_markup, IA_text, IA_label in _IA_REGEX.findall(line):
				if IA_label in interest_areas:
					raise ValueError('The interest area label %s has been used more than once.' % IA_label)
				c = line.find(IA_markup)
				interest_areas[IA_label] = (r, c, len(IA_text))#InterestArea([], IA_label) # THIS NEEDS TO BE FIXED - cannot create IA yet, because no chars created
				line = line.replace(IA_markup, IA_text)
			characters_line = []
			x_tl = self.x_tl
			for c, char in enumerate(line):
				character_width = self._get_character_width(char)
				character = Character(char, x_tl, y_tl, character_width, self.line_height)
				characters_line.append(character)
				x_tl += character_width
			characters.append(characters_line)
			y_tl += self.line_height
		for IA_label, (r, c, length) in interest_areas.items():
			interest_areas[IA_label] = InterestArea(characters[r][c:c+length], IA_label)
		return characters, interest_areas

	def _get_character_width(self, char):
		'''

		Compute the character width in the TextBlock's font.
		
		'''
		try:
			character_location = self._font['cmap'][ord(char)]
		except KeyError as exception:
			exception.args = (f'The character "{char}" is not available in "{self.font_name}".',)
			raise 
		character_width = self._font['glyph_set'][character_location].width
		return character_width * self._font_size / self._font['units_per_em']

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

def _memoize(f):
    memo = {}
    def helper(x):
        if x not in memo:            
            memo[x] = f(x)
        return memo[x]
    return helper

@_memoize
def _load_font(font_name):
	'''

	Given a font name, attempt to find its TrueType file on the system
	using Matplotlib's FontManager and then use fontTools to extract the
	character map, glyph set, and em size. The output of this function is
	memoized, so that this slow process doesn't have to be performed many
	times for the same font.

	'''
	fm = _font_manager.FontManager()
	try:
		
		font_path = fm.findfont(_font_manager.FontProperties([font_name]), fallback_to_default=False)
	except Exception as exception:
		exception.args = (f'Failed to find the font "{font_name}" on this system.',)
		raise
	try:
		font = _TTFont(font_path, fontNumber=0)
		cmap = font['cmap'].getBestCmap()
		glyph_set = font.getGlyphSet()
		units_per_em = font['head'].unitsPerEm
	except Exception as exception:
		exception.args = (f'Cannot properly handle the font "{font_name}".',)
	return {'cmap':cmap, 'glyph_set':glyph_set, 'units_per_em':units_per_em}
