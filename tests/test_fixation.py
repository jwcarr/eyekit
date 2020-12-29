import eyekit

seq = eyekit.FixationSequence(
    [
        [106, 490, 0, 100],
        [190, 486, 100, 200],
        [230, 505, 200, 300],
        [298, 490, 300, 400],
        [361, 497, 400, 500],
        [430, 489, 500, 600],
        [450, 505, 600, 700, True],
        [492, 491, 700, 800],
        [562, 505, 800, 900],
        [637, 493, 900, 1000],
        [712, 497, 1000, 1100],
        [763, 487, 1100, 1200],
    ]
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
    data = seq._serialize()
    assert len(data) == len(seq)
    for fxn_a, fxn_b in zip(data, seq):
        assert fxn_a[0] == fxn_b.x
        assert fxn_a[1] == fxn_b.y
        assert fxn_a[2] == fxn_b.start
        assert fxn_a[3] == fxn_b.end
        if len(fxn_a) == 5:
            assert fxn_b.discarded == True
