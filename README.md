Eyekit
======

Eyekit is a Python package for handling and visualizing eyetracking data, with a particular emphasis on the reading of multiline passages presented in a fixed-width font.


Python dependencies
-------------------

Eyekit requires Python 3.6 or greater and the following packages:

- numpy 1.13
- cairosvg 2.4


Installation
------------

Eyekit is not currently listed in PyPI, but the latest verison can be installed directly from this GitHub repo using `pip`:

```
pip install https://github.com/jwcarr/eyekit/archive/master.tar.gz
```


Getting started
---------------

Once installed, import Eyekit into your project in the normal way:

```python
import eyekit
```

Eyekit makes use of two basic types of object: the `Text` object and the `FixationSequence` object. Much of Eyekit's functionality centers around bringing these two objects into contact; typically, we have a passage of text and we want to analyze which parts of the text the participant is looking at.

### The `Text` object

A `Text` object represents a line or passage of text. It can be created by referencing a .txt file or by passing in a list of strings (one string for each line of text). When you initialize the `Passasge`, it is necessary to specify the pixel position of the first character, the pixel spacing between characters, and the pixel spacing between lines – this allows Eyekit to establish the position of every character:

```python
text = eyekit.Text('example_passage.txt',
	first_character_position=(368, 155),
	character_spacing=16,
	line_spacing=64
)
```

If necessary, texts can be marked up with interest areas using the following bracketing scheme:

```
The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.
```

Square brackets mark the interest areas (in this case *jump* and *ed*) and curly braces provide a unique label for each interest area (in this case `stem_1` and `suffix_1`). Interest areas can then be iterated over using the `iter_IAs()` method:

```python
for interest_area in text.iter_IAs():
	print(interest_area.label, interest_area.text)
```

```python
stem_1 jump
suffix_1 ed
```

### The `FixationSequence` object

Eyekit is not especially committed to one particular file format; so long as you have an x-coordinate, a y-coordinate, and a duration for each fixation, you are free to store data in whatever format you choose. However, Eyekit does provide built-in support for a JSON-based format, where a typical data file looks like this:

```json
{
  "trial_1" : {
    "participant_id" : "Jon",
    "passage_id" : "A",
    "fixations" : [[368, 161, 208], [428, 160, 178], [565, 151, 175], ..., [562, 924, 115]]
  },
  "trial_2" : {
    "participant_id" : "William",
    "passage_id" : "B",
    "fixations" : [[1236, 147, 6], [1250, 151, 242], [356, 159, 145], ..., [787, 272, 110]]
  }
}
```

This format is open, human-readable, and fairly flexible. Each trial object should contain a key called `fixations` that maps to an array containing x, y, and duration for each fixation. Aside from this, you can freely add other key–value pairs (e.g., participant IDs, trial IDs, timestamps, etc.). These data files can be loaded using the `read()` function from the `io` module:

```python
eyekit.io.read('example_data.json')
```

Alternatively, if you have your data in some other format, you can create a fixation sequence manually by doing something like this:

```python
fixation_sequence = eyekit.FixationSequence([[368, 161, 208], [428, 160, 178], [565, 151, 175], ..., [562, 924, 115]])
```

`FixationSequence`s can be traversed, indexed, and sliced as you'd expect. For example,

```python
print(fixation_sequence[10:15])
```

slices out fixations 10 through 14 into a new `FixationSequence`:

```python
FixationSequence[Fixation[1394,187], ..., Fixation[688,232]]
```


### Bringing a `FixationSequence` into contact with a `Text`

The `Text` object provides three methods for finding the nearest character, word, or ngram to a given fixation: nearest_word(), nearest_char(), and nearest_ngram(). For example, to retrieve the nearest word to each of the fixations in the sequence, you could do:

```python
for fixation in fixation_sequence:
	print(text.nearest_word(fixation))
```

```python
[c]
[e, r, a, n, o]
[v, o, l, t, a]
[o, r, s, i]
[v, i, v, e, v, a, n, o]
...
```


### Visualization

