from os import path as _path
from subprocess import call as _call
from subprocess import check_output as _check_output
from subprocess import STDOUT as _STDOUT
from subprocess import DEVNULL as _DEVNULL
import numpy as _np


INKSCAPE_BINARY = None
try:
	inkscape_path = _check_output(['which', 'inkscape']).decode().strip()
	if _path.isfile(inkscape_path):
		INKSCAPE_BINARY = inkscape_path
except:
	pass


class Diagram:

	def __init__(self, screen_width, screen_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.passage_location = None
		self.svg = ''

	# PUBLIC METHODS

	def render_passage(self, passage, fontsize):
		for char, char_rc, (x, y) in passage:
			self.svg += '<g id="row%i_col%i">\n' % char_rc
			self.svg += '	<text text-anchor="middle" dominant-baseline="central" x="%i" y="%i" fill="black" style="font-size:%fpx; font-family:Courier New">%s</text>\n' % (x, y, fontsize, char)
			self.svg += '</g>\n\n'
		self.passage_location = {'x':passage.first_character_position[0] - (passage.character_spacing * 0.5), 'y':passage.first_character_position[1] - (passage.line_spacing * 0.5), 'width':passage.n_cols * passage.character_spacing, 'height':passage.n_rows * passage.line_spacing}

	def render_fixations(self, fixation_sequence, connect_fixations=True, color='red', number_fixations=False, include_discards=False):
		last_fixation = None
		for i, fixation in enumerate(fixation_sequence.iter_with_discards()):
			if not include_discards and fixation.discarded:
				continue
			radius = duration_to_radius(fixation.duration)
			self.svg += '<g id="fixation%i">\n' % i
			if connect_fixations and last_fixation:
				if include_discards and (last_fixation.discarded or fixation.discarded):
					self.svg += '	<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:gray;"/>\n' % (last_fixation.x, last_fixation.y, fixation.x, fixation.y)
				else:
					self.svg += '	<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:%s;"/>\n' % (last_fixation.x, last_fixation.y, fixation.x, fixation.y, color)
			if include_discards and fixation.discarded:
				self.svg += '	<circle cx="%i" cy="%i" r="%f" style="stroke-width:0; fill:gray; opacity:0.3" />\n' % (fixation.x, fixation.y, radius)
			else:
				self.svg += '	<circle cx="%i" cy="%i" r="%f" style="stroke-width:0; fill:%s; opacity:0.3" />\n' % (fixation.x, fixation.y, radius, color)
			if number_fixations:
				self.svg += '	<text text-anchor="middle" dominant-baseline="central" x="%i" y="%i" fill="black" style="font-size:10px; font-family:Helvetica">%s</text>\n' % (fixation.x, fixation.y, i+1)
			self.svg += '</g>\n\n'
			last_fixation = fixation

	def render_heatmap(self, passage, distribution, n=1, color='red'):
		distribution = normalize_min_max(distribution)
		subcell_height = passage.line_spacing / n
		levels = [subcell_height*i for i in range(n)]
		level = 0
		for ngram in passage.iter_ngrams(n):
			if level == n:
				level = 0
			p = distribution[ngram[0].rc]
			subcell_width = ngram[-1].c - ngram[0].c + 1
			self.svg += '<rect x="%f" y="%f" width="%i" height="%i" style="fill:%s; stroke-width:0; opacity:%f" />' % (ngram[0].x-passage.character_spacing/2., (ngram[0].y-passage.line_spacing/2.)+levels[level], passage.character_spacing*subcell_width, subcell_height, color, p)
			level += 1
		for line_i in range(passage.n_rows-1):
			start_x = passage.first_character_position[0] - (passage.character_spacing - passage.character_spacing/2)
			end_x = passage.first_character_position[0] + (passage.n_cols * passage.character_spacing) - passage.character_spacing/2
			y = passage.first_character_position[1] + (passage.line_spacing * line_i) + passage.line_spacing/2
			self.svg += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:black; stroke-width:2"/>' % (start_x, y, end_x, y)

	def draw_arbitrary_line(self, start_xy, end_xy, color='black'):
		start_x, start_y = start_xy
		end_x, end_y = end_xy
		self.svg += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s; stroke-width:2" stroke-dasharray="6 2"/>' % (start_x, start_y, end_x, end_y, color)

	def save(self, output_path, diagram_width=200, crop_to_passage=False):
		if INKSCAPE_BINARY is None and not output_path.endswith('.svg'):
			raise ValueError('Cannot save to this format. Use .svg or install inkscape to save as .pdf, .eps, or .png.')
		if crop_to_passage and self.passage_location is not None:
			diagram_height = self.passage_location['height'] / (self.passage_location['width'] / diagram_width)
			svg = '<svg width="%fmm" height="%fmm" viewBox="%i %i %i %i" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect x="%i" y="%i" width="%i" height="%i" fill="white"/>\n\n' % (diagram_width, diagram_height, self.passage_location['x'], self.passage_location['y'], self.passage_location['width'], self.passage_location['height'], self.passage_location['x'], self.passage_location['y'], self.passage_location['width'], self.passage_location['height'])
		else:
			diagram_height = self.screen_height / (self.screen_width / diagram_width)
			svg = '<svg width="%fmm" height="%fmm" viewBox="0 0 %i %i" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect width="%i" height="%i" fill="white"/>\n\n' % (diagram_width, diagram_height, self.screen_width, self.screen_height, self.screen_width, self.screen_height)
		svg += self.svg
		svg += '</svg>'
		with open(output_path, mode='w', encoding='utf-8') as file:
			file.write(svg)
		if not output_path.endswith('.svg'):
			convert_svg(output_path, output_path, png_width=self.screen_width)


def convert_svg(svg_file_path, out_file_path, png_width=1000):
	filename, extension = _path.splitext(out_file_path)
	if extension == '.pdf':
		_call([INKSCAPE_BINARY, svg_file_path, '-A', out_file_path, '--export-text-to-path'], stdout=_DEVNULL, stderr=_STDOUT)
	elif extension == '.eps':
		_call([INKSCAPE_BINARY, svg_file_path, '-E', out_file_path, '--export-text-to-path'], stdout=_DEVNULL, stderr=_STDOUT)
	elif extension == '.png':
		_call([INKSCAPE_BINARY, svg_file_path, '-e', out_file_path, '--export-width=%i'%png_width], stdout=_DEVNULL, stderr=_STDOUT)
	else:
		raise ValueError('Cannot save to this format. Use either .pdf, .eps, or .png')

def normalize_min_max(distribution):
	'''
	Normalizes a numpy array such that the minimum value becomes 0 and
	the maximum value becomes 1.
	'''
	return (distribution - distribution.min()) / (distribution.max() - distribution.min())

def duration_to_radius(duration):
	'''
	Converts a duration to a radius for plotting fixation circles so
	that the area of the circle corresponds to duration.
	'''
	return _np.sqrt(duration / _np.pi)
