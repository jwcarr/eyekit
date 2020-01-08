from .fixation import Fixation
from .passage import Passage
from .diagram import Diagram

def set_alphabet(alphabet):
	for char in alphabet:
		if not isinstance(char, str) or len(char) != 1:
			raise ValueError('Invalid alphabet. Should be list of 1-character strings.')
	passage.ALPHABET = alphabet

def set_special_characters(special_characters):
	for char, mapped_char in special_characters.items():
		if not isinstance(char, str) or len(char) != 1 or not isinstance(mapped_char, str) or len(mapped_char) != 1:
			raise ValueError('Invalid alphabet. Should be dictionary of 1-character strings mapped to 1-character strings.')
	passage.SPECIALS = special_characters

def fixation_sequence(fixation_data, gamma=30, min_duration=0):
	return [Fixation(x, y, d, gamma) for x, y, d in fixation_data if d > min_duration]
