import re
import cairocffi as cairo

regex_italic = re.compile(" italic", re.IGNORECASE)
regex_bold = re.compile(" bold", re.IGNORECASE)


class Font:

    """

    Wrapper around Cairo's font selection mechanism.

    """

    def __init__(self, face, size):
        if regex_italic.search(face):
            self.slant = "italic"
            slant = cairo.FONT_SLANT_ITALIC
            face = regex_italic.sub("", face)
        else:
            self.slant = "normal"
            slant = cairo.FONT_SLANT_NORMAL
        if regex_bold.search(face):
            self.weight = "bold"
            weight = cairo.FONT_WEIGHT_BOLD
            face = regex_bold.sub("", face)
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
