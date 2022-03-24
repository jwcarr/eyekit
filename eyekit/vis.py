"""
Defines the `Image`, `Figure`, and `Booklet` objects, which are used to create
visualizations.
"""


import re as _re
import pathlib as _pathlib
import cairocffi as _cairo
from . import _color
from . import _font
from .fixation import _is_FixationSequence
from .text import _is_TextBlock, _fail

try:
    from ._version import __version__
except ImportError:
    __version__ = "???"


_FONT_FACE = "Arial"
_FONT_SIZE = 8


def set_default_font(font_face=None, font_size=None):
    """
    Set the default font face and/or size that will be used in figure captions
    and image annotations. This selection can be overridden on a per-image,
    per-figure, or per-annotation basis. If no font is set, Eyekit defaults to
    8pt Arial.
    """
    global _FONT_FACE, _FONT_SIZE
    if font_face is not None:
        _FONT_FACE = str(font_face)
    if font_size is not None:
        _FONT_SIZE = float(font_size)


class Image:

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
        """
        Initialized with:

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
        self._block_extents = None
        self._manual_block_extents = False

    ################
    # PUBLIC METHODS
    ################

    def set_caption(self, caption, *, font_face=None, font_size=None):
        """
        Set the image's caption, which will be shown above the image if you
        place it inside a `Figure`. If no font is set, the default font will
        be used (see `set_default_font`).
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
        self._background_color = _color_to_rgb(color, default=None)

    def set_crop_area(self, rect):
        """
        Crop the final image to a particular rectangular area of the screen.
        `rect` should be a tuple of the form `(x, y, width, height)`
        specifying the crop area (in screen coordinates) or a Box-like
        object, such as a TextBlock or InterestArea. If no crop area is set,
        then it defaults to the maximum extents of all TextBlocks drawn to
        the Image.
        """
        if hasattr(rect, "box"):
            x, y, width, height = rect.box
        else:
            try:
                x, y, width, height = rect
            except Exception as e:
                e.args = (
                    "rect should be a Box-like object (e.g. a TextBlock) or a tuple of the form (x, y, width, height).",
                )
                raise
        self._block_extents = (float(x), float(y), float(x + width), float(y + height))
        self._manual_block_extents = True

    def draw_text_block(self, text_block, *, color=None, mask_text=False):
        """
        Draw a `eyekit.text.TextBlock` on the image. `color` defaults to black
        if unspecified. If `mask_text` is set to `True`, the text will be
        displayed as a series of rectangles, which is useful if you want to
        deemphasize the linguistic content.
        """
        _is_TextBlock(text_block)
        if not self._manual_block_extents:
            self._update_block_extents(text_block)
        if mask_text:
            rgb_color = _color_to_rgb(color, default=(0.8, 0.8, 0.8))
            for word in text_block.words(alphabetical_only=False):
                self._add_component(
                    _draw_rectangle,
                    {
                        "x": word._x_tl,
                        "y": word._y_tl,
                        "width": word._x_br - word._x_tl,
                        "height": word._y_br - word._y_tl,
                        "color": None,
                        "stroke_width": 0,
                        "dashed": False,
                        "fill_color": rgb_color,
                        "opacity": 1,
                    },
                )
        else:
            rgb_color = _color_to_rgb(color, default=(0, 0, 0))
            for line in text_block.lines():
                self._add_component(
                    _draw_text,
                    {
                        "x": line._x_tl,
                        "y": line.baseline,
                        "text": line.display_text,
                        "font": text_block._font,
                        "color": rgb_color,
                        "anchor": None,
                    },
                )

    def draw_fixation_sequence(
        self,
        fixation_sequence,
        *,
        show_saccades=True,
        show_discards=False,
        color="black",
        discard_color="gray",
        saccade_color=None,
        number_fixations=False,
        fixation_radius=None,
        stroke_width=0.5,
        opacity=1,
    ):
        """
        Draw a `eyekit.fixation.FixationSequence` on the image. Optionally,
        you can choose whether or not to display saccade lines and discarded
        fixations. `color`, `discard_color`, and `saccade_color` determine
        the colors of fixations, discarded fixations, and saccade lines
        respectively. If `number_fixations` is `True`, each fixation is
        superimposed with its index. By default, the radius of each fixation
        is calculated as `sqrt(duration/pi)`, such that the area of each
        fixation will correspond to duration. If `fixation_radius` is set to
        a number, all fixations will be rendered at a constant size.
        `stroke_width` controls the thickness of saccade lines. `opacity`
        controls the opacity of fixations. If you want to set the `color` or
        `fixation_radius` of each fixation independently, pass in a function
        that takes a fixation and returns a color. For example, to color code
        fixations that have the tag `special_fixation` you could use a lambda
        function such as

        ```
        color = lambda fxn: 'red' if fxn.has_tag('special_fixation') else 'black'
        ```

        or to base the fixation size on pupil size, you could use:

        ```
        fixation_radius = lambda fxn: (fxn.pupil_size / 3.14159) ** 0.5
        ```
        """
        _is_FixationSequence(fixation_sequence)
        if show_discards:
            seq_iterator = fixation_sequence.iter_with_discards
        else:
            seq_iterator = fixation_sequence.iter_without_discards
        if show_saccades:
            if saccade_color is None and not callable(color):
                saccade_color = color
            rgb_saccade_color = _color_to_rgb(saccade_color, default=(0, 0, 0))
            path = [fixation.xy for fixation in seq_iterator()]
            if path:
                self._add_component(
                    _draw_line,
                    {
                        "path": path,
                        "stroke_width": stroke_width,
                        "color": rgb_saccade_color,
                        "dashed": False,
                        "opacity": 1,
                    },
                )
        if callable(color):
            color_func = color
        else:
            color_func = lambda fxn: discard_color if fxn.discarded else color
        if fixation_radius is None:
            radius_func = lambda fxn: (fxn.duration / 3.141592653589793) ** 0.5
        elif callable(fixation_radius):
            radius_func = fixation_radius
        else:
            radius_func = lambda fxn: fixation_radius
        for fixation in seq_iterator():
            radius = radius_func(fixation)
            rgb_color = _color_to_rgb(color_func(fixation), default=(0, 0, 0))
            self._add_component(
                _draw_circle,
                {
                    "x": fixation.x,
                    "y": fixation.y,
                    "radius": radius,
                    "color": None,
                    "stroke_width": None,
                    "dashed": False,
                    "fill_color": rgb_color,
                    "opacity": opacity,
                },
            )
        if number_fixations:
            number_font = _font.Font(_FONT_FACE, _FONT_SIZE)
            number_y_offset = number_font.calculate_height("0") / 2
            for fixation in seq_iterator():
                self._add_component(
                    _draw_text,
                    {
                        "x": fixation.x,
                        "y": fixation.y + number_y_offset,
                        "text": str(fixation.index),
                        "font": number_font,
                        "color": (1, 1, 1),
                        "anchor": "center",
                    },
                )

    def draw_heatmap(self, text_block, distribution, *, color="red"):
        """
        Draw a `eyekit.text.TextBlock` on the image along with an associated
        distribution, which is represented in heatmap form. This is can be
        used to visualize the output from `eyekit.measure.duration_mass()`.
        `color` determines the color of the heatmap.
        """
        _is_TextBlock(text_block)
        rgb_color = _color_to_rgb(color, default=(1, 0, 0))
        ngram_width = (text_block.n_cols - distribution.shape[1]) + 1
        distribution = distribution / distribution.max()
        subcell_height = text_block.line_height / ngram_width
        level = 0
        for ngram in text_block.ngrams(ngram_width, alphabetical_only=False):
            r, s, _ = ngram.location
            cell_color = _pseudo_alpha(rgb_color, distribution[r, s])
            self._add_component(
                _draw_rectangle,
                {
                    "x": ngram._x_tl,
                    "y": ngram.y_tl + subcell_height * level,
                    "width": ngram._x_br - ngram._x_tl,
                    "height": subcell_height,
                    "stroke_width": None,
                    "color": None,
                    "fill_color": cell_color,
                    "dashed": False,
                    "opacity": 1,
                },
            )
            level += 1
            if level == ngram_width:
                level = 0
        self.draw_text_block(text_block)

    def draw_line(
        self,
        start_xy,
        end_xy,
        *,
        color="black",
        stroke_width=1,
        dashed=False,
        opacity=1,
    ):
        """
        Draw an arbitrary line on the image from `start_xy` to `end_xy`.
        `stroke_width` is set in points for vector output or pixels for PNG
        output. If `dashed` is `True`, the line will have a dashed style (or a
        custom dash pattern can be supplied, e.g. `dashed=(1,2,4,2)`).
        """
        if dashed is True:
            dashed = (10, 4)
        rgb_color = _color_to_rgb(color, default=(0, 0, 0))
        self._add_component(
            _draw_line,
            {
                "path": [start_xy, end_xy],
                "stroke_width": float(stroke_width),
                "color": rgb_color,
                "dashed": dashed,
                "opacity": opacity,
            },
        )

    def draw_circle(
        self,
        xy,
        radius,
        *,
        color=None,
        stroke_width=1,
        dashed=False,
        fill_color=None,
        opacity=1,
    ):
        """
        Draw an arbitrary circle on the image centered at `xy` with some
        `radius`. `stroke_width` is set in points for vector output or pixels
        for PNG output. If `dashed` is `True`, the line will have a dashed
        style (or a custom dash pattern can be supplied, e.g.
        `dashed=(1,2,4,2)`). If no `color` or `fill_color` is provided,
        `color` will default to black. `opacity` controls the opacity of the
        circle's fill color and should be set between 0 (fully transparent)
        and 1 (fully opaque).
        """
        if color is None and fill_color is None:
            color = "black"
        rgb_color = _color_to_rgb(color, default=None)
        rgb_fill_color = _color_to_rgb(fill_color, default=None)
        if dashed is True:
            dashed = (10, 4)
        self._add_component(
            _draw_circle,
            {
                "x": float(xy[0]),
                "y": float(xy[1]),
                "radius": float(radius),
                "color": rgb_color,
                "stroke_width": float(stroke_width),
                "dashed": dashed,
                "fill_color": rgb_fill_color,
                "opacity": float(opacity),
            },
        )

    def draw_rectangle(
        self,
        rect,
        *,
        color=None,
        stroke_width=1,
        dashed=False,
        fill_color=None,
        opacity=1,
    ):
        """
        Draw a rectangle on the image. You can pass in some Box-like object,
        such as an `eyekit.text.InterestArea`, or you can pass a tuple of the
        form (x, y, width, height). `stroke_width` is set in points for vector
        output or pixels for PNG output. If `dashed` is `True`, the line will
        have a dashed style (or a custom dash pattern can be supplied, e.g.
        `dashed=(1,2,4,2)`). If no `color` or `fill_color` is provided,
        `color` will default to black. `opacity` controls the opacity of the
        rectangle's fill color and should be set between 0 (fully transparent)
        and 1 (fully opaque).
        """
        if color is None and fill_color is None:
            color = "black"
        rgb_color = _color_to_rgb(color, default=None)
        rgb_fill_color = _color_to_rgb(fill_color, default=None)
        if dashed is True:
            dashed = (10, 4)
        if hasattr(rect, "box"):
            x, y, width, height = rect.box
        else:
            try:
                assert len(rect) == 4
                x, y, width, height = rect
            except Exception as e:
                e.args = (
                    "rect should be a Box-like object (e.g. an InterestArea) or a tuple of the form (x, y, width, height).",
                )
                raise
        self._add_component(
            _draw_rectangle,
            {
                "x": float(x),
                "y": float(y),
                "width": float(width),
                "height": float(height),
                "color": rgb_color,
                "stroke_width": float(stroke_width),
                "dashed": dashed,
                "fill_color": rgb_fill_color,
                "opacity": float(opacity),
            },
        )

    def draw_annotation(
        self, xy, text, *, font_face=None, font_size=None, color="black", anchor="left"
    ):
        """
        Draw arbitrary text on the image located at `xy`. If no font is set,
        the default font will be used (see `set_default_font`). `font_size` is
        set in points for vector output or pixels for PNG output. `anchor`
        controls how the text is aligned relative to `xy` and may be set to
        `left`, `center`, or `right`.
        """
        if font_face is None:
            font_face = _FONT_FACE
        if font_size is None:
            font_size = _FONT_SIZE
        font = _font.Font(font_face, font_size)
        rgb_color = _color_to_rgb(color, default=(0, 0, 0))
        self._add_component(
            _draw_text,
            {
                "x": float(xy[0]),
                "y": float(xy[1]),
                "text": str(text),
                "font": font,
                "color": rgb_color,
                "anchor": anchor,
                "annotation": True,
            },
        )

    def save(self, output_path, *, width=150, crop_margin=None):
        """
        Save the image to some `output_path`. Images can be saved as .pdf,
        .eps, .svg, or .png. `width` only applies to the vector formats and
        determines the millimeter width of the output file; PNG images are
        saved at actual pixel size. If you set a crop margin, the image will
        be cropped to the size of the `eyekit.text.TextBlock` plus the
        specified margin. Margins are specified in millimeters (PDF, EPS, SVG)
        or pixels (PNG). EPS does not support opacity effects.
        """
        if crop_margin is None and self._manual_block_extents:
            crop_margin = 0
        output_path = _pathlib.Path(output_path)
        if not output_path.parent.exists():
            raise ValueError(f"Path does not exist: {output_path.parent}")
        image_format = output_path.suffix[1:].upper()
        if image_format not in ["PDF", "EPS", "SVG", "PNG"]:
            raise ValueError(
                "Unrecognized format. Use .pdf, .eps, or .svg for vector output, or .png for raster output."
            )
        image_width = _mm_to_pts(width)
        surface, context, scale = self._make_surface(
            str(output_path), image_format, image_width, crop_margin
        )
        self._render_background(context)
        self._render_components(context, scale, image_format == "EPS")
        if image_format == "PNG":
            surface.write_to_png(str(output_path))
        surface.finish()
        if image_format == "SVG":
            _strip_cairo_surface_id_from_SVG(output_path)

    #################
    # PRIVATE METHODS
    #################

    def _update_block_extents(self, text_block):
        """
        Update the Image's block_extents (the most extreme coordinates of all
        TextBlocks that have been drawn), which may be used to crop the Image
        at save time.
        """
        if self._block_extents is None:
            self._block_extents = [
                text_block.x_tl,
                text_block.y_tl,
                text_block.x_br,
                text_block.y_br,
            ]
        else:
            self._block_extents[0] = min(self._block_extents[0], text_block.x_tl)
            self._block_extents[1] = min(self._block_extents[1], text_block.y_tl)
            self._block_extents[2] = max(self._block_extents[2], text_block.x_br)
            self._block_extents[3] = max(self._block_extents[3], text_block.y_br)

    def _add_component(self, func, arguments):
        """
        Add a component to the stack. This should be a draw_ function and its
        arguments. This function will be called with its arguments at save
        time.
        """
        self._components.append((func, arguments))

    def _make_surface(self, output_path, image_format, image_width, crop_margin):
        """
        Make the relevant Cairo surface and context with appropriate sizing.
        """
        if image_format == "PNG":
            surface = self._make_raster_surface(image_width, crop_margin)
            scale = 1
        else:
            surface, scale, crop_margin = self._make_vector_surface(
                output_path, image_format, image_width, crop_margin
            )
        context = _cairo.Context(surface)
        if crop_margin is not None:
            crop_margin = crop_margin / scale
            context.translate(
                -self._block_extents[0] + crop_margin,
                -self._block_extents[1] + crop_margin,
            )
        return surface, context, scale

    def _make_raster_surface(self, image_width, crop_margin):
        """
        Make a PNGSurface at the appropriate size depending on whether or not
        there is a crop margin. In a raster image, 1 screen pixel = 1 image
        pixel.
        """
        if crop_margin is None:
            image_width = self.screen_width
            image_height = self.screen_height
        else:
            image_width = int(
                (self._block_extents[2] - self._block_extents[0]) + crop_margin * 2
            )
            image_height = int(
                (self._block_extents[3] - self._block_extents[1]) + crop_margin * 2
            )
        return _cairo.ImageSurface(_cairo.FORMAT_ARGB32, image_width, image_height)

    def _make_vector_surface(self, output_path, image_format, image_width, crop_margin):
        """
        Make a vector surface in the appropriate format and with the
        appropriate size depending on whether or not there is a crop margin.
        In a vector image, 1 screen pixel is scaled to a certain number of
        points, such that the figure as a whole will conform to a certain
        physical size.
        """
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
                self._block_extents[2] - self._block_extents[0]
            )
            image_height = (
                self._block_extents[3] - self._block_extents[1]
            ) * scale + crop_margin * 2
        if image_format == "PDF":
            surface = _cairo.PDFSurface(output_path, image_width, image_height)
            surface.set_metadata(_cairo.PDF_METADATA_CREATOR, f"eyekit {__version__}")
        elif image_format == "EPS":
            surface = _cairo.PSSurface(output_path, image_width, image_height)
            surface.set_eps(True)
        elif image_format == "SVG":
            surface = _cairo.SVGSurface(output_path, image_width, image_height)
        surface.set_device_scale(scale, scale)
        return surface, scale, crop_margin

    def _render_background(self, context):
        """
        Render the background color.
        """
        if self._background_color is not None:
            with context:
                context.set_source_rgb(*self._background_color)
                context.paint()

    def _render_components(self, context, scale, eps):
        """
        Render all components in the components stack (functions and function
        arguments that must be called in sequence).
        """
        for func, arguments in self._components:
            if eps and "opacity" in arguments and arguments["opacity"] < 1:
                arguments = arguments.copy()
                arguments["opacity"] = 1  # do not allow EPS files to have opacity < 1
            with context:
                func(context, scale, **arguments)

    def _render_to_figure(self, context, scale, eps):
        """
        Render the image to a figure panel.
        """
        self._render_background(context)
        self._render_components(context, scale, eps)


