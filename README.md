<img src='./docs/logo.png' width='300'>

Eyekit is a Python package for handling, analyzing, and visualizing eyetracking data, with a particular emphasis on the reading of sentences and multiline passages presented in a fixed-width font. Eyekit is currently in the pre-alpha stage and is licensed under the terms of the MIT License. [Full documentation is available here](https://jwcarr.github.io/eyekit/).


Philosophy
----------

Eyekit is a lightweight tool for doing open, transparent, reproducible science on reading behavior. Eyekit is entirely independent of any particular eyetracker hardware, presentation software, or data formats, and has a very minimal set of Python dependencies. It has an object-oriented style that defines two core objects – the TextBlock and the FixationSequence – that you can bring into contact with a bit of coding.


Is Eyekit the Right Tool for Me?
--------------------------------

- You basically just want to analyze which parts of a text someone is looking at by defining areas of interest.

- You are interested in a fixation-level analysis, as opposed to, for example, saccades or millisecond-by-millisecond eye movements.

- You are working with monospaced text that is suitable for laying out on a grid.

- You don't mind doing a little bit of legwork to transform your raw fixation data and texts into something Eyekit can understand.

- You want the flexibility to define custom measures and to build your own reproducible processing pipeline.

- You would like tools for dealing with noise and calibration issues, such as vertical drift, and for discarding fixations according to your own criteria.

- You want to produce publication-ready visualizations and to share your data in a standard and open format.

- You are *not* looking for statistical solutions (this is outwith Eyekit's purview).


Installation
------------

The latest version of Eyekit can be installed using `pip`:

```shell
$ pip install eyekit
```

Eyekit is compatible with Python 3.5 and up. The only required dependency is [Numpy](https://numpy.org), which will be installed automatically by pip if necessary. [CairoSVG](https://cairosvg.org) is required if you want to export visualizations into formats other than SVG. [Scipy](https://www.scipy.org) and [Scikit-learn](https://scikit-learn.org) are required by certain tools.


Getting Started
---------------

Once installed, import Eyekit in the normal way:

```python
>>> import eyekit
```

Eyekit makes use of two core objects: the `TextBlock` object and the `FixationSequence` object. Much of Eyekit's functionality involves bringing these two objects into contact. Typcally, you define particular areas of the `TextBlock` that are of interest (phrases, words, morphemes, letters...) and check to see which fixations from the `FixationSequence` fall in those areas and for how long.

### The `TextBlock` object

A `TextBlock` can represent a word, sentence, or passage of text. When you create a `TextBlock` object, it is necessary to specify the pixel position of the center of the first character, the character width, and the line height (even if there's only one line, this will still determine the height of any interest areas). Since Eyekit assumes a fixed-width font, it uses these details to establish the position of every character on an imaginary grid. Optionally, you can also specify the `font` and `fontsize` when you create the `TextBlock`, but this only affects how the text is rendered in any images you create. Let's begin by creating a `TextBlock` representing a single sentence:

```python
>>> sentence = 'The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.'
>>> txt = eyekit.TextBlock(sentence, position=(100, 540), character_width=16, line_height=64)
>>> print(txt)
### TextBlock[The quick brown ...]
```

Eyekit has a simple scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case *jump* and *ed*) and curly braces are used to provide a unique label for each interest area (in this case `stem_1` and `suffix_1`). We can iterate over these interest areas using the `TextBlock.interest_areas()` iterator method:

```python
>>> for interest_area in txt.interest_areas():
>>>     print(interest_area.label, interest_area.text, interest_area.bounding_box)
### stem_1 jump (412, 508, 64, 64)
### suffix_1 ed (476, 508, 32, 64)
```

In this case, we are printing each interest area's label, its textual representation, and its bounding box (x, y, width, and height). Various other methods are available for treating all lines, words, characters, or ngrams as interest areas. If, for example, you were interested in every word, you could use the `TextBlock.words()` iterator without needing to explicitly mark up every word as an interest area:

```python
>>> for word in txt.words():
>>>     print(word.label, word.text, word.bounding_box)
### word_0 The (92, 508, 48, 64)
### word_1 quick (156, 508, 80, 64)
### word_2 brown (252, 508, 80, 64)
### word_3 fox (348, 508, 48, 64)
### word_4 jumped (412, 508, 96, 64)
### word_5 over (524, 508, 64, 64)
### word_6 the (604, 508, 48, 64)
### word_7 lazy (668, 508, 64, 64)
### word_8 dog (748, 508, 48, 64)
```

Since the text is arranged on a grid, you can also slice out arbitrary interest areas by using the row and column indices of a section of text. Here, for example, we are taking a slice from row 0 (the first line) and columns 10 through 18:

```python
>>> arbitrary_interest_area = txt[0, 10:19]
>>> print(arbitrary_interest_area.text, arbitrary_interest_area.bounding_box)
### brown fox (252, 508, 144, 64)
```

This could be useful if you wanted to slice up the text in some programmatic way, creating interest areas from each three-letter chunk, for example.

### The `FixationSequence` object

Fixation data is represented in a `FixationSequence` object. Let's create some pretend data to play around with:

```python
>>> seq = eyekit.FixationSequence([[106, 540, 100], [190, 536, 100], [230, 555, 100], [298, 540, 100], [361, 547, 100], [430, 539, 100], [450, 539, 100], [492, 540, 100], [562, 555, 100], [637, 541, 100], [712, 539, 100], [763, 529, 100]])
```

Each fixation is represented by three numbers: its x-coordinate, its y-coordinate, and its duration (in this example, they're all 100ms). Once created, a `FixationSequence` can be traversed, indexed, and sliced as you'd expect. For example,

```python
>>> print(seq[5:10])
### FixationSequence[Fixation[430,539], ..., Fixation[637,541]]
```

slices out fixations 5 through 9 into a new `FixationSequence` object. This could be useful, for example, if you wanted to remove superfluous fixations from the start and end of the sequence.

A basic question we might have at this point is: Do any of these fixations fall inside my interest areas? We can write some simple code to answer this:

```python
>>> for fixation in seq:
>>>     ia = txt.which_interest_area(fixation)
>>>     if ia is not None:
>>>         print('There was a fixation inside interest area {}, which is "{}".'.format(ia.label, ia.text))
### There was a fixation inside interest area stem_1, which is "jump".
### There was a fixation inside interest area stem_1, which is "jump".
### There was a fixation inside interest area suffix_1, which is "ed".
```


Analysis
--------

At the moment, Eyekit has a fairly limited set of analysis functions; in general, you are expected to write code to calculate whatever you are interested in measuring. The functions that are currently available can be explored in the `analysis` module, but two common functions are `analysis.initial_fixation_duration()` and `analysis.total_fixation_duration()`, which may be used like this:

```python
>>> tot_durations = eyekit.analysis.total_fixation_duration(txt.interest_areas(), seq)
>>> print(tot_durations)
### {'stem_1': 200, 'suffix_1': 100}
>>> init_durations = eyekit.analysis.initial_fixation_duration(txt.interest_areas(), seq)
>>> print(init_durations)
### {'stem_1': 100, 'suffix_1': 100}
```

In this case, we see that the total time spent inside the `stem_1` interest area was 200ms, while the duration of the initial fixation on that interest area was 100ms. Similarly, these analysis functions can be applied to other kinds of interest areas, such as words:

```python
>>> tot_durations_on_words = eyekit.analysis.total_fixation_duration(txt.words(), seq)
>>> print(tot_durations_on_words)
### {'word_0': 100, 'word_1': 200, 'word_2': 100, 'word_3': 100, 'word_4': 300, 'word_5': 100, 'word_6': 100, 'word_7': 100, 'word_8': 100}
```

Here we see that a total of 300ms was spent on `word_4`, "jumped".


Visualization
-------------

Eyekit has some basic tools to help you create visualizations of your data. We begin by creating an `Image` object, specifying the pixel dimensions of the screen:

```python
>>> img = eyekit.Image(1920, 1080)
```

Next we render our text and fixations:

```python
>>> img.render_text(txt, font='Courier New', fontsize=28)
>>> img.render_fixations(seq)
```

Since we did not specify the font and fontsize when we first created the `TextBlock`, it is necessary to specify these details as arguments to `Image.render_text()`. You can use any font available on your system, but note that only monospaced fonts are appropriate because of the strict grid layout. Note also that the elements of the image will be layered in the order in which these methods are called – in this case, the fixations will be rendered on top of the text.

Finally, we save the image. Eyekit natively creates images in the SVG format, but, if you have [CairoSVG](https://cairosvg.org) installed, the images can be converted to PDF, EPS, or PNG on the fly by using the appropriate file extension:

```python
>>> img.save('quick_brown.pdf')
```
<img src='./docs/quick_brown.svg'>

Sometimes it's useful to see the text in the context of the entire screen, as is the case here; other times, we'd like to remove all that excess white space and focus on the text. To do this, you can call the `crop_to_text()` method prior to saving, optionally specifying some amount of margin:

```python
>>> img.crop_to_text(margin=5)
>>> img.save('quick_brown_cropped.pdf')
```
<img src='./docs/quick_brown_cropped.svg'>

There are many other options for creating custom visualizations, which you can explore in the `image` module. For example, if you wanted to depict the bounding boxes around the two interest areas, with different colors for stems and suffixes, you might do this:

```python
>>> img = eyekit.Image(1920, 1080)
>>> img.render_text(txt, font='Courier New', fontsize=28)
>>> for interest_area in txt.interest_areas():
>>>     if interest_area.label.startswith('stem'):
>>>         img.draw_rectangle(interest_area.bounding_box, color='red')
>>>     elif interest_area.label.startswith('suffix'):
>>>         img.draw_rectangle(interest_area.bounding_box, color='blue')
>>> img.render_fixations(seq)
>>> img.crop_to_text(margin=5)
>>> img.save('quick_brown_with_IAs.pdf')
```
<img src='./docs/quick_brown_with_IAs.svg'>


Multiline Passages
------------------

So far, we've only looked at a single line `TextBlock`, but handling multiline passages works in largely the same way. The principal difference is that when you instantiate your `TextBlock` object, you must pass a *list* of strings (one for each line of text):

```python
>>> txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], position=(100, 540), character_width=16, line_height=64)
```

 To see an example, we'll load in some multiline passage data that is included in this repository:

```python
>>> example_data = eyekit.io.read('example/example_data.json')
>>> example_texts = eyekit.io.load_texts('example/example_texts.json')
```

and in particular we'll extract the fixation sequence for trial 0 and its associated text:

```python
>>> seq = example_data['trial_0']['fixations']
>>> pid = example_data['trial_0']['passage_id']
>>> txt = example_texts[pid]
```

As before, we can plot the fixation sequence over the passage of text to see what the data looks like:

```python
>>> img = eyekit.Image(1920, 1080)
>>> img.render_text(txt)
>>> img.render_fixations(seq)
>>> img.crop_to_text(margin=50)
>>> img.save('multiline_passage.pdf')
```
<img src='./docs/multiline_passage.svg'>

A common issue with multiline passage reading is that fixations on one line may appear closer to another line due to imperfect eyetracker calibration or general noise. For example, the fixation on "voce" on line two actually falls into the bounding box of the word "vivevano" on line one. Likewise, the fixation on "passeggiata" in the middle of the text is closer to "Mamma" on the line above. Obviously, such "vertical drift" will cause issues in your analysis further downstream, so it may be useful to first clean up the data by snapping every fixation to its appropriate line. Eyekit implements several vertical drift correction algorithms, which can be applied using the `tools.snap_to_lines()` function from the `tools` module:

```python
>>> clean_seq = eyekit.tools.snap_to_lines(seq, txt, method='warp')
```

This process only affects the y-coordinate of each fixation; the x-coordinate is always left unchanged. The default method is `warp`, but you can also use `chain`, `cluster`, `merge`, `regress`, `segment`, and `split`. For a full description and evaluation of these methods, see [Carr et al. (2020)](https://osf.io/jg3nc/). Let's have a look at the fixation sequence after applying this cleaning step:

```python
>>> img = eyekit.Image(1920, 1080)
>>> img.render_text(txt)
>>> img.render_fixations(clean_seq)
>>> img.crop_to_text(50)
>>> img.save('multiline_passage_corrected.pdf')
```
<img src='./docs/multiline_passage_corrected.svg'>

The fixations on "voce" and "passeggiata", for example, are now clearly associated with the correct words, allowing us to proceed with our analysis. It is important to note, however, that drift correction should be applied with care, especially if the fixation data is very noisy or if the passage is being read nonlinearly.


Input–Output
------------

Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, and a duration for each fixation, you are free to store data in whatever format you choose. However, as we have seen above, Eyekit provides built-in support for a JSON-based format, where a typical data file looks like this:

```json
{
  "trial_0" : {
    "participant_id": "John",
    "passage_id": "passage_a",
    "fixations": [[412, 142, 131], [459, 163, 112], [551, 160, 334], ..., [588, 866, 224]]
  },
  "trial_1" : {
    "participant_id": "Mary",
    "passage_id": "passage_b",
    "fixations": [[368, 146, 191], [431, 154, 246], [512, 150, 192], ..., [725, 681, 930]]
  },
  "trial_2" : {
    "participant_id": "Jack",
    "passage_id": "passage_c",
    "fixations": [[374, 147, 277], [495, 151, 277], [542, 155, 138], ..., [1288, 804, 141]]
  }
}
```

This format is open, human-readable, and fairly flexible. Each trial object should contain a key called `fixations` that maps to an array containing x, y, and duration for each fixation. Aside from this, you can freely add other key–value pairs (e.g., participant IDs, trial IDs, timestamps, etc.). Data files that conform to this format can be loaded using the `io.read()` function from the `io` module:

```python
>>> data = eyekit.io.read('example_data.json')
```

and written using the `io.write()` function:

```python
>>> eyekit.io.write(data, 'example_data.json', indent=2)
```

Optionally, the `indent` parameter specifies how much indentation to use in the files – indentation results in larger files, but they are more human-readable.

If you store your fixation data in CSV files, you could load the data into a `FixationSequence` by doing something along these lines (assuming you have columns `x`, `y`, and `duration`):

```python
>>> import pandas
>>> data = pandas.read_csv('mydata.csv')
>>> seq = eyekit.FixationSequence([fxn for fxn in zip(data['x'], data['y'], data['duration'])])
```

Eyekit also has rudimentary support for importing data from ASC files. When importing data this way, you must specify the name of a trial variable and its possible values so that the importer can determine when a new trial begins:

```python
>>> data = eyekit.io.import_asc('mydata.asc', 'trial_type', ['Experimental'], extract_vars=['passage_id', 'response'])
```

In this case, when parsing the ASC file, the importer would consider

```plaintext
MSG 4244100 !V TRIAL_VAR trial_type Experimental
```

to mark the beginning of a new trial and will extract all `EFIX` lines that occur within the subsequent `START`–`END` block. Optionally, you can specify other variables that you want to extract (in this case `passage_id` and `response`), resulting in imported data that looks like this:

```python
{
  "trial_0" : {
    "trial_type" : "Experimental",
    "passage_id" : "passage_a",
    "response" : "yes",
    "fixations" : FixationSequence[[368, 161, 208], ..., [562, 924, 115]]
  }
}
```

In addition, rather than load one ASC file at a time, you can also point to a directory of ASC files, all of which will then be loaded into a single dataset:

```python
>>> data = eyekit.io.import_asc('asc_data_files/', 'trial_type', ['Experimental'], extract_variables=['passage_id', 'response'])
```

which could then be written out to Eyekit's native format:

```python
>>> eyekit.io.write(data, 'converted_asc_data.json')
```
