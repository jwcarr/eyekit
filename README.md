<img src='./docs/logo.png' width='300'>

Eyekit is a lightweight Python package for doing open, transparent, reproducible science on reading behavior. Eyekit is entirely independent of any particular eyetracker hardware, presentation software, or data formats, and has a minimal set of dependencies. It has an object-oriented style that defines two core objects – the TextBlock and the FixationSequence – that you bring into contact with a bit of coding. Eyekit is currently in the pre-alpha stage and is licensed under the terms of the MIT License. [Full documentation is available here](https://jwcarr.github.io/eyekit/).


Is Eyekit the Right Tool for Me?
--------------------------------

- You basically just want to analyze which parts of a text someone is looking at by defining areas of interest.

- You are interested in a fixation-level analysis, as opposed to, for example, saccades or millisecond-by-millisecond eye movements.

- You don't mind doing a little bit of legwork to transform your raw fixation data and texts into something Eyekit can understand.

- You need support for arbitrary fonts that may be monospaced or proportional.

- You want the flexibility to define custom measures and to build your own reproducible processing pipeline.

- You would like tools for dealing with noise and calibration issues, such as vertical drift, and for discarding fixations according to your own criteria.

- You want to produce publication-ready visualizations and to share your data in a standard and open format.


Installation
------------

The latest version of Eyekit can be installed using `pip`:

```shell
$ pip install eyekit
```

Eyekit is compatible with Python 3.6 and up and has four dependencies:

- [NumPy](https://numpy.org)
- [matplotlib](https://matplotlib.org)
- [fontTools](https://pypi.org/project/fonttools/)
- [CairoSVG](https://cairosvg.org)

[SciPy](https://www.scipy.org) and [scikit-learn](https://scikit-learn.org) are required by certain tools but can be installed later if needed.


Getting Started
---------------

Once installed, import Eyekit in the normal way:

```python
>>> import eyekit
```

Eyekit makes use of two core objects: the `TextBlock` and the `FixationSequence`. Much of Eyekit's functionality involves bringing these two objects into contact. Typically, you define particular areas of the `TextBlock` that are of interest (phrases, words, morphemes, letters...) and check to see which fixations from the `FixationSequence` fall in those areas and for how long.

### The TextBlock object

A `TextBlock` can represent a word, sentence, or passage of text. When you create a `TextBlock` object, it is necessary to specify the pixel position of the top-left corner, the font, and the font size. Optionally, you can also specify the line spacing (1 for single line spacing, 2 for double line spacing, etc.). Let's begin by creating a `TextBlock` representing a single sentence:

```python
>>> sentence = 'The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.'
>>> txt = eyekit.TextBlock(sentence, position=(100, 500), font_name='Times New Roman', font_size=36)
>>> print(txt)
### TextBlock[The quick brown ...]
```

Eyekit has a simple scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case *jump* and *ed*) and curly braces are used to provide a unique label for each interest area (in this case `stem_1` and `suffix_1`). These interest areas that have been specifically marked up in the raw text are called "zones". We can iterate over the zones using the `TextBlock.zones()` iterator:

```python
>>> for zone in txt.zones():
>>>     print(zone.label, zone.text, zone.box)
### stem_1 jump (411.923828125, 500.0, 74.00390625, 36.0)
### suffix_1 ed (485.927734375, 500.0, 33.978515625, 36.0)
```

In this case, we are printing each zone's label, the string of text it represents, and its bounding box (x, y, width, and height). In addition to manually marked-up zones, you can also create interest areas automatically based on the lines, words, characters, or ngrams of the text. If, for example, you were interested in all words, you could use `TextBlock.words()` to iterate over every word as an interest area without needing to explicitly mark them up in the raw text:

```python
>>> for word in txt.words():
>>>     print(word.label, word.text, word.box)
### word_0 The (95.5, 500.0, 64.96875, 36.0)
### word_1 quick (160.46875, 500.0, 88.98046875, 36.0)
### word_2 brown (249.44921875, 500.0, 100.986328125, 36.0)
### word_3 fox (350.435546875, 500.0, 56.98828125, 36.0)
### word_4 jumped (407.423828125, 500.0, 116.982421875, 36.0)
### word_5 over (524.40625, 500.0, 72.966796875, 36.0)
### word_6 the (597.373046875, 500.0, 52.98046875, 36.0)
### word_7 lazy (650.353515625, 500.0, 68.958984375, 36.0)
### word_8 dog (719.3125, 500.0, 63.0, 36.0)
```

You can also slice out arbitrary interest areas by using the row and column indices of a section of text. Here, for example, we are taking a slice from row 0 (the first and only line) and characters 10 through 18:

```python
>>> arbitrary_slice = txt[0, 10:19]
>>> print(arbitrary_slice.text, arbitrary_slice.box)
### brown fox (253.94921875, 500.0, 148.974609375, 36.0)
```

This could be useful if you wanted to slice up the text in some programmatic way, creating interest areas from each three-letter chunk, for example.

### The FixationSequence object

Fixation data is represented in a `FixationSequence` object. Let's create some pretend data to play around with:

```python
>>> seq = eyekit.FixationSequence([[106, 520, 100], [190, 516, 100], [230, 535, 100], [298, 520, 100], [361, 527, 100], [430, 519, 100], [450, 535, 100], [492, 521, 100], [562, 535, 100], [637, 523, 100], [712, 517, 100], [763, 517, 100]])
```

Each fixation is represented by three numbers: its x-coordinate, its y-coordinate, and its duration (in this example, they're all 100ms). Once created, a `FixationSequence` can be traversed, indexed, and sliced as you'd expect. For example,

```python
>>> print(seq[5:10])
### FixationSequence[Fixation[430,519], ..., Fixation[637,523]]
```

slices out fixations 5 through 9 into a new `FixationSequence` object. This could be useful, for example, if you wanted to remove superfluous fixations from the start and end of the sequence.

A basic question we might have at this point is: Do any of these fixations fall inside the zones I marked up? We can write some simple code to answer this, using one of the `which_` methods:

```python
>>> for fixation in seq:
>>>     zone = txt.which_zone(fixation)
>>>     if zone is not None:
>>>         print(f'There was a fixation inside {zone.label}, which is "{zone.text}".')
### There was a fixation inside stem_1, which is "jump".
### There was a fixation inside stem_1, which is "jump".
### There was a fixation inside suffix_1, which is "ed".
```


Analysis
--------

At the moment, Eyekit has a fairly limited set of analysis functions; in general, you are expected to write code to calculate whatever you are interested in measuring. The functions that are currently available can be explored in the `analysis` module, but two common eyetracking measures that *are* implemented are `analysis.initial_fixation_duration()` and `analysis.total_fixation_duration()`, which may be used like this:

```python
>>> tot_durations = eyekit.analysis.total_fixation_duration(txt.zones(), seq)
>>> print(tot_durations)
### {'stem_1': 200, 'suffix_1': 100}
>>> init_durations = eyekit.analysis.initial_fixation_duration(txt.zones(), seq)
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
>>> img.render_text(txt)
>>> img.render_fixations(seq)
```

Note that the elements of the image will be layered in the order in which these methods are called – in this case, the fixations will be rendered on top of the text. Finally, we save the image. Eyekit natively creates images in the SVG format, but the images can be converted to PDF, EPS, or PNG on the fly by using the appropriate file extension:

```python
>>> img.save('quick_brown.pdf')
```
<img src='./docs/quick_brown.svg'>

Sometimes it's useful to see the text in the context of the entire screen, as is the case here; other times, we'd like to remove all that excess white space and focus in on the text. To do this, you can call the `crop_to_text()` method prior to saving, optionally specifying some amount of margin:

```python
>>> img.crop_to_text(margin=5)
>>> img.save('quick_brown_cropped.pdf')
```
<img src='./docs/quick_brown_cropped.svg'>

There are many other options for creating custom visualizations, which you can explore in the `image` module. For example, if you wanted to depict the bounding boxes around the two zoned interest areas we defined earlier, with different colors for stems and suffixes, you might do this:

```python
>>> img = eyekit.Image(1920, 1080)
>>> img.render_text(txt)
>>> for zone in txt.zones():
>>>     if zone.label.startswith('stem'):
>>>         img.draw_rectangle(zone.bounding_box, color='red')
>>>     elif zone.label.startswith('suffix'):
>>>         img.draw_rectangle(zone.bounding_box, color='blue')
>>> img.render_fixations(seq)
>>> img.crop_to_text(margin=5)
>>> img.save('quick_brown_with_IAs.pdf')
```
<img src='./docs/quick_brown_with_IAs.svg'>


Multiline Passages
------------------

So far, we've only looked at a single line `TextBlock`, but handling multiline passages works in largely the same way. The principal difference is that when you instantiate your `TextBlock` object, you must pass a *list* of strings (one for each line of text):

```python
>>> txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], position=(100, 500), font_name='Arial', font_size=24)
```

To see an example, we'll load in some real multiline passage data from [Pescuma et al.](https://osf.io/hx2sj/) which is included in the [GitHub repository](https://github.com/jwcarr/eyekit):

```python
>>> example_data = eyekit.io.read('example/example_data.json')
>>> example_texts = eyekit.io.read('example/example_texts.json')
```

and in particular we'll extract the fixation sequence for trial 0 and its associated text:

```python
>>> seq = example_data['trial_0']['fixations']
>>> pid = example_data['trial_0']['passage_id']
>>> txt = example_texts[pid]['text']
```

As before, we can plot the fixation sequence over the passage of text to see what the data looks like:

```python
>>> img = eyekit.Image(1920, 1080)
>>> img.render_text(txt)
>>> img.draw_rectangle(txt[0, 32:40].box, color='orange')
>>> img.draw_rectangle(txt[4, 12:17].box, color='orange')
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

Just as with single-line texts, we can iterate over lines, words, characters, and ngrams using the appropriate methods and apply the same kinds of analysis functions. For example, if we were interested in the word "piccolo"/"piccola" in this passage, we could do this:

```python
>>> piccol_zones = list(txt.words('piccol[oa]'))
>>> tot_durations = eyekit.analysis.total_fixation_duration(piccol_zones, clean_seq)
>>> img = eyekit.Image(1920, 1080)
>>> img.render_text(txt)
>>> img.render_fixations(clean_seq, color='gray')
>>> for word in piccol_zones:
>>>   img.draw_rectangle(word.box, color='green')
>>>   duration = tot_durations[word.label]
>>>   img.draw_text(f'{duration}ms', word.x_br, word.y_br, color='green', style={'font-family':'Arial', 'font-weight':'bold', 'font-size':20})
>>> img.crop_to_text(50)
>>> img.save('multiline_passage_piccol.pdf')
```
<img src='./docs/multiline_passage_piccol.svg'>


Input–Output
------------

Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, and a duration for each fixation, you are free to store data in whatever format you choose. However, as we have seen briefly above, Eyekit provides built-in support for JSON, where a typical data file might look somthing like this:

```json
{
  "trial_0" : {
    "participant_id": "John",
    "passage_id": "passage_a",
    "fixations": { "__FixationSequence__" : [[412, 142, 131], ..., [588, 866, 224]] }
  },
  "trial_1" : {
    "participant_id": "Mary",
    "passage_id": "passage_b",
    "fixations": { "__FixationSequence__" : [[368, 146, 191], ..., [725, 681, 930]] }
  },
  "trial_2" : {
    "participant_id": "Jack",
    "passage_id": "passage_c",
    "fixations": { "__FixationSequence__" : [[374, 147, 277], ..., [1288, 804, 141]] }
  }
}
```

This format is open, human-readable, and flexible. With the exception of the `__FixationSequence__` object, you can freely store whatever key-value pairs you want and you can organize the hierarchy of the data structure in any way that makes sense for your project. JSON files can be loaded using the `io.read()` function from the `io` module:

```python
>>> data = eyekit.io.read('example/example_data.json')
>>> print(data)
### {'trial_0': {'participant_id': 'John', 'passage_id': 'passage_a', 'fixations': FixationSequence[Fixation[412,142], ..., Fixation[588,866]]}, 'trial_1': {'participant_id': 'Mary', 'passage_id': 'passage_b', 'fixations': FixationSequence[Fixation[368,146], ..., Fixation[725,681]]}, 'trial_2': {'participant_id': 'Jack', 'passage_id': 'passage_c', 'fixations': FixationSequence[Fixation[374,147], ..., Fixation[1288,804]]}}
```

which automatically instantiates any `FixationSequence` objects. Similarly, an arbitrary dictionary of data can be written out using the `io.write()` function:

```python
>>> eyekit.io.write(data, 'output_data.json', compress=True)
```

If `compress` is set to `True` (the default), files are written in the most compact way; if `False`, the file will be larger but more human-readable (like the example above). JSON can also be used to store `TextBlock` objects – see `example_texts.json` for an example – and you can even store `FixationSequence` and `TextBlock` objects in the same file if you like to keep things together.


Getting Your Data into Eyekit
-----------------------------

Currently, the options for converting your raw data into something Eyekit can understand are quite limited. In time, I hope to add more functions that convert from common formats.

### Fixation data

If you have your fixation data in CSV files, you could load the data into a `FixationSequence` by doing something along these lines (assuming you have columns `x`, `y`, and `duration`):

```python
>>> import pandas
>>> data = pandas.read_csv('mydata.csv')
>>> fixations = [fxn for fxn in zip(data['x'], data['y'], data['duration'])]
>>> seq = eyekit.FixationSequence(fixations)
```

Eyekit has rudimentary support for importing data from ASC files. When importing data this way, you must specify the name of a trial variable and its possible values so that the importer can determine when a new trial begins:

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

which could then be written out to Eyekit's native format for quick access in the future:

```python
>>> eyekit.io.write(data, 'converted_asc_data.json')
```

### Text data

Getting texts into Eyekit can be a little tricky because their precise layout will be highly dependent on many different factors – not just the font and fontsize, but also the presentation software and its text rendering engine, the size and resolution of the display, the positioning of the text, and perhaps even the operating system itself.

Ideally, all of your texts will be presented so that the top-left corner of the block of text is located in a consistent position on the screen (depending on how you set up your experiment, this may already be the case). Eyekit uses this position to figure out the precise location of characters and interest areas based on the particular font and font size you are using. However, this process is somewhat imperfect and you might need to experiment a little to get up and running. The best way to do this is to create a `TextBlock` with values that seem to make sense and then output a PNG image, which will have the exact pixel dimensions of the screen; you can then check that this image matches up with a screenshot of what your participants are actually seeing.
