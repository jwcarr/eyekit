from pathlib import Path
import eyekit

EXAMPLE_DATA = Path("example") / "example_data.json"
EXAMPLE_TEXTS = Path("example") / "example_texts.json"

sentence = "The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog."
txt = eyekit.TextBlock(
    sentence, position=(100, 500), font_face="Times New Roman", font_size=36
)


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
    eyekit.tools.discard_short_fixations(seq, 50)
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
    eyekit.tools.discard_out_of_bounds_fixations(seq, txt, 100)
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
    eyekit.tools.snap_to_lines(seq, txt)
    midline = int(txt.midlines[0])
    for fixation in seq:
        assert fixation.y == midline


def test_snap_to_lines_multi():
    example_data = eyekit.io.read(EXAMPLE_DATA)
    example_texts = eyekit.io.read(EXAMPLE_TEXTS)
    seq = example_data["trial_0"]["fixations"]
    txt = example_texts[example_data["trial_0"]["passage_id"]]["text"]
    midlines = [int(midline) for midline in txt.midlines]
    for method in eyekit.tools._drift.methods:
        seq_copy = seq.copy()
        eyekit.tools.snap_to_lines(seq_copy, txt, method)
        for fixation in seq_copy:
            assert fixation.y in midlines


def test_font_size_at_72dpi():
    assert eyekit.tools.font_size_at_72dpi(15, 96) == 20
