'''
.. include:: ../.GUIDE.md
   :start-line: 2
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
