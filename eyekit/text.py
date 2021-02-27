"""

Defines the `TextBlock` and `InterestArea` objects for handling texts.

"""


import re as _re
import cairocffi as _cairo
from . import _bidi


class _Font(object):

    """

    Wrapper around Cairo's font selection mechanism.

    """

    regex_italic = _re.compile(" italic", _re.IGNORECASE)
    regex_bold = _re.compile(" bold", _re.IGNORECASE)

    def __init__(self, face, size):
        if self.regex_italic.search(face):
            self.slant = "italic"
            slant = _cairo.FONT_SLANT_ITALIC
            face = self.regex_italic.sub("", face)
        else:
            self.slant = "normal"
            slant = _cairo.FONT_SLANT_NORMAL
        if self.regex_bold.search(face):
            self.weight = "bold"
            weight = _cairo.FONT_WEIGHT_BOLD
            face = self.regex_bold.sub("", face)
        else:
            self.weight = "normal"
            weight = _cairo.FONT_WEIGHT_NORMAL
        self.family = face.strip()
        self.size = float(size)
        self.toy_font_face = _cairo.ToyFontFace(self.family, slant, weight)
        self.scaled_font = _cairo.ScaledFont(
            self.toy_font_face, _cairo.Matrix(xx=self.size, yy=self.size)
        )

    def calculate_width(self, text):
        return self.scaled_font.text_extents(text)[4]

    def calculate_height(self, text):
        return self.scaled_font.text_extents(text)[3]


class Box(object):

    """

    Representation of a bounding box, which provides an underlying framework
    for `Character`, `InterestArea`, and `TextBlock`.

    """

    def __contains__(self, fixation):
        if (self.x_tl <= fixation.x <= self.x_br) and (
            self.y_tl <= fixation.y <= self.y_br
        ):
            return True
        return False

    @property
    def x(self) -> float:
        """X-coordinate of the center of the bounding box"""
        return self.x_tl + self.width / 2

    @property
    def y(self) -> float:
        """Y-coordinate of the center of the bounding box"""
        return self.y_tl + self.height / 2

    @property
    def x_tl(self) -> float:
        """X-coordinate of the top-left corner of the bounding box"""
        return self._x_tl

    @property
    def y_tl(self) -> float:
        """Y-coordinate of the top-left corner of the bounding box"""
        return self._y_tl

    @property
    def x_br(self) -> float:
        """X-coordinate of the bottom-right corner of the bounding box"""
        return self._x_br

    @property
    def y_br(self) -> float:
        """Y-coordinate of the bottom-right corner of the bounding box"""
        return self._y_br

    @property
    def width(self) -> float:
        """Width of the bounding box"""
        return self.x_br - self.x_tl

    @property
    def height(self) -> float:
        """Height of the bounding box"""
        return self.y_br - self.y_tl

    @property
    def box(self) -> tuple:
        """The bounding box represented as x_tl, y_tl, width, and height"""
        return self.x_tl, self.y_tl, self.width, self.height

    @property
    def center(self) -> tuple:
        """XY-coordinates of the center of the bounding box"""
        return self.x, self.y


class Character(Box):

    """

    Representation of a single character of text. A `Character` object is
    essentially a one-letter string that occupies a position in space and has
    a bounding box. It is not usually necessary to create `Character` objects
    manually; they are created automatically during the instantiation of a
    `TextBlock`.

    """

    def __init__(self, char, x_tl, y_tl, x_br, y_br, baseline, log_pos):
        if isinstance(char, str) and len(char) == 1:
            self._char = char
        else:
            raise ValueError("char must be one-letter string")
        self._x_tl, self._y_tl = float(x_tl), float(y_tl)
        self._x_br, self._y_br = float(x_br), float(y_br)
        self._baseline = float(baseline)
        self._log_pos = log_pos

    def __repr__(self):
        return self._char

    @property
    def baseline(self) -> float:
        """The y position of the character baseline"""
        return self._baseline

    @property
    def midline(self) -> float:
        """The y position of the character midline"""
        return self.y


