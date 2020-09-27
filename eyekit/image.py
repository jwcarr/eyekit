'''

Defines the `Image` and `Figure` objects, which are used to create visualizations.

'''


from os import path as _path
import cairocffi as _cairo
from . import _color


class Image(object):

	'''

	The Image class is used to create visualizations of text blocks and fixation
	sequences, and it provides methods for drawing various kinds of annotation.
	The general usage pattern is:

	```python
	img = eyekit.Image(1920, 1080)
	img.draw_text_block(txt)
	img.draw_fixation_sequence(seq)
	img.save('image.pdf')
	```

	'''

	def __init__(self, screen_width: int, screen_height: int):
		'''Initialized with:
		
		- `screen_width` Width of the screen in pixels.
		- `screen_height` Height of the screen in pixels.
		'''
		self.screen_width = int(screen_width)
		self.screen_height = int(screen_height)
		self._caption = None
		self._background_color = (1, 1, 1)
		self._components = []
		self._text_extents = None

	################
	# PUBLIC METHODS
	################

	def set_caption(self, caption):
		'''

		Set the image's caption, which will be shown above the image if you place it
		inside a `Figure`.

		'''
		self._caption = str(caption)

	def set_background_color(self, color):
		'''

		Set the background color of the image. By default the background color is
		white.

		'''
		self._background_color = _color_to_rgb(color)

	def draw_text_block(self, text_block, color='black'):
		'''

		Draw a `eyekit.text.TextBlock` on the image. `color` sets the color of the
		text.

		'''
		if self._text_extents is None:
			self._text_extents = [text_block.x_tl, text_block.y_tl, text_block.x_br, text_block.y_br]
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
			arguments = {'x':line.x_tl, 'y':line.baseline, 'text':line.text, 'font_face':text_block.font_face, 'font_size':text_block.font_size, 'color':rgb_color}
			self._add_component(_draw_text, arguments)

	def draw_text_block_heatmap(self, text_block, distribution, color='red'):
		'''

		Draw a `eyekit.text.TextBlock` on the image along with an associated
		distribution, which is represented in heatmap form. This is can be used to
		visualize the output from `eyekit.analysis.duration_mass()`. `color`
		determines the color of the heatmap.

		'''
		rgb_color = _color_to_rgb(color)
		n = (text_block.n_cols - distribution.shape[1]) + 1
		distribution /= distribution.max()
		subcell_height = text_block.line_height / n
		levels = [subcell_height*i for i in range(n)]
		level = 0
		for ngram in text_block.ngrams(n):
			r, s, e = ngram.id.split(':')
			if level == n:
				level = 0
			p = distribution[(int(r), int(s))]
			cell_color = _pseudo_alpha(rgb_color, opacity=p)
			arguments = {'x':ngram.x_tl, 'y':ngram.y_tl+subcell_height*level, 'width':ngram.width, 'height':subcell_height, 'stroke_width':None, 'color':None, 'fill_color':cell_color, 'dashed':False}
			self._add_component(_draw_rectangle, arguments)
			level += 1
		start_x = text_block.x_tl
		end_x = text_block.x_br
		for line_n, line in enumerate(text_block.lines()):
			if line_n == 0:
				continue
			y = line.y_tl
		self.draw_text_block(text_block)

	def draw_fixation_sequence(self, fixation_sequence, show_saccades=True, show_discards=False, color='black', discard_color='gray', number_fixations=False):
		'''

		Draw a `eyekit.fixation.FixationSequence` on the image. Optionally, you can
		choose whether or not to display saccade lines and discarded fixations, and
		which colors to use. `number_fixations` is not yet implemented.

		'''
		rgb_color = _color_to_rgb(color)
		rgb_discard_color = _color_to_rgb(discard_color)
		if show_discards:
			if show_saccades:
				path = [fixation.xy for fixation in fixation_sequence.iter_with_discards()]
				self._add_component(_draw_line, {'path':path, 'stroke_width':0.5, 'color':rgb_color, 'dashed':False})
			for fixation in fixation_sequence.iter_with_discards():
				f_color = rgb_discard_color if fixation.discarded else rgb_color
				arguments = {'x':fixation.x, 'y':fixation.y, 'radius':_duration_to_radius(fixation.duration), 'color':None, 'stroke_width':None, 'dashed':False, 'fill_color':f_color}
				self._add_component(_draw_circle, arguments)
		else:
			if show_saccades:
				path = [fixation.xy for fixation in fixation_sequence.iter_without_discards()]
				self._add_component(_draw_line, {'path':path, 'stroke_width':0.5, 'color':rgb_color, 'dashed':False})
			for fixation in fixation_sequence.iter_without_discards():
				arguments = {'x':fixation.x, 'y':fixation.y, 'radius':_duration_to_radius(fixation.duration), 'color':None, 'stroke_width':None, 'dashed':False, 'fill_color':rgb_color}
				self._add_component(_draw_circle, arguments)

	def draw_sequence_comparison(self, reference_sequence, fixation_sequence, color_match='black', color_mismatch='red'):
		'''

		Draw a `eyekit.fixation.FixationSequence` on the image with the fixations
		colored according to whether or not they match a reference sequence in terms
		of the y-coordinate. This is mostly useful for comparing the outputs of two
		different drift correction algorithms.

		'''
		rgb_color_match = _color_to_rgb(color_match)
		rgb_color_mismatch = _color_to_rgb(color_mismatch)
		path = [fixation.xy for fixation in fixation_sequence.iter_with_discards()]
		self._add_component(_draw_line, {'path':path, 'stroke_width':0.5, 'color':rgb_color_match, 'dashed':False})
		for reference_fixation, fixation in zip(reference_sequence.iter_with_discards(), fixation_sequence.iter_with_discards()):
			color = rgb_color_match if reference_fixation.y == fixation.y else rgb_color_mismatch
			arguments = {'x':fixation.x, 'y':fixation.y, 'radius':_duration_to_radius(fixation.duration), 'color':None, 'stroke_width':None, 'dashed':False, 'fill_color':color}
			self._add_component(_draw_circle, arguments)

	def draw_line(self, start_xy, end_xy, color='black', stroke_width=1, dashed=False):
		'''

		Draw an arbitrary line on the image from `start_xy` to `end_xy`.
		`stroke_width` is set in points for vector output or pixels for PNG output.

		'''
		rgb_color = _color_to_rgb(color)
		arguments = {'path':[start_xy, end_xy], 'stroke_width':stroke_width, 'color':rgb_color, 'dashed':dashed}
		self._add_component(_draw_line, arguments)

	def draw_circle(self, x, y, radius, color='black', stroke_width=1, dashed=False, fill_color=None):
		'''

		Draw an arbitrary circle on the image centered at `x`, `y` and with some
		`radius`. `stroke_width` is set in points for vector output or pixels for
		PNG output.

		'''
		rgb_color = _color_to_rgb(color) if color else None
		rgb_fill_color = _color_to_rgb(fill_color) if fill_color else None
		arguments = {'x':x, 'y':y, 'radius':radius, 'color':rgb_color, 'stroke_width':stroke_width, 'dashed':dashed, 'fill_color':rgb_fill_color}
		self._add_component(_draw_circle, arguments)

	def draw_rectangle(self, rect, y=None, width=None, height=None, color='black', stroke_width=1, dashed=False, fill_color=None):
		'''

		Draw an arbitrary rectangle on the image. `rect` should be a tuple
		specifying x, y, width, and height, or these four values can be passed in
		separately as the first four arguments. `stroke_width` is set in points for
		vector output or pixels for PNG output.

		'''
		rgb_color = _color_to_rgb(color) if color else None
		rgb_fill_color = _color_to_rgb(fill_color) if fill_color else None
		if isinstance(rect, tuple) and len(rect) == 4:
			x, y, width, height = rect
		else:
			x = rect
		arguments = {'x':x, 'y':y, 'width':width, 'height':height, 'color':rgb_color, 'stroke_width':stroke_width, 'dashed':dashed, 'fill_color':rgb_fill_color}
		self._add_component(_draw_rectangle, arguments)

	def draw_annotation(self, x, y, text, font_face='Arial', font_size=8, color='black'):
		'''

		Draw arbitrary text on the image located at `x`, `y`. `font_size` is set in
		points for vector output or pixels for PNG output.

		'''
		rgb_color = _color_to_rgb(color)
		arguments = {'x':x, 'y':y, 'text':text, 'font_face':font_face, 'font_size':font_size, 'color':rgb_color, 'annotation':True}
		self._add_component(_draw_text, arguments)

	def save(self, output_path, width=150, crop_margin=None):
		'''

		Save the image to some `output_path`. Images can be saved as .pdf, .eps,
		.svg, or .png. `width` only applies to the vector formats and determines the
		millimeter width of the output file; PNG images are saved at actual pixel
		size. If you set a crop margin, the image will be cropped to the size of the
		`eyekit.text.TextBlock` plus the specified margin. Margins are specified in
		millimeters (PDF, EPS, SVG) or pixels (PNG).

		'''
		image_format = _path.splitext(output_path)[1][1:].upper()
		if image_format not in ['PDF', 'EPS', 'SVG', 'PNG']:
			raise ValueError('Unrecognized format. Use .pdf, .eps, or .svg for vector output, or .png for raster output.')
		image_width = _mm_to_pts(width)
		surface, context, scale = self._make_surface(output_path, image_format, image_width, crop_margin)
		self._render_background(context)
		self._render_components(context, scale)
		if image_format == 'PNG':
			surface.write_to_png(output_path)
		surface.finish()

	#################
	# PRIVATE METHODS
	#################

	def _make_surface(self, output_path, image_format, image_width, crop_margin):
		text_width = self._text_extents[2] - self._text_extents[0]
		text_height = self._text_extents[3] - self._text_extents[1]
		if image_format == 'PNG':
			scale = 1
			if crop_margin is None:
				image_width = self.screen_width
				image_height = self.screen_height
			else:
				image_width = text_width + crop_margin*2
				image_height = text_height + crop_margin*2
			surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, int(image_width), int(image_height))
		else:
			if crop_margin is None:
				scale = image_width / self.screen_width
				image_height = self.screen_height * scale
			else:
				crop_margin = _mm_to_pts(crop_margin)
				if crop_margin > image_width / 3:
					raise ValueError('The crop margin set on this image is too large for the image width. Increase the image width or decrease the crop margin.')
				scale = (image_width - crop_margin*2) / text_width
				image_height = text_height * scale + crop_margin*2
			if image_format == 'PDF':
				surface = _cairo.PDFSurface(output_path, image_width, image_height)
			elif image_format == 'EPS':
				surface = _cairo.PSSurface(output_path, image_width, image_height)
				surface.set_eps(True) # encapsulate postscript file
			elif image_format == 'SVG':
				surface = _cairo.SVGSurface(output_path, image_width, image_height)
			surface.set_device_scale(scale, scale)
		context = _cairo.Context(surface)
		if crop_margin is not None:
			crop_margin = crop_margin / scale
			context.translate(-self._text_extents[0]+crop_margin, -self._text_extents[1]+crop_margin)
		return surface, context, scale

	def _add_component(self, func, arguments):
		self._components.append((func, arguments))

	def _render_background(self, context):
		with context:
			context.set_source_rgb(*self._background_color)
			context.paint()

	def _render_components(self, context, scale):
		for func, arguments in self._components:
			with context:
				func(context, scale, **arguments)

	def _render_to_subsurface(self, context, scale):
		self._render_background(context)
		self._render_components(context, scale)


