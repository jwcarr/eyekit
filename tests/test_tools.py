import eyekit


def test_font_size_at_72dpi():
    assert eyekit.tools.font_size_at_72dpi(15, 96) == 20
