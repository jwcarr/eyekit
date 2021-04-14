"""

Functions for checking that a variable is of the correct Eyekit type.

"""


from .fixation import Fixation, FixationSequence
from .text import InterestArea, TextBlock


def fail(obj, expectation):
    raise TypeError(f"Expected {expectation}, got {obj.__class__.__name__}")


def is_Fixation(fixation):
    if not isinstance(fixation, Fixation):
        fail(fixation, "Fixation")


def is_FixationSequence(fixation_sequence):
    if not isinstance(fixation_sequence, FixationSequence):
        fail(fixation_sequence, "FixationSequence")


def is_InterestArea(interest_area):
    if not isinstance(interest_area, InterestArea):
        fail(interest_area, "InterestArea")


def is_TextBlock(text_block):
    if not isinstance(text_block, TextBlock):
        fail(text_block, "TextBlock")