class Figure(object):

	'''

	The Figure class is used to combine one or more images into a
	publication-ready figure. The general usage pattern is:

	```python
	fig = eyekit.Figure(1, 2)
	fig.add_image(img1)
	fig.add_image(img2)
	fig.save('figure.pdf')
	```

	'''

	def __init__(self, n_rows: int=1, n_cols: int=1):
		'''Initialized with:
		
		- `n_rows` Number of rows in the figure.
		- `n_cols` Number of columns in the figure.
		'''
		self._n_rows = int(n_rows)
		if self._n_rows <= 0:
			raise ValueError('Invalid number of rows')
		self._n_cols = int(n_cols)
		if self._n_rows <= 0:
			raise ValueError('Invalid number of columns')
		self._grid = [[None]*self._n_cols for _ in range(self._n_rows)]
		self._font_face = 'Arial'
		self._font_size = 8
		self._v_padding = 4
		self._h_padding = 4
		self._e_padding = 1
		self._auto_letter = True

	################
	# PUBLIC METHODS
	################

	def set_caption_font(self, font_face=None, font_size=None):
		'''

		Set the font face and size of image captions. By default, captions are set
		in 8pt Arial.

		'''
		if font_face is not None:
			self._font_face = str(font_face)
		if font_size is not None:
			self._font_size = float(font_size)

	def set_padding(self, vertical=None, horizontal=None, edge=None):
		'''

		Set the vertical or horizontal padding between images or the padding around
		the edge of the figure. Padding is expressed in millimeters. By default, the
		vertical and horizontal padding between images is 4mm and the edge padding
		is 1mm.

		'''
		if vertical is not None:
			self._v_padding = float(vertical)
		if horizontal is not None:
			self._h_padding = float(horizontal)
		if edge is not None:
			self._e_padding = float(edge)

	def set_auto_letter(self, auto_letter=True):
		'''

		By default, each image caption is prefixed with a letter, **(A)**, **(B)**,
		**(C)**, etc. If you want to turn this off, call
		```Figure.set_auto_letter(False)``` prior to saving.

		'''
		self._auto_letter = bool(auto_letter)

	def add_image(self, image, row=None, col=None):
		'''

		Add an `Image` to the `Figure`. If a row and column index is specified, the
		image is placed in that position. Otherwise, `image` is placed in the next
		available position.

		'''
		if not isinstance(image, Image):
			raise TypeError('image should be of type Image.')
		if row is None or col is None:
			row, col = self._next_available_cell(row, col)
		if row >= self._n_rows or col >= self._n_cols:
			raise ValueError('Row or column index is not inside the grid.')
		self._grid[row][col] = image

	def save(self, output_path, width=150, crop_margin=None):
		'''

		Save the figure to some `output_path`. Figures can be saved as .pdf, .eps,
		or .svg. `width` determines the millimeter width of the output file. If you
		set a crop margin, each image in the figure will be cropped to the size and
		positioning of the most extreme text block extents, plus the specified
		margin. This has the effect of zooming in to all images in a consistent way
		– maintaining the aspect ratio and relative positioning of the text blocks
		across images. Margins are specified in figure millimeters.

		'''
		figure_format = _path.splitext(output_path)[1][1:].upper()
		if figure_format not in ['PDF', 'EPS', 'SVG']:
			raise ValueError('Unrecognized format. Use .pdf, .eps, or .svg.')
		figure_width = _mm_to_pts(width)
		if crop_margin is not None:
			crop_margin = _mm_to_pts(crop_margin)
		layout, components, height, text_block_extents = self._make_layout(figure_width, crop_margin)
		surface, context = self._make_surface(output_path, figure_format, figure_width, height)
		self._render_background(context)
		self._render_images(surface, layout, text_block_extents, crop_margin)
		self._render_components(context, components)

	#################
	# PRIVATE METHODS
	#################

	def _next_available_cell(self, row_i=None, col_i=None):
		for i, row in enumerate(self._grid):
			if row_i is not None and row_i != i:
				continue
			for j, cell in enumerate(row):
				if col_i is not None and col_i != j:
					continue
				if cell is None:
					return i, j
		raise ValueError('Cannot add image to the figure because there are no available positions. Make a new Figure with more rows or columns, or specify a specific row and column index to overwrite the image that is currently in that position.')

	def _make_surface(self, output_path, figure_format, figure_width, figure_height):
		if figure_format == 'PDF':
			surface = _cairo.PDFSurface(output_path, figure_width, figure_height)
		elif figure_format == 'EPS':
			surface = _cairo.PSSurface(output_path, figure_width, figure_height)
			surface.set_eps(True) # encapsulate postscript file
		elif figure_format == 'SVG':
			surface = _cairo.SVGSurface(output_path, figure_width, figure_height)
		context = _cairo.Context(surface)
		return surface, context

	def _max_text_block_extents(self):
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
			return x_tl, y_tl, x_br-x_tl, y_br-y_tl
		if fallback is None:
			raise ValueError('Cannot make figure because no images have been added. Use Figure.add_image()')
		return tuple(fallback)

	def _make_layout(self, figure_width, crop_margin):
		layout, components = [], []
		letter_index = 65 # 65 == A, etc...
		text_block_extents = self._max_text_block_extents()
		v_padding = _mm_to_pts(self._v_padding)
		h_padding = _mm_to_pts(self._h_padding)
		e_padding = _mm_to_pts(self._e_padding)
		y = e_padding
		for row in self._grid:
			x = e_padding
			tallest_in_row = 0
			if self._auto_letter or sum([bool(image._caption) for image in row if isinstance(image, Image)]):
				y += self._font_size + 8 # row contains captions, so make some space
			n_cols = len(row)
			cell_width = (figure_width - 2 * e_padding - (n_cols-1) * h_padding) / n_cols
			for image in row:
				if image is None:
					x += cell_width + h_padding
					continue
				if crop_margin is None:
					scale = cell_width / image.screen_width
					aspect_ratio = image.screen_width / image.screen_height
				else:
					scale = (cell_width - crop_margin*2) / text_block_extents[2]
					aspect_ratio = text_block_extents[2] / text_block_extents[3]
				cell_height = cell_width / aspect_ratio
				if cell_height > tallest_in_row:
					tallest_in_row = cell_height
				letter = None
				caption = None
				if self._auto_letter:
					letter = chr(letter_index)
				if image._caption:
					caption = image._caption
				if letter or caption:
					arguments = {'x':x, 'y':y-8, 'letter':letter, 'caption':caption, 'font_face':self._font_face, 'font_size':self._font_size, 'color':(0, 0, 0)}
					components.append((_draw_caption, arguments))
				layout.append((image, x, y, cell_width, cell_height, scale))
				arguments = {'x':x, 'y':y, 'width':cell_width, 'height':cell_height, 'color':(0,0,0), 'stroke_width':1, 'dashed':False, 'fill_color':None}
				components.append((_draw_rectangle, arguments))
				x += cell_width + h_padding
				letter_index += 1
			y += tallest_in_row + v_padding
		figure_height = y - (v_padding - e_padding)
		return layout, components, figure_height, text_block_extents

	def _render_background(self, context):
		with context:
			context.set_source_rgb(1, 1, 1)
			context.paint()

	def _render_images(self, surface, layout, text_block_extents, crop_margin):
		min_x, min_y, max_width, max_height = text_block_extents
		aspect_ratio = max_width/max_height
		for image, x, y, width, height, scale in layout:
			subsurface = surface.create_for_rectangle(x, y, width, height)
			subsurface.set_device_scale(scale, scale)
			context = _cairo.Context(subsurface)
			if crop_margin is not None:
				context.translate(-min_x+crop_margin/scale, -min_y+crop_margin/(scale*aspect_ratio))
			image._render_to_subsurface(context, 1)

	def _render_components(self, context, components):
		for func, arguments in components:
			with context:
				func(context, 1, **arguments)


