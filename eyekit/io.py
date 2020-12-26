"""

Functions for reading and writing data.

"""


from os import listdir as _listdir, path as _path
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
    user-defined variables. For example, if the filter_variables argument is
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

    then this trial would be extracted. The extract_variables argument can be
    used to extract further variables without any filtering. This could be
    used, for example, to extract trial or stimulus IDs that were written to
    the data stream as messages. If unsure, you should first inspect your ASC
    file to see what messages you wrote to the data stream.

    The importer will return something like this:

    ```
    {
        "imported_from" : "my_asc_file.asc",
        "trials" : [
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
    }
    ```

    """
    file_path = str(file_path)
    for var, vals in filter_variables.items():
        if var not in extract_variables:
            extract_variables.append(var)
        if isinstance(vals, str):
            filter_variables[var] = [vals]
    if extract_variables:
        msg_line_regex = _re.compile(
            r"^MSG\t\d+.+?(?P<var>(" + "|".join(extract_variables) + r"))(?P<val>.+?)$"
        )
    efix_line_regex = _re.compile(
        r"^EFIX R\s+(?P<stime>.+?)\s+(?P<etime>.+?)\s+(?P<duration>.+?)\s+(?P<x>.+?)\s+(?P<y>.+?)\s"
    )
    data = {
        "imported_from": _path.basename(file_path),
        "trials": [],
    }
    with open(file_path) as file:
        raw_data = [
            line.strip()
            for line in file
            if line.startswith(("START", "END", "MSG", "EFIX"))
        ]
    start_indices = [i for i, line in enumerate(raw_data) if line.startswith("START")]
    for start, end in zip(start_indices, start_indices[1:] + [len(raw_data)]):
        trial = {}
        fixations = []
        for line in raw_data[start:end]:
            if line.startswith("EFIX"):
                efix_match = efix_line_regex.match(line)
                if efix_match:
                    x = int(round(float(efix_match["x"]), 0))
                    y = int(round(float(efix_match["y"]), 0))
                    d = int(efix_match["duration"])
                    fixations.append((x, y, d))
            elif line.startswith("MSG") and extract_variables:
                msg_match = msg_line_regex.match(line)
                if msg_match:
                    trial[msg_match["var"].strip()] = msg_match["val"].strip()
        for var, vals in filter_variables.items():
            if var not in trial or trial[var] not in vals:
                break
        else:  # For loop exited normally, so keep trial
            trial["fixations"] = _FixationSequence(fixations)
            data["trials"].append(trial)
    return data


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
