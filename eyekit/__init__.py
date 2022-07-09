# Eyekit https://jwcarr.github.io/eyekit/
# Copyright (C) 2019-2022 Jon Carr

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or(at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.

"""
.. include:: ../.GUIDE.md
   :start-line: 2
"""

from .fixation import FixationSequence
from .text import TextBlock
from . import measure
from . import io
from . import tools
from . import vis

del fixation, text

__version__ = vis.__version__
