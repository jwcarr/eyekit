"""
Defines the `Fixation` and `FixationSequence` objects, which are used to
represent fixation data.
"""


import warnings as _warnings
from .text import _is_TextBlock
from . import _snap


class Fixation:

    """
    Representation of a single fixation event. It is not usually necessary to
    create `Fixation` objects manually; they are created automatically during
    the instantiation of a `FixationSequence`.
    """

    def __init__(
        self,
        index: int,
        x: int,
        y: int,
        start: int,
        end: int,
        pupil_size: int = None,
        *,
        discarded: bool = False,
        tags: list = None,
    ):
        if end <= start:
            raise ValueError(
                f"A fixation cannot have an end time ({end}) that is earlier its start time ({start})."
            )
        self._index = int(index)
        self._x = int(x)
        self._y = int(y)
        self._start = int(start)
        self._end = int(end)

        if pupil_size is True or pupil_size == "discarded":
            # For backwards compatibility with < 0.4, when discarded could be
            # passed in as the sixth positional argument - eventually this
            # will be removed and pupil_size may also become keyword-only
            _warnings.warn(
                "In the future, discarded will be a keyword-only argument.",
                FutureWarning,
            )
            pupil_size = None
            discarded = True

        self.pupil_size = pupil_size
        self.discarded = discarded
        self.tags = tags

    def __repr__(self):
        return f"Fixation[{self.x},{self.y}]"

    @property
    def index(self) -> int:
        """Index of the fixation in its parent `FixationSequence`"""
        return self._index

    @property
    def x(self) -> int:
        """X-coordinate of the fixation."""
        return self._x

    @x.setter
    def x(self, x):
        self._x = int(x)

    @property
    def y(self) -> int:
        """Y-coordinate of the fixation."""
        return self._y

    @y.setter
    def y(self, y):
        self._y = int(y)

    @property
    def xy(self) -> tuple:
        """XY-coordinates of the fixation."""
        return self._x, self._y

    @property
    def start(self) -> int:
        """Start time of the fixation in milliseconds."""
        return self._start

    @start.setter
    def start(self, start):
        if start >= self._end:
            raise ValueError(f"The start time cannot be after the end time ({end}).")
        self._start = int(start)

    @property
    def end(self) -> int:
        """End time of the fixation in milliseconds."""
        return self._end

    @end.setter
    def end(self, end):
        if end <= self._start:
            raise ValueError(f"The end time cannot be before the start time ({start}).")
        self._end = int(end)

    @property
    def duration(self) -> int:
        """Duration of the fixation in milliseconds."""
        return self._end - self._start

    @property
    def pupil_size(self) -> int:
        """Size of the pupil. `None` if no pupil size is recorded."""
        return self._pupil_size

    @pupil_size.setter
    def pupil_size(self, pupil_size):
        if pupil_size is None:
            self._pupil_size = None
        else:
            self._pupil_size = int(pupil_size)

    @property
    def discarded(self) -> bool:
        """`True` if the fixation has been discarded, `False` otherwise."""
        return self._discarded

    @discarded.setter
    def discarded(self, discarded):
        self._discarded = bool(discarded)

    @property
    def tags(self) -> list:
        """Size of the pupil. `None` if no pupil size is recorded."""
        return self._tags

    @tags.setter
    def tags(self, tags):
        if tags is None:
            self._tags = []
        else:
            self._tags = [str(tag) for tag in tags]

    def discard(self):
        """
        Mark this fixation as discarded. To completely remove the fixation,
        you should also call `FixationSequence.purge()`.
        """
        self._discarded = True

    def add_tag(self, tag):
        """
        Tag this fixation with some arbitrary tag.
        """
        self._tags.append(str(tag))

    def has_tag(self, tag):
        """
        Returns `True` if the fixation has a given tag.
        """
        return tag in self._tags

    def shift_time(self, amount):
        """
        Shift this fixation forwards (+) or backwards (-) in time by some
        amount (in milliseconds).
        """
        self._start += int(amount)
        self._end += int(amount)

    def serialize(self):
        """
        Returns representation of the fixation as a tuple for serialization.
        """
        fixation = {
            "x": self._x,
            "y": self._y,
            "start": self._start,
            "end": self._end,
        }
        if self._pupil_size is not None:
            fixation["pupil_size"] = self._pupil_size
        if self._discarded:
            fixation["discarded"] = True
        if self._tags:
            fixation["tags"] = self._tags
        return fixation


