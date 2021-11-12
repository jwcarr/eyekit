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
