'''

Eyekit is a lightweight Python package for doing open,
transparent, reproducible science on reading behavior. Eyekit is
entirely independent of any particular eyetracker hardware,
presentation software, or data formats, and has a minimal set of
dependencies. It has an object-oriented style that defines two core
objects – the TextBlock and the FixationSequence – that you bring into
contact with a bit of coding. Eyekit is currently in the pre-alpha
stage and is licensed under the terms of the MIT License.

.. include:: ../.README.md
   :start-line: 5
'''

from .fixation import FixationSequence
from .image import Image
from .text import TextBlock, set_default_alphabet
from . import analysis
from . import io
from . import tools

try:
	from ._version import __version__
except ImportError:
	__version__ = '???'

ALPHABETS = {
	'Dutch': 'A-Za-z',
	'English': 'A-Za-z',
	'French': 'A-ZÇÉÀÈÙÂÊÎÔÛËÏÜŸŒa-zçéàèùâêîôûëïüÿœ',
	'German': 'A-ZÄÖÜa-zäöüß',
	'Greek': 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΣΤΥΦΧΨΩΆΈΉΊΌΎΏΪΫΪ́Ϋ́αβγδεζηθικλμνξοπρσςτυφχψωάέήίόύώϊϋΐΰ',
	'Italian': 'A-ZÀÉÈÍÌÓÒÚÙa-zàéèíìóòúù',
	'Polish': 'A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż',
	'Portuguese': 'A-ZÁÂÃÀÇÉÊÍÓÔÕÚa-záâãàçéêíóôõú',
	'Russian': 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя',
	'Spanish': 'A-ZÑÁÉÍÓÚÜa-zñáéíóúü'
}
