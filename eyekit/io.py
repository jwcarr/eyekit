'''

Functions for reading and writing data.

'''


from os import listdir as _listdir
from os import path as _path
import re as _re
import json as _json
from .fixation import FixationSequence as _FixationSequence
from .fixation import _FixationSequenceEncoder
from .text import TextBlock as _TextBlock

def read(file_path):
	'''

	Read in an Eyekit JSON file with the following structure:

	```
	{
	  "trial_0" : {
	    "participant_id" : "John",
	    "passage_id" : "passage_a",
	    "fixations" : [[412, 142, 131], ..., [588, 866, 224]]
	  },
	  "trial_1" : {
	    "participant_id" : "Mary",
	    "passage_id" : "passage_b",
	    "fixations" : [[368, 146, 191], ..., [725, 681, 930]]
	  }
	}
	```

	Lists of fixations are automatically converted into
	`FixationSequence` objects.
	
	'''
	with open(file_path) as file:
		data = _json.load(file)
	for trial_id, trial in data.items():
		if 'fixations' in trial:
			trial['fixations'] = _FixationSequence(trial['fixations'])
	return data

def write(data, file_path, indent=None):
	'''

	Write out to an Eyekit JSON file. `FixationSequence` objects are
	automatically serialized. Optionally, the `indent` parameter
	specifies how much indentation to use in the files.
	
	'''
	with open(file_path, 'w') as file:
		_json.dump(data, file, cls=_FixationSequenceEncoder, indent=indent)

def load_texts(file_path):
	'''

	Load texts from a JSON file with the following structure:

	```
	{
	  "sentence_0" : {
	    "first_character_position" : [368, 155],
	    "character_spacing" : 16,
	    "line_spacing" : 64,
	    "fontsize" : 28,
	    "text" : "The quick brown fox jumped over the lazy dog."
	  },
	  "sentence_1" : {
	    "first_character_position" : [368, 155],
	    "character_spacing" : 16,
	    "line_spacing" : 64,
	    "fontsize" : 28,
	    "text" : "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
	  }
	}
	```

	`TextBlock` objects are created automatically, resulting in the dictionary:

	```
	{
	  "sentence_0" : TextBlock[The quick brown ...],
	  "sentence_1" : TextBlock[Lorem ipsum dolo...]
	}
	```

	'''
	texts = {}
	with open(file_path) as file:
		data = _json.load(file)
	for text_id, text in data.items():
		texts[text_id] = _TextBlock(**text)
	return texts

def import_asc(file_path, trial_begin_var, trial_begin_vals, extract_vars=[]):
	'''

	Import a single ASC file or a directory of ASC files. The importer
	looks for a `trial_begin_var` that is set to one of the
	`trial_begin_vals`, and then extracts all `EFIX` lines that occur
	within the subsequent `START`–`END` block. Optionally, you can
	specify other variables that you want to extract, resulting in
	imported data that looks like this:
	```
	{
	  "trial_0" : {
	    "trial_type" : "Experimental",
	    "passage_id" : "passage_a",
	    "response" : "yes",
	    "fixations" : FixationSequence[[368, 161, 208], ..., [562, 924, 115]]
	  }
	}
	```
	
	'''
	if _path.isfile(file_path):
		file_paths = [file_path]
	else:
		file_paths = [_path.join(file_path, filename) for filename in _listdir(file_path) if filename.endswith('.asc')]
	if isinstance(trial_begin_vals, str):
		trial_begin_vals = [trial_begin_vals]
	trial_line_regex = _re.compile(r'^.+?TRIAL_VAR\s(?P<var>(' + '|'.join([trial_begin_var] + extract_vars) + r')?)\s(?P<val>.+?)$')
	efix_line_regex = _re.compile(r'^EFIX R\s+(?P<stime>.+?)\s+(?P<etime>.+?)\s+(?P<duration>.+?)\s+(?P<x>.+?)\s+(?P<y>.+?)\s')
	data = {}
	for file_path in file_paths:
		curr_trial = {}
		start_flag = False
		with open(file_path) as file:
			for line in file:
				if start_flag:
					if line.startswith('EFIX'):
						line_match = efix_line_regex.match(line)
						if line_match:
							curr_trial['fixations'].append((int(round(float(line_match['x']), 0)), int(round(float(line_match['y']), 0)), int(line_match['duration'])))
					elif line.startswith('END'):
						curr_trial['fixations'] = _FixationSequence(curr_trial['fixations'])
						data['trial_%i'%len(data)] = curr_trial
						start_flag = False
						curr_trial = {}
				else:
					if line.startswith('MSG'):
						line_match = trial_line_regex.match(line)
						if line_match:
							if line_match['var'] == trial_begin_var and line_match['val'] not in trial_begin_vals:
								continue
							curr_trial[line_match['var']] = line_match['val']
					elif line.startswith('START') and trial_begin_var in curr_trial:
						start_flag = True
						curr_trial['fixations'] = []
	return data
