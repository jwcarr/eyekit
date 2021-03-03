"""

Defines the `Image`, `Figure`, and `Booklet` objects, which are used to create
visualizations.

"""


from os.path import splitext as _splitext
import cairocffi as _cairo
from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock, Box as _Box, _Font
from . import _color

try:
    from ._version import __version__
except ImportError:
    __version__ = "???"


_FONT_FACE = "Arial"
_FONT_SIZE = 8


def set_default_font(font_face=None, font_size=None):
    """

    Set the default font face and/or size that will be used in figure captions
    and image annotations. This selection can be overridden on a per-image or
    per-figure basis. If no font is set, Eyekit defaults to 8pt Arial.

    """
    global _FONT_FACE, _FONT_SIZE
    if font_face is not None:
        _FONT_FACE = str(font_face)
    if font_size is not None:
        _FONT_SIZE = float(font_size)


class Image(object):

    """

    The Image class is used to create visualizations of text blocks and
    fixation sequences, and it provides methods for drawing various kinds of
    annotation. The general usage pattern is:

    ```python
    img = eyekit.vis.Image(1920, 1080)
    img.draw_text_block(txt)
    img.draw_fixation_sequence(seq)
    img.save('image.pdf')
    ```

    """

    def __init__(self, screen_width: int, screen_height: int):
        """Initialized with:

        - `screen_width` Width of the screen in pixels.
        - `screen_height` Height of the screen in pixels.
        """
        self.screen_width = int(screen_width)
        self.screen_height = int(screen_height)
        self._caption = None
        self._caption_font_face = _FONT_FACE
        self._caption_font_size = _FONT_SIZE
        self._background_color = (1, 1, 1)
        self._components = []
        self._text_extents = None

    ################
    # PUBLIC METHODS
    ################

    def set_caption(self, caption, font_face=None, font_size=None):
        """

        Set the image's caption, which will be shown above the image if you
        place it inside a `Figure`.

        """
        self._caption = str(caption)
        if font_face is not None:
            self._caption_font_face = str(font_face)
        if font_size is not None:
            self._caption_font_size = float(font_size)

    def set_background_color(self, color):
        """

        Set the background color of the image. By default the background color
        is white. If `color` is set to `None`, the background will be
        transparent.

        """
        if color is None:
            self._background_color = None
        else:
            self._background_color = _color_to_rgb(color)

    def draw_text_block(self, text_block, color="black"):
        """

        Draw a `eyekit.text.TextBlock` on the image. `color` sets the color of
        the text.

        """
        if not isinstance(text_block, _TextBlock):
            raise TypeError("text_block should be of type TextBlock")
        if self._text_extents is None:
            self._text_extents = [
                text_block.x_tl,
                text_block.y_tl,
                text_block.x_br,
                text_block.y_br,
            ]
        else:
            if text_block.x_tl < self._text_extents[0]:
                self._text_extents[0] = text_block.x_tl
            if text_block.y_tl < self._text_extents[1]:
                self._text_extents[1] = text_block.y_tl
            if text_block.x_br > self._text_extents[2]:
                self._text_extents[2] = text_block.x_br
            if text_block.y_br > self._text_extents[3]:
                self._text_extents[3] = text_block.y_br
        rgb_color = _color_to_rgb(color)
        for line in text_block.lines():
            arguments = {
                "x": line._x_tl,  # _x_tl is unpadded x_tl
                "y": line.baseline,
                "text": line.display_text,
                "font": text_block._font,
                "color": rgb_color,
            }
            self._add_component(_draw_text, arguments)

    def draw_text_block_heatmap(self, text_block, distribution, color="red"):
        """

        Draw a `eyekit.text.TextBlock` on the image along with an associated
        distribution, which is represented in heatmap form. This is can be
        used to visualize the output from `eyekit.analysis.duration_mass()`.
        `color` determines the color of the heatmap.

        """
        if not isinstance(text_block, _TextBlock):
            raise TypeError("text_block should be of type TextBlock")
        rgb_color = _color_to_rgb(color)
        n = (text_block.n_cols - distribution.shape[1]) + 1
        distribution /= distribution.max()
        subcell_height = text_block.line_height / n
        levels = [subcell_height * i for i in range(n)]
        level = 0
        for ngram in text_block.ngrams(n, alphabetical_only=False):
            r, s, _ = ngram.location
            if level == n:
                level = 0
            p = distribution[(int(r), int(s))]
            cell_color = _pseudo_alpha(rgb_color, opacity=p)
            arguments = {
                "x": ngram._x_tl,
                "y": ngram.y_tl + subcell_height * level,
                "width": ngram._x_br - ngram._x_tl,
                "height": subcell_height,
                "stroke_width": None,
                "color": None,
                "fill_color": cell_color,
                "dashed": False,
            }
            self._add_component(_draw_rectangle, arguments)
            level += 1
        self.draw_text_block(text_block)

    def draw_fixation_sequence(
        self,
        fixation_sequence,
        show_saccades=True,
        show_discards=False,
        color="black",
        discard_color="gray",
        number_fixations=False,
        fixation_radius=None,
    ):
        """

        Draw a `eyekit.fixation.FixationSequence` on the image. Optionally,
        you can choose whether or not to display saccade lines and discarded
        fixations, and which colors to use. `number_fixations` is not yet
        implemented. `fixation_radius` can be used to set a constant radius
        for all fixations (rather than a radius that is proportional to
        duration).

        """
        if not isinstance(fixation_sequence, _FixationSequence):
            raise TypeError("fixation_sequence should be of type FixationSequence")
        rgb_color = _color_to_rgb(color)
        rgb_discard_color = _color_to_rgb(discard_color)
        if show_discards:
            if show_saccades:
                path = [
                    fixation.xy for fixation in fixation_sequence.iter_with_discards()
                ]
                arguments = {
                    "path": path,
                    "stroke_width": 0.5,
                    "color": rgb_color,
                    "dashed": False,
                }
                self._add_component(_draw_line, arguments)
            for fixation in fixation_sequence.iter_with_discards():
                radius = fixation_radius or _duration_to_radius(fixation.duration)
                f_color = rgb_discard_color if fixation.discarded else rgb_color
                arguments = {
                    "x": fixation.x,
                    "y": fixation.y,
                    "radius": radius,
                    "color": None,
                    "stroke_width": None,
                    "dashed": False,
                    "fill_color": f_color,
                }
                self._add_component(_draw_circle, arguments)
        else:
            if show_saccades:
                path = [
                    fixation.xy
                    for fixation in fixation_sequence.iter_without_discards()
                ]
                arguments = {
                    "path": path,
                    "stroke_width": 0.5,
                    "color": rgb_color,
                    "dashed": False,
                }
                self._add_component(_draw_line, arguments)
            for fixation in fixation_sequence.iter_without_discards():
                radius = fixation_radius or _duration_to_radius(fixation.duration)
                arguments = {
                    "x": fixation.x,
                    "y": fixation.y,
                    "radius": radius,
                    "color": None,
                    "stroke_width": None,
                    "dashed": False,
                    "fill_color": rgb_color,
                }
                self._add_component(_draw_circle, arguments)

    def draw_sequence_comparison(
        self,
        reference_sequence,
        fixation_sequence,
        color_match="black",
        color_mismatch="red",
        fixation_radius=None,
    ):
        """

        Draw a `eyekit.fixation.FixationSequence` on the image with the
        fixations colored according to whether or not they match a reference
        sequence in terms of the y-coordinate. This is mostly useful for
        comparing the outputs of two different drift correction algorithms.

        """
        if not isinstance(fixation_sequence, _FixationSequence):
            raise TypeError("fixation_sequence should be of type FixationSequence")
        if not isinstance(reference_sequence, _FixationSequence):
            raise TypeError("reference_sequence should be of type FixationSequence")
        rgb_color_match = _color_to_rgb(color_match)
        rgb_color_mismatch = _color_to_rgb(color_mismatch)
        path = [fixation.xy for fixation in fixation_sequence.iter_with_discards()]
        arguments = {
            "path": path,
            "stroke_width": 0.5,
            "color": rgb_color_match,
            "dashed": False,
        }
        self._add_component(_draw_line, arguments)
        for reference_fixation, fixation in zip(
            reference_sequence.iter_with_discards(),
            fixation_sequence.iter_with_discards(),
        ):
            if reference_fixation.y == fixation.y:
                color = rgb_color_match
            else:
                color = rgb_color_mismatch
            radius = fixation_radius or _duration_to_radius(fixation.duration)
            arguments = {
                "x": fixation.x,
                "y": fixation.y,
                "radius": radius,
                "color": None,
                "stroke_width": None,
                "dashed": False,
                "fill_color": color,
            }
            self._add_component(_draw_circle, arguments)

    def draw_line(self, start_xy, end_xy, color="black", stroke_width=1, dashed=False):
        """

        Draw an arbitrary line on the image from `start_xy` to `end_xy`.
        `stroke_width` is set in points for vector output or pixels for PNG
        output.

        """
        rgb_color = _color_to_rgb(color)
        arguments = {
            "path": [start_xy, end_xy],
            "stroke_width": float(stroke_width),
            "color": rgb_color,
            "dashed": dashed,
        }
        self._add_component(_draw_line, arguments)

    def draw_circle(
        self, x, y, radius, color="black", stroke_width=1, dashed=False, fill_color=None
    ):
        """

        Draw an arbitrary circle on the image centered at `x`, `y` and with
        some `radius`. `stroke_width` is set in points for vector output or
        pixels for PNG output.

        """
        rgb_color = _color_to_rgb(color) if color else None
        rgb_fill_color = _color_to_rgb(fill_color) if fill_color else None
        arguments = {
            "x": float(x),
            "y": float(y),
            "radius": float(radius),
            "color": rgb_color,
            "stroke_width": float(stroke_width),
            "dashed": dashed,
            "fill_color": rgb_fill_color,
        }
        self._add_component(_draw_circle, arguments)

    def draw_rectangle(
        self,
        rect,
        y=None,
        width=None,
        height=None,
        color="black",
        stroke_width=1,
        dashed=False,
        fill_color=None,
    ):
        """

        Draw a rectangle on the image. You can pass in some box-like object,
        such as an `text.InterestArea`, or you can specify an x, y, width, and
        height to draw an arbitrary rectangle. `stroke_width` is set in
        points for vector output or pixels for PNG output.

        """
        rgb_color = _color_to_rgb(color) if color else None
        rgb_fill_color = _color_to_rgb(fill_color) if fill_color else None
        if isinstance(rect, _Box):
            x, y, width, height = rect.box
        elif isinstance(rect, tuple) and len(rect) == 4:
            x, y, width, height = rect
        else:
            x = rect
        arguments = {
            "x": float(x),
            "y": float(y),
            "width": float(width),
            "height": float(height),
            "color": rgb_color,
            "stroke_width": float(stroke_width),
            "dashed": dashed,
            "fill_color": rgb_fill_color,
        }
        self._add_component(_draw_rectangle, arguments)

    def draw_annotation(
        self, x, y, text, font_face=None, font_size=None, color="black"
    ):
        """

        Draw arbitrary text on the image located at `x`, `y`. `font_size` is
        set in points for vector output or pixels for PNG output.

        """
        if font_face is None:
            font_face = _FONT_FACE
        if font_size is None:
            font_size = _FONT_SIZE
        font = _Font(font_face, font_size)
        rgb_color = _color_to_rgb(color)
        arguments = {
            "x": float(x),
            "y": float(y),
            "text": str(text),
            "font": font,
            "color": rgb_color,
            "annotation": True,
        }
        self._add_component(_draw_text, arguments)

    def save(self, output_path, width=150, crop_margin=None):
        """

        Save the image to some `output_path`. Images can be saved as .pdf,
        .eps, .svg, or .png. `width` only applies to the vector formats and
        determines the millimeter width of the output file; PNG images are
        saved at actual pixel size. If you set a crop margin, the image will
        be cropped to the size of the `eyekit.text.TextBlock` plus the
        specified margin. Margins are specified in millimeters (PDF, EPS, SVG)
        or pixels (PNG).

        """
        output_path = str(output_path)
        image_format = _splitext(output_path)[1][1:].upper()
        if image_format not in ["PDF", "EPS", "SVG", "PNG"]:
            raise ValueError(
                "Unrecognized format. Use .pdf, .eps, or .svg for vector output, or .png for raster output."
            )
        image_width = _mm_to_pts(width)
        surface, context, scale = self._make_surface(
            output_path, image_format, image_width, crop_margin
        )
        self._render_background(context)
        self._render_components(context, scale)
        if image_format == "PNG":
            surface.write_to_png(output_path)
        surface.finish()

    #################
    # PRIVATE METHODS
    #################

    def _add_component(self, func, arguments):
        """

        Add a component to the stack. This should be a draw_ function and its
        argumments. This function will be called with its arguments at save
        time.

        """
        self._components.append((func, arguments))

    def _make_surface(self, output_path, image_format, image_width, crop_margin):
        """

        Make the relevant Cairo surface and context with appropriate sizing.

        """
        if image_format == "PNG":
            scale = 1
            if crop_margin is None:
                image_width = self.screen_width
                image_height = self.screen_height
            else:
                image_width = int(
                    (self._text_extents[2] - self._text_extents[0]) + crop_margin * 2
                )
                image_height = int(
                    (self._text_extents[3] - self._text_extents[1]) + crop_margin * 2
                )
            surface = _cairo.ImageSurface(
                _cairo.FORMAT_ARGB32, image_width, image_height
            )
        else:
            if crop_margin is None:
                scale = image_width / self.screen_width
                image_height = self.screen_height * scale
            else:
                crop_margin = _mm_to_pts(crop_margin)
                if crop_margin > image_width / 3:
                    raise ValueError(
                        "The crop margin set on this image is too large for the image width. Increase the image width or decrease the crop margin."
                    )
                scale = (image_width - crop_margin * 2) / (
                    self._text_extents[2] - self._text_extents[0]
                )
                image_height = (
                    self._text_extents[3] - self._text_extents[1]
                ) * scale + crop_margin * 2
            if image_format == "PDF":
                surface = _cairo.PDFSurface(output_path, image_width, image_height)
                surface.set_metadata(
                    _cairo.PDF_METADATA_CREATOR, f"eyekit {__version__}"
                )
            elif image_format == "EPS":
                surface = _cairo.PSSurface(output_path, image_width, image_height)
                surface.set_eps(True)
            elif image_format == "SVG":
                surface = _cairo.SVGSurface(output_path, image_width, image_height)
            surface.set_device_scale(scale, scale)
        context = _cairo.Context(surface)
        if crop_margin is not None:
            crop_margin = crop_margin / scale
            context.translate(
                -self._text_extents[0] + crop_margin,
                -self._text_extents[1] + crop_margin,
            )
        return surface, context, scale

    def _render_background(self, context):
        """

        Render the background color.

        """
        if self._background_color is not None:
            with context:
                context.set_source_rgb(*self._background_color)
                context.paint()

    def _render_components(self, context, scale):
        """

        Render all components in the components stack (functions and function
        arguments that must be called in sequence).

        """
        for func, arguments in self._components:
            with context:
                func(context, scale, **arguments)

    def _render_to_figure(self, context, scale):
        """

        Render the image to a figure panel.

        """
        self._render_background(context)
        self._render_components(context, scale)


