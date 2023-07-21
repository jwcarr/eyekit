from pathlib import Path
import eyekit
from eyekit._snap import methods


seq = eyekit.FixationSequence(
    [
        [106, 490, 0, 100],
        [190, 486, 100, 200],
        [230, 505, 200, 300],
        [298, 490, 300, 400],
        [361, 497, 400, 500],
        [430, 489, 500, 600],
        {"x": 450, "y": 505, "start": 600, "end": 700, "discarded": True},
        [492, 491, 700, 800],
        [562, 505, 800, 900],
        [637, 493, 900, 1000],
        [712, 497, 1000, 1100],
        [763, 487, 1100, 1200],
    ]
)

EXAMPLE_DATA = Path("example") / "example_data.json"
EXAMPLE_TEXTS = Path("example") / "example_texts.json"

sentence = "The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog."
txt = eyekit.TextBlock(
    sentence, position=(100, 500), font_face="Times New Roman", font_size=36
)


def test_initialization():
    assert seq[0].x == 106
    assert seq[0].y == 490
    assert seq[0].start == 0
    assert seq[0].end == 100
    assert seq[0].pupil_size == None
    assert seq[0].duration == 100
    assert seq[6].discarded == True
    assert seq.start == 0
    assert seq.end == 1200
    assert seq.duration == 1200


def test_serialize():
    data = seq.serialize()
    assert len(data) == len(seq)
    for fxn_a, fxn_b in zip(data, seq):
        assert fxn_a["x"] == fxn_b.x
        assert fxn_a["y"] == fxn_b.y
        assert fxn_a["start"] == fxn_b.start
        assert fxn_a["end"] == fxn_b.end
        if "discarded" in fxn_a:
            assert fxn_a["discarded"] == fxn_b.discarded


def test_iter_pairs():
    answers = [
        (106, 190),
        (190, 230),
        (230, 298),
        (298, 361),
        (361, 430),
        (430, 450),
        (450, 492),
        (492, 562),
        (562, 637),
        (637, 712),
        (712, 763),
    ]
    for (fix1, fix2), answer in zip(seq.iter_pairs(), answers):
        assert (fix1.x, fix2.x) == answer
    answers = [
        (106, 190),
        (190, 230),
        (230, 298),
        (298, 361),
        (361, 430),
        (430, 492),
        (492, 562),
        (562, 637),
        (637, 712),
        (712, 763),
    ]
    for (fix1, fix2), answer in zip(seq.iter_pairs(False), answers):
        assert (fix1.x, fix2.x) == answer


def test_discard_short_fixations():
    seq = eyekit.FixationSequence(
        [
            [106, 490, 0, 100],
            [190, 486, 100, 200],
            [230, 505, 200, 240],
            [298, 490, 300, 400],
            [361, 497, 400, 500],
            [430, 489, 500, 600],
            [450, 505, 600, 700],
            [492, 491, 700, 800],
            [562, 505, 800, 820],
            [637, 493, 900, 1000],
            [712, 497, 1000, 1100],
            [763, 487, 1100, 1200],
        ]
    )
    seq.discard_short_fixations(50)
    assert seq[2].discarded == True
    assert seq[8].discarded == True
    seq.purge()
    assert len(seq) == 10


def test_discard_long_fixations():
    seq = eyekit.FixationSequence(
        [
            [106, 490, 0, 100],
            [190, 486, 100, 200],
            [230, 505, 200, 300],
            [298, 490, 300, 900],
            [361, 497, 900, 1000],
            [430, 489, 1000, 1100],
            [450, 505, 1100, 1200],
            [492, 491, 1200, 1300],
            [562, 505, 1300, 1400],
            [637, 493, 1400, 2000],
            [712, 497, 2000, 2100],
            [763, 487, 2100, 2200],
        ]
    )
    seq.discard_long_fixations(500)
    assert seq[3].discarded == True
    assert seq[9].discarded == True
    seq.purge()
    assert len(seq) == 10


def test_discard_out_of_bounds_fixations():
    seq = eyekit.FixationSequence(
        [
            [106, 490, 0, 100],
            [190, 486, 100, 200],
            [230, 505, 200, 300],
            [298, 490, 300, 400],
            [1, 1, 400, 500],
            [430, 489, 500, 600],
            [450, 505, 600, 700],
            [492, 491, 700, 800],
            [562, 505, 800, 900],
            [1000, 1000, 900, 1000],
            [712, 497, 1000, 1100],
            [763, 487, 1100, 1200],
        ]
    )
    seq.discard_out_of_bounds_fixations(txt, 100)
    assert seq[4].discarded == True
    assert seq[9].discarded == True
    seq.purge()
    assert len(seq) == 10


def test_segment():
    seq = eyekit.FixationSequence(
        [
            [106, 490, 0, 100],
            [190, 486, 100, 200],
            [230, 505, 200, 300],
            [298, 490, 300, 400],
            [1, 1, 400, 500],
            [430, 489, 500, 600],
            [450, 505, 600, 700],
            [492, 491, 700, 800],
            [562, 505, 800, 900],
            [1000, 1000, 900, 1000],
            [712, 497, 1000, 1100],
            [763, 487, 1100, 1200],
        ]
    )
    subseqs = seq.segment([(0, 600), (600, 1200)])
    assert len(subseqs) == 2
    assert subseqs[0][0].x == 106
    assert subseqs[0][-1].x == 430
    assert subseqs[1][0].x == 450
    assert subseqs[1][-1].x == 763


