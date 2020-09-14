'''

Eyekit is a Python package for handling, analyzing, and visualizing
eyetracking data from reading experiments. Eyekit is currently in the
pre-alpha stage and is licensed under the terms of the MIT License.

.. include:: ../README.md
   :start-line: 5
'''

from pkg_resources import get_distribution as _get_distribution
from .fixation import FixationSequence
from .image import Image
from .text import TextBlock
from . import analysis
from . import io
from . import tools

try:
	__version__ = _get_distribution('eyekit').version
except:
	__version__ = None

# def get_case_sensitive():
# 	return text.CASE_SENSITIVE

# def set_case_sensitive(case_sensitive):
# 	text.CASE_SENSITIVE = case_sensitive

# def get_alphabet():
# 	return text.ALPHABET

# def set_alphabet(alphabet):
# 	for char in alphabet:
# 		if not isinstance(char, str) or len(char) != 1:
# 			raise ValueError('Invalid alphabet. Should be list of 1-character strings.')
# 	text.ALPHABET = alphabet

# def get_special_characters():
# 	return text.SPECIAL_CHARACTERS

# def set_special_characters(special_characters):
# 	for char, mapped_char in special_characters.items():
# 		if not isinstance(char, str) or len(char) != 1 or not isinstance(mapped_char, str) or len(mapped_char) != 1:
# 			raise ValueError('Invalid alphabet. Should be dictionary of 1-character strings mapped to 1-character strings.')
# 	text.SPECIAL_CHARACTERS = special_characters


