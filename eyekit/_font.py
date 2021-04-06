import re
import cairocffi as cairo


class Font(object):

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
        self.toy_font_face = cairo.ToyFontFace(self.family, slant, weight)
        self.scaled_font = cairo.ScaledFont(
            self.toy_font_face, cairo.Matrix(xx=self.size, yy=self.size)
        )

    def calculate_width(self, text):
        return self.scaled_font.text_extents(text)[4]

    def calculate_height(self, text):
        return self.scaled_font.text_extents(text)[3]

    def get_descent(self):
        return self.scaled_font.extents()[1]
