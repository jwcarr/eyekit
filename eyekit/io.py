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
    written in the most compact way; if `False`, the file will be larger but
    more human-readable. `eyekit.fixation.FixationSequence` and
    `eyekit.text.TextBlock` objects are automatically serialized.

    """
    if compress:
        indent = None
        separators = (",", ":")
    else:
        indent = "\t"
        separators = (", ", " : ")
    with open(str(file_path), "w", encoding="utf-8") as file:
        _json.dump(
            data,
            file,
            default=_eyekit_encoder,
            ensure_ascii=False,
            indent=indent,
            separators=separators,
        )


def import_asc(file_path, filter_variables={}, extract_variables=[]):
    """

    Import an ASC file produced from an EyeLink device. By default, this will
    import all trials in the ASC file, where a trial is defined as all
    fixations (EFIX lines) that occur within a START–END block. Optionally,
    the importer can try to filter only those trials that match certain
    user-defined variables. For example, if the `filter_variables` argument is
    set to:

    ```
    {"trial_type":"test", "passage_id":["A", "B", "C"]}
    ```

    the importer will only extract trials where "trial_type" is set to "test"
    and "passage_id" is set to either "A", "B", or "C". Variables are somewhat
    loosely defined as some string that occurs in a MSG line; anything that
    follows this string is its value. For example, if a trial in your ASC file
    contained these messages:

    ```
    MSG 4244101 !V TRIAL_VAR trial_type test
    MSG 4244101 !V TRIAL_VAR passage_id A
    ```

    then this trial would be extracted. The `extract_variables` argument can
    be used to extract further variables without any filtering. This could be
    used, for example, to extract trial or stimulus IDs that were written to
    the data stream as messages. If unsure, you should first inspect your ASC
    file to see what messages you wrote to the data stream.

    The importer will return something like this:

    ```
    [
        {
            "trial_type" : "test",
            "passage_id" : "A",
            "fixations" : FixationSequence[...]
        },
        {
            "trial_type" : "test",
            "passage_id" : "B",
            "fixations" : FixationSequence[...]
        }
    ]
    ```

    """
    extracted_trials = []
    for var, vals in filter_variables.items():
        if var not in extract_variables:
            extract_variables.append(var)  # ensure filter variables are also extracted
        if isinstance(vals, str):
            filter_variables[var] = [vals]  # if vals is str, place inside a list
    msg_regex = _re.compile(  # regex for parsing messages
        r"^MSG\t\d+.+?(?P<var>("
        + "|".join(map(_re.escape, extract_variables))
        + r"))(?P<val>.+?)$"
    )
    efix_regex = _re.compile(  # regex for parsing fixations
        r"^EFIX\s(L|R)\s+(?P<stime>.+?)\s+(?P<etime>.+?)\s+(?P<duration>.+?)\s+(?P<x>.+?)\s+(?P<y>.+?)\s"
    )
    # Open ASC file and extract lines that begin with START, END, MSG, or EFIX
    with open(str(file_path)) as file:
        raw_data = [
            line.strip()
            for line in file
            if line.startswith(("START", "END", "MSG", "EFIX"))
        ]
    # Determine the points where one trial ends and the next begins
    break_indices = [i for i, line in enumerate(raw_data) if line.startswith("START")]
    break_indices.append(len(raw_data))
    for start, end in zip(break_indices[:-1], break_indices[1:]):  # iterate over trials
        trial_lines = raw_data[start:end]
        trial = {}
        fixations = []
        for line in trial_lines:  # iterate over lines belonging to this trial
            if line.startswith("EFIX"):
                # Extract fixation from the EFIX line
                efix_extraction = efix_regex.match(line)
                if efix_extraction:
                    x = int(round(float(efix_extraction["x"]), 0))
                    y = int(round(float(efix_extraction["y"]), 0))
                    d = int(efix_extraction["duration"])
                    fixations.append((x, y, d))
            elif line.startswith("MSG") and extract_variables:
                # Attempt to extract a variable and its value from the MSG line
                msg_extraction = msg_regex.match(line)
                if msg_extraction:
                    trial[msg_extraction["var"].strip()] = msg_extraction["val"].strip()
        # Filter out unwanted trials
        for var, vals in filter_variables.items():
            if var not in trial or trial[var] not in vals:
                break
        else:  # For loop exited normally, so keep this trial
            trial["fixations"] = _FixationSequence(fixations)
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
