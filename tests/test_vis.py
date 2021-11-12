from tempfile import TemporaryDirectory
from pathlib import Path
import eyekit

sentence = "The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog."
txt = eyekit.TextBlock(
    sentence, position=(100, 500), font_face="Times New Roman", font_size=36
)
seq = eyekit.FixationSequence(
    [
        [106, 490, 0, 100],
        [190, 486, 100, 200],
        [230, 505, 200, 300],
        [298, 490, 300, 400],
        [361, 497, 400, 500],
        [430, 489, 500, 600],
        [450, 505, 600, 700],
        [492, 491, 700, 800],
        [562, 505, 800, 900],
        [637, 493, 900, 1000],
        [712, 497, 1000, 1100],
        [763, 487, 1100, 1200],
    ]
)


def test_Image():
    img = eyekit.vis.Image(1920, 1080)
    img.set_caption("Quick Brown Fox", font_face="Helvetica Neue italic", font_size=8)
    img.set_background_color("snow")
    img.draw_text_block(txt)
    for word in txt.words():
        img.draw_rectangle(word.box, color="crimson")
    img.draw_fixation_sequence(seq)
    img.draw_line((0, 0), (1920, 1080), color="coral", stroke_width=2, dashed=True)
    img.draw_circle((200, 200), 200)
    img.draw_annotation(
        (1000, 500),
        "Hello world!",
        font_face="Courier New",
        font_size=26,
        color="yellowgreen",
    )
    with TemporaryDirectory() as temp_dir:
        img.save(Path(temp_dir) / "test_image.pdf")
        img.save(Path(temp_dir) / "test_image.eps")
        img.save(Path(temp_dir) / "test_image.svg")
        img.save(Path(temp_dir) / "test_image.png")
    fig = eyekit.vis.Figure(1, 2)
    fig.set_padding(vertical=10, horizontal=5, edge=2)
    fig.add_image(img)
    fig.add_image(img)
    with TemporaryDirectory() as temp_dir:
        fig.save(Path(temp_dir) / "test_figure.pdf")
        fig.save(Path(temp_dir) / "test_figure.eps")
        fig.save(Path(temp_dir) / "test_figure.svg")


def test_mm_to_pts():
    assert str(eyekit.vis._mm_to_pts(1))[:5] == "2.834"
    assert str(eyekit.vis._mm_to_pts(10))[:5] == "28.34"


def test_color_to_rgb():
    assert eyekit.vis._color_to_rgb("#FFFFFF", (0, 0, 0)) == (1.0, 1.0, 1.0)
    assert eyekit.vis._color_to_rgb("#ffffff", (0, 0, 0)) == (1.0, 1.0, 1.0)
    assert eyekit.vis._color_to_rgb("#000000", (0, 0, 0)) == (0.0, 0.0, 0.0)
    assert eyekit.vis._color_to_rgb("#01010", (0, 0, 0)) == (0, 0, 0)
    assert eyekit.vis._color_to_rgb("#red", (0, 0, 0)) == (0, 0, 0)
    assert eyekit.vis._color_to_rgb("blue", (0, 0, 0)) == (0.0, 0.0, 1.0)
    assert eyekit.vis._color_to_rgb("REd", (0, 0, 0)) == (1.0, 0.0, 0.0)
    assert eyekit.vis._color_to_rgb((0, 0, 255), (0, 0, 0)) == (0.0, 0.0, 1.0)
    assert eyekit.vis._color_to_rgb([0, 255, 0], (0, 0, 0)) == (0.0, 1.0, 0.0)
    assert eyekit.vis._color_to_rgb(0, (1, 0, 0)) == (1, 0, 0)
    assert eyekit.vis._color_to_rgb(1, (0, 1, 0)) == (0, 1, 0)
    assert eyekit.vis._color_to_rgb(255, (0, 0, 1)) == (0, 0, 1)
