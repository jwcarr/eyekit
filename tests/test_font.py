from eyekit import _font

def test_Font():
	font = _font.Font('Helvetica Neue bold italic', 12)
	assert font.family == 'Helvetica Neue'
	assert font.slant == 'italic'
	assert font.weight == 'bold'
	assert font.size == 12