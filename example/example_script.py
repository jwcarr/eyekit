'''

Eyekit example script. Load in some fixation data and the associated texts.
For each trial, produce a pdf showing the relevant text overlaid with the
fixation sequence.

'''

import eyekit

data = eyekit.io.read('example_data.json')
texts = eyekit.io.read('example_texts.json')

for trial_id, trial in data.items():
	passage_id = trial['passage_id']
	txt = texts[passage_id]['text']
	img = eyekit.Image(1920, 1080)
	img.render_text(txt)
	img.render_fixations(trial['fixations'])
	img.save(f'{trial_id}.pdf')
