from eyekit import _bidi

test_cases_LtR = [
    ("the cat sat on the mat.", "the cat sat on the mat."),
    ("the CAT sat on the mat.", "the TAC sat on the mat."),
    ("the CAT sat on 10 mats.", "the TAC sat on 10 mats."),
    ("the CAT sat on 10 MATS.", "the TAC sat on 10 STAM."),
]

test_cases_RtL = [
    ("THE CAT SAT ON THE MAT.", ".TAM EHT NO TAS TAC EHT"),
    ("THE cat SAT ON THE MAT.", ".TAM EHT NO TAS cat EHT"),
    ("THE cat SAT ON 10 MATS.", ".STAM 10 NO TAS cat EHT"),
    ("THE cat SAT ON 10 mats.", ".mats 10 NO TAS cat EHT"),
]


def test_LtR():
    for input_str, output_str in test_cases_LtR:
        display_str = _bidi.display(input_str, False, upper_is_rtl=True)
        assert display_str == output_str


def test_RtL():
    for input_str, output_str in test_cases_RtL:
        display_str = _bidi.display(input_str, True, upper_is_rtl=True)
        assert display_str == output_str
