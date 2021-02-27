<img src='./docs/images/logo.png' width='300'>

**[If you don't see the images below, this guide, along with full documentation, can also be read here](https://jwcarr.github.io/eyekit/)**

Eyekit is a Python package for analyzing reading behavior using eyetracking data. Eyekit aims to be entirely independent of any particular eyetracker hardware, presentation software, or data formats. It has an object-oriented style that defines two core objects – the TextBlock and the FixationSequence – that you bring into contact with a bit of coding. Eyekit is currently in the alpha stage of development and is licensed under the terms of the MIT License.


Is Eyekit the Right Tool for Me?
--------------------------------

- You want to analyze which parts of a text someone is looking at and for how long.

- You are mostly interested in fixations, as opposed to, for example, saccades, blinks, or millisecond-by-millisecond eye movements.

- You need convenient tools for extracting areas of interest from texts, such as specific words, phrases, or letter combinations.

- You need support for arbitrary fonts, multiline passages, right-to-left text, or non-alphabetical scripts.

- You want the flexibility to define custom reading measures and to build your own reproducible processing pipeline.

- You would like tools for dealing with noise and calibration issues, and for discarding fixations according to your own criteria.

- You want to share your data in an open format and produce publication-ready vector graphics.


Installation
------------

Eyekit can be installed using `pip`:

```shell
$ pip install eyekit
```

Eyekit is compatible with Python 3.6+ and has two dependencies:

- [NumPy](https://numpy.org)
- [Cairocffi](https://github.com/Kozea/cairocffi)

Cairocffi is a Python wrapper around the graphics library [Cairo](https://cairographics.org), which you will also need to install if you don't already have it on your system. Many Linux distributions have Cairo built in. On a Mac, it can be installed using [Homebrew](https://brew.sh): `brew install cairo`. On Windows, your best bet might be [Anaconda](https://anaconda.org/anaconda/cairo).


Getting Started
---------------

Once installed, import Eyekit in the normal way:

```python
>>> import eyekit
```

Eyekit makes use of two core objects: the `FixationSequence` and the `TextBlock`. Much of Eyekit's functionality involves bringing these two objects into contact. Typically, you define particular areas of the `TextBlock` that are of interest (phrases, words, morphemes, letters...) and check to see which fixations from the `FixationSequence` fall in those areas and for how long.

### The FixationSequence object

Fixation data is represented in a `FixationSequence`. Usually you will import fixation data from some raw data files, but for now let's just create some pretend data to play around with:

```python
>>> seq = eyekit.FixationSequence([[106, 490, 0, 100], [190, 486, 100, 200], [230, 505, 200, 300], [298, 490, 300, 400], [361, 497, 400, 500], [430, 489, 500, 600], [450, 505, 600, 700], [492, 491, 700, 800], [562, 505, 800, 900], [637, 493, 900, 1000], [712, 497, 1000, 1100], [763, 487, 1100, 1200]])
```

Each fixation is represented by four numbers: its x-coordinate, its y-coordinate, its start time, and its end time (so, in this example, they all last 100ms). Once created, a `FixationSequence` can be traversed, indexed, and sliced just like an ordinary `list`. For example,

```python
>>> print(seq[5:10])
### FixationSequence[Fixation[430,489], ..., Fixation[637,493]]
```

slices out fixations 5 through 9 into a new `FixationSequence` object. This could be useful, for example, if you wanted to remove superfluous fixations from the start and end of the sequence. A `FixationSequence` (and the `Fixation` objects it contains) has various properties that you can query:

```python
>>> print(len(seq)) # Number of fixations
### 12
>>> print(seq.duration) # Duration of whole sequence
### 1200
>>> print(seq[0].duration) # Duration of first fixation
### 100
>>> print(seq[-1].xy) # xy coordinates of final fixation
### (763, 487)
>>> print(seq[1].x) # x coordinate of second fixation
### 190
```

### The TextBlock object

A `TextBlock` can represent a word, sentence, or passage of text. When you create a `TextBlock` object, it is necessary to specify various details such as its position on the screen and the font:

```python
>>> sentence = 'The quick brown fox [jump]{stem}[ed]{suffix} over the lazy dog.'
>>> txt = eyekit.TextBlock(sentence, position=(100, 500), font_face='Times New Roman', font_size=36)
>>> print(txt)
### TextBlock[The quick brown ...]
```

Eyekit has a simple scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case *jump* and *ed*) and curly braces are used to provide a unique ID for each interest area (in this case `stem` and `suffix`). These interest areas that have been specifically marked up in the raw text are called "zones". We can extract a particular zone as an `InterestArea` object by using its ID:

```python
>>> print(txt['stem'])
### InterestArea[stem, jump]
```

or indeed we can iterate over all the marked-up zones using the `TextBlock.zones()` iterator:

```python
>>> for zone in txt.zones():
>>>   print(zone)
### InterestArea[stem, jump]
### InterestArea[suffix, ed]
```

Zones are useful if you have a small number of interest areas that are convenient to mark up in the raw text. However, Eyekit also provides more powerful tools for automatically extracting interest areas. For example, you can use `TextBlock.words()` to iterate over every word in the text as an `InterestArea` without needing to explicitly mark each of them up in the raw text:

```python
>>> for word in txt.words():
>>>   print(word)
### InterestArea[0:0:3, The]
### InterestArea[0:4:9, quick]
### InterestArea[0:10:15, brown]
### InterestArea[0:16:19, fox]
### InterestArea[0:20:26, jumped]
### InterestArea[0:27:31, over]
### InterestArea[0:32:35, the]
### InterestArea[0:36:40, lazy]
### InterestArea[0:41:44, dog]
```

You can also supply a regular expression to iterate over words that match a certain pattern; words that end in *ed* for example:

```python
>>> for word in txt.words('.+ed'):
>>>   print(word)
### InterestArea[0:20:26, jumped]
```

or just the four-letter words:

```python
>>> for word in txt.words('.{4}'):
>>>   print(word)
### InterestArea[0:27:31, over]
### InterestArea[0:36:40, lazy]
```

or case-insensitive occurrences of the word *the*:

```python
>>> for word in txt.words('(?i)the'):
>>>   print(word)
### InterestArea[0:0:3, The]
### InterestArea[0:32:35, the]
```

You can also collate a bunch of interest areas into a list for convenient access later on. For example, if you wanted to do some analysis on all the three-letter words, you might extract them and assign them to a variable like so:

```python
>>> three_letter_words = list(txt.words('.{3}'))
>>> print(three_letter_words)
### [InterestArea[0:0:3, The], InterestArea[0:16:19, fox], InterestArea[0:32:35, the], InterestArea[0:41:44, dog]]
```

You can also slice out arbitrary interest areas by using the row and column indices of a section of text. Here, for example, we are extracting a two-word section of text from line 0 (the first and only line) and characters 10 through 18:

```python
>>> print(txt[0:10:19])
### InterestArea[0:10:19, brown fox]
```

### The InterestArea object

Once you've extracted an `InterestArea`, you can access various properties about it:

```python
>>> brown_fox = txt[0:10:19]
>>> print(brown_fox.text) # get the string represented in this IA
### brown fox
>>> print(brown_fox.width) # get the pixel width of this IA
### 157.974609375
>>> print(brown_fox.center) # get the xy coordinates of the center of the IA
### (328.4365234375, 491.94921875)
>>> print(brown_fox.onset) # get the x coordinate of the IA onset
### 253.94921875
>>> print(brown_fox.location) # get the location of the IA in its parent TextBlock
### (0, 10, 19)
>>> print(brown_fox.id) # get the ID of the IA
### 0:10:19
```

By default, an `InterestArea` will have an ID of the form `0:10:19`, which refers to the unique position that it occupies in the text. However, you can also change the IDs to something more descriptive, if you wish. For example, you could enumerate the words in the text and give each one a number:

```python
>>> for i, word in enumerate(txt.words()):
>>>   word.id = f'word{i}'
```

and, since `InterestArea`s are passed around by reference, the IDs will update everywhere. For example, it we print the `three_letter_words` list we created earlier, we find that it now reflects the new IDs:

```python
>>> print(three_letter_words)
### [InterestArea[word0, The], InterestArea[word3, fox], InterestArea[word6, the], InterestArea[word8, dog]]
```

The `InterestArea` defines the `in` operator in a special way so that you can conveniently check if a fixation falls inside its bounding box. For example:

```python
>>> for fixation in seq:
>>>   if fixation in brown_fox:
>>>     print(fixation)
### Fixation[298,490]
### Fixation[361,497]
```

```python
>>> for fixation in seq:
>>>   for zone in txt.zones():
>>>     if fixation in zone:
>>>       print(f'{fixation} is inside {zone}')
### Fixation[430,489] is inside InterestArea[stem, jump]
### Fixation[450,505] is inside InterestArea[stem, jump]
### Fixation[492,491] is inside InterestArea[suffix, ed]
```

The `TextBlock` also provides some more convenient methods for asking these kinds of questions, for example:

```python
>>> print(txt.which_word(seq[3])) # which word is fixation 3 inside?
### InterestArea[word2, brown]
>>> print(txt.which_character(seq[3])) # which character specifically?
### InterestArea[0:12:13, o]
```

An `InterestArea` can be any sequence of consecutive characters, and, as you can see, it's possible to define several overlapping `InterestArea`s at the same time: `txt['word4']` (*jumped*), `txt['stem']` (*jump*), `txt['suffix']` (*ed*), and `txt[0:24:25]` (the *p* in *jumped*) can all coexist.


Visualization
-------------

Now that we've created a `FixationSequence` and `TextBlock`, it would be useful to visualize how they relate to each other. To create a visualization, we begin by creating an `Image` object, specifying the pixel dimensions of the screen:

```python
>>> img = eyekit.vis.Image(1920, 1080)
```

Next we render our text and fixations onto this image:

```python
>>> img.draw_text_block(txt)
>>> img.draw_fixation_sequence(seq)
```

Note that the elements of the image will be layered in the order in which these methods are called – in this case, the fixations will be rendered on top of the text. Finally, we save the image (Eyekit supports PDF, EPS, SVG, or PNG):

```python
>>> img.save('quick_brown.pdf')
```
<img src='./docs/images/quick_brown.pdf' width='100%'>

Sometimes it's useful to see the text in the context of the entire screen, as is the case here; other times, we'd like to remove all that excess white space and focus in on the text. To do this, you need to specify a crop margin; the image will then be cropped to the size of the text block plus the specified margin:

```python
>>> img.save('quick_brown_cropped.pdf', crop_margin=1)
```
<img src='./docs/images/quick_brown_cropped.pdf' width='100%'>

There are many other options for creating custom visualizations, which you can explore in the `vis` module. For example, if you wanted to depict the bounding boxes around the two zoned interest areas we defined earlier, you might do this:

```python
>>> img = eyekit.vis.Image(1920, 1080)
>>> img.draw_text_block(txt)
>>> img.draw_rectangle(txt['stem'], color='crimson')
>>> img.draw_rectangle(txt['suffix'], color='cadetblue')
>>> img.draw_fixation_sequence(seq)
>>> img.save('quick_brown_with_zones.pdf', crop_margin=1)
```
<img src='./docs/images/quick_brown_with_zones.pdf' width='100%'>

Colors can be specified as a tuple of RGB values (e.g. `(220, 20, 60)`), a hex triplet (e.g. `#DC143C`), or any [standard HTML color name](https://www.w3schools.com/colors/colors_names.asp) (e.g. `crimson`). Similarly, we can do the same thing with the list of three-letter words we created earlier:

```python
>>> img = eyekit.vis.Image(1920, 1080)
>>> img.draw_text_block(txt)
>>> for word in three_letter_words:
>>>   img.draw_rectangle(word, color='slateblue')
>>> img.draw_fixation_sequence(seq)
>>> img.save('quick_brown_with_3letter_words.pdf', crop_margin=1)
```
<img src='./docs/images/quick_brown_with_3letter_words.pdf' width='100%'>

Or, indeed, all words in the text:

```python
>>> img = eyekit.vis.Image(1920, 1080)
>>> img.draw_text_block(txt)
>>> for word in txt.words():
>>>   img.draw_rectangle(word, color='hotpink')
>>> img.draw_fixation_sequence(seq)
>>> img.save('quick_brown_with_all_words.pdf', crop_margin=1)
```
<img src='./docs/images/quick_brown_with_all_words.pdf' width='100%'>

Note that, by default, each `InterestArea`'s bounding box is slightly padded by, at most, half of the width of a space character. This ensures that, even if a fixation falls between two words, it will still be assigned to one of them. Padding is only applied to an `InterestArea`'s edge if that edge adjoins a non-alphabetical character (i.e. spaces and punctuation). Thus, when *jumped* was divided into separate stem and suffix areas above, no padding was applied word-internally. If desired, automatic padding can be turned off by setting the `autopad` argument to `False` during the creation of the `TextBlock`, or it can be controlled manually using the `InterestArea.adjust_padding()` method.


Performing Analyses
-------------------

At the moment, Eyekit has a fairly limited set of analysis functions, which you can explore in the `analysis` module. These functions take as input a collection of `InterestArea` objects and a `FixationSequence`, and they return as output a dictionary in which the keys are the `InterestArea` IDs and the values are the relevant measure. For example, if we wanted to calculate the initial fixation duration on the three-letter words we extracted earlier, we can do this:

```python
>>> results = eyekit.analysis.initial_fixation_duration(three_letter_words, seq)
>>> print(results)
### {'word0': 100, 'word3': 100, 'word6': 100, 'word8': 100}
```

In this case, we see that the initial fixation on each of the three-letter words lasted 100ms. Or, if we wanted to know the total fixation duration on all words:

```python
>>> results = eyekit.analysis.total_fixation_duration(txt.words(), seq)
>>> print(results)
### {'word0': 100, 'word1': 200, 'word2': 100, 'word3': 100, 'word4': 300, 'word5': 100, 'word6': 100, 'word7': 100, 'word8': 100}
```

Here we see that the total fixation duration on `word4` (*jumped*) was 300ms. Another thing we can measure is the initial landing position:

```python
>>> results = eyekit.analysis.initial_landing_position(txt.zones(), seq)
>>> print(results)
### {'stem': 2, 'suffix': 1}
```

Here we see that the initial fixation on `stem` (*jump*) landed in position 2, and the initial fixation on `suffix` (*ed*) landed in position 1.


Multiline Passages
------------------

So far, we've only looked at a single line `TextBlock`, but handling multiline passages works in largely the same way. The principal difference is that when you instantiate your `TextBlock` object, you must pass a *list* of strings (one for each line of text):

```python
>>> txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], position=(100, 500), font_face='Helvetica', font_size=24)
```

To see an example, we'll load in some real multiline passage data from [Pescuma et al.](https://osf.io/hx2sj/) which is included in the [Eyekit GitHub repository](https://github.com/jwcarr/eyekit):

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
>>> img = eyekit.vis.Image(1920, 1080)
>>> img.draw_text_block(txt)
>>> img.draw_rectangle(txt[0:32:40], color='orange')
>>> img.draw_rectangle(txt[1:34:38], color='orange')
>>> img.draw_fixation_sequence(seq)
>>> img.save('multiline_passage.pdf', crop_margin=4)
```
<img src='./docs/images/multiline_passage.pdf' width='100%'>

First, we might decide that we want to discard that final fixation, where the participant jumped a few lines up right at the end:

```python
>>> seq[-1].discard() # discard the final fixation
```

A second problem we can see here is that fixations on one line sometimes appear slightly closer to another line due to imperfect eyetracker calibration. For example, the fixation on the word *voce* on line two actually falls into the bounding box of the word *vivevano* on line one. Obviously, this will cause issues in your analysis further downstream, so it can be useful to first clean up the data by snapping every fixation to its appropriate line. Eyekit implements several different line assignment algorithms, which can be applied using the `tools.snap_to_lines()` function from the `tools` module:

```python
>>> original_seq = seq.copy() # keep a copy of the original sequence
>>> eyekit.tools.snap_to_lines(seq, txt)
```

This process only affects the y-coordinate of each fixation (the x-coordinate is always left unchanged). To compare the corrected fixation sequence to the original, we can make two images and then combine them in a single `Figure`:

```python
>>> img1 = eyekit.vis.Image(1920, 1080)
>>> img1.draw_text_block(txt)
>>> img1.draw_rectangle(txt[0:32:40], color='orange')
>>> img1.draw_rectangle(txt[1:34:38], color='orange')
>>> img1.draw_fixation_sequence(original_seq)
>>> img1.set_caption('Before correction')
>>> 
>>> img2 = eyekit.vis.Image(1920, 1080)
>>> img2.draw_text_block(txt)
>>> img2.draw_rectangle(txt[0:32:40], color='orange')
>>> img2.draw_rectangle(txt[1:34:38], color='orange')
>>> img2.draw_fixation_sequence(seq)
>>> img2.set_caption('After correction')
>>> 
>>> fig = eyekit.vis.Figure(1, 2) # one row, two columns
>>> fig.add_image(img1)
>>> fig.add_image(img2)
>>> fig.set_crop_margin(3)
>>> fig.save('multiline_passage_corrected.pdf')
```
<img src='./docs/images/multiline_passage_corrected.pdf' width='100%'>

The fixation on *voce* is now clearly associated with that word. It is important to note, however, that drift correction should be applied with care, especially if the fixation data is very noisy or if the passage is being read nonlinearly.

Just like single-line texts, we can extract interest areas from the passage and apply analysis functions in the same way. For example, if we were interested in the word *piccolo*/*piccola* in this passage, we could extract all occurrences of this word and calculate the total fixation duration:

```python
>>> piccol_words = list(txt.words('piccol[oa]'))
>>> durations = eyekit.analysis.total_fixation_duration(piccol_words, seq)
>>> print(durations)
### {'2:64:71': 253, '3:0:7': 347, '3:21:28': 246, '3:29:36': 319, '7:11:18': 268, '10:43:50': 178}
```

Furthermore, we could make a visualization to show this information:

```python
>>> img = eyekit.vis.Image(1920, 1080)
>>> img.draw_text_block(txt)
>>> for word in piccol_words:
>>>   img.draw_rectangle(word, color='lightseagreen')
>>>   x = word.onset
>>>   y = word.y_br - 3
>>>   label = f'{durations[word.id]}ms'
>>>   img.draw_annotation(x, y, label, color='lightseagreen', font_face='Arial bold', font_size=4)
>>> img.draw_fixation_sequence(seq, color='gray')
>>> img.save('multiline_passage_piccol.pdf', crop_margin=4)
```
<img src='./docs/images/multiline_passage_piccol.pdf' width='100%'>

Another way to look at the data is to distribute the fixations across the characters of the passage probabilistically, under the assumption that the closer a character is to a fixation point, the more likely it is that the reader is perceiving that character. This can be performed with the `analysis.duration_mass` function and plotted in a heatmap like so:

```python
>>> mass = eyekit.analysis.duration_mass(txt, seq)
>>> img = eyekit.vis.Image(1920, 1080)
>>> img.draw_text_block_heatmap(txt, mass, color='green')
>>> img.save('multiline_passage_mass.pdf', crop_margin=4)
```
<img src='./docs/images/multiline_passage_mass.pdf' width='100%'>


Input–Output
------------

Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, a start time, and an end time for each fixation, you are free to store data in whatever format you choose. However, as we have seen briefly above, Eyekit provides built-in support for JSON, where a typical data file might look something like this:

```json
{
  "trial_0" : {
    "participant_id": "John",
    "passage_id": "passage_a",
    "fixations": { "__FixationSequence__" : [[412, 142, 770, 900], ..., [655, 653, 46483, 46532]] }
  },
  "trial_1" : {
    "participant_id": "Mary",
    "passage_id": "passage_b",
    "fixations": { "__FixationSequence__" : [[368, 146, 7, 197], ..., [725, 681, 30331, 31260]] }
  },
  "trial_2" : {
    "participant_id": "Jack",
    "passage_id": "passage_c",
    "fixations": { "__FixationSequence__" : [[374, 147, 7, 283], ..., [890, 267, 31931, 32153]] }
  }
}
```

This format is compact, structured, human-readable, and flexible. With the exception of the `__FixationSequence__` object, you can freely store whatever key-value pairs you want and you can organize the hierarchy of the data structure in any way that makes sense for your project. JSON files can be loaded using the `io.read()` function from the `io` module:

```python
>>> data = eyekit.io.read('example/example_data.json')
```

which automatically instantiates any `FixationSequence` objects. Similarly, an arbitrary dictionary or list can be written out using the `io.write()` function:

```python
>>> eyekit.io.write(data, 'output_data.json', compress=True)
```

If `compress` is set to `True`, files are written in the most compact way; if `False`, the file will be larger but more human-readable (like the example above). JSON can also be used to store `TextBlock` objects – see `example_texts.json` for an example – and you can even store `FixationSequence` and `TextBlock` objects in the same file if you like to keep things organized together.

The `io` module also provides functions for importing data from other formats: `io.import_asc()` and `io.import_csv()`. Once data has been imported this way, it may then be written out to Eyekit's native JSON format for quick access in the future. In time, I hope to add more functions to import data from common eyetracking formats.


Getting Texts into Eyekit
-------------------------

Getting texts into Eyekit can be a little tricky because their precise layout will be highly dependent on many different factors – not just the font and its size, but also the peculiarities of the presentation software and its text rendering engine.

Ideally, all of your texts will be presented in some consistent way. For example, they might be centralized on the screen or they might have a consistent left edge. Once you specify how a text is positioned on screen, Eyekit calculates the location and bounding box of every character based on the particular font and font size you are using. This process is somewhat imperfect, however, especially if you are using a proportional font that makes use of advanced typographical features such as kerning and ligatures, as is the case in the example below.

The best way to check that the `TextBlock` is set up correctly is to check it against a screenshot from your actual experiment. Eyekit provides the `tools.align_to_screenshot()` tool to help you do this. First, set up your text block with parameters that you think are correct:

```python
>>> txt = eyekit.TextBlock(saramago_text, position=(300, 100), font_face='Baskerville', font_size=30, line_height=60, align='left', anchor='left')
```

Then pass it to the `tools.align_to_screenshot()` function along with the path to a PNG screenshot file:

```python
>>> eyekit.tools.align_to_screenshot(txt, 'screenshot.png')
```
<img src='./docs/images/screenshot_eyekit.png' width='100%'>

This will create a new image file ending `_eyekit.png` (e.g. `screenshot_eyekit.png`). In this file, Eyekit's rendering of the text is presented in green overlaying the original screenshot image. The point where the two solid green lines intersect corresponds to the `TextBlock`'s `position` argument, and the dashed green lines show the baselines of subsequent lines of text, which is based on the `line_height` argument. You can use this output image to adjust the parameters of the `TextBlock` accordingly. If all of your texts are presented in a consistent way, you should only need to establish these parameters once.

An alternative strategy would be to produce your experimental stimuli using Eyekit. For example, you could export images of your TextBlocks, and then display them full-size in some experimental presentation software of your choice.


Contributing
------------

Eyekit is still in an early stage of development, but I am very happy to receive bug reports and suggestions via the [GitHub Issues page](https://github.com/jwcarr/eyekit/issues). If you'd like to work on new features or fix stuff that's currently broken, please feel free to fork the repo and/or raise an issue to discuss details. Before sending a pull request, you should check that the unit tests pass using [Pytest](https://pytest.org):

```shell
$ pytest tests/
```

and run [Black](https://black.readthedocs.io) over the codebase to normalize the style:

```shell
$ black eyekit/
```

Here are some areas of Eyekit that are currently underdeveloped:

- Additional analytical measures (e.g. of saccades and regressions)
- Awareness of different experimental paradigms
- Creation of animations/videos
- More convenient methods for collating results into dataframes etc.
- Importing data from other eyetracker data formats
- Synchronization of fixation data with other types of experimental event
- Support for nontextual objects, such as images or shapes
- Interactive tools for cleaning up raw data
