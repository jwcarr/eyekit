from os import path
from subprocess import call, check_output, STDOUT, DEVNULL
import numpy as np


INKSCAPE_BINARY = None
try:
	inkscape_path = check_output(['which', 'inkscape']).decode().strip()
	if path.isfile(inkscape_path):
		INKSCAPE_BINARY = inkscape_path
except:
	pass


class Diagram:

	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.svg = ''

	# PRIVATE METHODS

	def _duration_to_radius(self, duration):
		'''
		Converts a duration to a radius for plotting fixation circles so
		that the area of the circle corresponds to duration.
		'''
		return np.sqrt(duration / np.pi)

	# PUBLIC METHODS

	def render_passage(self, passage, fontsize):
		for char, char_rc, (x, y) in passage:
			self.svg += '<g id="row%i_col%i">\n' % char_rc
			self.svg += '	<text text-anchor="middle" dominant-baseline="central" x="%i" y="%i" fill="black" style="font-size:%fpx; font-family:Courier New">%s</text>\n' % (x, y, fontsize, char)
			self.svg += '</g>\n\n'
		self.passage_x = passage.first_character_position[0] - (passage.character_spacing * 0.5)
		self.passage_y = passage.first_character_position[1] - (passage.line_spacing * 0.5)
		self.passage_width = passage.n_cols * passage.character_spacing
		self.passage_height = passage.n_rows * passage.line_spacing

	def render_fixations(self, fixations, connect_fixations=True, color='red'):
		for i, fixation in enumerate(fixations):
			radius = self._duration_to_radius(fixation.duration)
			self.svg += '<g id="fixation%i">\n' % i
			if connect_fixations and i > 0:
				self.svg += '	<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;"/>\n' % (last_x, last_y, fixation.x, fixation.y, color)
			self.svg += '	<circle cx="%f" cy="%f" r="%f" style="stroke-width:0; fill:%s; opacity:0.3" />\n' % (fixation.x, fixation.y, radius, color)
			self.svg += '</g>\n\n'
			last_x, last_y = fixation.x, fixation.y

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
		if crop_to_passage:
			diagram_height = self.passage_height / (self.passage_width / diagram_width)
			svg = '<svg width="%fmm" height="%fmm" viewBox="%i %i %i %i" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect x="%i" y="%i" width="%i" height="%i" fill="white"/>\n\n' % (diagram_width, diagram_height, self.passage_x, self.passage_y, self.passage_width, self.passage_height, self.passage_x, self.passage_y, self.passage_width, self.passage_height)
		else:
			diagram_height = self.height / (self.width / diagram_width)
			svg = '<svg width="%fmm" height="%fmm" viewBox="0 0 %i %i" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1">\n\n<rect width="%i" height="%i" fill="white"/>\n\n' % (diagram_width, diagram_height, self.width, self.height, self.width, self.height)
		svg += self.svg
		svg += '</svg>'
		with open(output_path, mode='w', encoding='utf-8') as file:
			file.write(svg)
		if not output_path.endswith('.svg'):
			convert_svg(output_path, output_path, png_width=diagram_width)


def convert_svg(svg_file_path, out_file_path, png_width=1000):
	filename, extension = path.splitext(out_file_path)
	if extension == '.pdf':
		call([INKSCAPE_BINARY, svg_file_path, '-A', out_file_path, '--export-text-to-path'], stdout=DEVNULL, stderr=STDOUT)
	elif extension == '.eps':
		call([INKSCAPE_BINARY, svg_file_path, '-E', out_file_path, '--export-text-to-path'], stdout=DEVNULL, stderr=STDOUT)
	elif extension == '.png':
		call([INKSCAPE_BINARY, svg_file_path, '-e', out_file_path, '--export-width=%i'%png_width], stdout=DEVNULL, stderr=STDOUT)
	else:
		raise ValueError('Cannot save to this format. Use either .pdf, .eps, or .png')

def normalize_min_max(distribution):
	return (distribution - distribution.min()) / (distribution.max() - distribution.min())