The `Image` object is used to create visualizations of a text and associated fixation data. When creating a `Image`, you specify the width and height of the screen. You can then chose to render the text itself and/or an associated fixation sequence.

```python
image1 = eyekit.Image(1920, 1080)
image1.render_text(text, fontsize=28)
image1.render_fixations(fixation_sequence)
```

Images can be saved as .svg, .pdf, .eps, or .png files, and optionally they can be cropped to remove any margins:

```python
image1.crop_to_text()
image1.save('example_images/fixations.svg')
```

<img src='./example_images/fixations.svg'>


### Analysis tools

Eyekit provides a number of tools for handling and analyzing eyetracking data.

#### Correcting vertical drift

As can be seen in visualization above, the raw data suffers from vertical drift – the fixations gradually become misaligned with the lines of text. The `correct_vertical_drift` function can be used to snap the fixations to the text lines:

```python
eyekit.tools.correct_vertical_drift(fixation_sequence, text)
```

We can then visually inspect the corrected fixation sequence in a new image:

```python
image2 = eyekit.Image(1920, 1080)
image2.render_text(text, fontsize=28)
image2.render_fixations(fixation_sequence)
image2.save('example_images/corrected_fixations.svg')
```

<img src='./example_images/corrected_fixations.svg'>

#### Analyzing duration mass

On each fixation, the reader takes in information from several characters. We can visualize this by spreading the fixation data across the text using the `spread_duration_mass` function:

```python
duration_mass = eyekit.tools.spread_duration_mass(text, fixation_sequence)

image3 = eyekit.Image(1920, 1080)
image3.render_heatmap(text, duration_mass)
image3.render_text(text, fontsize=28)
image3.save('example_images/duration_mass.svg')
```

<img src='./example_images/duration_mass.svg'>


### Input–output

Within the `io` module, Eyekit provides a few functions for loading and saving data. The `read()` and `write()` functions can be used to load and save data into Eyekit's native JSON-based format.

```python
data = eyekit.io.read('example_data.json')
eyekit.io.write(data, 'example_data_copy.json', indent=True)
```

If `indent` is set to `True`, the output JSON file will include indentation (larger file sizes but easier to read).

Eyekit also has rudimentary support for importing data from an ASC file. When importing data this way, you must specify the name of a trial variable and its possible values so that the importer can determine when a new trial begins:

```python
data = eyekit.io.import_asc('example_data.asc', 'trial_type', ['Experimental'], extract_variables=['passage_id', 'response'])
```

In this case, when parsing the ASC file, the importer would consider

```
MSG	4244100 !V TRIAL_VAR trial_type Experimental
```

to mark the beginning of a new trial. Optionally, you can specify other variables that you want to extract (in this case `passage_id` and `response`), resulting in imported data that looks like this:

```python
{
  "1" : {
    "trial_type" : "Experimental",
    "passage_id" : "A",
    "response" : "yes",
    "fixations" : FixationSequence[[368, 161, 208], ..., [562, 924, 115]]
  }
}
```

Rather than load a single ASC file, you can also pass the path to a directory of ASC files, all of which will then be loaded into a single dataset:

```python
data = eyekit.io.import_asc('asc_data_files/', 'trial_type', ['Experimental'], extract_variables=['passage_id', 'response'])
```

### Miscellaneous

Depending on the language you're working with and your particular assumptions, you may want to specify an alternative alphabet or how special characters should be treated. Any character in the text that is not specified in the alphabet will be ignored (for example, when iterating over characters in the text). Setting the special characters allows you to specifiy that certain characters should be treated as identical (for example, that à is the same as a or that an apostrophe is the same as a space).

```python
eyekit.set_case_sensitive(False)
eyekit.set_alphabet(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'à', 'á', 'è', 'é', 'ì', 'í', 'ò', 'ó', 'ù', 'ú', ' ', '’'])
eyekit.set_special_characters({'à':'a', 'á':'a', 'è':'e', 'é':'e', 'ì':'i', 'í':'i', 'ò':'o', 'ó':'o', 'ù':'u', 'ú':'u', ' ':'_', '’':'_'})
```


License
-------

Eyekit is licensed under the terms of the MIT License.