class Figure:

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
        """
        Initialized with:

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
        self._enum_style = "(<A>)"
        self._enum_face = _FONT_FACE + " bold"
        self._enum_size = _FONT_SIZE
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

    def set_border_style(self, *, stroke_width=None, color=None):
        """
        Set the thickness and color of the image borders. By default, image
        border are 1pt black.
        """
        if stroke_width is not None:
            self._border_width = float(stroke_width)
        if color is not None:
            self._border_color = _color_to_rgb(color, default=(0, 0, 0))

    def set_enumeration(self, style=None, *, font_face=None, font_size=None):
        """
        By default, each image caption is prefixed with a letter in
        parentheses: **(A)**, **(B)**, **(C)**, etc. If you want to turn this
        off, call ```Figure.set_enumeration(False)``` prior to saving. You can
        also specify a custom style using the `<A>`, `<a>`, or `<1>` tags; for
        example ```Figure.set_enumeration('[<1>]')``` will result in **[1]**,
        **[2]**, **[3]** etc. If no font is set, the default font will be used
        (see `set_default_font`).
        """
        if style is not None:
            if style is False:
                self._enum_style = False
            elif isinstance(style, str):
                if "<A>" in style or "<a>" in style or "<1>" in style:
                    self._enum_style = style
                else:
                    raise ValueError("Enumeration style must contain <A>, <a>, or <1>.")
            else:
                raise ValueError(
                    "Enumeration style must be a string containing <A>, <a>, or <1>."
                )
        if font_face is not None:
            self._enum_face = str(font_face)
        if font_size is not None:
            self._enum_size = float(font_size)

    def set_padding(self, *, vertical=None, horizontal=None, edge=None):
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

    def add_image(self, image, *, row=None, col=None):
        """
        Add an `Image` to the figure. If a row and column index is specified,
        the image is placed in that position. Otherwise, `image` is placed in
        the next available position.
        """
        if not isinstance(image, Image):
            _fail(image, "Image")
        if row is None or col is None:
            row, col = self._next_available_cell(row, col)
        if row >= self._n_rows or col >= self._n_cols:
            raise ValueError("Row or column index is not inside the grid.")
        self._grid[row][col] = image

    def save(self, output_path, *, width=150):
        """
        Save the figure to some `output_path`. Figures can be saved as .pdf,
        .eps, or .svg. `width` determines the millimeter width of the output
        file. EPS does not support opacity effects.
        """
        output_path = _pathlib.Path(output_path)
        if not output_path.parent.exists():
            raise ValueError(f"Path does not exist: {output_path.parent}")
        figure_format = output_path.suffix[1:].upper()
        if figure_format not in ["PDF", "EPS", "SVG"]:
            raise ValueError("Unrecognized format. Use .pdf, .eps, or .svg.")
        figure_width = _mm_to_pts(width)
        layout, components, height, text_block_extents = self._make_layout(figure_width)
        surface, context = self._make_surface(
            str(output_path), figure_format, figure_width, height
        )
        self._render_background(context)
        self._render_images(surface, layout, text_block_extents, figure_format == "EPS")
        self._render_components(context, components, figure_format == "EPS")
        surface.finish()
        if figure_format == "SVG":
            _strip_cairo_surface_id_from_SVG(output_path)

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
                if isinstance(image, Image) and image._block_extents:
                    if image._block_extents[0] < x_tl:
                        x_tl = image._block_extents[0]
                    if image._block_extents[1] < y_tl:
                        y_tl = image._block_extents[1]
                    if image._block_extents[2] > x_br:
                        x_br = image._block_extents[2]
                    if image._block_extents[3] > y_br:
                        y_br = image._block_extents[3]
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
        text_block_extents = self._max_text_block_extents()
        v_padding = _mm_to_pts(self._v_padding)
        h_padding = _mm_to_pts(self._h_padding)
        e_padding = _mm_to_pts(self._e_padding)
        enum_font = _font.Font(self._enum_face, self._enum_size)
        caption_padding = enum_font.get_descent() + 4
        enum_i = 1
        y = e_padding

        # ITERATE OVER ROWS IN THE GRID
        for row in self._grid:

            x = e_padding
            tallest_in_row = 0
            caption_count = sum(
                [bool(image._caption) for image in row if isinstance(image, Image)]
            )
            if self._enum_style or caption_count > 0:
                # row contains captions, so make some space
                y += self._enum_size + 4
            n_cols = len(row)
            cell_width = (
                figure_width - 2 * e_padding - (n_cols - 1) * h_padding
            ) / n_cols

            # ITERATE OVER COLUMNS IN THE ROW
            for image in row:

                if image is None:
                    x += cell_width + h_padding
                    continue

                # CALCULATE CELL HEIGHT AND SCALE
                if self._crop_margin is None:
                    scale = cell_width / image.screen_width
                    cell_height = image.screen_height * scale
                else:
                    scale = (cell_width - self._crop_margin * 2) / text_block_extents[2]
                    cell_height = text_block_extents[3] * scale + self._crop_margin * 2
                if cell_height > tallest_in_row:
                    tallest_in_row = cell_height

                # ADD THE IMAGE TO LAYOUT WITH ITS POSITION AND SCALE INFO
                layout.append((image, x, y, cell_width, cell_height, scale))

                # DISPLAY THE ENUMERATION NUMBER, IF REQUESTED
                caption_advance = 0
                if self._enum_style:
                    if "<A>" in self._enum_style:
                        enum = self._enum_style.replace("<A>", chr(enum_i + 64)) + " "
                    elif "<a>" in self._enum_style:
                        enum = (
                            self._enum_style.replace("<a>", chr(enum_i + 64).lower())
                            + " "
                        )
                    elif "<1>" in self._enum_style:
                        enum = self._enum_style.replace("<1>", str(enum_i)) + " "
                    components.append(
                        (
                            _draw_text,
                            {
                                "x": x,
                                "y": y - caption_padding,
                                "text": enum,
                                "font": enum_font,
                                "color": (0, 0, 0),
                                "anchor": "left",
                            },
                        )
                    )
                    caption_advance += enum_font.calculate_width(enum)

                # DISPLAY THE CAPTION, IF REQUESTED
                if image._caption:
                    caption_font = _font.Font(
                        image._caption_font_face, image._caption_font_size
                    )
                    components.append(
                        (
                            _draw_text,
                            {
                                "x": x + caption_advance,
                                "y": y - caption_padding,
                                "text": image._caption,
                                "font": caption_font,
                                "color": (0, 0, 0),
                                "anchor": "left",
                            },
                        )
                    )

                # Display the image border, if requested
                if self._border_width > 0:
                    components.append(
                        (
                            _draw_rectangle,
                            {
                                "x": x,
                                "y": y,
                                "width": cell_width,
                                "height": cell_height,
                                "color": self._border_color,
                                "stroke_width": self._border_width,
                                "dashed": False,
                                "fill_color": None,
                                "opacity": 1,
                            },
                        )
                    )

                x += cell_width + h_padding
                enum_i += 1
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

    def _render_images(self, surface, layout, text_block_extents, eps):
        """
        Render all images. This creates a separate subsurface for each image
        to be rendered to.
        """
        for image, x, y, width, height, scale in layout:
            # create_for_rectangle() requires x and y to be in full device
            # units, and it always rounds the values up. Instead we will round
            # to nearest to ameliorate the awkward positioning of the image
            # within its border. This is still not ideal because the image
            # will not be perfectly centered in the border, but rounding the
            # border position as well results in inconsistencies in the
            # padding between panels, which is more noticeable.
            subsurface = surface.create_for_rectangle(round(x), round(y), width, height)
            subsurface.set_device_scale(scale, scale)
            context = _cairo.Context(subsurface)
            if self._crop_margin is not None:
                context.translate(
                    -text_block_extents[0] + self._crop_margin / scale,
                    -text_block_extents[1] + self._crop_margin / scale,
                )
            image._render_to_figure(context, scale, eps)

    def _render_components(self, context, components, eps):
        """
        Render all components in the components stack (functions and function
        arguments that must be called in sequence).
        """
        for func, arguments in components:
            if eps and "opacity" in arguments and arguments["opacity"] < 1:
                arguments = arguments.copy()
                arguments["opacity"] = 1  # do not allow EPS files to have opacity < 1
            with context:
                func(context, 1, **arguments)

    def _render_to_booklet(self, surface, context, width):
        """
        Render the figure to a booklet page.
        """
        layout, components, _, text_block_extents = self._make_layout(width)
        self._render_background(context)
        self._render_images(surface, layout, text_block_extents, False)
        self._render_components(context, components, False)


class Booklet:

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
            _fail(figure, "Figure")
        self._figures.append(figure)

    def save(self, output_path, *, width=210, height=297):
        """
        Save the booklet to some `output_path`. Booklets can only be saved as
        .pdf. `width` and `height` determine the millimeter sizing of the
        booklet pages, which defaults to A4 (210x297mm).
        """
        output_path = _pathlib.Path(output_path)
        if not output_path.parent.exists():
            raise ValueError(f"Path does not exist: {output_path.parent}")
        if output_path.suffix[1:].upper() != "PDF":
            raise ValueError("Books must be saved in PDF format.")
        page_width = _mm_to_pts(width)
        page_height = _mm_to_pts(height)
        surface = _cairo.PDFSurface(str(output_path), page_width, page_height)
        surface.set_metadata(_cairo.PDF_METADATA_CREATOR, f"eyekit {__version__}")
        context = _cairo.Context(surface)
        for figure in self._figures:
            figure._render_to_booklet(surface, context, page_width)
            surface.show_page()
        surface.finish()


################
# DRAW FUNCTIONS
################


def _draw_line(context, scale, path, color, stroke_width, dashed, opacity):
    context.set_source_rgba(*color, opacity)
    context.set_line_width(stroke_width / scale)
    context.set_line_join(_cairo.LINE_JOIN_ROUND)
    context.set_line_cap(_cairo.LINE_CAP_ROUND)
    if dashed:
        context.set_dash(dashed)
    context.move_to(*path[0])
    for end_xy in path[1:]:
        context.line_to(*end_xy)
    context.stroke()


def _draw_circle(
    context,
    scale,
    x,
    y,
    radius,
    color,
    stroke_width,
    dashed,
    fill_color,
    opacity,
):
    context.new_sub_path()  # prevent initial line segment
    context.arc(x, y, radius, 0, 6.283185307179586)
    if fill_color:
        context.set_source_rgba(*fill_color, opacity)
        if color and stroke_width:
            context.fill_preserve()
        else:
            context.fill()
    if color and stroke_width:
        context.set_source_rgb(*color)
        context.set_line_width(stroke_width / scale)
        if dashed:
            context.set_dash(dashed)
        context.stroke()


def _draw_rectangle(
    context,
    scale,
    x,
    y,
    width,
    height,
    color,
    stroke_width,
    dashed,
    fill_color,
    opacity,
):
    context.rectangle(x, y, width, height)
    if fill_color:
        context.set_source_rgba(*fill_color, opacity)
        if color and stroke_width:
            context.fill_preserve()
        else:
            context.fill()
    if color and stroke_width:
        context.set_source_rgb(*color)
        context.set_line_width(stroke_width / scale)
        context.set_line_join(_cairo.LINE_JOIN_ROUND)
        if dashed:
            context.set_dash(dashed)
        context.stroke()


def _draw_text(context, scale, x, y, text, font, color, anchor, annotation=False):
    context.set_source_rgb(*color)
    context.set_font_face(font.toy_font_face)
    if annotation:
        text_width = font.calculate_width(text) / scale
        context.set_font_size(font.size / scale)
    else:
        text_width = font.calculate_width(text)
        context.set_font_size(font.size)
    if anchor == "center":
        x -= text_width / 2
    elif anchor == "right":
        x -= text_width
    context.move_to(x, y)
    context.show_text(text)


##################
# HELPER FUNCTIONS
##################


def _mm_to_pts(mm):
    """
    Convert millimeters to points.
    """
    return mm / (25.4 / 72)


def _color_to_rgb(color, default=(0, 0, 0)):
    """
    Convert a color to RGB values in [0, 1]. Can take an RGB tuple in [0,
    255], a hex triplet, or a named color. If the color cannot be interpreted,
    the passed-in default is returned.
    """
    if color is not None:
        if isinstance(color, str):
            color = color.lower()
            if color in _color.colors:
                r, g, b = _color.colors[color]
                return r / 255, g / 255, b / 255
            if color.startswith("#") and len(color) == 7:
                r, g, b = tuple(bytes.fromhex(color[1:]))
                return r / 255, g / 255, b / 255
        try:
            if len(color) == 3:
                return color[0] / 255, color[1] / 255, color[2] / 255
        except Exception:
            pass
    return default


def _pseudo_alpha(rgb, opacity):
    """
    Given an RGB value in [0, 1], return a new RGB value which blends in a
    certain amount of white to create a fake alpha effect. This allosws us to
    produce an alpha-like effect in EPS, which doesn't support transparency.
    """
    return tuple((value * opacity - opacity + 1 for value in rgb))


def _strip_cairo_surface_id_from_SVG(output_path):
    """
    Cairo's SVG output includes a random ID number in the global <g> tag.
    Remove this ID to produce deterministic SVG output.
    """
    with open(output_path, "r") as file:
        file_content = file.read()
    file_content = _re.sub(r'<g id="surface.+?">', "<g>", file_content)
    with open(output_path, "w") as file:
        file.write(file_content)
