"""
Class for representing a font face in a particular size and style, and for
providing a convenient interface to Cairo's font selection mechanism.

Create font:
    my_font = _font.Font('Helvetica bold', 12)

Query some metrics:
    x_height = my_font.calculate_height('x')
    text_width = my_font.calculate_width('example')

Use the face in a Cairo context:
    context.set_font_face(my_font.face)
"""

import re
import cairocffi as cairo


class Font:
    """
    Wrapper around Cairo's font selection mechanism.
    """

    regex_italic = re.compile(" italic", re.IGNORECASE)
    regex_bold = re.compile(" bold", re.IGNORECASE)

    def __init__(self, face, size):
        if self.regex_italic.search(face):
            self.slant = "italic"
            slant = cairo.FONT_SLANT_ITALIC
            face = self.regex_italic.sub("", face)
        else:
            self.slant = "normal"
            slant = cairo.FONT_SLANT_NORMAL
        if self.regex_bold.search(face):
            self.weight = "bold"
            weight = cairo.FONT_WEIGHT_BOLD
            face = self.regex_bold.sub("", face)
        else:
            self.weight = "normal"
            weight = cairo.FONT_WEIGHT_NORMAL
        self.family = face.strip()
        self.size = float(size)
        self.face = cairo.ToyFontFace(self.family, slant, weight)
        self.scaled_font = cairo.ScaledFont(
            self.face, cairo.Matrix(xx=self.size, yy=self.size)
        )

    def calculate_width(self, text):
        """
        Return pixel width of a piece of text rendered in the font.
        """
        return self.scaled_font.text_extents(text)[4]

    def calculate_height(self, text):
        """
        Return pixel height of a piece of text rendered in the font.
        """
        return self.scaled_font.text_extents(text)[3]

    def get_descent(self):
        """
        Return the font's descent in pixels.
        """
        return self.scaled_font.extents()[1]
