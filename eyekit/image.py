'''

Defines the `Image` object, which is used to create visualizations,
and other functions for handling images.

'''


from os import path as _path
import re as _re
import numpy as _np
try:
	import cairosvg as _cairosvg
except ImportError:
	_cairosvg = None

_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Image:

	'''

	Visualization of texts and fixation sequences.

	'''

	def __init__(self, screen_width, screen_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.text_x = 0
		self.text_y = 0
		self.text_width = screen_width
		self.text_height = screen_height
		self.svg = ''
		self.label = None

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
		self.text_x = text_block.x_tl
		self.text_y = text_block[0, 0].y_tl
		self.text_width = text_block.width
		self.text_height = text_block.height
		self.svg += svg

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
			svg += '\t<g id="fixation_%i">\n' % i
			if connect_fixations and last_fixation:
				if include_discards and (last_fixation.discarded or fixation.discarded):
					svg += '\t\t<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:%s;"/>\n' % (last_fixation.x, last_fixation.y, fixation.x, fixation.y, discard_color)
				else:
					svg += '\t\t<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:%s;"/>\n' % (last_fixation.x, last_fixation.y, fixation.x, fixation.y, this_color)
			if include_discards and fixation.discarded:
				svg += '\t\t<circle cx="%i" cy="%i" r="%f" style="stroke-width:0; fill:%s; opacity:1.0" />\n' % (fixation.x, fixation.y, radius, discard_color)
			else:
				svg += '\t\t<circle cx="%i" cy="%i" r="%f" style="stroke-width:0; fill:%s; opacity:1.0" />\n' % (fixation.x, fixation.y, radius, this_color)
			last_fixation = fixation
			svg += '\t</g>\n\n'
		svg += '</g>\n\n'
		if number_fixations:
			svg += '<g id="fixation_numbers">\n'
			for i, fixation in enumerate(fixation_sequence.iter_with_discards()):
				if not include_discards and fixation.discarded:
					continue
				svg += '\t<text text-anchor="middle" alignment-baseline="middle" x="%i" y="%i" fill="white" style="font-size:10px; font-family:Helvetica">%s</text>\n' % (fixation.x, fixation.y, i+1)
			svg += '</g>\n\n'
		self.svg += svg

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
			svg += '\t<g id="fixation_%i">\n' % i
			if last_fixation:
				svg += '\t\t<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:black;"/>\n' % (last_fixation.x, last_fixation.y, fixation.x, fixation.y)
			svg += '\t\t<circle cx="%i" cy="%i" r="%f" style="stroke-width:0; fill:%s; opacity:1.0" />\n' % (fixation.x, fixation.y, radius, color)
			svg += '\t</g>\n\n'
			last_fixation = fixation
		svg += '</g>\n\n'
		self.svg += svg

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
		self.svg += svg

	def draw_line(self, start_xy, end_xy, color='black', dashed=False):
		'''

		Draw an arbitrary line on the image from `start_xy` to `end_xy`.

		'''
		start_x, start_y = start_xy
		end_x, end_y = end_xy
		if dashed:
			self.svg += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s; stroke-width:2" stroke-dasharray="4" />\n\n' % (start_x, start_y, end_x, end_y, color)
		else:
			self.svg += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s; stroke-width:2" />\n\n' % (start_x, start_y, end_x, end_y, color)

	def draw_circle(self, x, y=None, radius=10, color='black'):
		'''

		Draw an arbitrary circle on the image with center `xy` and given
		`radius`.

		'''
		if isinstance(x, tuple) and len(x) == 2:
			x, y, = x
		self.svg += '<circle cx="%f" cy="%f" r="%f" style="stroke-width:0; fill:%s; opacity:1" />\n' % (x, y, radius, color)

	def draw_rectangle(self, x, y=None, width=None, height=None, stroke_width=2, color='black', fill_color=None, dashed=False, opacity=1):
		'''

		Draw an arbitrary rectangle on the image located at x,y with some
		width and height. Also accepts a tuple of four ints as the first
		argument.

		'''
		if isinstance(x, tuple) and len(x) == 4:
			x, y, width, height = x
		if dashed:
			self.svg += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" style="fill:{fill_color}; stroke:{color}; stroke-width:{stroke_width};" stroke-dasharray="4" />\n\n'
		else:
			self.svg += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" style="fill:{fill_color}; stroke:{color}; stroke-width:{stroke_width};" />\n\n'

	def draw_text(self, text, x, y=None, color='black', align='left', style={}):
		'''

		Draw arbitrary text on the image located at x,y. `align` determines
		the anchor of the given position. Some CSS styling can also be
		provided to customize the text.

		'''
		if isinstance(x, tuple) and len(x) == 2:
			x, y = x
		style = '; '.join(['%s:%s'%(key, value) for key, value in style.items()])
		self.svg += '\t<text text-anchor="%s" alignment-baseline="middle" x="%f" y="%f" fill="%s" style="%s">%s</text>\n' % (align, x, y, color, style, text)

	def crop_to_text(self, margin=0):
		'''

		Once a `eyekit.text.TextBlock` has been rendered using `Image.render_text()`, this
		method can be called to crop the image to the size of the text
		with some `margin`.

		'''
		x_adjustment = self.text_x - margin
		y_adjustment = self.text_y - margin
		replacements = {}
		for x_param in ['cx', 'x1', 'x2', 'x']:
			search_string = '( %s="(.+?)")' % x_param
			for match in _re.finditer(search_string, self.svg):
				surround, value = match.groups()
				new_value = float(value) - x_adjustment
				replacement = surround.replace(value, str(new_value))
				replacements[surround] = replacement
		regex = _re.compile("(%s)" % '|'.join(map(_re.escape, replacements.keys())))
		svg = regex.sub(lambda mo: replacements[mo.string[mo.start():mo.end()]], self.svg)
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
		self.screen_width = self.text_width + 2 * margin
		self.screen_height = self.text_height + 2 * margin
		self.svg = svg

	def set_label(self, label):
		'''

		Give the image a label which will be shown if you place the image in
		a combined image using `combine_images()`.

		'''
		self.label = label

	def reference_raster_image(self, image_path, x, y, width, height):
		'''

		Insert a reference to a raster image file. `image_path` must be absolute.

		'''
		self.svg += f'<image x="{x}" y="{y}" width="{width}" height="{height}" href="{image_path}"/>'

	def save(self, output_path, image_width=200):
		'''

		Save the image to some `output_path`. The format (SVG, PDF, EPS, or
		PNG) is determined from the filename extension. `image_width` only
		applies to SVG, PDF, and EPS where it determines the mm width. PNGs
		are rendered at actual pixel size. PDF, EPS, and PNG require
		[CairoSVG](https://cairosvg.org/): `pip install cairosvg`

		'''
		if _cairosvg is None and not output_path.endswith('.svg'):
			raise ValueError('Cannot save to this format. Use .svg or install cairosvg to save as .pdf, .eps, or .png.')
		image_height = self.screen_height / (self.screen_width / image_width)
		image_size = '' if output_path.endswith('.png') else 'width="%fmm" height="%fmm"' % (image_width, image_height)
		svg = '<svg %s viewBox="0 0 %i %i" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect width="%i" height="%i" fill="white"/>\n\n' % (image_size, self.screen_width, self.screen_height, self.screen_width, self.screen_height)
		svg += self.svg
		svg += '</svg>'
		with open(output_path, mode='w', encoding='utf-8') as file:
			file.write(svg)
		if not output_path.endswith('.svg'):
			convert_svg(output_path, output_path)


def convert_svg(svg_file_path, out_file_path):
	'''

	Convert an SVG file into PDF, EPS, or PNG. This function is
	essentially a wrapper around [CairoSVG](https://cairosvg.org/).
	
	'''
	if _cairosvg is None:
		raise ValueError('CairoSVG is required to convert SVGs to another format.')
	filename, extension = _path.splitext(out_file_path)
	if extension == '.pdf':
		_cairosvg.svg2pdf(url=svg_file_path, write_to=out_file_path)
	elif extension == '.eps':
		_cairosvg.svg2ps(url=svg_file_path, write_to=out_file_path)
	elif extension == '.png':
		_cairosvg.svg2png(url=svg_file_path, write_to=out_file_path)
	else:
		raise ValueError('Cannot save to this format. Use either .pdf, .eps, or .png')

def combine_images(images, output_path, image_width=200, image_height=None, v_padding=5, h_padding=5, e_padding=1, auto_letter=True):
	'''

	Combine image objects together into one larger image. `images` should
	be a *list* of *list* of `Image` structure. For example, `[[img1, img2], [img3, img4]]`
	results in a 2x2 grid of images. `image_width` is the desired mm
	(SVG, PDF, EPS) or pixel (PNG) width of the combined image. If
	`auto_letter` is set to `True`, each image will be given a letter
	label.

	'''
	svg = ''
	l = 0
	y = e_padding
	for row in images:
		x = e_padding
		tallest_in_row = 0
		if auto_letter or sum([bool(image.label) for image in row if isinstance(image, Image)]):
			y += 2.823 + 1 # row contains labels, so make some space
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
			label = None
			if auto_letter and image.label:
				label = '<tspan style="font-weight:bold">(%s)</tspan> %s' % (_ALPHABET[l], image.label)
			elif auto_letter:
				label = '<tspan style="font-weight:bold">(%s)</tspan>' % _ALPHABET[l]
			elif image.label:
				label = image.label
			if label:
				svg += '<text x="%f" y="%f" fill="black" style="font-size:2.823; font-family:Helvetica">%s</text>\n\n' % (x, y-2, label)
			svg += '<g transform="translate(%f, %f) scale(%f)">' % (x, y, scaling_factor)
			svg += image.svg
			svg += '</g>'
			svg += '<rect x="%f" y="%f" width="%f" height="%f" fill="none" stroke="black" style="stroke-width:0.25" />\n\n' % (x, y, cell_width, cell_height)			
			x += cell_width + h_padding
			l += 1
		y += tallest_in_row + v_padding
	if image_height is None:
		image_height = y - (v_padding - e_padding)
	if _cairosvg is None and not output_path.endswith('.svg'):
		raise ValueError('Cannot save to this format. Use .svg or install cairosvg to save as .pdf, .eps, or .png.')
	image_size = '' if output_path.endswith('.png') else 'width="%fmm" height="%fmm"' % (image_width, image_height)
	svg = '<svg %s viewBox="0 0 %i %i" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect width="%i" height="%i" fill="white"/>\n\n%s\n\n</svg>' % (image_size, image_width, image_height, image_width, image_height, svg)
	with open(output_path, mode='w', encoding='utf-8') as file:
		file.write(svg)
	if not output_path.endswith('.svg'):
		convert_svg(output_path, output_path)


def _duration_to_radius(duration):
	'''

	Converts a millisecond duration to a pixel radius for plotting
	fixation circles so that the area of the circle corresponds to
	duration.
	
	'''
	return _np.sqrt(duration / _np.pi)
