import re as _re
import json as _json
from .fixation import FixationSequence

def read(file_path):
	'''
	Read in an eyekit JSON file.
	'''
	with open(file_path) as file:
		data = _json.load(file)
	for trial_id, trial in data['trials'].items():
		trial['fixations'] = FixationSequence(trial['fixations'])
	return data

def write(data, file_path, indent=False):
	'''
	Write out to an eyekit JSON file.
	'''
	for trial_id, trial in data['trials'].items():
		trial['fixations'] = trial['fixations'].tolist(include_discards=True)
	with open(file_path, 'w') as file:
		if indent:
			_json.dump(data, file, indent=4)
		else:
			_json.dump(data, file)

def import_asc(file_path, trial_begin_var, trial_begin_val, extract_variables=[]):
	'''
	Import an ASC file.
	'''
	if isinstance(trial_begin_val, str):
		trial_begin_val = [trial_begin_val]
	trial_line_regex = _re.compile(r'^.+?TRIAL_VAR\s(?P<var>(' + '|'.join([trial_begin_var] + extract_variables) + r')?)\s(?P<val>.+?)$')
	efix_line_regex = _re.compile(r'^EFIX R\s+(?P<stime>.+?)\s+(?P<etime>.+?)\s+(?P<duration>.+?)\s+(?P<x>.+?)\s+(?P<y>.+?)\s')
	data = {'header':'', 'trials':{}}
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
					curr_trial['fixations'] = FixationSequence(curr_trial['fixations'])
					data['trials'][str(len(data['trials']))] = curr_trial
					start_flag = False
					curr_trial = {}
			else:
				if line.startswith('MSG'):
					line_match = trial_line_regex.match(line)
					if line_match:
						if line_match['var'] == trial_begin_var and line_match['val'] not in trial_begin_val:
							continue
						curr_trial[line_match['var']] = line_match['val']
				elif line.startswith('START') and trial_begin_var in curr_trial:
					start_flag = True
					curr_trial['fixations'] = []
	return data
