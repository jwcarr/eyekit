'''

Defines the `Image` object, which is used to create visualizations,
and other functions for handling images.

'''


from os import path as _path
import re as _re
from PIL import Image as _PILImage
try:
	import cairosvg as _cairosvg
except ImportError:
	_cairosvg = None


class Image:

	'''

	Visualization of texts and fixation sequences.

	'''

	def __init__(self, screen_width, screen_height):
		self.screen_width = int(screen_width)
		self.screen_height = int(screen_height)
		self._svg = ''
		self._text_x = 0
		self._text_y = 0
		self._text_width = screen_width
		self._text_height = screen_height
		self._caption = None

	@property
	def caption(self):
		'''*str* A caption that will be placed above the image if you create a figure using `make_figure()`. Set the caption using `Image.set_caption()`.'''
		return self._caption

	# PUBLIC METHODS

	def render_text(self, text_block, color='black', render_by_character=False):
		'''

		Render a `eyekit.text.TextBlock` on the image. If `render_by_character` is
		`True`, each character is positioned individually, which reflects what
		Eyekit is seeing underlyingly; however, rendering by line offers better
		presentation because it better handles kerning.

		'''
		svg = '<g id="text">\n\n'
		if render_by_character:
			for char in text_block:
				if str(char) != ' ':
					svg += f'\t<text text-anchor="start" x="{char.x_tl}" y="{char.baseline}" fill="{color}" style="font-size:{text_block.font_size}px; font-family:{text_block.font_name}">{char}</text>\n'
		else:
			for line in text_block.lines():
				svg += f'\t<text text-anchor="start" x="{line.x_tl}" y="{line.baseline}" fill="{color}" style="font-size:{text_block.font_size}px; font-family:{text_block.font_name}">{line.text}</text>\n'
		svg += '</g>\n\n'
		self._text_x = text_block.x_tl
		self._text_y = text_block[0, 0].y_tl
		self._text_width = text_block.width
		self._text_height = text_block.height
		self._svg += svg

	def render_fixations(self, fixation_sequence, connect_fixations=True, color='black', discard_color='gray', number_fixations=False, include_discards=False):
		'''

		Render a `eyekit.fixation.FixationSequence` on the image.

		'''
		svg = '<g id="fixation_sequence">\n\n'
		last_fixation = None
		for i, fixation in enumerate(fixation_sequence.iter_with_discards()):
			if not include_discards and fixation.discarded:
				continue
			radius = _duration_to_radius(fixation.duration)
			if isinstance(color, list):
				this_color = color[i]
			else:
				this_color = color
			svg += f'\t<g id="fixation_{i}">\n'
			if connect_fixations and last_fixation:
				if include_discards and (last_fixation.discarded or fixation.discarded):
					svg += f'\t\t<line x1="{last_fixation.x}" y1="{last_fixation.y}" x2="{fixation.x}" y2="{fixation.y}" style="stroke:{discard_color};"/>\n'
				else:
					svg += f'\t\t<line x1="{last_fixation.x}" y1="{last_fixation.y}" x2="{fixation.x}" y2="{fixation.y}" style="stroke:{this_color};"/>\n'
			if include_discards and fixation.discarded:
				svg += f'\t\t<circle cx="{fixation.x}" cy="{fixation.y}" r="{radius}" style="stroke-width:0; fill:{discard_color}; opacity:1.0" />\n'
			else:
				svg += f'\t\t<circle cx="{fixation.x}" cy="{fixation.y}" r="{radius}" style="stroke-width:0; fill:{this_color}; opacity:1.0" />\n'
			last_fixation = fixation
			svg += '\t</g>\n\n'
		svg += '</g>\n\n'
		if number_fixations:
			svg += '<g id="fixation_numbers">\n'
			for i, fixation in enumerate(fixation_sequence.iter_with_discards()):
				if not include_discards and fixation.discarded:
					continue
				svg += f'\t<text text-anchor="middle" alignment-baseline="middle" x="{fixation.x}" y="{fixation.y}" fill="white" style="font-size:10px; font-family:Helvetica">{i+1}</text>\n'
			svg += '</g>\n\n'
		self._svg += svg

	def render_fixation_comparison(self, reference_sequence, fixation_sequence, color_match='black', color_mismatch='red'):
		'''

		Render a `eyekit.fixation.FixationSequence` on the image with the fixations colored
		according to whether or not they match a reference sequence in terms
		of the y-coordinate. This is mostly useful for comparing the outputs
		of two different drift correction algorithms.

		'''
		svg = '<g id="fixation_comparison">\n\n'
		last_fixation = None
		for i, (reference_fixation, fixation) in enumerate(zip(reference_sequence.iter_with_discards(), fixation_sequence.iter_with_discards())):
			if reference_fixation.y == fixation.y:
				color = color_match
			else:
				color = color_mismatch
			radius = _duration_to_radius(fixation.duration)
			svg += f'\t<g id="fixation_{i}">\n'
			if last_fixation:
				svg += f'\t\t<line x1="{last_fixation.x}" y1="{last_fixation.y}" x2="{fixation.x}" y2="{fixation.y}" style="stroke:black;"/>\n'
			svg += f'\t\t<circle cx="{fixation.x}" cy="{fixation.y}" r="{radius}" style="stroke-width:0; fill:{color}; opacity:1.0" />\n'
			svg += '\t</g>\n\n'
			last_fixation = fixation
		svg += '</g>\n\n'
		self._svg += svg

	def render_heatmap(self, text_block, distribution, color='red'):
		'''

		Render a heatmap on the image. This is typically useful for
		visualizing the output from `eyekit.analysis.duration_mass()`.

		'''
		svg = '<g id="heatmap">\n\n'
		n = (text_block.n_cols - distribution.shape[1]) + 1
		distribution /= distribution.max()
		subcell_height = text_block.line_height / n
		levels = [subcell_height*i for i in range(n)]
		level = 0
		for ngram, rc in text_block.ngrams(n, yield_rc=True):
			if level == n:
				level = 0
			p = distribution[rc]
			svg += f'\t<rect x="{ngram.x_tl}" y="{ngram.y_tl+subcell_height*level}" width="{ngram.width}" height="{subcell_height}" style="fill:{color}; stroke-width:0; opacity:{p}" />\n\n'
			level += 1
		for line_i in range(1, text_block.n_rows):
			start_x = text_block.x_tl
			end_x = text_block.x_br 
			y = text_block.y_tl + (text_block.line_height * line_i)
			svg += f'\t<line x1="{start_x}" y1="{y}" x2="{end_x}" y2="{y}" style="stroke:black; stroke-width:2"/>\n\n'
		svg += '</g>\n\n'
		self._svg += svg

	def insert_raster_image(self, image_path, x, y, width, height):
		'''

		Insert a a raster image file. If outputting to SVG, the raster image is only
		referenced; for all other formats, the raster image is embedded.

		'''
		image_path = _path.abspath(image_path)
		self._svg += f'<image x="{x}" y="{y}" width="{width}" height="{height}" href="{image_path}"/>'

	def draw_line(self, start_xy, end_xy, color='black', dashed=False):
		'''

		Draw an arbitrary line on the image from `start_xy` to `end_xy`.

		'''
		start_x, start_y = start_xy
		end_x, end_y = end_xy
		if dashed:
			self._svg += f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" style="stroke:{color}; stroke-width:2" stroke-dasharray="4" />\n\n'
		else:
			self._svg += f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" style="stroke:{color}; stroke-width:2" />\n\n'

	def draw_circle(self, x, y=None, radius=10, color='black'):
		'''

		Draw an arbitrary circle on the image with center `xy` and given
		`radius`.

		'''
		if isinstance(x, tuple) and len(x) == 2:
			x, y, = x
		self._svg += f'<circle cx="{x}" cy="{y}" r="{radius}" style="stroke-width:0; fill:{color}; opacity:1" />\n'

	def draw_rectangle(self, x, y=None, width=None, height=None, stroke_width=2, color='black', fill_color=None, dashed=False, opacity=1):
		'''

		Draw an arbitrary rectangle on the image located at x,y with some
		width and height. Also accepts a tuple of four ints as the first
		argument.

		'''
		if isinstance(x, tuple) and len(x) == 4:
			x, y, width, height = x
		if dashed:
			self._svg += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" style="fill:{fill_color}; stroke:{color}; stroke-width:{stroke_width};" stroke-dasharray="4" />\n\n'
		else:
			self._svg += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" style="fill:{fill_color}; stroke:{color}; stroke-width:{stroke_width};" />\n\n'

	def draw_text(self, text, x, y=None, color='black', align='left', style={}):
		'''

		Draw arbitrary text on the image located at x,y. `align` determines
		the anchor of the given position. Some CSS styling can also be
		provided to customize the text.

		'''
		if isinstance(x, tuple) and len(x) == 2:
			x, y = x
		style = '; '.join(['%s:%s'%(key, value) for key, value in style.items()])
		self._svg += f'\t<text text-anchor="{align}" alignment-baseline="middle" x="{x}" y="{y}" fill="{color}" style="{style}">{text}</text>\n'

	def crop_to_text(self, margin=0):
		'''

		Once a `eyekit.text.TextBlock` has been rendered using `Image.render_text()`, this
		method can be called to crop the image to the size of the text
		with some `margin`.

		'''
		x_adjustment = self._text_x - margin
		y_adjustment = self._text_y - margin
		replacements = {}
		for x_param in ['cx', 'x1', 'x2', 'x']:
			search_string = '( %s="(.+?)")' % x_param
			for match in _re.finditer(search_string, self._svg):
				surround, value = match.groups()
				new_value = float(value) - x_adjustment
				replacement = surround.replace(value, str(new_value))
				replacements[surround] = replacement
		regex = _re.compile("(%s)" % '|'.join(map(_re.escape, replacements.keys())))
		svg = regex.sub(lambda mo: replacements[mo.string[mo.start():mo.end()]], self._svg)
		replacements = {}
		for y_param in ['cy', 'y1', 'y2', 'y']:
			search_string = '( %s="(.+?)")' % y_param
			for match in _re.finditer(search_string, svg):
				surround, value = match.groups()
				new_value = float(value) - y_adjustment
				replacement = surround.replace(value, str(new_value))
				replacements[surround] = replacement
		regex = _re.compile("(%s)" % '|'.join(map(_re.escape, replacements.keys())))
		svg = regex.sub(lambda mo: replacements[mo.string[mo.start():mo.end()]], svg)
		self.screen_width = self._text_width + 2 * margin
		self.screen_height = self._text_height + 2 * margin
		self._svg = svg

	def set_caption(self, caption):
		'''

		Give the image a caption which will be shown if you place the image in a
		figure using `make_figure()`.

		'''
		self._caption = str(caption)

	def save(self, output_path, image_width=200):
		'''

		Save the image to some `output_path`. Images can be saved as .svg, .pdf, or
		.eps (vector formats) or .png, .jpg, or .tif (raster formats). `image_width`
		only applies to the vector formats where it determines the mm width; raster
		images are saved at actual pixel size.

		'''
		_, extension = _path.splitext(output_path)
		image_height = self.screen_height / (self.screen_width / image_width)
		image_size = 'width="{image_width}mm" height="{image_height}mm" ' if extension in ['.svg', '.pdf', '.eps'] else ''
		svg = f'<svg {image_size}viewBox="0 0 {self.screen_width} {self.screen_height}" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect width="{self.screen_width}" height="{self.screen_height}" fill="white"/>\n\n{self._svg}</svg>'
		_write_svg_to_file(svg, output_path)


