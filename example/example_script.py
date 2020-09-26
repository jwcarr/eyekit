'''

Eyekit example script. Load in some fixation data and the associated texts.
For each trial, produce a pdf showing the relevant text overlaid with the
fixation sequence.

'''

import eyekit

data = eyekit.io.read('example_data.json')
texts = eyekit.io.read('example_texts.json')

for trial_id, trial in data.items():
	seq = trial['fixations']
	passage_id = trial['passage_id']
	txt = texts[passage_id]['text']
	img = eyekit.Image(1920, 1080)
	img.draw_text_block(txt)
	img.draw_fixation_sequence(seq)
	img.save(f'{trial_id}.pdf')
