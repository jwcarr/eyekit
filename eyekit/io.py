"""
Functions for reading and writing data.
"""

import re as _re
import json as _json
from types import GeneratorType as _GeneratorType
from .fixation import FixationSequence as _FixationSequence
from .text import TextBlock as _TextBlock, InterestArea as _InterestArea


def load(file_path):
    """
    Read in a JSON file. `eyekit.fixation.FixationSequence` and
    `eyekit.text.TextBlock` objects are automatically decoded and
    instantiated.
    """
    with open(str(file_path), encoding="utf-8") as file:
        data = _json.load(file, object_hook=_eyekit_decoder)
    return data


def save(data, file_path, *, compress: bool = False):
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


def import_asc(
    file_path,
    *,
    variables: list = [],
    placement_of_variables: str = "after_end",
    import_samples: bool = False,
    encoding: str = "utf-8",
) -> list:
    """
    Import data from an ASC file produced from an SR Research EyeLink device
    (you will first need to use SR Research's Edf2asc tool to convert your
    original EDF files to ASC). The importer will extract all trials from the
    ASC file, where a trial is defined as a sequence of fixations (EFIX lines)
    that occur inside a START–END block. Optionally, the importer can extract
    user-defined variables and ms-by-ms samples. For example, if your ASC
    file contains messages like this:

    ```
    MSG 4244101 trial_type practice
    MSG 4244101 passage_id 1
    MSG 4244592 stim_onset
    ```

    then you could extract the variables `"trial_type"` and `"passage_id"`. A
    variable is some string that is followed by a space; anything that
    follows this space is the variable's value. If the variable is not
    followed by a value (e.g., `"stim_onset"` above), then the time of the
    message is recorded as its value; this can be useful for recording the
    precise timing of an event. By default, the importer looks for variables
    that follow the END tag. However, if your variables are placed before the
    START tag, then set the `placement_of_variables` argument to
    `"before_start"`. If unsure, you should first inspect your ASC file to
    see what messages you wrote to the data stream and where they are placed.
    The importer will return a list of dictionaries, where each dictionary
    represents a single trial and contains the fixations along with any other
    extracted variables. For example:

    ```
    [
        {
            "trial_type": "practice",
            "passage_id": "1",
            "stim_onset": 4244592,
            "fixations": FixationSequence[...]
        },
        {
            "trial_type": "test",
            "passage_id": "2",
            "stim_onset": 4256311,
            "fixations": FixationSequence[...]
        }
    ]
    ```
    """
    msg_regex = _re.compile(  # regex for parsing variables from MSG lines
        r"^MSG\s+(?P<time>\d+)\s+.*?(?P<var>("
        + "|".join(map(_re.escape, variables))
        + r"))(?P<val>.+?)?$"
    )
    efix_regex = _re.compile(  # regex for parsing fixations from EFIX lines
        r"^EFIX\s+(L|R)\s+(?P<start>.+?)\s+(?P<end>.+?)\s+(?P<duration>.+?)\s+(?P<x>.+?)\s+(?P<y>.+?)\s+(?P<pupil>.+?)$"
    )
    sample_regex = _re.compile(  # regex for parsing individual sample lines
        r"^(?P<time>\d+)\s+(?P<x>\d+\.\d?)\s+(?P<y>\d+\.\d?)\s+(?P<pupil>.+?)\s+\.\.\.$"
    )
    # Open ASC file and extract lines that begin with START, END, MSG, or EFIX
    with open(str(file_path), encoding=encoding) as file:
        if import_samples:
            raw_data = [
                line.strip()
                for line in file
                if line.endswith("...\n")
                or line.startswith(("START", "END", "MSG", "EFIX"))
            ]
        else:
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
        trial = {var: None for var in variables}
        fixations = []
        samples = []
        for line in raw_data[start:end]:  # lines belonging to this trial
            if line.startswith("EFIX"):
                # Extract fixation from an EFIX line
                efix_extraction = efix_regex.match(line)
                if efix_extraction:
                    fixations.append(
                        {
                            "x": int(round(float(efix_extraction["x"]), 0)),
                            "y": int(round(float(efix_extraction["y"]), 0)),
                            "start": int(efix_extraction["start"]),
                            "end": int(efix_extraction["end"]) + 1,
                            "pupil_size": int(efix_extraction["pupil"]),
                        }
                    )
            elif import_samples and line.endswith("..."):
                # Extract sample from a sample line
                sample_extraction = sample_regex.match(line)
                if sample_extraction:
                    samples.append(
                        (
                            int(sample_extraction["time"]),
                            int(round(float(sample_extraction["x"]), 0)),
                            int(round(float(sample_extraction["y"]), 0)),
                            int(float(sample_extraction["pupil"])),
                        )
                    )
            elif variables and line.startswith("MSG"):
                # Attempt to extract a variable and its value from a MSG line
                msg_extraction = msg_regex.match(line)
                if msg_extraction:
                    if msg_extraction["val"] is None:
                        val = int(msg_extraction["time"])
                    else:
                        val = msg_extraction["val"].strip()
                    trial[msg_extraction["var"]] = val
        trial["fixations"] = _FixationSequence(fixations)
        if import_samples:
            trial["samples"] = samples
        extracted_trials.append(trial)
    return extracted_trials


