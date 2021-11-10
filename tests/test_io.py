from tempfile import TemporaryDirectory
from pathlib import Path
import eyekit

EXAMPLE_DATA = Path("example") / "example_data.json"
EXAMPLE_TEXTS = Path("example") / "example_texts.json"
EXAMPLE_ASC = Path("example") / "example_data.asc"
EXAMPLE_CSV = Path("example") / "example_data.csv"


def test_load_data():
    data = eyekit.io.load(EXAMPLE_DATA)
    assert isinstance(data["trial_0"]["fixations"], eyekit.FixationSequence)
    assert isinstance(data["trial_1"]["fixations"], eyekit.FixationSequence)
    assert isinstance(data["trial_2"]["fixations"], eyekit.FixationSequence)
    assert data["trial_0"]["fixations"][0].x == 412
    assert data["trial_0"]["fixations"][1].y == 163
    assert data["trial_0"]["fixations"][2].duration == 333


def test_load_texts():
    texts = eyekit.io.load(EXAMPLE_TEXTS)
    assert isinstance(texts["passage_a"]["text"], eyekit.TextBlock)
    assert isinstance(texts["passage_b"]["text"], eyekit.TextBlock)
    assert isinstance(texts["passage_c"]["text"], eyekit.TextBlock)
    assert texts["passage_a"]["text"].position == (360, 161)
    assert texts["passage_b"]["text"].font_face == "Courier New"
    assert texts["passage_c"]["text"].align == "left"
    assert texts["passage_c"]["text"].anchor == "left"


def test_save():
    data = eyekit.io.load(EXAMPLE_DATA)
    with TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "output.json"
        eyekit.io.save(data, output_file)
        written_data = eyekit.io.load(output_file)
    original_seq = data["trial_0"]["fixations"]
    written_seq = written_data["trial_0"]["fixations"]
    for fxn1, fxn2 in zip(original_seq, written_seq):
        assert fxn1.serialize() == fxn2.serialize()


def test_import_asc():
    try:
        data = eyekit.io.import_asc(EXAMPLE_ASC, variables=["trial_type"])
    except FileNotFoundError:
        return
    assert data[0]["trial_type"] == "Practice"
    assert data[1]["fixations"].duration == 72279
    assert data[2]["fixations"][0].x == 1236


def test_import_csv():
    try:
        data = eyekit.io.import_csv(EXAMPLE_CSV, trial_header="trial")
    except FileNotFoundError:
        return
    assert data[0]["fixations"].duration == 78505
    assert data[1]["fixations"].duration == 60855
    assert data[2]["fixations"].duration == 57468
