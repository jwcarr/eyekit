'''

Defines classes for dealing with texts, most notably the
`TextBlock` and `InterestArea` objects.

'''


import re as _re
import numpy as _np
from fontTools.ttLib import TTFont as _TTFont
from matplotlib import font_manager as _font_manager


_IA_REGEX = _re.compile(r'(\[(.+?)\]\{(.+?)\})')
_ALPHABET = 'A-Za-z'
_ALPHA = _re.compile(f'[{_ALPHABET}]')
_ALPHA_PLUS = _re.compile(f'[{_ALPHABET}]+')


def set_default_alphabet(alphabet):
	'''

	By default, Eyekit considers the alphabet to be the standard 26 Latin
	characters in upper and lower case. If you are working with another
	language it may be useful to change this default, so that all new
	`TextBlock` objects are automatically initialized with another
	alphabet. To do this, call `set_default_alphabet()` at the top of
	your script. For German, for example, you might do this:

	```
	eyekit.set_default_alphabet('A-Za-zßÄÖÜäöü')
	```

	'''
	global _ALPHABET, _ALPHA, _ALPHA_PLUS
	if not isinstance(alphabet, str):
		raise ValueError('Invalid alphabet. Should be a string of acceptable characters, e.g."A-Za-zßÄÖÜäöü".')
	_ALPHABET = alphabet
	_ALPHA = _re.compile(f'[{_ALPHABET}]')
	_ALPHA_PLUS = _re.compile(f'[{_ALPHABET}]+')


class Box(object):

	'''

	Representation of a bounding box, which provides an underlying
	framework for `Character`, `InterestArea`, and `TextBlock`.

	'''

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

	@property
	def x(self):
		'''*float* X-coordinate of the center of the bounding box'''
		return self.x_tl + self.width / 2
	
	@property
	def y(self):
		'''*float* Y-coordinate of the center of the bounding box'''
		return self.y_tl + self.height / 2

	@property
	def x_tl(self):
		'''*float* X-coordinate of the top-left corner of the bounding box'''
		return self._x_tl
	
	@property
	def y_tl(self):
		'''*float* Y-coordinate of the top-left corner of the bounding box'''
		return self._y_tl

	@property
	def x_br(self):
		'''*float* X-coordinate of the bottom-right corner of the bounding box'''
		return self._x_br
	
	@property
	def y_br(self):
		'''*float* Y-coordinate of the bottom-right corner of the bounding box'''
		return self._y_br

	@property
	def width(self):
		'''*float* Width of the bounding box'''
		return self.x_br - self.x_tl
	
	@property
	def height(self):
		'''*float* Height of the bounding box'''
		return self.y_br - self.y_tl

	@property
	def box(self):
		'''*tuple* The bounding box represented as x_tl, y_tl, width, and height'''
		return self.x_tl, self.y_tl, self.width, self.height

	@property
	def center(self):
		'''*tuple* XY-coordinates of the center of the bounding box'''
		return self.x, self.y


class Character(Box):

	'''

	Representation of a single character of text. A `Character` object is
	essentially a one-letter string that occupies a position in space and
	has a bounding box. It is not usually necessary to create `Character`
	objects manually; they are created automatically during the
	instantiation of a `TextBlock`.

	'''

	def __init__(self, char, x_tl, y_tl, x_br, y_br):
		if isinstance(char, str) and len(char) == 1:
			self._char = char
		else:
			raise ValueError('char must be one-letter string')
		self._x_tl, self._y_tl = float(x_tl), float(y_tl)
		self._x_br, self._y_br = float(x_br), float(y_br)

	def __repr__(self):
		return self._char

	def __str__(self):
		return self._char


class InterestArea(Box):

	'''

	Representation of an interest area – a portion of a `TextBlock` object that
	is of potenital interest. It is not usually necessary to create
	`InterestArea` objects manually; they are created automatically when
	you slice a `TextBlock` object or when you iterate over lines, words,
	characters, ngrams, or zones parsed from the raw text.

	'''

	def __init__(self, chars, label=None, padding=0):
		for char in chars:
			if not isinstance(char, Character):
				raise ValueError('chars must only contain Character objects')
		self._x_tl = chars[0].x_tl - padding
		self._y_tl = chars[0].y_tl
		self._x_br = chars[-1].x_br + padding
		self._y_br = chars[-1].y_br
		self._chars = chars
		self.label = label

	def __repr__(self):
		return 'InterestArea[%s]' % self.label

	def __str__(self):
		return self.text

	def __getitem__(self, key):
		self._chars[key]

	def __len__(self):
		return len(self._chars)

	def __iter__(self):
		for char in self._chars:
			yield char	

	@property
	def text(self):
		'''*str* String represention of the interest area; same as calling `str()`'''
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