def test_snap_to_lines_single():
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
    seq.snap_to_lines(txt)
    midline = int(txt.midlines[0])
    for fixation in seq:
        assert fixation.y == midline


def test_snap_to_lines_multi():
    example_data = eyekit.io.load(EXAMPLE_DATA)
    example_texts = eyekit.io.load(EXAMPLE_TEXTS)
    seq = example_data["trial_0"]["fixations"]
    txt = example_texts[example_data["trial_0"]["passage_id"]]["text"]
    midlines = [int(midline) for midline in txt.midlines]
    for method in methods:
        seq_copy = seq.copy()
        seq_copy.snap_to_lines(txt, method)
        for fixation in seq_copy:
            assert fixation.y in midlines
    delta, kappa = seq.snap_to_lines(txt, method=["chain", "cluster", "warp"])
    for fixation in seq:
        assert fixation.y in midlines
    assert str(delta)[:4] == "19.6"
    assert str(kappa)[:4] == "0.96"


def test_snap_to_lines_RtL():
    txt = eyekit.TextBlock(
        text=["דג סקרן שט לו בים זך,", "אך לפתע פגש חבורה", "נחמדה שצצה כך."],
        font_face="Arial",
        line_height=180,
        font_size=150,
        position=(1627, 440),
        right_to_left=True,
    )
    seq = eyekit.FixationSequence(
        [
            (1609, 387, 0, 100),
            (1329, 397, 100, 200),
            (1483, 358, 200, 300),
            (1010, 401, 300, 400),
            (903, 393, 400, 500),
            (701, 340, 500, 600),
            (495, 406, 600, 700),
            (1612, 595, 700, 800),
            (1245, 575, 800, 900),
            (1410, 592, 900, 1000),
            (1001, 600, 1000, 1100),
            (701, 573, 1100, 1200),
            (784, 544, 1200, 1300),
            (1469, 828, 1300, 1400),
            (1521, 775, 1400, 1500),
            (1043, 755, 1500, 1600),
            (1202, 742, 1600, 1700),
            (777, 714, 1700, 1800),
        ]
    )
    correct_Ys = [
        401,
        401,
        401,
        401,
        401,
        401,
        401,
        581,
        581,
        581,
        581,
        581,
        581,
        761,
        761,
        761,
        761,
        761,
    ]
    for method in methods:
        seq_copy = seq.copy()
        seq_copy.snap_to_lines(txt, method)
        for fixation, correct_y in zip(seq_copy, correct_Ys):
            assert fixation.y == correct_y


def test_sequence_modifications():
    seq = eyekit.FixationSequence(
        [
            [106, 490, 0, 100],
            [190, 486, 100, 200],
        ]
    )
    seq[0].x = 107
    assert seq[0].x == 107
    seq[0].y = 491
    assert seq[0].y == 491
    seq[0].start = 1
    assert seq[0].start == 1
    seq[0].end = 99
    assert seq[0].end == 99
    seq[0].shift_x(10)
    assert seq[0].x == 117
    seq[0].shift_x(-20)
    assert seq[0].x == 97
    seq[0].shift_y(10)
    assert seq[0].y == 501
    seq[0].shift_y(-20)
    assert seq[0].y == 481
    seq[0].shift_time(+1)
    assert seq[0].start == 2
    assert seq[0].end == 100
    seq.shift_x(10)
    assert seq[0].x == 107
    assert seq[1].x == 200
    seq.shift_y(10)
    assert seq[0].y == 491
    assert seq[1].y == 496
    seq.shift_time(10)
    assert seq[0].start == 12
    assert seq[0].end == 110
    assert seq[1].start == 110
    assert seq[1].end == 210
    seq.shift_start_time_to_zero()
    assert seq[0].start == 0
    assert seq[0].end == 98
    assert seq.start == 0
    assert seq.end == 198


def test_empty_sequence():
    seq = eyekit.FixationSequence([])
    assert seq.start == 0
    assert seq.end == 0
    assert seq.duration == 0


def test_fixation_sequence_concatenation():
    seq1 = eyekit.FixationSequence(
        [
            [106, 490, 0, 100],
            [190, 486, 100, 200],
        ]
    )
    seq2 = eyekit.FixationSequence(
        [
            [230, 505, 200, 300],
            [298, 490, 300, 400],
        ]
    )
    seq = seq1 + seq2
    assert seq.start == 0
    assert seq.end == 400
    for fixation, correct_x in zip(seq, [106, 190, 230, 298]):
        assert fixation.x == correct_x


def test_tagging():
    seq = eyekit.FixationSequence(
        [
            [106, 490, 0, 100],
            [190, 486, 100, 200],
        ]
    )
    seq[0].add_tag("first fixation")
    seq[-1].add_tag("last fixation")
    assert seq[0].has_tag("first fixation") == True
    assert seq[-1].has_tag("last fixation") == True
    assert seq[0]["first fixation"] == True
    assert seq[-1]["last fixation"] == True
    del seq[0]["first fixation"]
    assert seq[0].has_tag("first fixation") == False
    seq[0]["fixation_number"] = 1
    seq[1]["fixation_number"] = 2
    assert seq[0].has_tag("fixation_number") == True
    assert seq[0].has_tag("fixation_number") == True
    assert seq[0]["fixation_number"] == 1
    assert seq[1]["fixation_number"] == 2