################
# DRAW FUNCTIONS
################

def _draw_line(context, scale, path, color, stroke_width, dashed):
	context.set_source_rgb(*color)
	context.set_line_width(stroke_width / scale)
	context.move_to(*path[0])
	if dashed:
		context.set_dash([10,4])
	for end_xy in path[1:]:
		context.line_to(*end_xy)
	context.stroke()

def _draw_circle(context, scale, x, y, radius, color, stroke_width, dashed, fill_color):
	context.arc(x, y, radius, 0, 6.283185307179586)
	if color and stroke_width:
		context.set_source_rgb(*color)
		context.set_line_width(stroke_width / scale)
		if dashed:
			context.set_dash([12, 4])
		if fill_color:
			context.stroke_preserve()
		else:
			context.stroke()
	if fill_color:
		context.set_source_rgb(*fill_color)
		context.fill()

def _draw_rectangle(context, scale, x, y, width, height, color, stroke_width, dashed, fill_color):		
	context.rectangle(x, y, width, height)
	if color and stroke_width:
		context.set_source_rgb(*color)
		context.set_line_width(stroke_width / scale)
		if dashed:
			context.set_dash([12, 4])
		if fill_color:
			context.stroke_preserve()
		else:
			context.stroke()
	if fill_color:
		context.set_source_rgb(*fill_color)
		context.fill()

