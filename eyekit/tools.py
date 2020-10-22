"""

Functions for performing common procedures, such as discarding out of
bounds fixations and snapping fixations to the lines of text.

"""


from os.path import splitext as _splitext
import cairocffi as _cairo
from ._core import distance as _distance
from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock
from . import _drift


def discard_short_fixations(fixation_sequence, threshold=50):
    """

    Given a `eyekit.fixation.FixationSequence`, discard all fixations that are
    shorter than some threshold value. Operates directly on the sequence and
    does not return a copy.

    """
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type eyekit.FixationSequence")
    for fixation in fixation_sequence:
        if fixation.duration < threshold:
            fixation.discarded = True


def discard_out_of_bounds_fixations(fixation_sequence, text_block, threshold=100):
    """

    Given a `eyekit.fixation.FixationSequence` and `eyekit.text.TextBlock`,
    discard all fixations that do not fall within some threshold distance of
    any character in the text. Operates directly on the sequence and does not
    return a copy.

    """
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type eyekit.FixationSequence")
    if not isinstance(text_block, _TextBlock):
        raise TypeError("text_block should be of type eyekit.TextBlock")
    for fixation in fixation_sequence:
        for char in text_block:
            if _distance(fixation.xy, char.center) < threshold:
                break
        else:  # For loop exited normally, so no char was within the threshold
            fixation.discarded = True


def snap_to_lines(fixation_sequence, text_block, method="warp", **kwargs):
    """

    Given a `eyekit.fixation.FixationSequence` and `eyekit.text.TextBlock`,
    snap each fixation to the line that it most likely belongs to, eliminating
    any y-axis variation or drift. Operates directly on the sequence and does
    not return a copy. Several methods are available, some of which take
    optional parameters or require SciPy to be installed. For a full
    description and evaluation of these methods, see [Carr et al.
    (2020)](https://osf.io/jg3nc/).

    - `chain` : Chain consecutive fixations that are sufficiently close to
    each other, and then assign chains to their closest text lines. Default
    params: `x_thresh=192`, `y_thresh=32`.

    - `cluster` : Classify fixations into *m* clusters based on their
    Y-values, and then assign clusters to text lines in positional order.
    Requires SciPy.

    - `merge` : Form a set of progressive sequences and then reduce the set to
    *m* by repeatedly merging those that appear to be on the same line. Merged
    sequences are then assigned to text lines in positional order. Default
    params: `y_thresh=32`, `gradient_thresh=0.1`, `error_thresh=20`.

    - `regress` : Find *m* regression lines that best fit the fixations and
    group fixations according to best fit regression lines, and then assign
    groups to text lines in positional order. Default params:
    `slope_bounds=(-0.1, 0.1)`, `offset_bounds=(-50, 50)`, `std_bounds=(1, 20)`.
    Requires SciPy.

    - `segment` : Segment fixation sequence into *m* subsequences based on
    *m*–1 most-likely return sweeps, and then assign subsequences to text
    lines in chronological order.

    - `split` : Split fixation sequence into subsequences based on best
    candidate return sweeps, and then assign subsequences to closest text
    lines. Requires SciPy.

    - `stretch` : Find a stretch factor and offset that results in a good
    alignment between the fixations and lines of text, and then assign the
    transformed fixations to the closest text lines. Default params:
    `stretch_bounds=(0.9, 1.1)`, `offset_bounds=(-50, 50)`. Requires SciPy.

    - `warp` : Map fixations to word centers by finding a monotonically
    increasing mapping with minimal cost, effectively resulting in *m*
    subsequences, and then assign fixations to the lines that their mapped
    words belong to, effectively assigning subsequences to text lines in
    chronological order.

    """
    if not isinstance(fixation_sequence, _FixationSequence):
        raise TypeError("fixation_sequence should be of type eyekit.FixationSequence")
    if not isinstance(text_block, _TextBlock):
        raise TypeError("text_block should be of type eyekit.TextBlock")
    if method not in _drift.methods:
        raise ValueError(
            f"Invalid method. Supported methods are: {', '.join(_drift.methods)}"
        )
    if text_block.n_rows == 1:
        for fixation in fixation_sequence.iter_without_discards():
            fixation.y = text_block.line_positions[0]
    else:
        fixation_XY = fixation_sequence.XYarray(include_discards=False)
        corrected_Y = _drift.methods[method](fixation_XY, text_block, **kwargs)
        for fixation, y in zip(fixation_sequence.iter_without_discards(), corrected_Y):
            fixation.y = y


def align_to_screenshot(
    text_block,
    screenshot_path,
    output_path=None,
    show_text=True,
    show_bounding_boxes=False,
):
    """

    Create an image depicting a PNG screenshot overlaid with a
    `eyekit.text.TextBlock` in green. If no output path is provided, the
    output is written to the same directory as the screenshot file. This is
    useful for establishing the correct `eyekit.text.TextBlock` parameters to
    match what participants are actually seeing.

    """
    surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, 1, 1).create_from_png(
        screenshot_path
    )
    context = _cairo.Context(surface)
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    context.set_source_rgb(0.60392, 0.80392, 0.19607)
    context.set_font_face(text_block._font.toy_font_face)
    context.set_font_size(text_block._font.size)
    context.set_line_width(2)
    context.move_to(text_block.x_tl, 0)
    context.line_to(text_block.x_tl, screen_height)
    context.stroke()
    for i, line in enumerate(text_block.lines()):
        if i == 0:
            context.move_to(0, text_block._first_baseline)
            context.line_to(screen_width, text_block._first_baseline)
            context.stroke()
            context.set_dash([8, 4])
        else:
            context.move_to(text_block.x_tl, line.baseline)
            context.line_to(screen_width, line.baseline)
            context.stroke()
        if show_text:
            context.move_to(line.x_tl, line.baseline)
            context.show_text(line.text)
    if show_bounding_boxes:
        context.set_dash([])
        for word in text_block.words(add_padding=False):
            context.rectangle(*word.box)
            context.stroke()
    if output_path is None:
        output_path = _splitext(screenshot_path)[0] + "_eyekit.png"
    surface.write_to_png(output_path)


def font_size_at_72dpi(font_size, at_dpi=96):
    """

    Convert a font size at some dpi to the equivalent font size at 72dpi.
    Typically, this can be used to convert a Windows-style 96dpi font size to
    the equivalent size at 72dpi.

    """
    return font_size * at_dpi / 72
