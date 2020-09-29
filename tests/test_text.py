import eyekit

sentence = 'The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.'
txt = eyekit.TextBlock(sentence, position=(100, 500), font_face='Times New Roman', font_size=36)
seq = eyekit.FixationSequence([[106, 490, 100], [190, 486, 100], [230, 505, 100], [298, 490, 100], [361, 497, 100], [430, 489, 100], [450, 505, 100], [492, 491, 100], [562, 505, 100], [637, 493, 100], [712, 497, 100], [763, 487, 100]])

def test_parameter_setup():
	assert txt.position == (100, 500)
	assert txt.font_face == 'Times New Roman'
	assert txt.font_size == 36
	assert txt.line_height == 36
	assert txt.alphabet is None

def test_zone_extraction():
	assert len(list(txt.zones())) == 2
	for zone in txt.zones():
		assert zone.id in ['stem_1', 'suffix_1']
		assert zone.text in ['jump', 'ed']
		assert zone.baseline == 500
		assert zone.height == 36

def test_word_extraction():
	assert len(list(txt.words())) == 9
	for word in txt.words():
		assert word.text in ['The', 'quick', 'brown', 'fox', 'jumped', 'over', 'the', 'lazy', 'dog']
		assert word.baseline == 500
		assert word.height == 36

def test_analysis_functions():
	results = eyekit.analysis.initial_fixation_duration(txt.zones(), seq)
	assert results['stem_1'] == 100
	assert results['suffix_1'] == 100
	results = eyekit.analysis.total_fixation_duration(txt.zones(), seq)
	assert results['stem_1'] == 200
	assert results['suffix_1'] == 100
	results = eyekit.analysis.initial_landing_position(txt.zones(), seq)
	assert results['stem_1'] == 2
	assert results['suffix_1'] == 1
	results = eyekit.analysis.initial_landing_x(txt.zones(), seq)
	assert int(results['stem_1']) == int(18)
	assert int(results['suffix_1']) == int(6)
