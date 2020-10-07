'''

Defines the `TextBlock` and `InterestArea` objects for handling texts.

'''


import re as _re
import cairocffi as _cairo
from . import _alpha, _font


class Box(object):

	'''

	Representation of a bounding box, which provides an underlying framework for
	`Character`, `InterestArea`, and `TextBlock`.

	'''

	def __contains__(self, fixation):
		if (self.x_tl <= fixation.x <= self.x_br) and (self.y_tl <= fixation.y <= self.y_br):
			return True
		return False

	@property
	def x(self) -> float:
		'''X-coordinate of the center of the bounding box'''
		return self.x_tl + self.width / 2
	
	@property
	def y(self) -> float:
		'''Y-coordinate of the center of the bounding box'''
		return self.y_tl + self.height / 2

	@property
	def x_tl(self) -> float:
		'''X-coordinate of the top-left corner of the bounding box'''
		return self._x_tl
	
	@property
	def y_tl(self) -> float:
		'''Y-coordinate of the top-left corner of the bounding box'''
		return self._y_tl

	@property
	def x_br(self) -> float:
		'''X-coordinate of the bottom-right corner of the bounding box'''
		return self._x_br
	
	@property
	def y_br(self) -> float:
		'''Y-coordinate of the bottom-right corner of the bounding box'''
		return self._y_br

	@property
	def width(self) -> float:
		'''Width of the bounding box'''
		return self.x_br - self.x_tl
	
	@property
	def height(self) -> float:
		'''Height of the bounding box'''
		return self.y_br - self.y_tl

	@property
	def box(self) -> tuple:
		'''The bounding box represented as x_tl, y_tl, width, and height'''
		return self.x_tl, self.y_tl, self.width, self.height

	@property
	def center(self) -> tuple:
		'''XY-coordinates of the center of the bounding box'''
		return self.x, self.y


class Character(Box):

	'''

	Representation of a single character of text. A `Character` object is
	essentially a one-letter string that occupies a position in space and has a
	bounding box. It is not usually necessary to create `Character` objects
	manually; they are created automatically during the instantiation of a
	`TextBlock`.

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
	def baseline(self) -> float:
		'''The y position of the character baseline'''
		return self._baseline


class InterestArea(Box):

	'''

	Representation of an interest area – a portion of a `TextBlock` object that
	is of potential interest. It is not usually necessary to create
	`InterestArea` objects manually; they are created automatically when you
	slice a `TextBlock` object or when you iterate over lines, words, characters,
	ngrams, or zones parsed from the raw text.

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
	def id(self) -> str:
		'''Interest area ID. By default, these ID's have the form 1:5:10, which represents the line number and column indices of the `InterestArea` in its parent `TextBlock`. However, IDs can also be changed to any arbitrary string.'''
		return self._id

	@id.setter
	def id(self, id):
		self._id = str(id)

	@property
	def baseline(self) -> float:
		'''The y position of the text baseline'''
		return self._chars[0].baseline

	@property
	def text(self) -> str:
		'''String representation of the interest area'''
		return ''.join(map(str, self._chars))