class Figure(object):

    """

    The Figure class is used to combine one or more images into a
    publication-ready figure. The general usage pattern is:

    ```python
    fig = eyekit.vis.Figure(1, 2)
    fig.add_image(img1)
    fig.add_image(img2)
    fig.save('figure.pdf')
    ```

    """

    def __init__(self, n_rows: int = 1, n_cols: int = 1):
        """Initialized with:

        - `n_rows` Number of rows in the figure.
        - `n_cols` Number of columns in the figure.
        """
        self._n_rows = int(n_rows)
        if self._n_rows <= 0:
            raise ValueError("Invalid number of rows")
        self._n_cols = int(n_cols)
        if self._n_rows <= 0:
            raise ValueError("Invalid number of columns")
        self._grid = [[None] * self._n_cols for _ in range(self._n_rows)]
        self._crop_margin = None
        self._lettering = True
        self._letter_font_face = _FONT_FACE + " bold"
        self._letter_font_size = _FONT_SIZE
        self._v_padding = 4
        self._h_padding = 4
        self._e_padding = 1
        self._border_color = (0, 0, 0)
        self._border_width = 1

    ################
    # PUBLIC METHODS
    ################

    def set_crop_margin(self, crop_margin):
        """

        Set the crop margin of the embedded images. Each image in the figure
        will be cropped to the size and positioning of the most extreme text
        block extents, plus the specified margin. This has the effect of
        zooming in to all images in a consistent way – maintaining the aspect
        ratio and relative positioning of the text blocks across images.
        Margins are specified in figure millimeters.

        """
        self._crop_margin = _mm_to_pts(crop_margin)

    def set_border_style(self, stroke_width=None, color=None):
        """

        Set the thickness and color of the image borders. By default, image
        border are 1pt black.

        """
        if stroke_width is not None:
            self._border_width = float(stroke_width)
        if color is not None:
            self._border_color = _color_to_rgb(color)

    def set_lettering(self, lettering=True, font_face=None, font_size=None):
        """

        By default, each image caption is prefixed with a letter, **(A)**,
        **(B)**, **(C)**, etc. If you want to turn this off, call
        ```Figure.set_lettering(False)``` prior to saving.

        """
        self._lettering = bool(lettering)
        if font_face is not None:
            self._letter_font_face = str(font_face)
        if font_size is not None:
            self._letter_font_size = float(font_size)

    def set_padding(self, vertical=None, horizontal=None, edge=None):
        """

        Set the vertical or horizontal padding between images or the padding
        around the edge of the figure. Padding is expressed in millimeters. By
        default, the vertical and horizontal padding between images is 4mm and
        the edge padding is 1mm.

        """
        if vertical is not None:
            self._v_padding = float(vertical)
        if horizontal is not None:
            self._h_padding = float(horizontal)
        if edge is not None:
            self._e_padding = float(edge)

    def add_image(self, image, row=None, col=None):
        """

        Add an `Image` to the figure. If a row and column index is specified,
        the image is placed in that position. Otherwise, `image` is placed in
        the next available position.

        """
        if not isinstance(image, Image):
            raise TypeError("image should be of type Image.")
        if row is None or col is None:
            row, col = self._next_available_cell(row, col)
        if row >= self._n_rows or col >= self._n_cols:
            raise ValueError("Row or column index is not inside the grid.")
        self._grid[row][col] = image

    def save(self, output_path, width=150):
        """

        Save the figure to some `output_path`. Figures can be saved as .pdf,
        .eps, or .svg. `width` determines the millimeter width of the output
        file.

        """
        output_path = str(output_path)
        figure_format = _splitext(output_path)[1][1:].upper()
        if figure_format not in ["PDF", "EPS", "SVG"]:
            raise ValueError("Unrecognized format. Use .pdf, .eps, or .svg.")
        figure_width = _mm_to_pts(width)
        layout, components, height, text_block_extents = self._make_layout(figure_width)
        surface, context = self._make_surface(
            output_path, figure_format, figure_width, height
        )
        self._render_background(context)
        self._render_images(surface, layout, text_block_extents)
        self._render_components(context, components)
        surface.finish()

    #################
    # PRIVATE METHODS
    #################

    def _next_available_cell(self, row_i=None, col_i=None):
        """

        Get the indices of the next available cell in the figure, optionally
        in a specific row or column.

        """
        for i, row in enumerate(self._grid):
            if row_i is not None and row_i != i:
                continue
            for j, cell in enumerate(row):
                if col_i is not None and col_i != j:
                    continue
                if cell is None:
                    return i, j
        raise ValueError(
            "Cannot add image to the figure because there are no available positions. Make a new Figure with more rows or columns, or specify a specific row and column index to overwrite the image that is currently in that position."
        )

    def _make_surface(self, output_path, figure_format, figure_width, figure_height):
        """

        Make the relevant Cairo surface and context with appropriate sizing.

        """
        if figure_format == "PDF":
            surface = _cairo.PDFSurface(output_path, figure_width, figure_height)
            surface.set_metadata(_cairo.PDF_METADATA_CREATOR, f"eyekit {__version__}")
        elif figure_format == "EPS":
            surface = _cairo.PSSurface(output_path, figure_width, figure_height)
            surface.set_eps(True)
        elif figure_format == "SVG":
            surface = _cairo.SVGSurface(output_path, figure_width, figure_height)
        context = _cairo.Context(surface)
        return surface, context

    def _max_text_block_extents(self):
        """

        Calculate the maximum text block extents from all images in the
        figure.

        """
        x_tl, y_tl, x_br, y_br = 999999, 999999, 0, 0
        fallback = None
        for row in self._grid:
            for image in row:
                if isinstance(image, Image) and image._text_extents:
                    if image._text_extents[0] < x_tl:
                        x_tl = image._text_extents[0]
                    if image._text_extents[1] < y_tl:
                        y_tl = image._text_extents[1]
                    if image._text_extents[2] > x_br:
                        x_br = image._text_extents[2]
                    if image._text_extents[3] > y_br:
                        y_br = image._text_extents[3]
                elif isinstance(image, Image):
                    fallback = [0, 0, image.screen_width, image.screen_height]
        if x_tl < x_br:
            return x_tl, y_tl, x_br - x_tl, y_br - y_tl
        if fallback is None:
            raise ValueError(
                "Cannot make figure because no images have been added. Use Figure.add_image()"
            )
        return tuple(fallback)

    def _make_layout(self, figure_width):
        """

        Figure out the layout of the figure, and append all the relevant
        components to the stack for rendering. This needs to be done in two
        steps in order to determine the appropriate figure height.

        """
        layout, components = [], []
        letter_index = 65  # 65 == A, etc...
        text_block_extents = self._max_text_block_extents()
        v_padding = _mm_to_pts(self._v_padding)
        h_padding = _mm_to_pts(self._h_padding)
        e_padding = _mm_to_pts(self._e_padding)
        letter_font = _Font(self._letter_font_face, self._letter_font_size)
        y = e_padding
        for row in self._grid:
            x = e_padding
            tallest_in_row = 0
            caption_count = sum(
                [bool(image._caption) for image in row if isinstance(image, Image)]
            )
            if self._lettering or caption_count > 0:
                # row contains captions, so make some space
                y += self._letter_font_size * 2
            n_cols = len(row)
            cell_width = (
                figure_width - 2 * e_padding - (n_cols - 1) * h_padding
            ) / n_cols
            for image in row:
                if image is None:
                    x += cell_width + h_padding
                    continue
                if self._crop_margin is None:
                    scale = cell_width / image.screen_width
                    cell_height = image.screen_height * scale
                else:
                    scale = (cell_width - self._crop_margin * 2) / text_block_extents[2]
                    cell_height = text_block_extents[3] * scale + self._crop_margin * 2
                if cell_height > tallest_in_row:
                    tallest_in_row = cell_height
                caption_advance = 0
                if self._lettering:
                    letter_prefix = f"({chr(letter_index)}) "
                    arguments = {
                        "x": x,
                        "y": y - self._letter_font_size,
                        "text": letter_prefix,
                        "font": letter_font,
                        "color": (0, 0, 0),
                    }
                    components.append((_draw_text, arguments))
                    caption_advance += letter_font.calculate_width(letter_prefix)
                if image._caption:
                    caption_font = _Font(
                        image._caption_font_face, image._caption_font_size
                    )
                    arguments = {
                        "x": x + caption_advance,
                        "y": y - self._letter_font_size,
                        "text": image._caption,
                        "font": caption_font,
                        "color": (0, 0, 0),
                    }
                    components.append((_draw_text, arguments))
                layout.append((image, x, y, cell_width, cell_height, scale))
                if self._border_width > 0:
                    arguments = {
                        "x": x,
                        "y": y,
                        "width": cell_width,
                        "height": cell_height,
                        "color": self._border_color,
                        "stroke_width": self._border_width,
                        "dashed": False,
                        "fill_color": None,
                    }
                    components.append((_draw_rectangle, arguments))
                x += cell_width + h_padding
                letter_index += 1
            y += tallest_in_row + v_padding
        figure_height = y - (v_padding - e_padding)
        return layout, components, figure_height, text_block_extents

    def _render_background(self, context):
        """

        Render the background color.

        """
        with context:
            context.set_source_rgb(1, 1, 1)
            context.paint()

    def _render_images(self, surface, layout, text_block_extents):
        """

        Render all images. This creates a separate subsurface for each image
        to be rendered to.

        """
        min_x, min_y, max_width, max_height = text_block_extents
        for image, x, y, width, height, scale in layout:
            subsurface = surface.create_for_rectangle(x, y, width, height)
            subsurface.set_device_scale(scale, scale)
            context = _cairo.Context(subsurface)
            if self._crop_margin is not None:
                context.translate(
                    -min_x + self._crop_margin / scale,
                    -min_y + self._crop_margin / scale,
                )
            image._render_to_figure(context, scale)

    def _render_components(self, context, components):
        """

        Render all components in the components stack (functions and function
        arguments that must be called in sequence).

        """
        for func, arguments in components:
            with context:
                func(context, 1, **arguments)

    def _render_to_booklet(self, surface, context, width):
        """

        Render the figure to a booklet page.

        """
        layout, components, height, text_block_extents = self._make_layout(width)
        self._render_background(context)
        self._render_images(surface, layout, text_block_extents)
        self._render_components(context, components)


