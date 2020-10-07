import eyekit

sentence = 'The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.'
txt = eyekit.TextBlock(sentence, position=(100, 500), font_face='Times New Roman', font_size=36)
seq = eyekit.FixationSequence([[106, 490, 100], [190, 486, 100], [230, 505, 100], [298, 490, 100], [361, 497, 100], [430, 489, 100], [450, 505, 100], [492, 491, 100], [562, 505, 100], [637, 493, 100], [712, 497, 100], [763, 487, 100]])

def test_Image():
	img = eyekit.vis.Image(1920, 1080)
	img.set_caption('Quick Brown Fox', 'Helvetica Neue italic', 8)
	img.set_background_color('snow')
	img.draw_text_block(txt)
	for word in txt.words():
		img.draw_rectangle(word.box, color='crimson')
	img.draw_fixation_sequence(seq)
	img.draw_line((0, 0), (1920, 1080), color='coral', stroke_width=2, dashed=True)
	img.draw_circle(200, 200, 200)
	img.draw_annotation(1000, 500, 'Hello world!', font_face='Courier New', font_size=26, color='yellowgreen')
	# img.save('private/dump/test_image.pdf')
	fig = eyekit.vis.Figure(1, 2)
	fig.set_padding(vertical=10, horizontal=5, edge=2)
	fig.add_image(img)
	fig.add_image(img)
	# fig.save('private/dump/test_figure.pdf')

def test_mm_to_pts():
	assert str(eyekit.vis._mm_to_pts(1))[:5] == '2.834'
	assert str(eyekit.vis._mm_to_pts(10))[:5] == '28.34'

def test_color_to_rgb():
	assert eyekit.vis._color_to_rgb((255, 0, 0)) == (1.0, 0.0, 0.0)
	assert eyekit.vis._color_to_rgb('#FF0000') == (1.0, 0.0, 0.0)
	assert eyekit.vis._color_to_rgb('red') == (1.0, 0.0, 0.0)