def _draw_text(context, scale, x, y, text, font_face, font_size, color, annotation=False):
	if annotation:
		font_size /= scale
	context.set_source_rgb(*color)
	context.select_font_face(font_face)
	context.set_font_size(font_size)
	context.move_to(x, y)
	context.show_text(text)

def _draw_caption(context, scale, x, y, letter, caption, font_face, font_size, color):
	context.set_source_rgb(*color)
	context.set_font_size(font_size)
	context.move_to(x, y)
	if letter:
		context.select_font_face(font_face, weight=_cairo.FONT_WEIGHT_BOLD)
		context.show_text(f'({letter}) ')
	if caption:
		context.select_font_face(font_face, weight=_cairo.FONT_WEIGHT_NORMAL)
		context.show_text(caption)


##################
# HELPER FUNCTIONS
##################

def _duration_to_radius(duration):
	'''
	
	Converts a millisecond duration to a pixel radius for plotting fixation
	circles so that the area of the circle corresponds to duration.
	
	'''
	return (duration / 3.141592653589793) ** 0.5

def _mm_to_pts(mm):
	'''

	Convert millimeters to points.

	'''
	return mm / (25.4 / 72)

def _color_to_rgb(color):
	'''
	
	Convert a color to RGB values in [0, 1]. Can take an RGB tuple in [0, 255], a
	hex triplet, or a named color.

	'''
	if isinstance(color, tuple) and len(color) == 3:
		return color[0]/255, color[1]/255, color[2]/255
	if isinstance(color, str) and color[0] == '#':
		r, g, b = tuple(bytes.fromhex(color[1:]))
		return r/255, g/255, b/255
	if color.lower() in _color.colors:
		color = _color.colors[color.lower()]
		return color[0]/255, color[1]/255, color[2]/255
	return 0, 0, 0

def _pseudo_alpha(rgb, opacity):
	'''

	Given an RGB value in [0, 1], return a new RGB value which blends in a
	certain amount of white to create a fake alpha effect. This allows us to
	produce an alpha-like effect in EPS, which doesn't support transparency.

	'''
	return tuple([value * opacity - opacity + 1 for value in rgb])
