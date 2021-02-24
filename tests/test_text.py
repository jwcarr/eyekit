import eyekit
from eyekit.text import _Font

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


def test_initialization():
    assert txt.position == (100, 500)
    assert txt.font_face == "Times New Roman"
    assert txt.font_size == 36
    assert txt.line_height == 36
    assert txt.align == "left"
    assert txt.anchor == "left"
    assert txt.alphabet is None
    assert txt.autopad == True
    assert txt.n_rows == 1
    assert txt.n_cols == 45
    assert len(txt) == 45


def test_zone_extraction():
    assert len(list(txt.zones())) == 2
    for zone in txt.zones():
        assert zone.id in ["stem_1", "suffix_1"]
        assert zone.text in ["jump", "ed"]
        assert zone.baseline == 500
        assert zone.height == 36


def test_zone_find():
    assert txt["stem_1"].text == "jump"
    assert txt["suffix_1"].text == "ed"
    txt[0:4:19].id = "test_id"
    assert txt["test_id"].text == "quick brown fox"
    assert txt[0:4:19].id == "test_id"


def test_word_extraction():
    assert len(list(txt.words())) == 9
    for word in txt.words():
        assert word.text in [
            "The",
            "quick",
            "brown",
            "fox",
            "jumped",
            "over",
            "the",
            "lazy",
            "dog",
        ]
        assert word.baseline == 500
        assert word.height == 36


def test_arbitrary_extraction():
    assert txt[0:0:3].text == "The"
    assert txt["0:0:3"].text == "The"
    assert txt[(0, 0, 3)].text == "The"
    assert txt[0:41:45].text == "dog."
    assert txt["0:41:45"].text == "dog."
    assert txt[(0, 41, 45)].text == "dog."
    assert txt[0:4:19].text == "quick brown fox"
    assert txt["0:4:19"].text == "quick brown fox"
    assert txt[(0, 4, 19)].text == "quick brown fox"


def test_IA_location():
    assert txt[0:0:3].location == (0, 0, 3)
    assert txt[0:5:40].location == (0, 5, 40)


def test_which_methods():
    for fixation, answer in zip(
        seq,
        [
            "The",
            "quick",
            "quick",
            "brown",
            "fox",
            "jumped",
            "jumped",
            "jumped",
            "over",
            "the",
            "lazy",
            "dog",
        ],
    ):
        assert txt.which_word(fixation).text == answer
    for fixation, answer in zip(
        seq, ["T", "u", "k", "o", "f", "u", "m", "e", "v", "e", "y", "g"]
    ):
        assert txt.which_character(fixation).text == answer
        assert txt.which_line(fixation).id == "0:0:45"


def test_iter_pairs():
    interest_area = txt["stem_1"]
    for curr_fixation, next_fixation in seq.iter_pairs():
        if curr_fixation in interest_area and next_fixation not in interest_area:
            assert next_fixation.x == 492


def test_serialize():
    data = txt._serialize()
    assert data["text"] == [sentence]
    assert data["position"] == (100, 500)
    assert data["font_face"] == "Times New Roman"
    assert data["font_size"] == 36
    assert data["line_height"] == 36
    assert data["align"] == "left"
    assert data["anchor"] == "left"
    assert data["alphabet"] is None
    assert data["autopad"] == True


def test_Font():
    font = _Font("Helvetica Neue bold italic", 12)
    assert font.family == "Helvetica Neue"
    assert font.slant == "italic"
    assert font.weight == "bold"
    assert font.size == 12


def test_align_and_anchor():
    positions = [
        ("left", "left", 1048),
        ("left", "center", 938),
        ("left", "right", 828),
        ("center", "left", 1060),
        ("center", "center", 950),
        ("center", "right", 840),
        ("right", "left", 1073),
        ("right", "center", 963),
        ("right", "right", 853),
    ]
    for align, anchor, target_x in positions:
        txt = eyekit.TextBlock(
            text=["The quick brown", "fox [jumps]{target} over", "the lazy dog"],
            position=(960, 540),
            font_face="Arial",
            font_size=30,
            align=align,
            anchor=anchor,
        )
        assert txt.align == align
        assert txt.anchor == anchor
        assert int(txt["target"].x) == target_x