class TextBlock(Box):

	'''

	Representation of a piece of text, which may be a word, sentence, or entire
	multiline passage.

	'''

	_default_position = (0, 0)
	_default_font_face = 'Courier New'
	_default_font_size = 20.0
	_default_line_height = None
	_default_alphabet = None
	
	_alpha_solo = _re.compile(f'[{_alpha.characters}]')
	_alpha_plus = _re.compile(f'[{_alpha.characters}]+')
	_zone_markup = _re.compile(r'(\[(.+?)\]\{(.+?)\})')

	@classmethod
	def defaults(cls, position: tuple=None, font_face: str=None, font_size: float=None, line_height: float=None, alphabet: str=None):
		'''

		Set default `TextBlock` parameters. If you plan to create several
		`TextBlock`s with the same parameters, it may be useful to set the default
		parameters at the top of your script or at the start of your session:

		```python
		import eyekit
		eyekit.TextBlock.defaults(font_face='Helvetica')
		txt = eyekit.TextBlock('The quick brown fox')
		print(txt.font_face) # 'Helvetica'
		```
		
		'''
		if position is not None:
			cls._default_position = (float(position[0]), float(position[1]))
		if font_face is not None:
			cls._default_font_face = str(font_face)
		if font_size is not None:
			cls._default_font_size = float(font_size)
		if line_height is not None:
			cls._default_line_height = float(line_height)
		if alphabet is not None:
			cls._default_alphabet = str(alphabet)
			cls._alpha_solo = _re.compile(f'[{cls._default_alphabet}]')
			cls._alpha_plus = _re.compile(f'[{cls._default_alphabet}]+')

	def __init__(self, text: list, position: tuple=None, font_face: str=None, font_size: float=None, line_height: float=None, alphabet: str=None):
		'''Initialized with:

		- ```text``` The line of text (string) or lines of text (list of strings). Optionally, these can be marked up with arbitrary interest areas (zones); for example, ```The quick brown fox jump[ed]{past-suffix} over the lazy dog```.
		- `position` XY-coordinates of the left edge of the first baseline of the block of text.
		- `font_face` Name of a font available on your system. The keywords `italic` and/or `bold` can also be included to select the desired style, e.g., `Minion Pro bold italic`.
		- `font_size` Font size in points (at 72dpi). To convert a font size from some other dpi, use `eyekit.tools.font_size_at_72dpi()`.
		- `line_height` Height of a line of text in points. Generally speaking, for single line spacing, the line height is equal to the font size, for double line spacing, the line height is equal to 2 × the font size, etc. By default, the line height is assumed to be the same as the font size (single line spacing). This parameter also effectively determines the height of the bounding boxes around interest areas.
		- `alphabet` A string of characters that are to be considered alphabetical, which determines, for example, what is considered a word. By default, Eyekit considers the standard Latin, Greek, and Cyrillic alphabets to be alphabetical, plus the special and accented characters from most European languages. However, if you need support for some other alphabet, or if you want to modify Eyekit's default behavior, you can set an alternative alphabet here. This parameter is case sensitive, so you must supply upper- and lower-case variants. For example, if you wanted to treat apostrophes and hyphens as alphabetical, you might use `alphabet="A-Za-z'-"`. This would allow, for example, "Where's the orang-utan?" to be treated as three words rather than five.
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
			self._first_baseline = self._default_position[1]
		else:
			self._x_tl = float(position[0])
			self._first_baseline = float(position[1])

		# FONT FACE
		if font_face is None:
			self._font_face = self._default_font_face
		else:
			self._font_face = str(font_face)

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

		# ALPHABET
		if alphabet is None:
			if self._default_alphabet is None:
				self._alphabet = None
			else:
				self._alphabet = self._default_alphabet
		else:
			self._alphabet = str(alphabet)
			self._alpha_solo = _re.compile(f'[{self._alphabet}]')
			self._alpha_plus = _re.compile(f'[{self._alphabet}]+')

		# LOAD FONT
		self._font = _font.Font(self._font_face, self._font_size)
		self._x_height = self._font.calculate_height('x')
		self._half_space_width = self._font.calculate_width(' ') / 2

		# INITIALIZE CHARACTERS AND ZONES
		self._characters, self._zones = self._initialize_text_block()

		# SET REMAINING TEXTBLOCK COORDINATES
		self._x_br = max([line[-1].x_br for line in self._characters])
		self._y_tl = self._characters[0][0].y_tl
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
	def text(self) -> str:
		'''String representation of the text'''
		return ' '.join([''.join(map(str, line)) for line in self._characters])

	@property
	def position(self) -> tuple:
		'''Position of the `TextBlock`'''
		return self._x_tl, self._first_baseline

	@property
	def font_face(self) -> str:
		'''Name of the font'''
		return self._font_face

	@property
	def font_size(self) -> float:
		'''Font size in points'''
		return self._font_size

	@property
	def line_height(self) -> float:
		'''Line height in points'''
		return self._line_height

	@property
	def alphabet(self) -> str:
		'''Characters that are considered alphabetical'''
		return self._alphabet

	@property
	def n_rows(self) -> int:
		'''Number of rows in the text (i.e. the number of lines)'''
		return len(self._characters)
	
	@property
	def n_cols(self) -> int:
		'''Number of columns in the text (i.e. the number of characters in the widest line)'''
		return max([len(row) for row in self._characters])

	@property
	def line_positions(self) -> list:
		'''Y-coordinates of the center of each line of text'''
		return [line[0].y for line in self._characters]

	@property
	def word_centers(self) -> list:
		'''XY-coordinates of the center of each word'''
		return [word.center for word in self.words()]

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

		Iterate over each word as an `InterestArea`. Optionally, you can supply a
		regex pattern to define what constitutes a word or to pick out specific
		words. For example, `r'\\b[Tt]he\\b'` gives you all occurrences of the word
		*the* or `'[a-z]+ing'` gives you all words ending with *-ing*. `add_padding`
		adds half of the width of a space character to the left and right edges of
		the word's bounding box, so that fixations that fall on a space between two
		words will at least fall into one of the two words' bounding boxes.

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

		Return the word that the fixation falls inside as an `InterestArea`. For the
		meaning of `pattern` and `add_padding` see `TextBlock.words()`.

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
				if alphabetical_only and not self._alpha_solo.match(str(char)):
					continue
				yield InterestArea([char], f'{r}:{s}:{s+1}')
				char_i += 1

	def which_character(self, fixation, line_n=None, alphabetical_only=True):
		'''

		Return the character that the fixation falls inside as an `InterestArea`.

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

	# No which_ngram() method because, by definition, a fixation is inside
	# multiple ngrams.

	#################
	# PRIVATE METHODS
	#################

	def _serialize(self):
		'''
		
		Returns the `TextBlock`'s initialization arguments as a dictionary for
		serialization.
		
		'''
		data = {
			'position': self.position,
			'font_face': self.font_face,
			'font_size': self.font_size,
			'line_height': self.line_height
		}
		if self.alphabet is not None:
			data['alphabet'] = self.alphabet
		data['text'] = self._text
		return data

	def _initialize_text_block(self):
		'''

		Parses out any marked up interest areas from the text and converts and
		stores every character as a Character object with the appropriate character
		width.

		'''
		characters = []
		zones = {}
		baseline = self._first_baseline
		midline = baseline - self._x_height / 2 # midline is half an x-height higher than the baseline
		y_tl = midline - self._line_height / 2 # top of bounding box is half a line height above the midline
		for r, line in enumerate(self._text):
			# Parse and strip out interest area zones from this line
			for zone_markup, zone_text, zone_id in self._zone_markup.findall(line):
				if zone_id in zones:
					raise ValueError('The zone ID "%s" has been used more than once.' % zone_id)
				c = line.find(zone_markup)
				zones[zone_id] = (r, c, len(zone_text)) # record row index, column index, and length of zone
				line = line.replace(zone_markup, zone_text) # replace the marked up zone with the unmarked up text
			# Create the set of Character objects for this line
			characters_line = []
			x_tl = self.x_tl # x_tl of first character bounding box on this line
			y_br = y_tl + self._line_height # y_br of all character bounding boxes on this line
			for char in line:
				char_width = self._font.calculate_width(char)
				x_br = x_tl + char_width
				characters_line.append(Character(char, x_tl, y_tl, x_br, y_br, baseline))
				x_tl = x_br
			characters.append(characters_line)
			y_tl += self._line_height
			baseline += self._line_height
		# Set up and store the zoned interest areas based on the indices stored earlier.
		for zone_id, (r, c, length) in zones.items(): # Needs to be done in two steps because IAs can't be created until character positions are known
			zones[zone_id] = InterestArea(characters[r][c:c+length], zone_id)
		return characters, zones
