from eyekit import _font

def test_Font():
	font = _font.Font('Helvetica Neue bold italic', 12)
	assert font.font_family == 'Helvetica Neue'
	assert font.font_slant == 'italic'
	assert font.font_weight == 'bold'
	assert font.font_size == 12