class Booklet(object):

    """

    The Booklet class is used to combine one or more figures into a multipage
    PDF booklet. The general usage pattern is:

    ```python
    booklet = eyekit.vis.Booklet()
    booklet.add_figure(fig1)
    booklet.add_figure(fig2)
    booklet.save('booklet.pdf')
    ```

    """

    def __init__(self):
        self._figures = []

    def add_figure(self, figure):
        """

        Add a `Figure` to a new page in the booklet.

        """
        if not isinstance(figure, Figure):
            raise TypeError("figure should be of type Figure.")
        self._figures.append(figure)

    def save(self, output_path, width=210, height=297):
        """

        Save the booklet to some `output_path`. Booklets can only be saved as
        .pdf. `width` and `height` determine the millimeter sizing of the
        booklet pages, which defaults to A4 (210x297mm).

        """
        output_path = str(output_path)
        if _splitext(output_path)[1][1:].lower() != "pdf":
            raise ValueError("Books must be saved in PDF format.")
        page_width = _mm_to_pts(width)
        page_height = _mm_to_pts(height)
        surface = _cairo.PDFSurface(output_path, page_width, page_height)
        surface.set_metadata(_cairo.PDF_METADATA_CREATOR, f"eyekit {__version__}")
        context = _cairo.Context(surface)
        for figure in self._figures:
            figure._render_to_booklet(surface, context, page_width)
            surface.show_page()
        surface.finish()


