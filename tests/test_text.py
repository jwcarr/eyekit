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
    assert txt.n_lines == 1
    assert txt.n_cols == 45
    assert len(txt) == 45
    assert txt.baselines[0] == 500


def test_IA_extraction():
    assert txt["stem_1"].id == "stem_1"
    assert txt["stem_1"].text == "jump"
    assert txt["stem_1"].baseline == 500
    assert int(txt["stem_1"].midline) == 491
    assert txt["stem_1"].height == 36
    assert txt["suffix_1"].id == "suffix_1"
    assert txt["suffix_1"].text == "ed"
    assert txt["suffix_1"].baseline == 500
    assert int(txt["suffix_1"].midline) == 491
    assert txt["suffix_1"].height == 36
    txt[0:4:19].id = "test_id"
    assert txt["test_id"].text == "quick brown fox"
    assert txt[0:4:19].id == "test_id"


def test_manual_ia_extraction():
    assert len(list(txt.interest_areas())) == 2
    for word in txt.interest_areas():
        assert word.text in ["jump", "ed"]
        assert word.baseline == 500
        assert word.height == 36


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
    assert txt[0::3].text == "The"
    assert txt[0:36:].text == "lazy dog."


def test_IA_location():
    assert txt[0:0:3].location == (0, 0, 3)
    assert txt[0:5:40].location == (0, 5, 40)


def test_IA_relative_positions():
    assert txt["stem_1"].is_right_of(seq[0]) == True
    assert txt["stem_1"].is_right_of(seq[-1]) == False
    assert txt["stem_1"].is_left_of(seq[-1]) == True
    assert txt["stem_1"].is_after(seq[0]) == True
    assert txt["stem_1"].is_before(seq[-1]) == True


def test_iter_pairs():
    interest_area = txt["stem_1"]
    for curr_fixation, next_fixation in seq.iter_pairs():
        if curr_fixation in interest_area and next_fixation not in interest_area:
            assert next_fixation.x == 492


def test_serialize():
    data = txt.serialize()
    assert data["text"] == [sentence]
    assert data["position"] == (100, 500)
    assert data["font_face"] == "Times New Roman"
    assert data["font_size"] == 36
    assert data["line_height"] == 36
    assert data["align"] == "left"
    assert data["anchor"] == "left"
    assert data["alphabet"] is None
    assert data["autopad"] == True


def test_complex_font_selection():
    txt = eyekit.TextBlock(
        sentence,
        position=(100, 500),
        font_face="Times New Roman bold italic",
        font_size=36,
    )
    assert txt._font.family == "Times New Roman"
    assert txt._font.slant == "italic"
    assert txt._font.weight == "bold"
    assert txt._font.size == 36


def test_align_and_anchor():
    positions = [
        ("left", "left", 1049),
        ("left", "center", 939),
        ("left", "right", 829),
        ("center", "left", 1061),
        ("center", "center", 951),
        ("center", "right", 841),
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


def test_right_to_left():
    txt = eyekit.TextBlock(
        text=["דג סקרן שט לו בים זך,", "אך לפתע פגש חבורה", "נחמדה שצצה כך."],
        position=(960, 540),
        font_face="Raanana bold",
        font_size=100,
        right_to_left=True,
        anchor="center",
    )
    for word, (logical_word, display_word, x, y) in zip(
        txt.words(),
        [
            ("דג", "גד", 1334, 502),
            ("סקרן", "ןרקס", 1176, 502),
            ("שט", "טש", 997, 502),
            ("לו", "ול", 875, 502),
            ("בים", "םיב", 745, 502),
            ("זך", "ךז", 611, 502),
            ("אך", "ךא", 1321, 602),
            ("לפתע", "עתפל", 1143, 602),
            ("פגש", "שגפ", 945, 602),
            ("חבורה", "הרובח", 732, 602),
            ("נחמדה", "הדמחנ", 1254, 702),
            ("שצצה", "הצצש", 1002, 702),
            ("כך", "ךכ", 824, 702),
        ],
    ):
        assert word.text == logical_word
        assert word.display_text == display_word
        assert int(word.x) == x
        assert int(word.y) == y


def test_custom_padding():
    txt = eyekit.TextBlock(
        text=["The quick brown", "fox [jumps]{target} over", "the lazy dog"],
        position=(960, 540),
        font_face="Arial",
        font_size=30,
        autopad=False,
    )
    assert txt["target"].padding == [0, 0, 0, 0]
    txt["target"].set_padding(top=10, bottom=10, left=10, right=10)
    assert txt["target"].padding == [10, 10, 10, 10]
    txt["target"].adjust_padding(top=2, bottom=2, left=-2, right=-2)
    assert txt["target"].padding == [12, 12, 8, 8]
