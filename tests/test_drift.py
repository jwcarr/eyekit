import eyekit


def test_single_line():
    sentence = "The quick brown fox jumped over the lazy dog."
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
    eyekit.tools.snap_to_lines(seq, txt)
    for fixation in seq:
        assert fixation.y == 491


def test_multi_line():
    example_data = eyekit.io.read("example/example_data.json")
    example_texts = eyekit.io.read("example/example_texts.json")
    seq = example_data["trial_0"]["fixations"]
    txt = example_texts[example_data["trial_0"]["passage_id"]]["text"]
    line_positions = list(map(int, txt.line_positions))
    for method in eyekit.tools._drift.methods:
        seq_copy = seq.copy()
        eyekit.tools.snap_to_lines(seq_copy, txt, method)
        for fixation in seq_copy:
            assert fixation.y in line_positions
