"""

Functions for performing common procedures, such as discarding out of
bounds fixations and snapping fixations to the lines of text.

"""


import pathlib as _pathlib
import cairocffi as _cairo
from . import _snap
from . import _validate


def discard_short_fixations(fixation_sequence, threshold=50):
    """

    Given a `eyekit.fixation.FixationSequence`, discard all fixations that are
    shorter than some threshold value. Operates directly on the sequence and
    does not return a copy. Note that this only flags fixations as discarded
    and doesn't actually remove them; to remove discarded fixations, use
    `eyekit.fixation.FixationSequence.purge()`.

    """
    _validate.is_FixationSequence(fixation_sequence)
    for fixation in fixation_sequence.iter_without_discards():
        if fixation.duration < threshold:
            fixation.discard()


def discard_out_of_bounds_fixations(fixation_sequence, text_block, threshold=100):
    """

    Given a `eyekit.fixation.FixationSequence` and `eyekit.text.TextBlock`,
    discard all fixations that do not fall within some threshold distance of
    any character in the text. Operates directly on the sequence and does not
    return a copy. Note that this only flags fixations as discarded and
    doesn't actually remove them; to remove discarded fixations, use
    `eyekit.fixation.FixationSequence.purge()`.

    """
    _validate.is_FixationSequence(fixation_sequence)
    _validate.is_TextBlock(text_block)
    check_inside_line = threshold > text_block.line_height / 2
    threshold_squared = threshold ** 2
    for fixation in fixation_sequence.iter_without_discards():
        if check_inside_line and text_block.which_line(fixation):
            continue  # Fixation is inside a line, so skip to next fixation
        for char in text_block:
            distance_squared = (fixation.x - char.x) ** 2 + (fixation.y - char.y) ** 2
            if distance_squared < threshold_squared:
                break
        else:  # For loop exited normally, so no char was within the threshold
            fixation.discard()


def snap_to_lines(fixation_sequence, text_block, method="warp", **kwargs):
    """

    Given a `eyekit.fixation.FixationSequence` and `eyekit.text.TextBlock`,
    snap each fixation to the line that it most likely belongs to, eliminating
    any y-axis variation or drift. Operates directly on the sequence and does
    not return a copy. Several methods are available, some of which take
    optional parameters or require SciPy to be installed. For a full
    description and evaluation of these methods, see [Carr et al.
    (2021)](https://doi.org/10.3758/s13428-021-01554-0). Note that in
    single-line TextBlocks, the `method` parameter has no effect: all
    fixations will be snapped to the one line.

    """
    _validate.is_FixationSequence(fixation_sequence)
    _validate.is_TextBlock(text_block)
    if method not in _snap.methods:
        raise ValueError(
            f"Invalid method. Supported methods are: {', '.join(_snap.methods)}"
        )
    if text_block.n_rows == 1:
        for fixation in fixation_sequence.iter_without_discards():
            fixation.y = text_block.midlines[0]  # move all fixations to midline
    else:
        fixation_XY = [
            fixation.xy for fixation in fixation_sequence.iter_without_discards()
        ]
        corrected_Y = _snap.methods[method](fixation_XY, text_block, **kwargs)
        for fixation, y in zip(fixation_sequence.iter_without_discards(), corrected_Y):
            fixation.y = y


# Append the docstring from each of the methods
snap_to_lines.__doc__ += "\n\n" + "\n\n".join(
    [
        f"- `{method}` : " + func.__doc__.strip()
        for method, func in _snap.methods.items()
    ]
)


def align_to_screenshot(
    text_block,
    screenshot_path,
    output_path=None,
    show_text=True,
    show_guide_lines=True,
    show_bounding_boxes=False,
):
    """

    Given a `eyekit.text.TextBlock` and the path to a PNG screenshot file,
    produce an image showing the original screenshot overlaid with the text
    block (shown in green). If no output path is provided, the output image is
    written to the same directory as the screenshot file. This is useful for
    establishing `eyekit.text.TextBlock` parameters (position, font size,
    etc.) that match what participants actually saw in your experiment.

    """
    _validate.is_TextBlock(text_block)
    screenshot_path = _pathlib.Path(screenshot_path)
    if not screenshot_path.exists():
        raise ValueError(f"Screenshot file does not exist: {screenshot_path}")
    if screenshot_path.suffix[1:].upper() != "PNG":
        raise ValueError("Screenshot must be PNG file")
    surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, 1, 1).create_from_png(
        str(screenshot_path)
    )
    context = _cairo.Context(surface)
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    context.set_source_rgb(0.60392, 0.80392, 0.19607)
    context.set_font_face(text_block._font.toy_font_face)
    context.set_font_size(text_block._font.size)
    if show_guide_lines:
        context.set_line_width(2)
        context.move_to(text_block.position[0], 0)
        context.line_to(text_block.position[0], screen_height)
        context.stroke()
    for line in text_block.lines():
        if show_guide_lines:
            context.move_to(0, line.baseline)
            context.line_to(screen_width, line.baseline)
            context.stroke()
            context.set_dash([8, 4])
        if show_text:
            context.move_to(line._x_tl, line.baseline)  # _x_tl is unpadded x_tl
            context.show_text(line.text)
    if show_bounding_boxes:
        context.set_dash([])
        for word in text_block.words():
            context.rectangle(*word.box)
            context.stroke()
    if output_path is None:
        output_path = screenshot_path.parent / f"{screenshot_path.stem}_eyekit.png"
    else:
        output_path = _pathlib.Path(output_path)
        if not output_path.parent.exists():
            raise ValueError(f"Output path does not exist: {output_path.parent}")
        if output_path.suffix[1:].upper() != "PNG":
            raise ValueError("Output must be PNG file")
    surface.write_to_png(str(output_path))


def font_size_at_72dpi(font_size, at_dpi=96):
    """

    Convert a font size at some dpi to the equivalent font size at 72dpi.
    Typically, this can be used to convert a Windows-style 96dpi font size to
    the equivalent size at 72dpi.

    """
    return font_size * at_dpi / 72