def import_csv(
    file_path,
    *,
    x_header: str = "x",
    y_header: str = "y",
    start_header: str = "start",
    end_header: str = "end",
    trial_header: str = None,
    encoding: str = "utf-8",
) -> list:
    """
    Import data from a CSV file. By default, the importer expects the CSV file
    to contain the column headers, `x`, `y`, `start`, and `end`, but this can
    be customized by setting the relevant arguments to whatever column
    headers your CSV file contains. Each row of the CSV file is expected to
    represent a single fixation. If your CSV file contains data from multiple
    trials, you should also specify the column header of a trial identifier,
    so that the data can be segmented into trials. The importer will return a
    list of dictionaries, where each dictionary represents a single trial and
    contains the fixations along with the trial identifier (if specified).
    For example:

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
    import csv as _csv

    extracted_trials = []
    if trial_header is None:
        headers = [x_header, y_header, start_header, end_header]
    else:
        headers = [x_header, y_header, start_header, end_header, trial_header]
    with open(file_path, encoding=encoding) as file:
        csv_reader = _csv.DictReader(file)
        for header in headers:
            if header not in csv_reader.fieldnames:
                raise ValueError(
                    f'This CSV file does not contain the header "{header}".'
                )
        if trial_header is None:
            fixations = [
                (
                    fixation[x_header],
                    fixation[y_header],
                    fixation[start_header],
                    fixation[end_header],
                )
                for fixation in csv_reader
            ]
            extracted_trials.append({"fixations": fixations})
        else:
            current_trial_identifier = None
            for fixation in csv_reader:
                if fixation[trial_header] != current_trial_identifier:
                    current_trial_identifier = fixation[trial_header]
                    extracted_trials.append(
                        {trial_header: current_trial_identifier, "fixations": []}
                    )
                extracted_trials[-1]["fixations"].append(
                    (
                        fixation[x_header],
                        fixation[y_header],
                        fixation[start_header],
                        fixation[end_header],
                    )
                )
    for extracted_trial in extracted_trials:
        extracted_trial["fixations"] = _FixationSequence(extracted_trial["fixations"])
    return extracted_trials


def _eyekit_encoder(obj):
    """
    Convert a `FixationSequence` or `TextBlock` object into something JSON
    serializable that can later be decoded by _eyekit_decoder().
    """
    if isinstance(obj, _FixationSequence):
        return {"__FixationSequence__": obj.serialize()}
    if isinstance(obj, _InterestArea):
        return {"__InterestArea__": obj.serialize()}
    if isinstance(obj, _TextBlock):
        return {"__TextBlock__": obj.serialize()}
    if isinstance(obj, _GeneratorType):
        return list(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _eyekit_decoder(obj):
    """
    Decode an object into a `FixationSequence` or `TextBlock` if the key
    implies that it is one of those types.
    """
    if "__FixationSequence__" in obj:
        return _FixationSequence(obj["__FixationSequence__"])
    if "__InterestArea__" in obj:
        return _InterestArea(**obj["__InterestArea__"])
    if "__TextBlock__" in obj:
        return _TextBlock(**obj["__TextBlock__"])
    return obj


# DEPRECATED FUNCTIONS TO BE REMOVED IN THE FUTURE


def read(file_path):  # pragma: no cover
    """
    **Deprecated in 0.4 and removed in 0.6.** Use `eyekit.io.load()`.
    """
    raise NotImplementedError(
        "eyekit.io.read() has been replaced with eyekit.io.load()"
    )


def write(data, file_path, compress=False):  # pragma: no cover
    """
    **Deprecated in 0.4 and removed in 0.6.** Use `eyekit.io.save()`.
    """
    raise NotImplementedError(
        "eyekit.io.write() has been replaced with eyekit.io.save()"
    )
