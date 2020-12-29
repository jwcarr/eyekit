import eyekit


def test_read():
    data = eyekit.io.read("example/example_data.json")
    texts = eyekit.io.read("example/example_texts.json")
    assert isinstance(data["trial_0"]["fixations"], eyekit.FixationSequence)
    assert isinstance(data["trial_1"]["fixations"], eyekit.FixationSequence)
    assert isinstance(data["trial_2"]["fixations"], eyekit.FixationSequence)
    assert data["trial_0"]["fixations"][0].x == 412
    assert data["trial_0"]["fixations"][1].y == 163
    assert data["trial_0"]["fixations"][2].duration == 333
    assert isinstance(texts["passage_a"]["text"], eyekit.TextBlock)
    assert isinstance(texts["passage_b"]["text"], eyekit.TextBlock)
    assert isinstance(texts["passage_c"]["text"], eyekit.TextBlock)
    assert texts["passage_a"]["text"].position == (360, 161)
    assert texts["passage_a"]["text"].font_face == "Courier New"


def test_import_asc():
    try:
        data = eyekit.io.import_asc(
            "example/example_data.asc", variables=["trial_type"]
        )
    except FileNotFoundError:
        return
    assert data[0]["trial_type"] == "Practice"
    assert data[1]["fixations"].duration == 72279
    assert data[2]["fixations"][0].x == 1236


def test_import_csv():
    try:
        data = eyekit.io.import_csv("example/example_data.csv", trial_header="trial")
    except FileNotFoundError:
        return
    assert data[0]["fixations"].duration == 78505
    assert data[1]["fixations"].duration == 60855
    assert data[2]["fixations"].duration == 57468