class FixationSequence:

    """
    Representation of a sequence of consecutive fixations, typically from a
    single trial.
    """

    def __init__(self, sequence: list):
        """
        Initialized with:

        - `sequence` List of tuples of ints, or something similar, that conforms
        to the following structure: `[(106, 540, 100, 200), (190, 536, 200,
        300), ..., (763, 529, 1000, 1100)]`, where each tuple contains the
        X-coordinate, Y-coordinate, start time, and end time of a fixation.
        Alternatively, `sequence` may be a list of dicts, where each dict is
        something like `{'x': 106, 'y': 540, 'start': 100, 'end': 200}`.
        """
        self._sequence = []
        for index, fixation in enumerate(sequence):
            if not isinstance(fixation, Fixation):
                if isinstance(fixation, dict):
                    fixation = Fixation(index, **fixation)
                else:
                    try:
                        fixation = Fixation(index, *fixation)
                    except:
                        raise ValueError(f"Cannot interpret as fixation: {fixation}")
                if self._sequence and fixation.start < self._sequence[-1].end:
                    raise ValueError(
                        f"A fixation that starts at t={fixation.start} occurs after a fixation that ends at t={self._sequence[-1].end}."
                    )
            self._sequence.append(fixation)

    def __repr__(self):
        if len(self) > 2:
            return f"FixationSequence[{self._sequence[0]}, ..., {self._sequence[-1]}]"
        if len(self) == 2:
            return f"FixationSequence[{self._sequence[0]}, {self._sequence[1]}]"
        if len(self) == 1:
            return f"FixationSequence[{self._sequence[0]}]"
        return "FixationSequence[]"

    def __len__(self):
        return len(self._sequence)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self._sequence[index]
        if isinstance(index, slice):
            return FixationSequence(self._sequence[index])
        raise TypeError(
            f"FixationSequence indices must be integers or slices, not {index.__class__.__name__}"
        )

    def __iter__(self):
        for fixation in self._sequence:
            yield fixation

    def __add__(self, other):
        if not isinstance(other, FixationSequence):
            raise TypeError("Can only concatenate with another FixationSequence")
        return FixationSequence(self.serialize() + other.serialize())

    @property
    def start(self) -> int:
        """
        Start time of the fixation sequence (in milliseconds).
        """
        if len(self) == 0:
            return 0
        return self._sequence[0].start

    @property
    def end(self) -> int:
        """
        End time of the fixation sequence (in milliseconds).
        """
        if len(self) == 0:
            return 0
        return self._sequence[-1].end

    @property
    def duration(self) -> int:
        """
        Duration of the fixation sequence, incuding any gaps between fixations
        (in milliseconds).
        """
        if len(self) == 0:
            return 0
        return self.end - self.start

    def copy(self, include_discards=True):
        """
        Returns a copy of the fixation sequence.
        """
        if include_discards:
            return FixationSequence(
                [fixation.serialize() for fixation in self.iter_with_discards()]
            )
        return FixationSequence(
            [fixation.serialize() for fixation in self.iter_without_discards()]
        )

    def purge(self):
        """
        Permanently removes all discarded fixations from the sequence, and
        reindexes the fixations.
        """
        sequence = []
        for index, fixation in enumerate(self.iter_without_discards()):
            fixation._index = index
            sequence.append(fixation)
        self._sequence = sequence

    def iter_with_discards(self):
        """
        Iterates over the fixation sequence including any discarded fixations.
        This is also the default behavior when iterating over a
        `FixationSequence` directly.
        """
        for fixation in self._sequence:
            yield fixation

    def iter_without_discards(self):
        """
        Iterates over the fixation sequence without any discarded fixations.
        """
        for fixation in self._sequence:
            if not fixation.discarded:
                yield fixation

    def iter_pairs(self, include_discards=True):
        """
        Iterate over fixations in consecutive pairs. This is useful if you
        want to compare consecutive fixations in some way. For example, if you
        wanted to detect when a fixation leaves an interest area, you might do
        something like this:

        ```
        for curr_fxn, next_fxn in seq.iter_pairs():
            if curr_fxn in interest_area and next_fxn not in interest_area:
                print('A fixation has left the interest area')
        ```
        """
        if len(self) < 2:
            return
        if include_discards:
            for i, j in zip(range(len(self) - 1), range(1, len(self))):
                yield self._sequence[i], self._sequence[j]
        else:
            sequence = list(self.iter_without_discards())
            for i, j in zip(range(len(sequence) - 1), range(1, len(sequence))):
                yield sequence[i], sequence[j]

    def shift_start_time_to_zero(self):
        """
        Shift all fixations backwards in time, such that the first fixation in
        the sequence starts at time 0. Returns the amount (in milliseconds)
        by which the entire sequence was shifted.
        """
        shift_amount = -self.start
        for fixation in self.iter_with_discards():
            fixation.shift_time(shift_amount)
        return -shift_amount

    def discard_short_fixations(self, threshold=50):
        """
        Discard all fixations that are shorter than some threshold value. Note
        that this only flags fixations as discarded and doesn't actually
        remove them; to remove discarded fixations, call
        `eyekit.fixation.FixationSequence.purge()` after discarding.
        """
        for fixation in self.iter_without_discards():
            if fixation.duration < threshold:
                fixation.discard()

    def discard_out_of_bounds_fixations(self, text_block, threshold=100):
        """
        Given a `eyekit.text.TextBlock`, discard all fixations that do not
        fall within some threshold distance of any character in the text.
        Note that this only flags fixations as discarded and doesn't actually
        remove them; to remove discarded fixations, call
        `eyekit.fixation.FixationSequence.purge()` after discarding.
        """
        _is_TextBlock(text_block)
        check_inside_line = threshold > text_block.line_height / 2
        threshold_squared = threshold**2
        for fixation in self.iter_without_discards():
            if check_inside_line and text_block.which_line(fixation):
                continue  # Fixation is inside a line, so skip to next fixation
            for char in text_block:
                distance_squared = (fixation.x - char.x) ** 2 + (
                    fixation.y - char.y
                ) ** 2
                if distance_squared < threshold_squared:
                    break
            else:  # For loop exited normally, so no char was within the threshold
                fixation.discard()

    def snap_to_lines(self, text_block, method="warp", **kwargs):
        """
        Given a `eyekit.text.TextBlock`, snap each fixation to the line that
        it most likely belongs to, eliminating any y-axis variation. Several
        methods are available (see below), some of which take optional
        parameters or require NumPy/SciPy to be installed. See [Carr et al.
        (2021)](https://doi.org/10.3758/s13428-021-01554-0) for a full
        description and evaluation of these methods. Note that in single-line
        TextBlocks, the `method` parameter has no effect: all fixations will
        be snapped to the one line. If a list of methods is passed in, each
        fixation will be snapped to the line with the most "votes" across the
        selection of methods(in the case of a tie, the left-most method takes
        priority). This "wisdom of the crowd" approach usually results in
        better performance; ideally, you should choose a selection of at
        least three methods that have different general properties: for
        example, `['chain', 'cluster', 'warp']`. When wisdom of the crowd is
        used, Fleiss's kappa is returned, indicating how much agreement there
        is among the methods; if this value is low (e.g. < 0.7), you may want
        to investigate the trial further.
        """
        _is_TextBlock(text_block)

        # SINGLE LINE TEXT BLOCK IS TREATED AS A SPECIAL CASE
        if text_block.n_rows == 1:
            for fixation in self.iter_without_discards():
                fixation.y = text_block.midlines[0]  # move all fixations to midline
            return 1.0  # Fleiss's kappa is 1 because hypothetically all methods would agree

        fixation_XY = [fixation.xy for fixation in self.iter_without_discards()]

        # APPLY ONE METHOD
        if isinstance(method, str):
            if method not in _snap.methods:
                raise ValueError(
                    f"Invalid method. Supported methods are: {', '.join(_snap.methods)}"
                )
            corrected_Y = _snap.methods[method](fixation_XY, text_block, **kwargs)
            kappa = None

        # TRY MANY METHODS AND USE WISDOM OF THE CROWD
        else:
            methods = method
            if len(methods) < 3:
                raise ValueError(
                    f"You must choose at least three methods. Supported methods are: {', '.join(_snap.methods)}"
                )
            corrections = []
            for method in methods:
                if isinstance(method, tuple):
                    method, kwargs = method
                else:
                    kwargs = {}
                if method not in _snap.methods:
                    raise ValueError(
                        f"Invalid method. Supported methods are: {', '.join(_snap.methods)}"
                    )
                corrections.append(
                    _snap.methods[method](fixation_XY, text_block, **kwargs)
                )
            corrected_Y, kappa = _snap.wisdom_of_the_crowd(corrections)

        # ADJUST Y-VALUES TO CORRECTED Y-VALUES
        for fixation, y in zip(self.iter_without_discards(), corrected_Y):
            fixation.y = y
        return kappa

    def serialize(self):
        """
        Returns representation of the fixation sequence in simple list format
        for serialization.
        """
        return [fixation.serialize() for fixation in self.iter_with_discards()]


# Append the docstring from each of the methods
FixationSequence.snap_to_lines.__doc__ += "\n\n" + "\n\n".join(
    [
        f"- `{method}` : " + func.__doc__.strip()
        for method, func in _snap.methods.items()
    ]
)


def _fail(obj, expectation):
    raise TypeError(f"Expected {expectation}, got {obj.__class__.__name__}")


def _is_Fixation(fixation):
    if not isinstance(fixation, Fixation):
        _fail(fixation, "Fixation")


def _is_FixationSequence(fixation_sequence):
    if not isinstance(fixation_sequence, FixationSequence):
        _fail(fixation_sequence, "FixationSequence")
