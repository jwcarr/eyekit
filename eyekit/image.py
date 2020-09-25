'''

Defines the `Image` and `Figure` objects, which are used to create visualizations.

'''


from os import path as _path
import cairocffi as _cairo


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

	def __init__(self, screen_width, screen_height):
		'''Initialized with:
		
		- `screen_width` *int* : Width of the screen in pixels.
		- `screen_height` *int* : Height of the screen in pixels.
		'''
		self.screen_width = int(screen_width)
		self.screen_height = int(screen_height)
		self._caption = None
		self._background_color = (1, 1, 1)
		self._crop_margin = None
		self._components = []
		self._text_x = 0
		self._text_y = 0
		self._text_width = screen_width
		self._text_height = screen_height

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

	def set_crop_margin(self, crop_margin):
		'''
		
		If you set a crop margin, the image will be cropped to the size of the
		`eyekit.text.TextBlock` plus the specified margin. Margins are specified in
		millimeters if you intend to output to a vector format or pixels in the case
		of PNG. Note that, if you place the image inside a `Figure`, this crop
		margin will be ignored; instead you should use `Figure.set_crop_margin()`.

		'''
		if crop_margin is None:
			self._crop_margin = None
		else:
			self._crop_margin = float(crop_margin)

	def draw_text_block(self, text_block, color='black'):
		'''

		Draw a `eyekit.text.TextBlock` on the image. `color` sets the color of the
		text.

		'''
		self._text_x = text_block.x_tl
		self._text_y = text_block.y_tl
		self._text_width = text_block.width
		self._text_height = text_block.height
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
			self._add_component(_draw_fixation, arguments)

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

	def save(self, output_path, image_width=150):
		'''

		Save the image to some `output_path`. Images can be saved as .pdf, .eps,
		.svg, or .png. `image_width` only applies to the vector formats and
		determines the millimeter width of the output file; PNG images are saved at
		actual pixel size.

		'''
		image_format = _path.splitext(output_path)[1][1:].upper()
		if image_format not in ['PDF', 'EPS', 'SVG', 'PNG']:
			raise ValueError('Unrecognized format. Use .pdf, .eps, or .svg for vector output, or .png for raster output.')
		image_width = _mm_to_pts(image_width)
		surface, context, scale = self._make_surface(output_path, image_format, image_width)
		self._render_background(context)
		self._render_components(context, scale)
		if image_format == 'PNG':
			surface.write_to_png(output_path)
		surface.finish()

	#################
	# PRIVATE METHODS
	#################

	def _make_surface(self, output_path, image_format, image_width):
		if image_format == 'PNG':
			scale = 1
			if self._crop_margin is None:
				image_width = self.screen_width
				image_height = self.screen_height
			else:
				crop_margin = self._crop_margin
				image_width = self._text_width + crop_margin*2
				image_height = self._text_height + crop_margin*2
			surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, int(image_width), int(image_height))
		else:
			if self._crop_margin is None:
				scale = image_width / self.screen_width
				image_height = self.screen_height * scale
			else:
				crop_margin = _mm_to_pts(self._crop_margin)
				if crop_margin > image_width / 3:
					raise ValueError('The crop margin set on this image is too large for the image width. Increase the image width or decrease the crop margin.')
				scale = (image_width - crop_margin*2) / self._text_width
				image_height = self._text_height * scale + crop_margin*2
			if image_format == 'PDF':
				surface = _cairo.PDFSurface(output_path, image_width, image_height)
			elif image_format == 'EPS':
				surface = _cairo.PSSurface(output_path, image_width, image_height)
				surface.set_eps(True) # encapsulate postscript file
			elif image_format == 'SVG':
				surface = _cairo.SVGSurface(output_path, image_width, image_height)
			surface.set_device_scale(scale, scale)
		context = _cairo.Context(surface)
		if self._crop_margin is not None:
			crop_margin = crop_margin / scale
			context.translate(-self._text_x+crop_margin, -self._text_y+crop_margin)
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

	def __init__(self, n_rows=1, n_cols=1):
		'''Initialized with:
		
		- `n_rows` *int* : Number of rows in the figure.
		- `n_cols` *int* : Number of columns in the figure.
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
		self._v_padding = 10
		self._h_padding = 10
		self._e_padding = 2
		self._auto_letter = True
		self._crop_margin = None

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
		the edge of the figure. Padding is expressed in millimeters.

		'''
		if vertical is not None:
			self._v_padding = _mm_to_pts(float(vertical))
		if horizontal is not None:
			self._h_padding = _mm_to_pts(float(horizontal))
		if edge is not None:
			self._e_padding = _mm_to_pts(float(edge))

	def set_auto_letter(self, auto_letter=True):
		'''

		By default, each image caption is prefixed with a letter, **(A)**, **(B)**,
		**(C)**, etc. If you want to turn this off, call
		```Figure.set_auto_letter(False)``` prior to saving.

		'''
		self._auto_letter = bool(auto_letter)

	def set_crop_margin(self, crop_margin):
		'''

		If you set a crop margin, each image in the figure will be cropped to the
		size and positioning of the most extreme text block extents, plus the
		specified margin. This has the effect of zooming in to all images in a
		consistent way – maintaining the aspect ratio and relative positioning of
		the text blocks across images. Margins are specified in figure millimeters.

		'''
		if crop_margin is None:
			self._crop_margin = None
		else:
			self._crop_margin = float(crop_margin)

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

	def save(self, output_path, width=150):
		'''

		Save the figure to some `output_path`. Figures can be saved as .pdf, .eps,
		or .svg. `width` determines the millimeter width of the output file.

		'''
		figure_format = _path.splitext(output_path)[1][1:].upper()
		if figure_format not in ['PDF', 'EPS', 'SVG']:
			raise ValueError('Unrecognized format. Use .pdf, .eps, or .svg.')
		width = _mm_to_pts(width)
		layout, components, height, text_block_extents, crop_margin = self._make_layout(width)
		surface, context = self._make_surface(output_path, figure_format, width, height)
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

	def _get_text_block_extents(self):
		x_tl = 99999999
		y_tl = 99999999
		x_br = 0
		y_br = 0
		for row in self._grid:
			for image in row:
				if image._text_x < x_tl:
					x_tl = image._text_x
				if image._text_y < y_tl:
					y_tl = image._text_y
				if image._text_x + image._text_width > x_br:
					x_br = image._text_x + image._text_width
				if image._text_y + image._text_height > y_br:
					y_br = image._text_y + image._text_height
		return x_tl, y_tl, x_br-x_tl, y_br-y_tl

	def _make_layout(self, figure_width):
		layout, components = [], []
		letter_index = 65 # 65 == A, etc...
		text_block_extents = self._get_text_block_extents()
		y = self._e_padding
		for row in self._grid:
			x = self._e_padding
			tallest_in_row = 0
			if self._auto_letter or sum([bool(image._caption) for image in row if isinstance(image, Image)]):
				y += self._font_size + 8 # row contains captions, so make some space
			n_cols = len(row)
			cell_width = (figure_width - 2 * self._e_padding - (n_cols-1) * self._h_padding) / n_cols
			for image in row:
				if image is None:
					x += cell_width + self._h_padding
					continue
				if self._crop_margin:
					crop_margin = _mm_to_pts(self._crop_margin)
					scale = (cell_width - crop_margin*2) / text_block_extents[2]
					aspect_ratio = text_block_extents[2] / text_block_extents[3]
				else:
					crop_margin = None
					scale = cell_width / image.screen_width
					aspect_ratio = image.screen_width / image.screen_height
				cell_height = cell_width / aspect_ratio
				if cell_height > tallest_in_row:
					tallest_in_row = cell_height
				caption = None
				if self._auto_letter and image._caption:
					letter = chr(letter_index)
					caption = image._caption
				elif self._auto_letter:
					letter = chr(letter_index)
					caption = None
				elif image._caption:
					letter = None
					caption = image._caption
				if caption:
					arguments = {'x':x, 'y':y-8, 'letter':letter, 'caption':caption, 'font_face':self._font_face, 'font_size':self._font_size, 'color':(0, 0, 0)}
					components.append((_draw_caption, arguments))
					layout.append((image, x, y, cell_width, cell_height, scale))
				arguments = {'x':x, 'y':y, 'width':cell_width, 'height':cell_height, 'color':(0,0,0), 'stroke_width':1, 'dashed':False, 'fill_color':None}
				components.append((_draw_rectangle, arguments))
				x += cell_width + self._h_padding
				letter_index += 1
			y += tallest_in_row + self._v_padding
		figure_height = y - (self._v_padding - self._e_padding)
		return layout, components, figure_height, text_block_extents, crop_margin

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
			if crop_margin:
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
	hex triplet, or a namaed color.

	'''
	if isinstance(color, tuple) and len(color) == 3:
		return color[0]/255, color[1]/255, color[2]/255
	if isinstance(color, str) and color[0] == '#':
		r, g, b = tuple(bytes.fromhex(color[1:]))
		return r/255, g/255, b/255
	if color.lower() in _COLORS:
		color = _COLORS[color.lower()]
		return color[0]/255, color[1]/255, color[2]/255
	return 0, 0, 0

def _pseudo_alpha(rgb, opacity):
	'''

	Given an RGB value in [0, 1], return a new RGB value which blends in a
	certain amount of white to create a fake alpha effect. This allows us to
	produce an alpha-like effect in EPS, which doesn't support transparency.

	'''
	opacity = 1 - opacity
	return tuple([(val*255 + ((255 - val*255) * opacity)) / 255 for val in rgb])


_COLORS = {
	'aliceblue': (240, 248, 255),
	'antiquewhite': (250, 235, 215),
	'aqua': (0, 255, 255),
	'aquamarine': (127, 255, 212),
	'azure': (240, 255, 255),
	'beige': (245, 245, 220),
	'bisque': (255, 228, 196),
	'black': (0, 0, 0),
	'blanchedalmond': (255, 235, 205),
	'blue': (0, 0, 255),
	'blueviolet': (138, 43, 226),
	'brown': (165, 42, 42),
	'burlywood': (222, 184, 135),
	'cadetblue': (95, 158, 160),
	'chartreuse': (127, 255, 0),
	'chocolate': (210, 105, 30),
	'coral': (255, 127, 80),
	'cornflowerblue': (100, 149, 237),
	'cornsilk': (255, 248, 220),
	'crimson': (220, 20, 60),
	'cyan': (0, 255, 255),
	'darkblue': (0, 0, 139),
	'darkcyan': (0, 139, 139),
	'darkgoldenrod': (184, 134, 11),
	'darkgray': (169, 169, 169),
	'darkgreen': (0, 100, 0),
	'darkgrey': (169, 169, 169),
	'darkkhaki': (189, 183, 107),
	'darkmagenta': (139, 0, 139),
	'darkolivegreen': (85, 107, 47),
	'darkorange': (255, 140, 0),
	'darkorchid': (153, 50, 204),
	'darkred': (139, 0, 0),
	'darksalmon': (233, 150, 122),
	'darkseagreen': (143, 188, 143),
	'darkslateblue': (72, 61, 139),
	'darkslategray': (47, 79, 79),
	'darkslategrey': (47, 79, 79),
	'darkturquoise': (0, 206, 209),
	'darkviolet': (148, 0, 211),
	'deeppink': (255, 20, 147),
	'deepskyblue': (0, 191, 255),
	'dimgray': (105, 105, 105),
	'dimgrey': (105, 105, 105),
	'dodgerblue': (30, 144, 255),
	'firebrick': (178, 34, 34),
	'floralwhite': (255, 250, 240),
	'forestgreen': (34, 139, 34),
	'fuchsia': (255, 0, 255),
	'gainsboro': (220, 220, 220),
	'ghostwhite': (248, 248, 255),
	'gold': (255, 215, 0),
	'goldenrod': (218, 165, 32),
	'gray': (128, 128, 128),
	'grey': (128, 128, 128),
	'green': (0, 128, 0),
	'greenyellow': (173, 255, 47),
	'honeydew': (240, 255, 240),
	'hotpink': (255, 105, 180),
	'indianred': (205, 92, 92),
	'indigo': (75, 0, 130),
	'ivory': (255, 255, 240),
	'khaki': (240, 230, 140),
	'lavender': (230, 230, 250),
	'lavenderblush': (255, 240, 245),
	'lawngreen': (124, 252, 0),
	'lemonchiffon': (255, 250, 205),
	'lightblue': (173, 216, 230),
	'lightcoral': (240, 128, 128),
	'lightcyan': (224, 255, 255),
	'lightgoldenrodyellow': (250, 250, 210),
	'lightgray': (211, 211, 211),
	'lightgreen': (144, 238, 144),
	'lightgrey': (211, 211, 211),
	'lightpink': (255, 182, 193),
	'lightsalmon': (255, 160, 122),
	'lightseagreen': (32, 178, 170),
	'lightskyblue': (135, 206, 250),
	'lightslategray': (119, 136, 153),
	'lightslategrey': (119, 136, 153),
	'lightsteelblue': (176, 196, 222),
	'lightyellow': (255, 255, 224),
	'lime': (0, 255, 0),
	'limegreen': (50, 205, 50),
	'linen': (250, 240, 230),
	'magenta': (255, 0, 255),
	'maroon': (128, 0, 0),
	'mediumaquamarine': (102, 205, 170),
	'mediumblue': (0, 0, 205),
	'mediumorchid': (186, 85, 211),
	'mediumpurple': (147, 112, 219),
	'mediumseagreen': (60, 179, 113),
	'mediumslateblue': (123, 104, 238),
	'mediumspringgreen': (0, 250, 154),
	'mediumturquoise': (72, 209, 204),
	'mediumvioletred': (199, 21, 133),
	'midnightblue': (25, 25, 112),
	'mintcream': (245, 255, 250),
	'mistyrose': (255, 228, 225),
	'moccasin': (255, 228, 181),
	'navajowhite': (255, 222, 173),
	'navy': (0, 0, 128),
	'oldlace': (253, 245, 230),
	'olive': (128, 128, 0),
	'olivedrab': (107, 142, 35),
	'orange': (255, 165, 0),
	'orangered': (255, 69, 0),
	'orchid': (218, 112, 214),
	'palegoldenrod': (238, 232, 170),
	'palegreen': (152, 251, 152),
	'paleturquoise': (175, 238, 238),
	'palevioletred': (219, 112, 147),
	'papayawhip': (255, 239, 213),
	'peachpuff': (255, 218, 185),
	'peru': (205, 133, 63),
	'pink': (255, 192, 203),
	'plum': (221, 160, 221),
	'powderblue': (176, 224, 230),
	'purple': (128, 0, 128),
	'red': (255, 0, 0),
	'rosybrown': (188, 143, 143),
	'royalblue': (65, 105, 225),
	'saddlebrown': (139, 69, 19),
	'salmon': (250, 128, 114),
	'sandybrown': (244, 164, 96),
	'seagreen': (46, 139, 87),
	'seashell': (255, 245, 238),
	'sienna': (160, 82, 45),
	'silver': (192, 192, 192),
	'skyblue': (135, 206, 235),
	'slateblue': (106, 90, 205),
	'slategray': (112, 128, 144),
	'slategrey': (112, 128, 144),
	'snow': (255, 250, 250),
	'springgreen': (0, 255, 127),
	'steelblue': (70, 130, 180),
	'tan': (210, 180, 140),
	'teal': (0, 128, 128),
	'thistle': (216, 191, 216),
	'tomato': (255, 99, 71),
	'turquoise': (64, 224, 208),
	'violet': (238, 130, 238),
	'wheat': (245, 222, 179),
	'white': (255, 255, 255),
	'whitesmoke': (245, 245, 245),
	'yellow': (255, 255, 0),
	'yellowgreen': (154, 205, 50)
}