################
# DRAW FUNCTIONS
################


def _draw_line(context, scale, path, color, stroke_width, dashed):
    context.set_source_rgb(*color)
    context.set_line_width(stroke_width / scale)
    context.move_to(*path[0])
    if dashed:
        context.set_dash([10, 4])
    for end_xy in path[1:]:
        context.line_to(*end_xy)
    context.stroke()


def _draw_circle(context, scale, x, y, radius, color, stroke_width, dashed, fill_color):
    context.new_sub_path()  # prevent initial line segment
    context.arc(x, y, radius, 0, 6.283185307179586)
    if fill_color:
        context.set_source_rgb(*fill_color)
        if color and stroke_width:
            context.fill_preserve()
        else:
            context.fill()
    if color and stroke_width:
        context.set_source_rgb(*color)
        context.set_line_width(stroke_width / scale)
        if dashed:
            context.set_dash([12, 4])
        context.stroke()


def _draw_rectangle(
    context, scale, x, y, width, height, color, stroke_width, dashed, fill_color
):
    context.rectangle(x, y, width, height)
    if fill_color:
        context.set_source_rgb(*fill_color)
        if color and stroke_width:
            context.fill_preserve()
        else:
            context.fill()
    if color and stroke_width:
        context.set_source_rgb(*color)
        context.set_line_width(stroke_width / scale)
        if dashed:
            context.set_dash([12, 4])
        context.stroke()


