import eyekit

data = eyekit.io.read('example/example_data.json')
texts = eyekit.io.read('example/example_texts.json')

def test_read():
	assert isinstance(data['trial_0']['fixations'], eyekit.FixationSequence)
	assert isinstance(data['trial_1']['fixations'], eyekit.FixationSequence)
	assert isinstance(data['trial_2']['fixations'], eyekit.FixationSequence)
	assert data['trial_0']['fixations'][0].x == 412
	assert data['trial_0']['fixations'][1].y == 163
	assert data['trial_0']['fixations'][2].duration == 334
	assert isinstance(texts['passage_a']['text'], eyekit.TextBlock)
	assert isinstance(texts['passage_b']['text'], eyekit.TextBlock)
	assert isinstance(texts['passage_c']['text'], eyekit.TextBlock)
	assert texts['passage_a']['text'].position == (360, 161)
	assert texts['passage_a']['text'].font_face == 'Courier New'
