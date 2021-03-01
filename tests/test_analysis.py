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
        [492, 491, 1200, 1300],
    ]
)


def test_number_of_fixations():
    results = eyekit.analysis.number_of_fixations(txt.zones(), seq)
    assert results["stem_1"] == 2
    assert results["suffix_1"] == 2


def test_initial_fixation_duration():
    results = eyekit.analysis.initial_fixation_duration(txt.zones(), seq)
    assert results["stem_1"] == 100
    assert results["suffix_1"] == 100


def test_total_fixation_duration():
    results = eyekit.analysis.total_fixation_duration(txt.zones(), seq)
    assert results["stem_1"] == 200
    assert results["suffix_1"] == 200


def test_gaze_duration():
    results = eyekit.analysis.gaze_duration(txt.zones(), seq)
    assert results["stem_1"] == 200
    assert results["suffix_1"] == 100


def test_initial_landing_position():
    results = eyekit.analysis.initial_landing_position(txt.zones(), seq)
    assert results["stem_1"] == 2
    assert results["suffix_1"] == 1


def test_initial_landing_distance():
    results = eyekit.analysis.initial_landing_distance(txt.zones(), seq)
    assert int(results["stem_1"]) == 18
    assert int(results["suffix_1"]) == 6


def test_number_of_regressions():
    results = eyekit.analysis.number_of_regressions(txt.zones(), seq)
    assert results["stem_1"] == 0
    assert results["suffix_1"] == 1