def _draw_text(context, scale, x, y, text, font, color, annotation=False):
    context.set_source_rgb(*color)
    context.set_font_face(font.toy_font_face)
    if annotation:
        context.set_font_size(font.size / scale)
    else:
        context.set_font_size(font.size)
    context.move_to(x, y)
    context.show_text(text)


##################
# HELPER FUNCTIONS
##################


def _duration_to_radius(duration):
    """

    Converts a millisecond duration to a pixel radius for plotting fixation
    circles so that the area of the circle corresponds to duration.

    """
    return (duration / 3.141592653589793) ** 0.5


def _mm_to_pts(mm):
    """

    Convert millimeters to points.

    """
    return mm / (25.4 / 72)


def _color_to_rgb(color):
    """

    Convert a color to RGB values in [0, 1]. Can take an RGB tuple in [0,
    255], a hex triplet, or a named color.

    """
    if isinstance(color, tuple) and len(color) == 3:
        return color[0] / 255, color[1] / 255, color[2] / 255
    if isinstance(color, str) and color[0] == "#":
        r, g, b = tuple(bytes.fromhex(color[1:]))
        return r / 255, g / 255, b / 255
    if color.lower() in _color.colors:
        color = _color.colors[color.lower()]
        return color[0] / 255, color[1] / 255, color[2] / 255
    return 0, 0, 0


def _pseudo_alpha(rgb, opacity):
    """

    Given an RGB value in [0, 1], return a new RGB value which blends in a
    certain amount of white to create a fake alpha effect. This allosws us to
    produce an alpha-like effect in EPS, which doesn't support transparency.

    """
    return tuple([value * opacity - opacity + 1 for value in rgb])
