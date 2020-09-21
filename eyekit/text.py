'''

Defines classes for dealing with texts, most notably the
`TextBlock` and `InterestArea` objects.

'''


import re as _re
import numpy as _np
from PIL import ImageFont as _ImageFont


ALPHABETS = {
	'Dutch': 'A-Za-z',
	'English': 'A-Za-z',
	'French': 'A-ZÇÉÀÈÙÂÊÎÔÛËÏÜŸŒa-zçéàèùâêîôûëïüÿœ',
	'German': 'A-ZÄÖÜa-zäöüß',
	'Greek': 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫΪ́Ϋ́αβγδεζηθικλμνξοπρσςτυφχψωάέήίόύώϊϋΐΰ',
	'Italian': 'A-ZÀÉÈÍÌÓÒÚÙa-zàéèíìóòúù',
	'Polish': 'A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż',
	'Portuguese': 'A-ZÁÂÃÀÇÉÊÍÓÔÕÚa-záâãàçéêíóôõú',
	'Russian': 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя',
	'Spanish': 'A-ZÑÁÉÍÓÚÜa-zñáéíóúü'
}
_ZONE_REGEX = _re.compile(r'(\[(.+?)\]\{(.+?)\})')
_ALPHABET = 'A-Za-z'
_ALPHA = _re.compile(f'[{_ALPHABET}]')
_ALPHA_PLUS = _re.compile(f'[{_ALPHABET}]+')


