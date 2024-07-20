"""
Defines the `TextBlock` and `InterestArea` objects for handling texts.
"""

import re as _re
from . import _bidi
from . import _font


class Box:
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

    def serialize(self) -> list:
        return [
            self._char,
            self._x_tl,
            self._y_tl,
            self._x_br,
            self._y_br,
            self._baseline,
            self._log_pos,
        ]


class InterestArea(Box):
    """
    Representation of an interest area – a portion of a `TextBlock` object
    that is of potential interest. It is not usually necessary to create
    `InterestArea` objects manually; they are created automatically when you
    extract areas of interest from a `TextBlock`.
    """

    def __init__(self, chars, location, padding, right_to_left, id=None):
        if isinstance(chars[0], Character):
            self._chars = chars
        else:
            self._chars = [Character(*char) for char in chars]
        self._location = location
        self._padding = padding
        self._right_to_left = right_to_left
        if id is None:
            self._id = "%i:%i:%i" % self._location
        else:
            self._id = str(id)
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
        return self._x_tl - self._padding[2]

    @property
    def y_tl(self) -> float:
        """Y-coordinate of the top-left corner of the bounding box"""
        return self._y_tl - self._padding[0]

    @property
    def x_br(self) -> float:
        """X-coordinate of the bottom-right corner of the bounding box"""
        return self._x_br + self._padding[3]

    @property
    def y_br(self) -> float:
        """Y-coordinate of the bottom-right corner of the bounding box"""
        return self._y_br + self._padding[1]

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
        """Bounding box padding on the top, bottom, left, and right edges"""
        return self._padding

    def set_padding(
        self,
        *,
        top: float = None,
        bottom: float = None,
        left: float = None,
        right: float = None,
    ):
        """
        Set the amount of bounding box padding on the top, bottom, left and/or
        right edges.
        """
        if top is not None:
            self._padding[0] = float(top)
        if bottom is not None:
            self._padding[1] = float(bottom)
        if left is not None:
            self._padding[2] = float(left)
        if right is not None:
            self._padding[3] = float(right)

    def adjust_padding(
        self,
        *,
        top: float = None,
        bottom: float = None,
        left: float = None,
        right: float = None,
    ):
        """
        Adjust the current amount of bounding box padding on the top, bottom,
        left, and/or right edges. Positive values increase the padding, and
        negative values decrease the padding.
        """
        if top is not None:
            self._padding[0] += float(top)
        if bottom is not None:
            self._padding[1] += float(bottom)
        if left is not None:
            self._padding[2] += float(left)
        if right is not None:
            self._padding[3] += float(right)

    def is_left_of(self, fixation) -> bool:
        """
        Returns True if the interest area is to the left of the fixation.
        """
        if self.x_br < fixation.x:
            return True
        return False

    def is_right_of(self, fixation) -> bool:
        """
        Returns True if the interest area is to the right of the fixation.
        """
        if self.x_tl > fixation.x:
            return True
        return False

    def is_before(self, fixation) -> bool:
        """
        Returns True if the interest area is before the fixation. An interest
        area comes before a fixation if it is to the left of that fixation (or
        to the right in the case of right-to-left text).
        """
        if self.right_to_left:
            return self.is_right_of(fixation)
        return self.is_left_of(fixation)

    def is_after(self, fixation) -> bool:
        """
        Returns True if the interest area is after the fixation. An interest
        area comes after a fixation if it is to the right of that fixation (or
        to the left in the case of right-to-left text).
        """
        if self.right_to_left:
            return self.is_left_of(fixation)
        return self.is_right_of(fixation)

    def serialize(self) -> dict:
        """
        Returns the `InterestArea`'s initialization arguments as a dictionary for
        serialization.
        """
        return {
            "chars": [char.serialize() for char in self._chars],
            "location": self.location,
            "padding": self.padding,
            "right_to_left": self.right_to_left,
            "id": self.id,
        }


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
    _IA_markup = _re.compile(r"(\[(.+?)\]\{(.+?)\})")

    @classmethod
    def defaults(
        cls,
        *,
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
        *,
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

        - `text` The line of text (string) or lines of text (list of strings).
        Optionally, these can be marked up with arbitrary interest areas; for
        example, `The quick brown fox jump[ed]{past-suffix} over the lazy
        dog`.

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
        the font size (single line spacing). If `autopad` is set to `True`
        (see below), the line height also effectively determines the height of
        the bounding boxes around interest areas.

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
        <img src='images/align_anchor.svg' width='100%' style='border: 0px; margin-top:10px;'>

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

        - `autopad` If `True` (the default), padding is automatically added to
        `InterestArea` bounding boxes to avoid horizontal gaps between words
        and vertical gaps between lines. Horizontal padding (half of the width
        of a space character) is added to the left and right edges, unless the
        character to the left or right of the interest area is alphabetical
        (e.g. if the interest area is word-internal). Vertical padding is
        added to the top and bottom edges, such that bounding box heights will
        be equal to the `line_height` (see above).
        <img src='images/autopad.svg' width='100%' style='border: 0px; margin-top:10px;'>
        """

        # TEXT
        if isinstance(text, str):
            self._text = [text.strip()]
        elif isinstance(text, list):
            self._text = [str(line).strip() for line in text]
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

        # LOAD FONT AND CALCULATE VARIOUS METRICS
        self._font = _font.Font(self._font_face, self._font_size)
        half_x_height = self._font.calculate_height("x") / 2
        half_font_size = self._font_size / 2
        if self._autopad:
            self._h_padding = self._font.calculate_width(" ") / 2
            self._v_padding = self._line_height / 2 - half_font_size

        # CALCULATE BASELINES AND MIDLINES
        self._baselines = [
            self._position[1] + i * self._line_height for i in range(self._n_rows)
        ]
        self._midlines = [baseline - half_x_height for baseline in self._baselines]

        # INITIALIZE CHARACTERS AND INTEREST AREAS
        self._chars, self._manual_IAs = [], {}
        for r, line in enumerate(self._text):
            baseline = self._baselines[r]

            # PARSE AND STRIP OUT INTEREST AREAS FROM THIS LINE
            for IA_markup, IA_text, IA_id in self._IA_markup.findall(line):
                if IA_id in self._manual_IAs:
                    raise ValueError(
                        f'The interest area ID "{IA_id}" has been used more than once.'
                    )
                s = line.find(IA_markup)
                e = s + len(IA_text)
                # record row/column position of the IA
                self._manual_IAs[IA_id] = (r, s, e)
                # replace the marked up IA with the unmarked up text
                line = line.replace(IA_markup, IA_text)

            # RESOLVE BIDIRECTIONAL TEXT AND REORDER THIS LINE IN DISPLAY FORM
            display_line = _bidi.display(line, self._right_to_left, return_log_pos=True)

            # CREATE THE SET OF CHARACTER OBJECTS FOR THIS LINE
            chars = []
            y_tl = self._midlines[r] - half_font_size
            y_br = self._midlines[r] + half_font_size
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

        # SET UP AND CACHE THE MARKED-UP INTEREST AREAS BASED ON THE INDICES
        # STORED EARLIER. This needs to be done in a second step because IAs
        # can't be created until character widths and positions are known.
        self._interest_areas = {}
        for IA_id, (r, s, e) in self._manual_IAs.items():
            self._create_interest_area(r, s, e, IA_id)

    def __repr__(self):
        if len(self._chars[0]) > 20:
            text = "".join(map(str, self._chars[0][:17])) + "..."
        else:
            text = "".join(map(str, self._chars[0]))
        text = _bidi.display(text, self.right_to_left)
        return f"TextBlock[{text}]"

    def __getitem__(self, rse):
        """
        Indexing a TextBlock object with a key of the form x:y:z returns an
        InterestArea representing characters y up to but not including z on
        line x. A key of this form may be passed in as a slice, tuple, or
        string. If a slice and s or e is elided, the start or end of the line
        is assumed. If a string is passed in that matches the ID of a
        previously created InterestArea, that InterestArea will be returned.

        0:5:10     Line 0, character 5 up to but not including character 10
        0:5:       Line 0, character 5 up to the end of the line
        0::10      Line 0, character 0 up to but not including character 10
        0::        All of line 0
        (0, 5, 10) Line 0, character 5 up to but not including character 10
        "0:5:10"   Line 0, character 5 up to but not including character 10
        "stem"     An InterestArea with the ID "stem"
        """
        if isinstance(rse, str):
            for _, interest_area in self._interest_areas.items():
                if interest_area.id == rse:
                    return interest_area
            rse = rse.split(":")
        elif isinstance(rse, slice):
            rse = rse.start, rse.stop, rse.step
        try:
            r, s, e = rse
            if s is None:
                s = 0
            if e is None:
                e = len(self._chars[r])
            r, s, e = int(r), int(s), int(e)
            assert (
                r >= 0
                and r < self.n_rows
                and s >= 0
                and s < e
                and e <= len(self._chars[r])
            )
        except:
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

    def interest_areas(self):
        """
        Iterate over each interest area that was manually marked up in the raw
        text. To mark up an interest area, use brackets to mark the area
        itself followed immediately by braces to provide an ID
        (e.g., `TextBlock("The quick [brown]{word_id} fox.")`).
        """
        for IA_id, rse in self._manual_IAs.items():
            yield self._interest_areas[rse]

    def lines(self):
        """
        Iterate over each line as an `InterestArea`.
        """
        for r, line in enumerate(self._chars):
            yield self[r, 0, len(line)]

    def words(
        self, pattern: str = None, *, line_n: int = None, alphabetical_only: bool = True
    ):
        """
        Iterate over each word as an `InterestArea`. Optionally, you can
        supply a regex pattern to pick out specific words. For example,
        `'(?i)the'` gives you case-insensitive occurrences of the word *the*
        or `'[a-z]+ing'` gives you lower-case words ending with *-ing*.
        `line_n` limits the iteration to a specific line number. If
        `alphabetical_only` is set to `True`, a word is defined as a string of
        consecutive alphabetical characters (as defined by the TextBlock's
        `alphabet` property); if `False`, a word is defined as a string of
        consecutive non-whitespace characters.
        """
        if pattern is not None:
            pattern = _re.compile(pattern)
        if alphabetical_only:
            word_pattern = self._alpha_plus
        else:
            word_pattern = _re.compile(r"[^\s]+")
        for r, line in enumerate(self._chars):
            if line_n is not None and r != line_n:
                continue
            line_str = "".join(map(str, line))
            for word in word_pattern.findall(line_str):
                s = line_str.find(word)
                e = s + len(word)
                line_str = line_str.replace(word, "#" * len(word), 1)
                if pattern and not pattern.fullmatch(word):
                    continue
                yield self[r, s, e]

    def characters(self, *, line_n: int = None, alphabetical_only: bool = True):
        """
        Iterate over each character as an `InterestArea`. `line_n` limits the
        iteration to a specific line number. If `alphabetical_only` is set to
        `True`, the iterator will only yield alphabetical characters (as
        defined by the TextBlock's `alphabet` property).
        """
        for r, line in enumerate(self._chars):
            if line_n is not None and r != line_n:
                continue
            for s, char in enumerate(line):
                if alphabetical_only and not self._alpha_solo.match(str(char)):
                    continue
                yield self[r, s, s + 1]

    def ngrams(
        self, ngram_width: int, *, line_n: int = None, alphabetical_only: bool = True
    ):
        """
        Iterate over each ngram, for given n, as an `InterestArea`. `line_n`
        limits the iteration to a specific line number. If `alphabetical_only`
        is set to `True`, an ngram is defined as a string of consecutive
        alphabetical characters (as defined by the TextBlock's `alphabet`
        property) of length `ngram_width`.
        """
        for r, line in enumerate(self._chars):
            if line_n is not None and r != line_n:
                continue
            for s in range(len(line) - (ngram_width - 1)):
                e = s + ngram_width
                if alphabetical_only and not self._alpha_plus.fullmatch(
                    "".join(map(str, line[s:e]))
                ):
                    continue
                yield self[r, s, e]

    ####################
    # DEPRECATED METHODS
    ####################

    def zones(self):  # pragma: no cover
        """
        **Deprecated in 0.4.1.** Use `TextBlock.interest_areas()` instead.
        """
        import warnings as _warnings

        _warnings.warn(
            "TextBlock.zones() is deprecated. Use TextBlock.interest_areas() instead",
            FutureWarning,
        )
        return self.interest_areas()

    def which_line(self, fixation) -> InterestArea:  # pragma: no cover
        """
        **Deprecated in 0.6.**
        """
        import warnings as _warnings

        _warnings.warn(
            "TextBlock.which_line() is deprecated and will be removed in the future.",
            FutureWarning,
        )
        for line in self.lines():
            if fixation in line:
                return line
        return None

    def which_word(
        self,
        fixation,
        pattern: str = None,
        *,
        line_n: int = None,
        alphabetical_only: bool = True,
    ) -> InterestArea:  # pragma: no cover
        """
        **Deprecated in 0.6.**
        """
        import warnings as _warnings

        _warnings.warn(
            "TextBlock.which_word() is deprecated and will be removed in the future.",
            FutureWarning,
        )
        for word in self.words(
            pattern, line_n=line_n, alphabetical_only=alphabetical_only
        ):
            if fixation in word:
                return word
        return None

    def which_character(
        self, fixation, *, line_n: int = None, alphabetical_only: bool = True
    ) -> InterestArea:  # pragma: no cover
        """
        **Deprecated in 0.6.**
        """
        import warnings as _warnings

        _warnings.warn(
            "TextBlock.which_character() is deprecated and will be removed in the future.",
            FutureWarning,
        )
        for character in self.characters(
            line_n=line_n, alphabetical_only=alphabetical_only
        ):
            if fixation in character:
                return character
        return None

    #################
    # PRIVATE METHODS
    #################

    def _create_interest_area(self, r, s, e, id):
        """
        Create a new interest area from the characters located at r:s:e (row,
        start, end), and cache the interest area for future use.
        """
        if self._autopad:
            padding = [self._v_padding, self._v_padding, 0, 0]
            if s == 0:
                padding[2] = self._h_padding  # Left edge, use half-space padding
            elif self._alpha_solo.match(str(self._chars[r][s - 1])):
                padding[2] = 0  # Alphabetical character to the left, no padding
            else:
                # Non-alphabetical character to the left, use half space or less
                padding[2] = min(
                    self._h_padding,
                    self._font.calculate_width(str(self._chars[r][s - 1])) / 2,
                )
            if e == len(self._chars[r]):
                padding[3] = self._h_padding  # Right edge, use half-space padding
            elif self._alpha_solo.match(str(self._chars[r][e])):
                padding[3] = 0  # Alphabetical character to the right, no padding
            else:
                # Non-alphabetical character to the right, use half space or less
                padding[3] = min(
                    self._h_padding,
                    self._font.calculate_width(str(self._chars[r][e])) / 2,
                )
            if self.right_to_left:
                padding[2], padding[3] = padding[3], padding[2]
        else:
            padding = [0, 0, 0, 0]
        self._interest_areas[(r, s, e)] = InterestArea(
            self._chars[r][s:e], (r, s, e), padding, self.right_to_left, id
        )
        return self._interest_areas[(r, s, e)]

    def serialize(self) -> dict:
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


def _fail(obj, expectation):
    raise TypeError(f"Expected {expectation}, got {obj.__class__.__name__}")


def _is_InterestArea(interest_area):
    if not isinstance(interest_area, InterestArea):
        _fail(interest_area, "InterestArea")


def _is_TextBlock(text_block):
    if not isinstance(text_block, TextBlock):
        _fail(text_block, "TextBlock")
