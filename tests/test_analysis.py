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


def test_number_of_regressions_in():
    txt = eyekit.TextBlock(
        "The quick brown [fox]{ia} jumps over the lazy dog",
        position=(500, 250),
        align="center",
        anchor="center",
    )

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (391, 240, 200, 300),
            (451, 250, 300, 400),  # first fixation in the IA
            (512, 240, 400, 500),  # first fixation to exit the IA
            (578, 250, 500, 600),
            (632, 240, 600, 700),
            (686, 250, 700, 800),
            (740, 240, 800, 900),
            (460, 245, 900, 1000),  # fixation that regresses back to the IA
        ]
    )
    assert eyekit.analysis.number_of_regressions_in(txt["ia"], seq)["ia"] == 1

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (391, 240, 200, 300),
            (451, 250, 300, 400),  # first fixation in the IA
            (512, 240, 400, 500),  # first fixation to exit the IA
            (578, 250, 500, 600),
            (632, 240, 600, 700),
            (455, 240, 700, 800),  # now the first regression to the IA
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # second regression to the IA
        ]
    )
    assert eyekit.analysis.number_of_regressions_in(txt["ia"], seq)["ia"] == 2

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (391, 240, 200, 300),
            (451, 250, 300, 400),  # first fixation in the IA
            (512, 240, 400, 500),  # first fixation to exit the IA
            (578, 250, 500, 600),
            (632, 240, 600, 700),
            (455, 240, 700, 800),  # now the first regression to the IA
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # second regression to the IA
            (7450, 255, 1100, 1200),
            (452, 240, 1200, 1300),  # third regression
        ]
    )
    assert eyekit.analysis.number_of_regressions_in(txt["ia"], seq)["ia"] == 3

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 150),
            (453, 245, 150, 200),  # technically the first fixation
            (391, 240, 200, 300),
            (451, 250, 300, 400),  # first real fixation in the IA
            (512, 240, 400, 500),  # first fixation to exit the IA
            (578, 250, 500, 600),
            (632, 240, 600, 700),
            (455, 240, 700, 800),  # first regression to the IA
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # second regression to the IA
        ]
    )
    assert eyekit.analysis.number_of_regressions_in(txt["ia"], seq)["ia"] == 2

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 150),
            (453, 245, 150, 200),  # technically the first fixation
            (391, 240, 200, 300),
            (451, 250, 300, 400),  # first real fixation in the IA
            (512, 240, 400, 500),  # first fixation to exit the IA
            (578, 250, 500, 600),
            (632, 240, 600, 700),
            (455, 240, 700, 800),  # first regression to the IA
            (460, 245, 800, 900),  # second fixation of the regression
            (686, 250, 900, 1000),
            (740, 240, 1000, 1100),
        ]
    )
    assert eyekit.analysis.number_of_regressions_in(txt["ia"], seq)["ia"] == 1


def test_go_past_time():
    txt = eyekit.TextBlock(
        "The quick brown [fox]{ia} jumps over the lazy dog.",
        position=(500, 250),
        align="center",
        anchor="center",
    )

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (391, 240, 200, 300),
            (451, 250, 300, 450),  # first fixation in the IA
            (454, 240, 450, 500),  # second fixation in the IA
            (512, 240, 500, 600),  # first fixation to exit the IA
            (578, 250, 600, 700),
            (632, 240, 700, 800),
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # regression back to the IA
        ]
    )
    assert eyekit.analysis.go_past_time(txt["ia"], seq)["ia"] == 200

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (391, 240, 200, 300),
            (451, 250, 300, 450),  # first fixation in the IA
            (512, 240, 450, 600),  # first fixation to exit the IA
            (578, 250, 600, 700),
            (632, 240, 700, 800),
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # regression back to the IA
        ]
    )
    assert eyekit.analysis.go_past_time(txt["ia"], seq)["ia"] == 150

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (451, 250, 200, 250),  # first fixation in the IA
            (391, 240, 250, 400),  # first fixation to exit the IA
            (455, 245, 400, 450),  # second fixation in the IA
            (512, 240, 450, 600),  # second exit from IA
            (578, 250, 600, 700),
            (632, 240, 700, 800),
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # regression back to the IA
        ]
    )
    assert eyekit.analysis.go_past_time(txt["ia"], seq)["ia"] == 250


def test_second_pass_duration():
    txt = eyekit.TextBlock(
        "The quick brown [fox]{ia} jumps over the lazy dog.",
        position=(500, 250),
        align="center",
        anchor="center",
    )

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (391, 240, 200, 300),
            (451, 250, 300, 450),  # first fixation in the IA
            (454, 240, 450, 500),  # second fixation in the IA
            (512, 240, 500, 600),  # first fixation to exit the IA
            (578, 250, 600, 700),
            (632, 240, 700, 800),
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # regression back to the IA
        ]
    )
    assert eyekit.analysis.second_pass_duration(txt["ia"], seq)["ia"] == 100

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (391, 240, 200, 300),
            (451, 250, 300, 450),  # first fixation in the IA
            (512, 240, 450, 600),  # first fixation to exit the IA
            (578, 250, 600, 700),
            (632, 240, 700, 800),
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # regression back to the IA
            (460, 245, 1100, 1200),  # second fixation in second pass
        ]
    )
    assert eyekit.analysis.second_pass_duration(txt["ia"], seq)["ia"] == 200

    seq = eyekit.FixationSequence(
        [
            (259, 240, 0, 100),
            (319, 250, 100, 200),
            (451, 250, 200, 250),  # first fixation in the IA
            (391, 240, 250, 400),  # first fixation to exit the IA
            (455, 245, 400, 450),  # second fixation in the IA
            (512, 240, 450, 600),  # second exit from IA
            (578, 250, 600, 700),
            (632, 240, 700, 800),
            (686, 250, 800, 900),
            (740, 240, 900, 1000),
            (460, 245, 1000, 1100),  # regression back to the IA
        ]
    )
    assert eyekit.analysis.second_pass_duration(txt["ia"], seq)["ia"] == 50
