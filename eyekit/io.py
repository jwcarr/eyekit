"""

Functions for reading and writing data.

"""


import re as _re
import json as _json
from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock


def read(file_path):
    """

    Read in a JSON file. `eyekit.fixation.FixationSequence` and
    `eyekit.text.TextBlock` objects are automatically decoded and
    instantiated.

    """
    with open(str(file_path), encoding="utf-8") as file:
        data = _json.load(file, object_hook=_eyekit_decoder)
    return data


def write(data, file_path, compress=False):
    """

    Write arbitrary data to a JSON file. If `compress` is `True`, the file is
    written in the most compact way; if `False`, the file will be  more human
    readable. `eyekit.fixation.FixationSequence` and `eyekit.text.TextBlock`
    objects are automatically encoded.

    """
    if compress:
        indent = None
        separators = (",", ":")
    else:
        indent = "\t"
        separators = (",", ": ")
    with open(str(file_path), "w", encoding="utf-8") as file:
        _json.dump(
            data,
            file,
            default=_eyekit_encoder,
            ensure_ascii=False,
            indent=indent,
            separators=separators,
        )


def import_asc(file_path, variables=[], placement_of_variables="after_end"):
    """

    Import data from an ASC file produced from an SR Research EyeLink device
    (you will first need to use SR Research's Edf2asc tool to convert your
    original EDF files to ASC). The importer will extract all trials from the
    ASC file, where a trial is defined as a sequence of fixations (EFIX lines)
    that occur inside a START–END block. Optionally, the importer can extract
    user-defined variables from the ASC file and associate them with the
    appropriate trial. For example, if your ASC file contains messages like
    this:

    ```
    MSG 4244101 !V TRIAL_VAR trial_type practice
    MSG 4244101 !V TRIAL_VAR passage_id 1
    ```

    then you could extract the variables `"trial_type"` and `"passage_id"`. A
    variable is some string that is followed by a space; anything that follows
    this space is the variable's value. By default, the importer looks for
    variables that follow the END tag. However, if your variables are placed
    before the START tag, then set the `placement_of_variables` argument to
    `"before_start"`. If unsure, you should first inspect your ASC file to see
    what messages you wrote to the data stream and where they are placed. The
    importer will return a list of dictionaries, where each dictionary
    represents a single trial and contains the fixations along with any other
    extracted variables. For example:

    ```
    [
        {
            "trial_type" : "practice",
            "passage_id" : "1",
            "fixations" : FixationSequence[...]
        },
        {
            "trial_type" : "test",
            "passage_id" : "2",
            "fixations" : FixationSequence[...]
        }
    ]
    ```

    """
    msg_regex = _re.compile(  # regex for parsing variables from MSG lines
        r"^MSG\s+\d+\s+.*?(?P<var>("
        + "|".join(map(_re.escape, variables))
        + r"))\s+(?P<val>.+?)$"
    )
    efix_regex = _re.compile(  # regex for parsing fixations from EFIX lines
        r"^EFIX\s+(L|R)\s+(?P<start>.+?)\s+(?P<end>.+?)\s+(?P<duration>.+?)\s+(?P<x>.+?)\s+(?P<y>.+?)\s"
    )
    # Open ASC file and extract lines that begin with START, END, MSG, or EFIX
    with open(str(file_path)) as file:
        raw_data = [
            line.strip()
            for line in file
            if line.startswith(("START", "END", "MSG", "EFIX"))
        ]
    # Determine the points where one trial ends and the next begins
    if placement_of_variables == "before_start":
        break_indices = [0] + [
            i for i, line in enumerate(raw_data) if line.startswith("END")
        ]
    elif placement_of_variables == "after_end":
        break_indices = [
            i for i, line in enumerate(raw_data) if line.startswith("START")
        ] + [len(raw_data)]
    else:
        raise ValueError(
            'placement_of_variables should be set to "before_start" or "after_end".'
        )
    # Extract trials based on the identified break points
    extracted_trials = []
    for start, end in zip(break_indices[:-1], break_indices[1:]):  # iterate over trials
        trial_lines = raw_data[start:end]  # lines belonging to this trial
        trial = {var: None for var in variables}
        fixations = []
        for line in trial_lines:
            if line.startswith("EFIX"):
                # Extract fixation from the EFIX line
                efix_extraction = efix_regex.match(line)
                if efix_extraction:
                    fixations.append(
                        (
                            int(round(float(efix_extraction["x"]), 0)),
                            int(round(float(efix_extraction["y"]), 0)),
                            int(efix_extraction["start"]),
                            int(efix_extraction["end"]),
                        )
                    )
            elif line.startswith("MSG") and variables:
                # Attempt to extract a variable and its value from the MSG line
                msg_extraction = msg_regex.match(line)
                if msg_extraction:
                    trial[msg_extraction["var"]] = msg_extraction["val"].strip()
        trial["fixations"] = _FixationSequence(fixations)
        extracted_trials.append(trial)
    return extracted_trials


def import_csv(
    file_path,
    x_header="x",
    y_header="y",
    start_header="start",
    end_header="end",
    trial_header=None,
):
    """

    Import data from a CSV file (requires Pandas to be installed). By default,
    the importer expects the CSV file to contain the column headers, `x`, `y`,
    `start`, and `end`, but this can be customized by setting the relevant
    arguments to whatever column headers your CSV file contains. Each row of
    the CSV file is expected to represent a single fixation. If your CSV file
    contains data from multiple trials, you should also specify the column
    header of a trial identifier, so that the data can be segmented into
    trials. The importer will return a list of dictionaries, where each
    dictionary represents a single trial and contains the fixations along with
    the trial identifier (if specified). For example:

    ```
    [
        {
            "trial_id" : 1,
            "fixations" : FixationSequence[...]
        },
        {
            "trial_id" : 2,
            "fixations" : FixationSequence[...]
        }
    ]
    ```

    """
    try:
        import pandas as _pd
    except ModuleNotFoundError as e:
        e.msg = 'The import_csv function requires Pandas. Run "pip install pandas" to use this function.'
        raise
    raw_data = _pd.read_csv(str(file_path))
    if trial_header is None:
        fixations = [
            tuple(fxn)
            for _, fxn in raw_data[
                [x_header, y_header, start_header, end_header]
            ].iterrows()
        ]
        return [{"fixations": _FixationSequence(fixations)}]
    trial_identifiers = raw_data[trial_header].unique()
    extracted_trials = []
    for identifier in trial_identifiers:
        trial_subset = raw_data[raw_data[trial_header] == identifier]
        fixations = [
            tuple(fxn)
            for _, fxn in trial_subset[
                [x_header, y_header, start_header, end_header]
            ].iterrows()
        ]
        trial = {trial_header: identifier, "fixations": _FixationSequence(fixations)}
        extracted_trials.append(trial)
    return extracted_trials


def _eyekit_encoder(obj):
    """

    Convert a `FixationSequence` or `TextBlock` object into something JSON
    serializable that can later be decoded by _eyekit_decoder().

    """
    if isinstance(obj, _FixationSequence):
        return {"__FixationSequence__": obj._serialize()}
    if isinstance(obj, _TextBlock):
        return {"__TextBlock__": obj._serialize()}
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _eyekit_decoder(obj):
    """

    Decode an object into a `FixationSequence` or `TextBlock` if the key
    implies that it is one of those types.

    """
    if "__FixationSequence__" in obj:
        return _FixationSequence(obj["__FixationSequence__"])
    if "__TextBlock__" in obj:
        return _TextBlock(**obj["__TextBlock__"])
    return obj