class TextBlock(Box):

	'''

	Representation of a piece of text, which may be a word, sentence, or
	entire multiline passage.

	'''

	def __init__(self, text, position, font_name, font_size, line_spacing=1.0, alphabet=None):
		'''Initialized with:

		- ```text``` *str* (single line) | *list* of *str* (multiline) : The line or lines of text. Optionally, these can be marked up with arbitrary interest areas (or zones); for example, ```The quick brown fox jump[ed]{past-suffix} over the lazy dog```.
		- `position` *tuple*[*float*, *float*] : XY-coordinates of the top left corner of the `TextBlock`'s bounding box.
		- `font_name` *str* : Name of a font available on your system. Eyekit can access TrueType fonts that are discoverable by Matplotlib's FontManager.
		- `font_size` *float* : Font size in points.
		- `line_spacing` *float* : Amount of line spacing (1 for single line spacing, 2 for double line spacing, etc.)
		- `alphabet` *str* : A string of characters that are considered alphabetical. This is case sensitive, so you must supply upper- and lower-case variants. By default, the alphabet is set to `A-Za-z`, but for German, for example, you might use this: `A-Za-zßÄÖÜäöü`. If you are creating many `TextBlock` objects with the same alphabet, it may be preferable to use `set_default_alphabet()`.
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
		self._half_space_width = self._get_character_width(' ') / 2

		try:
			self._line_spacing = float(line_spacing)
		except:
			raise ValueError('line_spacing should be numeric')
		if self._line_spacing < 0.5:
			raise ValueError('line_spacing should be at least 0.5')
		self._line_height = self._font_size * self._line_spacing

		self.alphabet = alphabet

		self._characters, self._zones = self._initialize_text_block()

		self._x_br = max([line[-1].x_br for line in self._characters])
		self._y_br = self._y_tl + self.n_rows * self._line_height

	def __repr__(self):
		return 'TextBlock[%s...]' % ''.join(map(str, self._characters[0][:16]))

	def __str__(self):
		return ' '.join([''.join(map(str, line)) for line in self._characters])

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

	@property
	def alphabet(self):
		'''*str* Characters that are considered alphabetical'''
		return self._alphabet
	
	@alphabet.setter
	def alphabet(self, alphabet):
		if alphabet:
			self._alphabet = alphabet
			self._alpha = _re.compile(f'[{alphabet}]')
			self._alpha_plus = _re.compile(f'[{alphabet}]+')
		else:
			self._alphabet = _ALPHABET
			self._alpha = _ALPHA
			self._alpha_plus = _ALPHA_PLUS

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

	def zones(self):
		'''

		Iterate over each marked up zone as an `InterestArea`.
		
		'''
		for _, zone in self._zones.items():
			yield zone

	def which_zone(self, fixation):
		'''

		Return the marked-up zone that the fixation falls inside as an
		`InterestArea`.

		'''
		for zone in self.zones():
			if fixation in zone:
				return zone
		return None

	def get_zone(self, label):
		'''

		Retrieve a marked-up zone by its label.
		
		'''
		if label not in self._zones:
			raise KeyError('There is no zone with the label %s' % label)
		return self._zones[label]

	def lines(self):
		'''

		Iterate over each line as an `InterestArea`.

		'''
		for r, line in enumerate(self._characters):
			yield InterestArea(line, 'line_%i'%r)

	def which_line(self, fixation):
		'''

		Return the line that the fixation falls inside as an `InterestArea`.

		'''
		for line in self.lines():
			if fixation in line:
				return line
		return None

	def words(self, pattern=None, line_n=None, add_padding=True):
		'''

		Iterate over each word as an `InterestArea`. Optionally, you can
		supply a regex pattern to define what constitutes a word or to pick
		out specific words. For example, `r'\\b[Tt]he\\b'` gives you all
		occurances of the word *the* or `'[a-z]+ing'` gives you all words
		ending with *-ing*. `add_padding` adds half of the width of a space
		character to the left and right edges of the word's bounding box, so
		that fixations that fall on a space between two words will at least
		fall into one of the word's bounding boxes.

		'''
		if pattern is None:
			pattern = self._alpha_plus
		else:
			pattern = _re.compile(pattern)
		if add_padding:
			padding = self._half_space_width
		else:
			padding = 0
		word_i = 0
		for r, line in enumerate(self._characters):
			if line_n is not None and r != line_n:
				continue
			line_str = ''.join(map(str, line))
			for word in pattern.findall(line_str):
				c = line_str.find(word)
				line_str = line_str.replace(word, '#'*len(word), 1)
				yield InterestArea(self._characters[r][c:c+len(word)], 'word_%i'%word_i, padding=padding)
				word_i += 1

	def which_word(self, fixation, pattern=None, line_n=None, add_padding=True):
		'''

		Return the word that the fixation falls inside as an `InterestArea`.
		For the meaning of `pattern` and `add_padding` see
		`TextBlock.words()`.

		'''
		for word in self.words(pattern, line_n, add_padding):
			if fixation in word:
				return word
		return None

	def characters(self, line_n=None, alphabetical_only=True):
		'''

		Iterate over each character as an `InterestArea`.

		'''
		char_i = 0
		for r, line in enumerate(self._characters):
			if line_n is not None and r != line_n:
				continue
			for char in line:
				if alphabetical_only and not self._alpha.match(str(char)):
					continue
				yield InterestArea([char], 'character_%i'%char_i)
				char_i += 1

	def which_character(self, fixation, line_n=None, alphabetical_only=True):
		'''

		Return the character that the fixation falls inside as an
		`InterestArea`.

		'''
		for character in self.characters(line_n, alphabetical_only):
			if fixation in character:
				return character
		return None

	def ngrams(self, n, line_n=None, alphabetical_only=True, yield_rc=False):
		'''

		Iterate over each ngram, for given n, as an `InterestArea`.

		'''
		ngram_i = 0
		for r, line in enumerate(self._characters):
			if line_n is not None and r != line_n:
				continue
			for c in range(len(line)-(n-1)):
				if alphabetical_only and not self._alpha_plus.fullmatch(''.join(map(str, line[c:c+n]))):
					continue
				ngram = InterestArea(line[c:c+n], '%igram_%i'%(n, ngram_i))
				if yield_rc:
					yield ngram, (r, c)
				else:
					yield ngram
				ngram_i += 1

	# No which_ngram() method because, by definition, a fixation is
	# inside multiple ngrams.

	def _serialize(self):
		'''
		
		Returns the `TextBlock`'s ininialization arguments as a dictionary
		for serialization.
		
		'''
		return {'position': (self.x_tl, self.y_tl), 'font_name': self.font_name, 'font_size': self.font_size, 'line_spacing': self.line_spacing, 'alphabet': self.alphabet, 'text': self._text}

	#################
	# PRIVATE METHODS
	#################

	def _initialize_text_block(self):
		'''

		Parses out any marked up interest areas from the text and converts
		and stores every character as a Character object with the
		appropriate character width.

		'''
		characters = []
		zones = {}
		y_tl = self.y_tl
		for r, line in enumerate(self._text):
			for IA_markup, IA_text, IA_label in _IA_REGEX.findall(line):
				if IA_label in zones:
					raise ValueError('The zone label %s has been used more than once.' % IA_label)
				c = line.find(IA_markup)
				zones[IA_label] = (r, c, len(IA_text))
				line = line.replace(IA_markup, IA_text)
			characters_line = []
			x_tl = self.x_tl
			for c, char in enumerate(line):
				character_width = self._get_character_width(char)
				character = Character(char, x_tl, y_tl, x_tl+character_width, y_tl+self.line_height)
				characters_line.append(character)
				x_tl += character_width
			characters.append(characters_line)
			y_tl += self.line_height
		for IA_label, (r, c, length) in zones.items():
			zones[IA_label] = InterestArea(characters[r][c:c+length], IA_label)
		return characters, zones

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
	try:
		font_path = _font_manager.findfont(_font_manager.FontProperties([font_name]), fallback_to_default=False)
	except Exception as exception:
		exception.args = (f'Failed to find the font "{font_name}" on this system. Not found by Matplotlib\'s FontManager.' ,)
		raise
	try:
		font = _TTFont(font_path, fontNumber=0)
		cmap = font['cmap'].getBestCmap()
		glyph_set = font.getGlyphSet()
		units_per_em = font['head'].unitsPerEm
	except Exception as exception:
		exception.args = (f'Cannot properly handle the font "{font_name}".',)
	return {'cmap':cmap, 'glyph_set':glyph_set, 'units_per_em':units_per_em}