def make_figure(images, output_path, image_width=200, image_height=None, caption_font_name='Helvetica', caption_font_size=8, v_padding=5, h_padding=5, e_padding=1, auto_letter=True):
	'''

	Combine image objects together into one larger image. `images` should be a
	*list* of *list* of `Image` structure representing the layout of the grid.
	For example, `[[img1, img2], [img3, img4]]` results in a 2x2 grid of images.
	`image_width` is the desired mm (SVG, PDF, EPS) or pixel (PNG, JPEG, TIFF)
	width of the combined image. If `auto_letter` is set to `True`, each image
	caption will be prefixed with a letter. Vertical, horizontal, and edge
	padding can be controlled with the relevant parameter.

	'''
	svg = ''
	letter_index = 65 # 65 == A, etc...
	mm_font_size = caption_font_size / 72 * 25.4
	y = e_padding
	for row in images:
		x = e_padding
		tallest_in_row = 0
		if auto_letter or sum([bool(image.caption) for image in row if isinstance(image, Image)]):
			y += mm_font_size + 1 # row contains captions, so make some space
		n_cols = len(row)
		cell_width = (image_width - 2 * e_padding - (n_cols-1) * h_padding) / n_cols
		for image in row:
			if image is None:
				x += cell_width + h_padding
				continue
			scaling_factor = cell_width / image.screen_width
			aspect_ratio = image.screen_width / image.screen_height
			cell_height = cell_width / aspect_ratio
			if cell_height > tallest_in_row:
				tallest_in_row = cell_height
			caption = None
			if auto_letter and image.caption:
				caption = f'<tspan style="font-weight:bold">({chr(letter_index)})</tspan> {image.caption}'
			elif auto_letter:
				caption = f'<tspan style="font-weight:bold">({chr(letter_index)})</tspan>'
			elif image.caption:
				caption = image.caption
			if caption:
				svg += f'<text x="{x}" y="{y-2}" fill="black" style="font-size:{mm_font_size}; font-family:{caption_font_name}">{caption}</text>\n\n'
			svg += f'<g transform="translate({x}, {y}) scale({scaling_factor})">\n\n'
			svg += image._svg
			svg += '</g>\n\n'
			svg += f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" fill="none" stroke="black" style="stroke-width:0.25" />\n\n'
			x += cell_width + h_padding
			letter_index += 1
		y += tallest_in_row + v_padding
	if image_height is None:
		image_height = y - (v_padding - e_padding)
	svg = f'<svg width="{image_width}mm" height="{image_height}mm" viewBox="0 0 {image_width} {image_height}" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect width="{image_width}" height="{image_height}" fill="white"/>\n\n{svg}</svg>'
	_write_svg_to_file(svg, output_path)