def set_default_alphabet(alphabet):
	'''

	By default, Eyekit considers the alphabet to be the standard 26 Latin
	characters in upper and lower case. If you are working with another language
	it may be useful to change this default, so that all new `TextBlock` objects
	are automatically initialized with a particular alphabet. To do this, call
	`set_default_alphabet()` at the top of your script. For German, for example,
	you might do this:

	```
	eyekit.set_default_alphabet('A-Za-zßÄÖÜäöü')
	```

	Eyekit also provides built-in alphabets for several European languages, so
	it's also possible to do this:

	```
	eyekit.set_default_alphabet(eyekit.ALPHABETS['Polish'])
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

	def __init__(self, char, x_tl, y_tl, x_br, y_br, baseline):
		if isinstance(char, str) and len(char) == 1:
			self._char = char
		else:
			raise ValueError('char must be one-letter string')
		self._x_tl, self._y_tl = float(x_tl), float(y_tl)
		self._x_br, self._y_br = float(x_br), float(y_br)
		self._baseline = float(baseline)

	def __repr__(self):
		return self._char

	@property
	def baseline(self):
		'''*float* The y position of the character baseline'''
		return self._baseline


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

	def __getitem__(self, key):
		return self._chars[key]

	def __len__(self):
		return len(self._chars)

	def __iter__(self):
		for char in self._chars:
			yield char	

	@property
	def baseline(self):
		'''*float* The y position of the text baseline'''
		return self._chars[0].baseline

	@property
	def text(self):
		'''*str* String represention of the interest area'''
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

	def __init__(self, text, position, font_name, font_size, line_height=None, adjust_bbox=None, alphabet=None):
		'''Initialized with:

		- ```text``` *str* (single line) | *list* of *str* (multiline) : The line or lines of text. Optionally, these can be marked up with arbitrary interest areas (or zones); for example, ```The quick brown fox jump[ed]{past-suffix} over the lazy dog```.
		- `position` *tuple*[*float*, *float*] : XY-coordinates of the top left corner of the `TextBlock`'s bounding box.
		- `font_name` *str* : Name of a font available on your system. Eyekit can access TrueType fonts that are discoverable by Pillow.
		- `font_size` *float* : Font size in points (at 72dpi). To convert a font size from some other dpi, use `eyekit.tools.font_size_at_72dpi()`.
		- `line_height` *float* : Height of a line of text in points. Generally speaking, for single line spacing, the line height is equal to the font size, for double line spacing, the light height is equal to 2 × the font size, etc. By default, the line height is assumed to be the same as the font size (single line spacing). This parameter also effectively determines the height of the bounding boxes around interest areas.
		- `adjust_bbox` *float* : Pixel adjustment to the y-position of bounding boxes relative to the font baseline. Some fonts, such as Courier and Helvetica have quite high baselines making the bounding boxes a little low relative to the text. This parameter can be used to adjust this.
		- `alphabet` *str* : A string of characters that are considered alphabetical. This is case sensitive, so you must supply upper- and lower-case variants. By default, the alphabet is set to `A-Za-z`, but for German, for example, you might use this: `A-Za-zßÄÖÜäöü`. Eyekit also provides built-in alphabets for several European languages, for example, `eyekit.ALPHABETS['French']`. If you are creating many `TextBlock` objects with the same alphabet, it may be preferable to use `set_default_alphabet()`.
		'''

		# TEXT
		if isinstance(text, str):
			self._text = [text]
		elif isinstance(text, list):
			self._text = [str(line) for line in text]
		else:
			raise ValueError('text should be a string or a list of strings')

		# POSITION
		try:
			self._x_tl = float(position[0])
			self._y_tl = float(position[1])
		except:
			raise ValueError('position should be tuple representing the XY coordinates of the top left corner of the TextBlock')

		# FONT NAME AND SIZE
		self._font_name = str(font_name)
		self._font_size = float(font_size)

		# LINE HEIGHT
		if line_height is None:
			self._line_height = self._font_size
		else:
			self._line_height = float(line_height)

		# BOUNDING BOX ADJUSTMENT
		if adjust_bbox is None:
			self._adjust_bbox = 0
		else:
			self._adjust_bbox = float(adjust_bbox)

		# ALPHABET
		self.alphabet = alphabet

		# LOAD FONT
		try:
			self._font = _ImageFont.truetype(self._font_name, int(self._font_size * 64)).font # font_size must be int, so we'll work with a much larger font size and scale the widths back down later for greater precision
		except:
			raise ValueError(f'Unable to load font "{self._font_name}" in size {self._font_size}.')
		self._first_baseline = self._y_tl + (self._font.ascent - self._font.descent) / 64
		self._half_space_width = self._font.getsize(' ')[0][0] / 128

		# INITIALIZE CHARACTERS AND ZONES
		self._characters, self._zones = self._initialize_text_block()

		# SET BOTTOM-RIGHT CORNER OF BOUNDING BOX
		self._x_br = max([line[-1].x_br for line in self._characters])
		self._y_br = self._y_tl + self.n_rows * self._line_height

	def __repr__(self):
		return 'TextBlock[%s...]' % ''.join(map(str, self._characters[0][:16]))

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
	def text(self):
		'''*str* String represention of the text`'''
		return ' '.join([''.join(map(str, line)) for line in self._characters])

	@property
	def font_name(self):
		'''*str* Name of the font'''
		return self._font_name

	@property
	def font_size(self):
		'''*float* Font size in points'''
		return self._font_size

	@property
	def line_height(self):
		'''*float* Line height in points'''
		return self._line_height

	@property
	def adjust_bbox(self):
		'''*float* Line height in points'''
		return self._adjust_bbox

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
		fall into one of the two words' bounding boxes.

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

	#################
	# PRIVATE METHODS
	#################

	def _serialize(self):
		'''
		
		Returns the `TextBlock`'s ininialization arguments as a dictionary
		for serialization.
		
		'''
		return {'position': (self.x_tl, self.y_tl), 'font_name': self.font_name, 'font_size': self.font_size, 'line_height': self.line_height, 'adjust_bbox':self.adjust_bbox, 'alphabet': self.alphabet, 'text': self._text}

	def _initialize_text_block(self):
		'''

		Parses out any marked up interest areas from the text and converts
		and stores every character as a Character object with the
		appropriate character width.

		'''
		characters = []
		zones = {}
		y_tl = self.y_tl - (self._line_height - self._font_size) / 2 + self._adjust_bbox # y_tl of character bounding boxes on first lines
		baseline = self._first_baseline
		for r, line in enumerate(self._text):
			# Parse and strip out interest area zones from this line
			for zone_markup, zone_text, zone_label in _ZONE_REGEX.findall(line):
				if zone_label in zones:
					raise ValueError('The zone label %s has been used more than once.' % zone_label)
				c = line.find(zone_markup)
				zones[zone_label] = (r, c, len(zone_text)) # record row index, column index, and length of zone
				line = line.replace(zone_markup, zone_text) # replace the marked up zone with the unmarked up text
			# Create the set of Character objects for this line
			characters_line = []
			x_tl = self.x_tl # x_tl of first character bounding box on this line
			y_br = y_tl + self._line_height # y_br of all character bounding boes on this line
			line_width = self._font.getsize(line)[0][0] # anticipate the length of the line
			words = line.split(' ')
			word_widths = [(word + ' ', self._font.getsize(word + ' ')[0][0]) for word in words[:-1]]
			word_widths.append((words[-1], self._font.getsize(words[-1])[0][0])) # calculate word widths - all words include a trailing space except the last word in the line
			line_scaling_factor = line_width / sum([width for _, width in word_widths]) # calculate scaling factor needed to scale down the word widths so that their sum width matches the anticipated line width
			for word, word_width in word_widths:
				word_width *= line_scaling_factor # scale down the word width
				char_widths = [self._font.getsize(char)[0][0] for char in word]
				word_scaling_factor = word_width / sum(char_widths) # calculate a scaling factor for scaling down character widths so that their sum width matches the target word length
				for char, char_width in zip(word, char_widths):
					char_width *= word_scaling_factor
					char_width /= 64
					characters_line.append(Character(char, x_tl, y_tl, x_tl+char_width, y_br, baseline))
					x_tl += char_width
			characters.append(characters_line)
			y_tl += self._line_height
			baseline += self._line_height
		# Set up and store the zoned interest areas based on the indices stored earlier.
		for zone_label, (r, c, length) in zones.items(): # Needs to be done in two steps because IAs can't be created until character positions are known
			zones[zone_label] = InterestArea(characters[r][c:c+length], zone_label)
		return characters, zones
