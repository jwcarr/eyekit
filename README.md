eyekit
======

Eyekit is a lite Python package for handling and visualizing eyetracking data, with a particular emphasis on the reading of multiline passages presented in a fixed-width font.


Dependencies
------------

- python 3
- numpy
- inkscape (optional; required for producing .pdf, .eps, or .png graphics)
- scipy (optional; only required by certain tools)


Installation
------------

```
pip install https://github.com/jwcarr/eyekit/archive/master.tar.gz
```


Usage examples
--------------

Start by importing eyekit:

```python
import eyekit
```

Eyekit makes use of two basic types of object: the `Passage` object and the `FixationSequence` object. Much of eyekit's functionality centers around bringing these two objects into contact; typically, we have a passage of text and we want to analyze which parts of the passage the participant is looking at.


### The `Passage` object

A `Passage` object represents the passage of text. It can be created by referencing a .txt file or by passing in a list of strings (one string for each line of text). When you initialize the `Passasge`, it is necessary to specify the pixel position of the first character, the pixel spacing between characters, and the pixel spacing between lines:

```python
passage = eyekit.Passage('example_passage.txt',
	first_character_position=(368, 155),
	character_spacing=16,
	line_spacing=64
)
```

By assuming a fixed-width font, eyekit uses these details to place the passage of text on an imaginary grid, such that each character has a row and column index. Subsetting the passage with a row,column index, for example,

```python
print(passage[0,0])
```

returns the character in that position along with its pixel coordinates:

```python
('C', (368, 155))
```

The `Passage` object has three iterators: `iter_words()`, `iter_chars()`, and `iter_ngrams()`. Each of these can optionally accept a filtering function. For example, here we are printing all five letter words in the passage that begin with 'b', along with the pixel coordinates of their initial and final letters:

```python
for word in passage.iter_words(lambda word : len(word) == 5 and word[0] == 'b'):
	print(word, word[0].xy, word[-1].xy)
```

```python
[b, o, s, c, o] (1312, 155) (1376, 155)
[b, o, s, c, o] (768, 475) (832, 475)
[b, o, s, c, o] (1088, 539) (1152, 539)
[b, i, m, b, a] (672, 603) (736, 603)
[b, i, m, b, a] (720, 731) (784, 731)
```


### The `FixationSequence` object

Raw fixation data can be stored in whatever format you want, but when you load in your data you will represent each passage reading as a `FixationSequence`. Creation of a `FixationSequence` expects an x-coordinate, y-coordinate, and duration for each of the fixations, for example `[[368, 161, 208], [427, 159, 178], ...]`. Here we will load in some example data from a json file:

```python
import json
with open('example_data.json') as file:
	data = json.load(file)
fixation_sequence = eyekit.FixationSequence(data['fixations'])
```

A `FixationSequence` is, as you'd expect, a sequence of fixations, and it can be traversed, indexed, and sliced as expected. For example,

```python
print(fixation_sequence[10:15])
```

slices out fixations 10 through 14 into a new `FixationSequence`:

```python
FixationSequence[Fixation[1394,187], ..., Fixation[688,232]]
```


### Bringing a `FixationSequence` into contact with a `Passage`

The `Passage` object provides three methods for finding the nearest character, word, or ngram to a given fixation: nearest_word(), nearest_char(), and nearest_ngram(). For example, to retrieve the nearest word to each of the fixations in the sequence, you could do:

```python
for fixation in fixation_sequence:
	print(passage.nearest_word(fixation))
```

```python
[c]
[e, r, a, n, o]
[v, o, l, t, a]
[o, r, s, i]
[v, i, v, e, v, a, n, o]
...
```


### Visualizing the data

The `Diagram` object is used to create visualizations of a passage and associated fixation data. When creating a `Diagram`, you specify the width and height of the screen. You can then chose to render the text itself and/or an associated fixation sequence.

```python
diagram1 = eyekit.Diagram(1920, 1080)
diagram1.render_passage(passage, fontsize=28)
diagram1.render_fixations(fixation_sequence)
```

The diagram can be saved as an .svg file. If you have Inkscape installed, you can also save as a .pdf, .eps, or .png file. The `crop_to_passage` option removes any margins around the passage:

```python
diagram1.save('example_diagrams/fixations.svg', crop_to_passage=True)
```

<img src='./example_diagrams/fixations.svg'>


### Analysis tools

Eyekit provides a number of tools for handling and analyzing eyetracking data.

#### Correcting vertical drift

As can be seen in visualization above, the raw data suffers from vertical drift – the fixations gradually become misaligned with the lines of text. The `correct_vertical_drift` function can be used to snap the fixations to the lines of the passage:

```python
corrected_fixation_sequence = eyekit.tools.correct_vertical_drift(passage, fixation_sequence)
```

We can then visually inspect this corrected fixation sequence like so:

```python
diagram2 = eyekit.Diagram(1920, 1080)
diagram2.render_passage(passage, fontsize=28)
diagram2.render_fixations(corrected_fixation_sequence)
diagram2.save('example_diagrams/corrected_fixations.svg', crop_to_passage=True)
```

<img src='./example_diagrams/corrected_fixations.svg'>

#### Analyzing duration mass

On each fixation, the reader takes in information from several characters. We can visualize this by spreading the fixation data across the passage using the `spread_duration_mass` function:

```python
duration_mass = eyekit.tools.spread_duration_mass(passage, corrected_fixation_sequence)

diagram3 = eyekit.Diagram(1920, 1080)
diagram3.render_heatmap(passage, duration_mass)
diagram3.render_passage(passage, fontsize=28)
diagram3.save('example_diagrams/duration_mass.svg', crop_to_passage=True)
```

<img src='./example_diagrams/duration_mass.svg'>


### Miscellaneous

Depending on the language you're working with and your particular assumptions, you may want to specify an alternative alphabet or how special characters should be treated. Any character in the passage that is not specified in the alphabet will be ignored (for example, when iterating over characters in the passage). Setting the special characters allows you to specifiy that certain characters should be treated as identical (for example, that à is the same as a or that an apostrophe is the same as a space).

```python
eyekit.set_case_sensitive(False)
eyekit.set_alphabet(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'à', 'á', 'è', 'é', 'ì', 'í', 'ò', 'ó', 'ù', 'ú', ' ', '’'])
eyekit.set_special_characters({'à':'a', 'á':'a', 'è':'e', 'é':'e', 'ì':'i', 'í':'i', 'ò':'o', 'ó':'o', 'ù':'u', 'ú':'u', ' ':'_', '’':'_'})
```


License
-------

eyekit is licensed under the terms of the MIT License.