class InterestArea(Box):

    """

    Representation of an interest area – a portion of a `TextBlock` object
    that is of potential interest. It is not usually necessary to create
    `InterestArea` objects manually; they are created automatically when you
    slice a `TextBlock` object or when you iterate over lines, words,
    characters, ngrams, or zones parsed from the raw text.

    """

    def __init__(
        self, chars, location, id=None, right_to_left=False, left_pad=0, right_pad=0
    ):
        for char in chars:
            if not isinstance(char, Character):
                raise ValueError("chars must only contain Character objects")
        self._chars = chars
        self._location = location
        if id is None:
            self._id = "%i:%i:%i" % self._location
        else:
            self._id = str(id)
        self._right_to_left = bool(right_to_left)
        self._left_pad = left_pad
        self._right_pad = right_pad
        self._x_tl = min([char.x_tl for char in self._chars])
        self._y_tl = self._chars[0].y_tl
        self._x_br = max([char.x_br for char in self._chars])
        self._y_br = self._chars[0].y_br

    def __repr__(self):
        if len(self) > 20:
            text = "".join(map(str, self._chars[:17])) + "..."
        else:
            text = "".join(map(str, self._chars))
        text = _bidi.display(text, self.right_to_left)
        return f"InterestArea[{self.id}, {text}]"

    def __getitem__(self, key):
        return self._chars[key]

    def __len__(self):
        return len(self._chars)

    def __iter__(self):
        for char in self._chars:
            yield char

    @property
    def x_tl(self) -> float:
        """X-coordinate of the top-left corner of the bounding box"""
        return self._x_tl - self._left_pad

    @property
    def x_br(self) -> float:
        """X-coordinate of the bottom-right corner of the bounding box"""
        return self._x_br + self._right_pad

    @property
    def location(self) -> tuple:
        """Location of the interest area in its parent TextBlock (row, start, end)"""
        return self._location

    @property
    def id(self) -> str:
        """

        Interest area ID. By default, these ID's have the form 1:5:10, which
        represents the line number and column indices of the `InterestArea` in
        its parent `TextBlock`. However, IDs can also be changed to any
        arbitrary string.

        """
        return self._id

    @id.setter
    def id(self, id):
        self._id = str(id)

    @property
    def right_to_left(self) -> bool:
        """`True` if interest area represents right-to-left text"""
        return self._right_to_left

    @property
    def text(self) -> str:
        """String representation of the interest area"""
        return "".join(map(str, self._chars))

    @property
    def display_text(self) -> str:
        """Same as `text` except right-to-left text is output in display form"""
        return _bidi.display(self.text, self.right_to_left)

    @property
    def baseline(self) -> float:
        """The y position of the text baseline"""
        return self._chars[0].baseline

    @property
    def midline(self) -> float:
        """The y position of the text midline"""
        return self._chars[0].midline

    @property
    def onset(self) -> float:
        """

        The x position of the onset of the interest area. The onset is the
        left edge of the interest area text without any bounding box padding
        (or the right edge in the case of right-to-left text).

        """
        if self._right_to_left:
            return self._x_br
        return self._x_tl

    @property
    def padding(self) -> tuple:
        """Bounding box padding on the left and right edge"""
        return self._left_pad, self._right_pad

    def set_padding(self, left=None, right=None):
        """

        Set the amount of bounding box padding on the left and/or right edge.

        """
        if left is not None:
            self._left_pad = float(left)
        if right is not None:
            self._right_pad = float(right)

    def adjust_padding(self, left=None, right=None):
        """

        Adjust the current amount of bounding box padding on the left and/or
        right edge. Positive values increase the padding, and negative values
        decrease the padding.

        """
        if left is not None:
            self._left_pad += float(left)
        if right is not None:
            self._right_pad += float(right)