def _write_svg_to_file(svg, output_path):
	'''

	Write SVG markup to a given file, using CairoSVG and Pillow to convert to the
	relevant format as necessary.

	'''
	_, extension = _path.splitext(output_path)
	if _cairosvg is None and extension != '.svg':
		raise ValueError('Cannot save in this format. Use .svg or install CairoSVG to save in other formats.')
	if extension not in ['.svg', '.pdf', '.eps', '.png', '.jpg', '.jpeg', '.tif', '.tiff']:
		raise ValueError('Cannot save in this format. Use .svg, .pdf, or .eps (for vector graphics), or .png., .jpg, or .tif (for raster graphics).')
	if extension == '.svg':
		data = svg.encode()
	elif extension == '.pdf':
		data = _cairosvg.svg2pdf(svg.encode())
	elif extension == '.eps':
		data = _cairosvg.svg2ps(svg.encode())
	else: # For raster formats, make PNG first
		data = _cairosvg.svg2png(svg.encode(), dpi=300)
	with open(output_path, mode='wb') as file:
		file.write(data)
	if extension in ['.png', '.jpg', '.jpeg', '.tif', '.tiff']:
		with _PILImage.open(output_path) as image:
			image.save(output_path, dpi=(300, 300))

def _duration_to_radius(duration):
	'''

	Converts a millisecond duration to a pixel radius for plotting
	fixation circles so that the area of the circle corresponds to
	duration.
	
	'''
	return (duration / 3.14159) ** 0.5
