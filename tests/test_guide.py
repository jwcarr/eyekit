import io
from contextlib import redirect_stdout
from sys import version_info


def extract_codeblocks(file_path, skip_marker, replacements):
    codeblocks = []
    in_codeblock = False
    with open(file_path) as file:
        for line in file:
            if in_codeblock:
                if line.startswith("```"):
                    in_codeblock = False
                elif skip_marker not in line:
                    for search_string, replace_string in replacements.items():
                        line = line.replace(search_string, replace_string)
                    codeblocks[-1] += line
            elif line.startswith("```python"):
                in_codeblock = True
                codeblocks.append("")
    return codeblocks


def test_guide():
    codeblocks = extract_codeblocks(
        "GUIDE.md", "#skiptest", {".save('": ".save('docs/images/"}
    )
    for block in codeblocks:
        captured_from_stdout = io.StringIO()
        with redirect_stdout(captured_from_stdout):
            if version_info.minor >= 13:
                # In Python 3.13, global scope needs to be passed in explicitly
                exec(block, globals=globals())
            else:
                exec(block)
        actual_output = captured_from_stdout.getvalue().strip().split("\n")
        expected_output = [l[2:] for l in block.split("\n") if l.startswith("# ")]
        for actual, expected in zip(actual_output, expected_output):
            assert actual == expected
