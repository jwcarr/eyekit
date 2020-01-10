from .fixation import FixationSequence
from .passage import Passage
from .diagram import Diagram

def get_case_sensitive():
	return passage.CASE_SENSITIVE

def set_case_sensitive(case_sensitive):
	passage.CASE_SENSITIVE = case_sensitive

def get_alphabet():
	return passage.ALPHABET

def set_alphabet(alphabet):
	for char in alphabet:
		if not isinstance(char, str) or len(char) != 1:
			raise ValueError('Invalid alphabet. Should be list of 1-character strings.')
	passage.ALPHABET = alphabet

def get_special_characters():
	return passage.SPECIAL_CHARACTERS

def set_special_characters(special_characters):
	for char, mapped_char in special_characters.items():
		if not isinstance(char, str) or len(char) != 1 or not isinstance(mapped_char, str) or len(mapped_char) != 1:
			raise ValueError('Invalid alphabet. Should be dictionary of 1-character strings mapped to 1-character strings.')
	passage.SPECIAL_CHARACTERS = special_characters
