'''

Functions for reading and writing data.

'''


from os import listdir as _listdir, path as _path
import re as _re
import json as _json
from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock

def read(file_path):
	'''

	Read in a JSON file. `eyekit.fixation.FixationSequence` and
	`eyekit.text.TextBlock` objects are automatically decoded and instantiated.
	
	'''
	with open(file_path, encoding='utf-8') as file:
		data = _json.load(file, object_hook=_eyekit_decoder)
	return data

def write(data, file_path, compress=True):
	'''

	Write arbitrary data to a JSON file. If `compress` is `True`, the file is
	written in the most compact way; if `False`, the file will be larger but more
	human-readable. `eyekit.fixation.FixationSequence` and
	`eyekit.text.TextBlock` objects are automatically serialized.
	
	'''
	if compress:
		indent = None
		separators = (',', ':')
	else:
		indent = '\t'
		separators = (', ', ' : ')
	with open(file_path, 'w', encoding='utf-8') as file:
		_json.dump(data, file, default=_eyekit_encoder, ensure_ascii=False, indent=indent, separators=separators)

def import_asc(file_path, trial_begin_var, trial_begin_vals, extract_vars=[]):
	'''

	Import a single ASC file or a directory of ASC files. The importer looks for
	a `trial_begin_var` that is set to one of the `trial_begin_vals`, and then
	extracts all `EFIX` lines that occur within the subsequent `START`–`END`
	block. Optionally, you can specify other variables that you want to extract,
	resulting in imported data that looks like this:

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

def _eyekit_encoder(obj):
	'''
	Convert a `FixationSequence` or `TextBlock` object into something JSON
	serializable that can later be decoded by _eyekit_decoder().
	'''
	if isinstance(obj, _FixationSequence):
		return {'__FixationSequence__': obj._serialize()}
	if isinstance(obj, _TextBlock):
		return {'__TextBlock__': obj._serialize()}
	raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def _eyekit_decoder(obj):
	'''
	Decode an object into a `FixationSequence` or `TextBlock` if the key
	implies that it is one of those types.
	'''
	if '__FixationSequence__' in obj:
		return _FixationSequence(obj['__FixationSequence__'])
	if '__TextBlock__' in obj:
		return _TextBlock(**obj['__TextBlock__'])
	return obj
