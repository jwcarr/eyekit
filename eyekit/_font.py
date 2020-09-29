import re
import cairocffi as cairo

regex_italic = re.compile(' italic', re.IGNORECASE)
regex_bold = re.compile(' bold', re.IGNORECASE)

class Font:

	'''

	Wrapper around Cairo's font selection mechanism.

	'''

	def __init__(self, face, size):
		if regex_italic.search(face):
			self.font_slant = 'italic'
			slant = cairo.FONT_SLANT_ITALIC
			face = regex_italic.sub('', face)
		else:
			self.font_slant = 'normal'
			slant = cairo.FONT_SLANT_NORMAL
		if regex_bold.search(face):
			self.font_weight = 'bold'
			weight = cairo.FONT_WEIGHT_BOLD
			face = regex_bold.sub('', face)
		else:
			self.font_weight = 'normal'
			weight = cairo.FONT_WEIGHT_NORMAL
		self.font_family = face.strip()
		self.font_size = float(size)
		self.font_face = cairo.ToyFontFace(self.font_family, slant, weight)
		self._scaled_font = cairo.ScaledFont(self.font_face, cairo.Matrix(xx=self.font_size, yy=self.font_size))

	def character_width(self, char):
		return self._scaled_font.text_extents(char)[4]
		
	def character_height(self, char):
		return self._scaled_font.text_extents(char)[3]
