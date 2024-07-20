"""
Miscellaneous utility functions.
"""

import pathlib as _pathlib
import cairocffi as _cairo
from .text import _is_TextBlock, TextBlock as _TextBlock
from .vis import Image as _Image
from .io import save as _save


def create_stimuli(
    input_texts,
    output_stimuli,
    *,
    screen_width: int,
    screen_height: int,
    color: str = "black",
    background_color: str = "white",
    **kwargs,
):
    """
    Create PNG stimuli for a set of texts. This may be useful if you want to
    use Eyekit to create your experimental stimuli. If `input_texts` is a
    string, it will be treated as a path to a directory of .txt files. If
    `input_texts` is a list, it is assumed to be a list of texts (strings or
    lists of strings). If `input_texts` is a dictionary, it should be of the
    form `{'stim_id': TextBlock, ...}`. `output_stimuli` must be a path to a
    directory. The `screen_width` and `screen_height` must be specified and
    should match the final display size of the experimental stimuli
    (typically, the experimental computer's screen resolution). A `color` and
    `background_color` can optionally be specified (defaulting to black on
    white). Additional arguments are passed to `TextBlock`, and may include
    `position`, `font_face`, `font_size`, and `line_height`
    (see `eyekit.text.TextBlock` for more info). The function will also store
    the texts as `TextBlock` objects in `stimuli.json` for use at the
    analysis stage.

    """
    stimuli = {}
    if isinstance(input_texts, dict):
        stimuli = input_texts
    elif isinstance(input_texts, str):
        input_texts = _pathlib.Path(input_texts)
        if not input_texts.exists() or not input_texts.is_dir():
            raise ValueError(
                f"Specified input_texts {input_texts} is not an existing directory"
            )
        for file_path in input_texts.iterdir():
            if file_path.suffix != ".txt":
                continue
            with open(file_path) as file:
                text = [line.strip() for line in file]
            stimuli[file_path.stem] = _TextBlock(text, **kwargs)
    elif isinstance(input_texts, list):
        for i, text in enumerate(input_texts):
            if isinstance(text, str):
                text = text.split("\n")
            stimuli[f"text{i}"] = _TextBlock(text, **kwargs)
    else:
        raise ValueError(
            "Cannot interpret input_texts. Should be path, list of texts, or dictionary of TextBlocks."
        )
    output_stimuli = _pathlib.Path(output_stimuli)
    if output_stimuli.exists() and not output_stimuli.is_dir():
        raise ValueError(
            f"Specified output_stimuli {output_stimuli} is not a directory"
        )
    if not output_stimuli.exists():
        output_stimuli.mkdir()
    for stim_id, text_block in stimuli.items():
        img = _Image(screen_width, screen_height)
        img.set_background_color(background_color)
        img.draw_text_block(text_block, color=color)
        img.save(output_stimuli / f"{stim_id}.png")
    _save(stimuli, output_stimuli / f"stimuli.json")


def align_to_screenshot(
    text_block,
    screenshot_path,
    *,
    output_path=None,
    show_text: bool = True,
    show_guide_lines: bool = True,
    show_bounding_boxes: bool = False,
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
    context.set_font_face(text_block._font.face)
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


def font_size_at_72dpi(font_size, at_dpi: int = 96) -> float:
    """
    Convert a font size at some dpi to the equivalent font size at 72dpi.
    Typically, this can be used to convert a Windows-style 96dpi font size to
    the equivalent size at 72dpi.
    """
    return font_size * at_dpi / 72


# DEPRECATED FUNCTIONS TO BE REMOVED IN THE FUTURE


def discard_short_fixations(fixation_sequence, threshold=50):  # pragma: no cover
    """
    **Deprecated in 0.4 and removed in 0.6.** Use
    `eyekit.fixation.FixationSequence.discard_short_fixations()`.
    """
    raise NotImplementedError(
        "eyekit.tools.discard_short_fixations() has been removed, use FixationSequence.discard_short_fixations() instead"
    )


def discard_out_of_bounds_fixations(
    fixation_sequence, text_block, threshold=100
):  # pragma: no cover
    """
    **Deprecated in 0.4 and removed in 0.6.** Use
    `eyekit.fixation.FixationSequence.discard_out_of_bounds_fixations()`.
    """
    raise NotImplementedError(
        "eyekit.tools.discard_out_of_bounds_fixations() has been removed, use FixationSequence.discard_out_of_bounds_fixations() instead"
    )


def snap_to_lines(
    fixation_sequence, text_block, method="warp", **kwargs
):  # pragma: no cover
    """
    **Deprecated in 0.4 and removed in 0.6.** Use
    `eyekit.fixation.FixationSequence.snap_to_lines()`.
    """
    raise NotImplementedError(
        "eyekit.tools.snap_to_lines() has been removed, use FixationSequence.snap_to_lines() instead"
    )