class TextBlock(Box):

    """

    Representation of a piece of text, which may be a word, sentence, or
    entire multiline passage.

    """

    _default_position = (100, 100)
    _default_font_face = "Courier New"
    _default_font_size = 20.0
    _default_line_height = None
    _default_align = None
    _default_anchor = None
    _default_right_to_left = False
    _default_alphabet = None
    _default_autopad = True

    _alpha_solo = _re.compile(r"\w")
    _alpha_plus = _re.compile(r"\w+")
    _zone_markup = _re.compile(r"(\[(.+?)\]\{(.+?)\})")

    @classmethod
    def defaults(
        cls,
        position: tuple = None,
        font_face: str = None,
        font_size: float = None,
        line_height: float = None,
        align: str = None,
        anchor: str = None,
        right_to_left: bool = None,
        alphabet: str = None,
        autopad: bool = None,
    ):
        """

        Set default `TextBlock` parameters. If you plan to create several
        `TextBlock`s with the same parameters, it may be useful to set the
        default parameters at the top of your script or at the start of your
        session:

        ```python
        import eyekit
        eyekit.TextBlock.defaults(font_face='Helvetica')
        txt = eyekit.TextBlock('The quick brown fox')
        print(txt.font_face) # 'Helvetica'
        ```

        """
        if position is not None:
            cls._default_position = (float(position[0]), float(position[1]))
        if font_face is not None:
            cls._default_font_face = str(font_face)
        if font_size is not None:
            cls._default_font_size = float(font_size)
        if line_height is not None:
            cls._default_line_height = float(line_height)
        if align is not None:
            if align not in ["left", "center", "right"]:
                raise ValueError('align should be "left", "center", or "right".')
            cls._default_align = align
        if anchor is not None:
            if anchor not in ["left", "center", "right"]:
                raise ValueError('anchor should be "left", "center", or "right".')
            cls._default_anchor = anchor
        if right_to_left is not None:
            if not isinstance(right_to_left, bool):
                raise ValueError("right_to_left should be boolean.")
            cls._default_right_to_left = right_to_left
        if alphabet is not None:
            cls._default_alphabet = str(alphabet)
            cls._alpha_solo = _re.compile(f"[{cls._default_alphabet}]")
            cls._alpha_plus = _re.compile(f"[{cls._default_alphabet}]+")
        if autopad is not None:
            if not isinstance(autopad, bool):
                raise ValueError("autopad should be boolean.")
            cls._default_autopad = autopad

    def __init__(
        self,
        text: list,
        position: tuple = None,
        font_face: str = None,
        font_size: float = None,
        line_height: float = None,
        align: str = None,
        anchor: str = None,
        right_to_left: bool = None,
        alphabet: str = None,
        autopad: bool = None,
    ):
        """
        Initialized with:

        - ```text``` The line of text (string) or lines of text (list of
        strings). Optionally, these can be marked up with arbitrary interest
        areas (zones); for example, ```The quick brown fox
        jump[ed]{past-suffix} over the lazy dog```.

        - `position` XY-coordinates describing the position of the TextBlock
        on the screen. The x-coordinate should be either the left edge, right
        edge, or center point of the TextBlock, depending on how the `anchor`
        argument has been set (see below). The y-coordinate should always
        correspond to the baseline of the first (or only) line of text.

        - `font_face` Name of a font available on your system. The keywords
        `italic` and/or `bold` can also be included to select the desired
        style, e.g., `Minion Pro bold italic`.

        - `font_size` Font size in pixels. At 72dpi, this is equivalent to the
        font size in points. To convert a font size from some other dpi, use
        `eyekit.tools.font_size_at_72dpi()`.

        - `line_height` Distance between lines of text in pixels. In general,
        for single line spacing, the line height is equal to the font size;
        for double line spacing, the line height is equal to 2 × the font
        size, etc. By default, the line height is assumed to be the same as
        the font size (single line spacing). This parameter also effectively
        determines the height of the bounding boxes around interest areas.

        - `align` Alignment of the text within the TextBlock. Must be set to
        `left`, `center`, or `right`, and defaults to `left` (unless
        `right_to_left` is set to `True`, in which case `align` defaults to
        `right`).

        - `anchor` Anchor point of the TextBlock. This determines the
        interpretation of the `position` argument (see above). Must be set to
        `left`, `center`, or `right`, and defaults to the same as the `align`
        argument. For example, if `position` was set to the center of the
        screen, the `align` and `anchor` arguments would have the following
        effects:
        <img src='images/align_anchor.pdf' width='100%' style='border: 0px; margin-top:10px;'>

        - `right_to_left` Set to `True` if the text is in a right-to-left script
        (Arabic, Hebrew, Urdu, etc.). If you are working with the Arabic
        script, you should reshape the text prior to passing it into Eyekit
        by using, for example, the Arabic-reshaper package.

        - `alphabet` A string of characters that are to be considered
        alphabetical, which determines what counts as a word. By default, this
        includes any character defined as a letter or number in unicode, plus
        the underscore character. However, if you need to modify Eyekit's
        default behavior, you can set a specific alphabet here. For example,
        if you wanted to treat apostrophes and hyphens as alphabetical, you
        might use `alphabet="A-Za-z'-"`. This would allow a sentence like
        "Where's the orang-utan?" to be treated as three words rather than
        five.

        - `autopad` If `True` (the default), a small amount of padding (half of
        the width of a space character) is added to each side of an interest
        area. Fixations that are very close to, but technically outside of, an
        interest area will therefore still be considered to be inside that
        interest area. If the character to the left or right of the interest
        area is alphabetical (i.e. if the interest area is word-internal),
        padding will not be added on that side.
        <img src='images/autopad.pdf' width='100%' style='border: 0px; margin-top:10px;'>

        """

        # TEXT
        if isinstance(text, str):
            self._text = [text]
        elif isinstance(text, list):
            self._text = [str(line) for line in text]
        else:
            raise ValueError("text should be a string or a list of strings")
        self._n_rows = len(self._text)

        # POSITION
        if position is None:
            self._position = self._default_position
        else:
            self._position = tuple(position)

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

        # RIGHT-TO-LEFT
        if right_to_left is None:
            self._right_to_left = self._default_right_to_left
        elif isinstance(right_to_left, bool):
            self._right_to_left = right_to_left
        else:
            raise ValueError("right_to_left should be boolean.")

        # ALIGN
        if align is None:
            if self._default_align is None:
                self._align = "right" if self._right_to_left else "left"
            else:
                self._align = self._default_align
        elif align in ["left", "center", "right"]:
            self._align = align
        else:
            raise ValueError('align should be "left", "center", or "right".')

        # ANCHOR
        if anchor is None:
            if self._default_anchor is None:
                self._anchor = self._align
            else:
                self._anchor = self._default_anchor
        elif anchor in ["left", "center", "right"]:
            self._anchor = anchor
        else:
            raise ValueError('anchor should be "left", "center", or "right".')

        # ALPHABET
        if alphabet is None:
            if self._default_alphabet is None:
                self._alphabet = None
            else:
                self._alphabet = self._default_alphabet
        else:
            self._alphabet = str(alphabet)
            self._alpha_solo = _re.compile(f"[{self._alphabet}]")
            self._alpha_plus = _re.compile(f"[{self._alphabet}]+")

        # AUTOPAD
        if autopad is None:
            self._autopad = self._default_autopad
        elif isinstance(autopad, bool):
            self._autopad = autopad
        else:
            raise ValueError("autopad should be boolean.")

        # LOAD FONT
        self._font = _Font(self._font_face, self._font_size)
        self._half_space_width = self._font.calculate_width(" ") / 2
        half_x_height = self._font.calculate_height("x") / 2
        half_line_height = self._line_height / 2

        # CALCULATE BASELINES AND MIDLINES
        self._baselines = [
            self._position[1] + i * self._line_height for i in range(self._n_rows)
        ]
        self._midlines = [baseline - half_x_height for baseline in self._baselines]

        # INITIALIZE CHARACTERS AND ZONES
        self._chars, self._zones = [], {}
        for r, line in enumerate(self._text):
            baseline = self._baselines[r]

            # PARSE AND STRIP OUT INTEREST AREA ZONES FROM THIS LINE
            for zone_markup, zone_text, zone_id in self._zone_markup.findall(line):
                if zone_id in self._zones:
                    raise ValueError(
                        f'The zone ID "{zone_id}" has been used more than once.'
                    )
                s = line.find(zone_markup)
                e = s + len(zone_text)
                # record row/column position of the zone
                self._zones[zone_id] = (r, s, e)
                # replace the marked up zone with the unmarked up text
                line = line.replace(zone_markup, zone_text)

            # RESOLVE BIDIRECTIONAL TEXT AND REORDER THIS LINE IN DISPLAY FORM
            display_line = _bidi.display(line, self._right_to_left, return_log_pos=True)

            # CREATE THE SET OF CHARACTER OBJECTS FOR THIS LINE
            chars = []
            y_tl = self._midlines[r] - half_line_height
            y_br = self._midlines[r] + half_line_height
            x_tl = self._position[0]  # first x_tl is left edge of text block
            for char, log_pos in display_line:
                x_br = x_tl + self._font.calculate_width(char)
                chars.append(Character(char, x_tl, y_tl, x_br, y_br, baseline, log_pos))
                x_tl = x_br  # next x_tl is x_br
            self._chars.append(chars)  # initially the characters are in display order

        # SET TEXTBLOCK COORDINATES
        self._x_tl = self._position[0]
        self._x_br = max([line[-1].x_br for line in self._chars])
        self._y_tl = self._chars[0][0].y_tl
        self._y_br = self._chars[-1][0].y_br

        # RECALCULATE X COORDINATES ACCORDING TO ALIGN AND ANCHOR. This needs
        # to be done in a second step because aligned positions cannot be
        # calculated until the maximum line width is known.
        block_width = self._x_br - self._x_tl
        if self._anchor == "left":
            block_shift = 0
        elif self._anchor == "center":
            block_shift = -block_width / 2
        elif self._anchor == "right":
            block_shift = -block_width
        self._x_tl += block_shift
        self._x_br += block_shift
        for line in self._chars:
            line_width = line[-1]._x_br - line[0]._x_tl
            if self._align == "left":
                line_shift = 0
            elif self._align == "center":
                line_shift = (block_width - line_width) / 2
            elif self._align == "right":
                line_shift = block_width - line_width
            if block_shift or line_shift:
                total_shift = block_shift + line_shift
                for char in line:
                    char._x_tl += total_shift
                    char._x_br += total_shift
            line.sort(key=lambda char: char._log_pos)  # reorder characters logically

        # SET UP AND CACHE THE ZONED INTEREST AREAS BASED ON THE INDICES
        # STORED EARLIER. This needs to be done in a second step because IAs
        # can't be created until character widths and positions are known.
        self._interest_areas = {}
        for zone_id, (r, s, e) in self._zones.items():
            self._create_interest_area(r, s, e, zone_id)

    def __repr__(self):
        if len(self._chars[0]) > 20:
            text = "".join(map(str, self._chars[0][:17])) + "..."
        else:
            text = "".join(map(str, self._chars[0]))
        text = _bidi.display(text, self.right_to_left)
        return f"TextBlock[{text}]"

    def __getitem__(self, key):
        """

        Subsetting a TextBlock object with a key of the form x:y:z returns
        characters y to z on row x as an InterestArea.

        """
        if isinstance(key, slice):
            rse = key.start, key.stop, key.step
        elif isinstance(key, tuple):
            rse = key
        elif isinstance(key, str):
            for _, interest_area in self._interest_areas.items():
                if interest_area.id == key:
                    return interest_area
            rse = key.split(":")
        else:
            raise KeyError("Invalid InterestArea key")
        try:
            r, s, e = int(rse[0]), int(rse[1]), int(rse[2])
        except:
            raise KeyError("Invalid InterestArea key")
        if r < 0 or r >= self.n_rows or s < 0 or s >= e or e > len(self._chars[r]):
            raise KeyError("Invalid InterestArea key")
        if (r, s, e) in self._interest_areas:
            return self._interest_areas[(r, s, e)]
        return self._create_interest_area(r, s, e, None)

    def __len__(self):
        return sum([len(line) for line in self._chars])

    def __iter__(self):
        """

        Iterating over a TextBlock object yields each character in the text.

        """
        for line in self._chars:
            for char in line:
                yield char

    @property
    def text(self) -> list:
        """Original input text"""
        return self._text

    @property
    def position(self) -> tuple:
        """Position of the `TextBlock`"""
        return self._position

    @property
    def font_face(self) -> str:
        """Name of the font"""
        return self._font_face

    @property
    def font_size(self) -> float:
        """Font size in points"""
        return self._font_size

    @property
    def line_height(self) -> float:
        """Line height in points"""
        return self._line_height

    @property
    def align(self) -> str:
        """Alignment of the text (either `left`, `center`, or `right`)"""
        return self._align

    @property
    def anchor(self) -> str:
        """Anchor point of the text (either `left`, `center`, or `right`)"""
        return self._anchor

    @property
    def right_to_left(self) -> bool:
        """Right-to-left text"""
        return self._right_to_left

    @property
    def alphabet(self) -> str:
        """Characters that are considered alphabetical"""
        return self._alphabet

    @property
    def autopad(self) -> bool:
        """Whether or not automatic padding is switched on"""
        return self._autopad

    @property
    def n_rows(self) -> int:
        """Number of rows in the text (i.e. the number of lines)"""
        return self._n_rows

    @property
    def n_cols(self) -> int:
        """Number of columns in the text (i.e. the number of characters in the widest line)"""
        return max([len(row) for row in self._chars])

    @property
    def n_lines(self) -> int:
        """Number of lines in the text (i.e. alias of `n_rows`)"""
        return self._n_rows

    @property
    def baselines(self) -> list:
        """Y-coordinate of the baseline of each line of text"""
        return self._baselines

    @property
    def midlines(self) -> list:
        """Y-coordinate of the midline of each line of text"""
        return self._midlines

    ################
    # PUBLIC METHODS
    ################

    def zones(self):
        """

        Iterate over each marked up zone as an `InterestArea`.

        """
        for zone_id, rse in self._zones.items():
            yield self._interest_areas[rse]

    def which_zone(self, fixation):
        """

        Return the marked-up zone that the fixation falls inside as an
        `InterestArea`.

        """
        for zone in self.zones():
            if fixation in zone:
                return zone
        return None

    def lines(self):
        """

        Iterate over each line as an `InterestArea`.

        """
        for r, line in enumerate(self._chars):
            yield self[r, 0, len(line)]

    def which_line(self, fixation):
        """

        Return the line that the fixation falls inside as an `InterestArea`.

        """
        for line in self.lines():
            if fixation in line:
                return line
        return None

    def words(self, pattern=None, line_n=None):
        """

        Iterate over each word as an `InterestArea`. Optionally, you can
        supply a regex pattern to pick out specific words. For example,
        `'(?i)the'` gives you case-insensitive occurrences of the word *the*
        or `'[a-z]+ing'` gives you lower-case words ending with *-ing*.

        """
        if pattern is not None:
            pattern = _re.compile(pattern)
        for r, line in enumerate(self._chars):
            if line_n is not None and r != line_n:
                continue
            line_str = "".join(map(str, line))
            for word in self._alpha_plus.findall(line_str):
                s = line_str.find(word)
                e = s + len(word)
                line_str = line_str.replace(word, "#" * len(word), 1)
                if pattern and not pattern.fullmatch(word):
                    continue
                yield self[r:s:e]

    def which_word(self, fixation, pattern=None, line_n=None):
        """

        Return the word that the fixation falls inside as an `InterestArea`.
        For the meaning of `pattern` see `TextBlock.words()`.

        """
        for word in self.words(pattern, line_n):
            if fixation in word:
                return word
        return None

    def characters(self, line_n=None, alphabetical_only=True):
        """

        Iterate over each character as an `InterestArea`.

        """
        for r, line in enumerate(self._chars):
            if line_n is not None and r != line_n:
                continue
            for s, char in enumerate(line):
                if alphabetical_only and not self._alpha_solo.match(str(char)):
                    continue
                yield self[r, s, s + 1]

    def which_character(self, fixation, line_n=None, alphabetical_only=True):
        """

        Return the character that the fixation falls inside as an
        `InterestArea`.

        """
        for character in self.characters(line_n, alphabetical_only):
            if fixation in character:
                return character
        return None

    def ngrams(self, n, line_n=None, alphabetical_only=True):
        """

        Iterate over each ngram, for given n, as an `InterestArea`.

        """
        for r, line in enumerate(self._chars):
            if line_n is not None and r != line_n:
                continue
            for s in range(len(line) - (n - 1)):
                e = s + n
                if alphabetical_only and not self._alpha_plus.fullmatch(
                    "".join(map(str, line[s:e]))
                ):
                    continue
                yield self[r, s, e]

    # No which_ngram() method because, by definition, a fixation is inside
    # multiple ngrams.

    def word_centers(self):
        """

        Return the XY-coordinates of the center of each word.

        """
        return [word.center for word in self.words()]

    #################
    # PRIVATE METHODS
    #################

    def _create_interest_area(self, r, s, e, id):
        """

        Create a new interest area from the characters located at r:s:e (row,
        start, end), and cache the interest area for future use.

        """
        left_pad, right_pad = 0, 0
        if self._autopad:
            if s == 0:  # Left edge, add half-space padding
                left_pad = self._half_space_width
            elif not self._alpha_solo.match(str(self._chars[r][s - 1])):
                # Non-alphabetical character to the left, add half space or less
                left_pad = min(
                    self._half_space_width,
                    self._font.calculate_width(str(self._chars[r][s - 1])) / 2,
                )
            if e == len(self._chars[r]):  # Right edge, add half-space padding
                right_pad = self._half_space_width
            elif not self._alpha_solo.match(str(self._chars[r][e])):
                # Non-alphabetical character to the right, add half space or less
                right_pad = min(
                    self._half_space_width,
                    self._font.calculate_width(str(self._chars[r][e])) / 2,
                )
            if self.right_to_left:
                left_pad, right_pad = right_pad, left_pad
        self._interest_areas[(r, s, e)] = InterestArea(
            self._chars[r][s:e], (r, s, e), id, self.right_to_left, left_pad, right_pad
        )
        return self._interest_areas[(r, s, e)]

    def _serialize(self):
        """

        Returns the `TextBlock`'s initialization arguments as a dictionary for
        serialization.

        """
        return {
            "text": self.text,
            "position": self.position,
            "font_face": self.font_face,
            "font_size": self.font_size,
            "line_height": self.line_height,
            "align": self.align,
            "anchor": self.anchor,
            "right_to_left": self.right_to_left,
            "alphabet": self.alphabet,
            "autopad": self.autopad,
        }
