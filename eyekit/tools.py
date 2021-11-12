"""
Miscellaneous utility functions.
"""


import pathlib as _pathlib
import cairocffi as _cairo
from . import _snap
from .text import _is_TextBlock


def align_to_screenshot(
    text_block,
    screenshot_path,
    *,
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
    _is_TextBlock(text_block)
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


# DEPRECATED FUNCTIONS TO BE REMOVED IN THE FUTURE

import warnings as _warnings


def discard_short_fixations(fixation_sequence, threshold=50):
    """
    Deprecated in 0.4. Use `eyekit.fixation.FixationSequence.discard_short_fixations()`.
    """
    _warnings.warn(
        "eyekit.tools.discard_short_fixations() is deprecated, use FixationSequence.discard_short_fixations() instead",
        FutureWarning,
    )
    return fixation_sequence.discard_short_fixations(threshold)


def discard_out_of_bounds_fixations(fixation_sequence, text_block, threshold=100):
    """
    Deprecated in 0.4. Use `eyekit.fixation.FixationSequence.discard_out_of_bounds_fixations()`.
    """
    _warnings.warn(
        "eyekit.tools.discard_out_of_bounds_fixations() is deprecated, use FixationSequence.discard_out_of_bounds_fixations() instead",
        FutureWarning,
    )
    return fixation_sequence.discard_out_of_bounds_fixations(text_block, threshold)


def snap_to_lines(fixation_sequence, text_block, method="warp", **kwargs):
    """
    Deprecated in 0.4. Use `eyekit.fixation.FixationSequence.snap_to_lines()`.
    """
    _warnings.warn(
        "eyekit.tools.snap_to_lines() is deprecated, use FixationSequence.snap_to_lines() instead",
        FutureWarning,
    )
    return fixation_sequence.snap_to_lines(text_block, method, **kwargs)
