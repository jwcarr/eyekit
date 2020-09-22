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

	def __init__(self, chars, id, padding=0):
		for char in chars:
			if not isinstance(char, Character):
				raise ValueError('chars must only contain Character objects')
		self._x_tl = chars[0].x_tl - padding
		self._y_tl = chars[0].y_tl
		self._x_br = chars[-1].x_br + padding
		self._y_br = chars[-1].y_br
		self._chars = chars
		self._id = str(id)

	def __repr__(self):
		return f'InterestArea[{self.id}, {self.text}]'

	def __getitem__(self, key):
		return self._chars[key]

	def __len__(self):
		return len(self._chars)

	def __iter__(self):
		for char in self._chars:
			yield char	

	@property
	def id(self):
		'''*str* Interest area ID. By default, these ID's have the form 1:5:10, which represents the line number and column indices of the `InterestArea` in its parent `TextBlock`. However, IDs can also be changed to any arbitrary string.'''
		return self._id

	@id.setter
	def id(self, id):
		self._id = str(id)

	@property
	def baseline(self):
		'''*float* The y position of the text baseline'''
		return self._chars[0].baseline

	@property
	def text(self):
		'''*str* String represention of the interest area'''
		return ''.join(map(str, self._chars))


class TextBlock(Box):

	'''

	Representation of a piece of text, which may be a word, sentence, or
	entire multiline passage.

	'''

	_default_position = (0, 0)
	_default_font_name = 'Courier New'
	_default_font_size = 20.0
	_default_line_height = None
	_default_adjust_bbox = 0.0
	_default_alphabet = 'A-Za-z'

	@classmethod
	def defaults(cls, position=None, font_name=None, font_size=None, line_height=None, adjust_bbox=None, alphabet=None):
		'''

		Set default `TextBlock` parameters. If you plan to create several
		`TextBlock`s with the same parameters, it may be useful to set the default
		parameters at the top of your script:

		```
		import eyekit
		eyekit.TextBlock.defaults(font_name='Helvetica')
		txt = eyekit.TextBlock('The quick brown fox')
		print(txt.font_name) # 'Helvetica'
		```
		
		'''
		if position is not None:
			cls._default_position = (float(position[0]), float(position[1]))
		if font_name is not None:
			cls._default_font_name = str(font_name)
		if font_size is not None:
			cls._default_font_size = float(font_size)
		if line_height is not None:
			cls._default_line_height = float(line_height)
		if adjust_bbox is not None:
			cls._default_adjust_bbox = float(adjust_bbox)
		if alphabet is not None:
			cls._default_alphabet = str(alphabet)

	def __init__(self, text, position=None, font_name=None, font_size=None, line_height=None, adjust_bbox=None, alphabet=None):
		'''Initialized with:

		- ```text``` *str* (single line) | *list* of *str* (multiline) : The line or lines of text. Optionally, these can be marked up with arbitrary interest areas (zones); for example, ```The quick brown fox jump[ed]{past-suffix} over the lazy dog```.
		- `position` *tuple*[*float*, *float*] : XY-coordinates of the top left corner of the `TextBlock`'s bounding box.
		- `font_name` *str* : Name of a font available on your system. Eyekit can access TrueType fonts that are discoverable by Pillow.
		- `font_size` *float* : Font size in points (at 72dpi). To convert a font size from some other dpi, use `eyekit.tools.font_size_at_72dpi()`.
		- `line_height` *float* : Height of a line of text in points. Generally speaking, for single line spacing, the line height is equal to the font size, for double line spacing, the light height is equal to 2 × the font size, etc. By default, the line height is assumed to be the same as the font size (single line spacing). This parameter also effectively determines the height of the bounding boxes around interest areas.
		- `adjust_bbox` *float* : Pixel adjustment to the y-position of bounding boxes relative to the font baseline. Some fonts, such as Courier and Helvetica have quite high baselines making the bounding boxes a little low relative to the text. This parameter can be used to adjust this.
		- `alphabet` *str* : A string of characters that are considered alphabetical, which determines what is considered a word. This is case sensitive, so you must supply upper- and lower-case variants. By default, the alphabet is set to the standard 26 Latin characters in upper- and lower-case, `A-Za-z`, but for German, for example, you might use `A-Za-zßÄÖÜäöü`. Eyekit also provides built-in alphabets for several European languages, for example, `eyekit.ALPHABETS['French']`.
		'''

		# TEXT
		if isinstance(text, str):
			self._text = [text]
		elif isinstance(text, list):
			self._text = [str(line) for line in text]
		else:
			raise ValueError('text should be a string or a list of strings')

		# POSITION
		if position is None:
			self._x_tl = self._default_position[0]
			self._y_tl = self._default_position[1]
		else:
			self._x_tl = float(position[0])
			self._y_tl = float(position[1])

		# FONT NAME
		if font_name is None:
			self._font_name = self._default_font_name
		else:
			self._font_name = str(font_name)

		# FONT SIZE
		if font_size is None:
			self._font_size = self._default_font_size
		else:
			self._font_size = float(font_size)

		# LINE HEIGHT
		if line_height is None:
			if self._default_line_height is None:
				self._line_height = self._font_size
			else:
				self._line_height = self._default_line_height
		else:
			self._line_height = float(line_height)

		# BOUNDING BOX ADJUSTMENT
		if adjust_bbox is None:
			self._adjust_bbox = self._default_adjust_bbox
		else:
			self._adjust_bbox = float(adjust_bbox)

		# ALPHABET
		if alphabet is None:
			self._alphabet = self._default_alphabet
		else:
			self._alphabet = str(alphabet)
		self._alpha = _re.compile(f'[{self._alphabet}]')
		self._alpha_plus = _re.compile(f'[{self._alphabet}]+')

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

	def __getitem__(self, id):
		'''
		Subsetting a TextBlock object with a key of the form x:y:z returns
		characters y to z on row x as an InterestArea.
		'''
		if isinstance(id, str):
			if id in self._zones:
				return self._zones[id]
			rse = id.split(':')
			try:
				r, s, e = int(rse[0]), int(rse[1]), int(rse[2])
			except:
				raise KeyError('Invalid InterestArea ID')
		elif isinstance(id, slice):
			r, s, e = id.start, id.stop, id.step
		return InterestArea(self._characters[r][s:e], f'{r}:{s}:{e}')

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
	def position(self):
		'''*tuple* Position of the `TextBlock`'''
		return self._x_tl, self._y_tl

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
		'''*float* Pixel adjustment to the y-position of bounding boxes relative to the font baseline'''
		return self._adjust_bbox

	@property
	def alphabet(self):
		'''*str* Characters that are considered alphabetical'''
		return self._alphabet

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

	def lines(self):
		'''

		Iterate over each line as an `InterestArea`.

		'''
		for r, line in enumerate(self._characters):
			yield InterestArea(line, f'{r}:{0}:{len(line)}')

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
				s = line_str.find(word)
				e = s + len(word)
				line_str = line_str.replace(word, '#'*len(word), 1)
				yield InterestArea(self._characters[r][s:e], f'{r}:{s}:{e}', padding=padding)
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
			for s, char in enumerate(line):
				if alphabetical_only and not self._alpha.match(str(char)):
					continue
				yield InterestArea([char], f'{r}:{s}:{s+1}')
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

	def ngrams(self, n, line_n=None, alphabetical_only=True):
		'''

		Iterate over each ngram, for given n, as an `InterestArea`.

		'''
		ngram_i = 0
		for r, line in enumerate(self._characters):
			if line_n is not None and r != line_n:
				continue
			for s in range(len(line)-(n-1)):
				e = s + n
				if alphabetical_only and not self._alpha_plus.fullmatch(''.join(map(str, line[s:e]))):
					continue
				ngram = InterestArea(line[s:e], f'{r}:{s}:{e}')
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
			for zone_markup, zone_text, zone_id in _ZONE_REGEX.findall(line):
				if zone_id in zones:
					raise ValueError('The zone ID "%s" has been used more than once.' % zone_id)
				c = line.find(zone_markup)
				zones[zone_id] = (r, c, len(zone_text)) # record row index, column index, and length of zone
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
		for zone_id, (r, c, length) in zones.items(): # Needs to be done in two steps because IAs can't be created until character positions are known
			zones[zone_id] = InterestArea(characters[r][c:c+length], zone_id)
		return characters, zones
