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
from .text import TextBlock, set_default_alphabet
from . import analysis
from . import io
from . import tools

try:
	__version__ = _get_distribution('eyekit').version
except:
	__version__ = None
