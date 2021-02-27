URLS=[
"index.html",
"fixation.html",
"analysis.html",
"tools.html",
"io.html",
"vis.html",
"text.html"
];
INDEX=[
{
"ref":"eyekit",
"url":0,
"doc":"Eyekit is a Python package for analyzing reading behavior using eyetracking data. Eyekit aims to be entirely independent of any particular eyetracker hardware, presentation software, or data formats. It has an object-oriented style that defines two core objects \u2013 the TextBlock and the FixationSequence \u2013 that you bring into contact with a bit of coding. Eyekit is currently in the alpha stage of development and is licensed under the terms of the MIT License. Is Eyekit the Right Tool for Me?                 - You want to analyze which parts of a text someone is looking at and for how long. - You are mostly interested in fixations, as opposed to, for example, saccades, blinks, or millisecond-by-millisecond eye movements. - You need convenient tools for extracting areas of interest from texts, such as specific words, phrases, or letter combinations. - You need support for arbitrary fonts, multiline passages, right-to-left text, or non-alphabetical scripts. - You want the flexibility to define custom reading measures and to build your own reproducible processing pipeline. - You would like tools for dealing with noise and calibration issues, and for discarding fixations according to your own criteria. - You want to share your data in an open format and produce publication-ready vector graphics. Installation       Eyekit can be installed using  pip :   $ pip install eyekit   Eyekit is compatible with Python 3.6+ and has two dependencies: - [NumPy](https: numpy.org) - [Cairocffi](https: github.com/Kozea/cairocffi) Cairocffi is a Python wrapper around the graphics library [Cairo](https: cairographics.org), which you will also need to install if you don't already have it on your system. Many Linux distributions have Cairo built in. On a Mac, it can be installed using [Homebrew](https: brew.sh):  brew install cairo . On Windows, your best bet might be [Anaconda](https: anaconda.org/anaconda/cairo). Getting Started        - Once installed, import Eyekit in the normal way:   >>> import eyekit   Eyekit makes use of two core objects: the  fixation.FixationSequence and the  text.TextBlock . Much of Eyekit's functionality involves bringing these two objects into contact. Typically, you define particular areas of the  text.TextBlock that are of interest (phrases, words, morphemes, letters .) and check to see which fixations from the  fixation.FixationSequence fall in those areas and for how long.  The FixationSequence object Fixation data is represented in a  fixation.FixationSequence . Usually you will import fixation data from some raw data files, but for now let's just create some pretend data to play around with:   >>> seq = eyekit.FixationSequence( 106, 490, 0, 100], [190, 486, 100, 200], [230, 505, 200, 300], [298, 490, 300, 400], [361, 497, 400, 500], [430, 489, 500, 600], [450, 505, 600, 700], [492, 491, 700, 800], [562, 505, 800, 900], [637, 493, 900, 1000], [712, 497, 1000, 1100], [763, 487, 1100, 1200 )   Each fixation is represented by four numbers: its x-coordinate, its y-coordinate, its start time, and its end time (so, in this example, they all last 100ms). Once created, a  fixation.FixationSequence can be traversed, indexed, and sliced just like an ordinary  list . For example,   >>> print(seq[5:10])  FixationSequence[Fixation[430,489],  ., Fixation[637,493   slices out fixations 5 through 9 into a new  fixation.FixationSequence object. This could be useful, for example, if you wanted to remove superfluous fixations from the start and end of the sequence. A  fixation.FixationSequence (and the  fixation.Fixation objects it contains) has various properties that you can query:   >>> print(len(seq  Number of fixations  12 >>> print(seq.duration)  Duration of whole sequence  1200 >>> print(seq[0].duration)  Duration of first fixation  100 >>> print(seq[-1].xy)  xy coordinates of final fixation  (763, 487) >>> print(seq[1].x)  x coordinate of second fixation  190    The TextBlock object A  text.TextBlock can represent a word, sentence, or passage of text. When you create a  text.TextBlock object, it is necessary to specify various details such as its position on the screen and the font:   >>> sentence = 'The quick brown fox [jump]{stem}[ed]{suffix} over the lazy dog.' >>> txt = eyekit.TextBlock(sentence, position=(100, 500), font_face='Times New Roman', font_size=36) >>> print(txt)  TextBlock[The quick brown  .]   Eyekit has a simple scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case  jump and  ed ) and curly braces are used to provide a unique ID for each interest area (in this case  stem and  suffix ). These interest areas that have been specifically marked up in the raw text are called \"zones\". We can extract a particular zone as an  text.InterestArea object by using its ID:   >>> print(txt['stem'])  InterestArea[stem, jump]   or indeed we can iterate over all the marked-up zones using the  text.TextBlock.zones() iterator:   >>> for zone in txt.zones(): >>> print(zone)  InterestArea[stem, jump]  InterestArea[suffix, ed]   Zones are useful if you have a small number of interest areas that are convenient to mark up in the raw text. However, Eyekit also provides more powerful tools for automatically extracting interest areas. For example, you can use  text.TextBlock.words() to iterate over every word in the text as an  text.InterestArea without needing to explicitly mark each of them up in the raw text:   >>> for word in txt.words(): >>> print(word)  InterestArea[0:0:3, The]  InterestArea[0:4:9, quick]  InterestArea[0:10:15, brown]  InterestArea[0:16:19, fox]  InterestArea[0:20:26, jumped]  InterestArea[0:27:31, over]  InterestArea[0:32:35, the]  InterestArea[0:36:40, lazy]  InterestArea[0:41:44, dog]   You can also supply a regular expression to iterate over words that match a certain pattern; words that end in  ed for example:   >>> for word in txt.words('.+ed'): >>> print(word)  InterestArea[0:20:26, jumped]   or just the four-letter words:   >>> for word in txt.words('.{4}'): >>> print(word)  InterestArea[0:27:31, over]  InterestArea[0:36:40, lazy]   or case-insensitive occurrences of the word  the :   >>> for word in txt.words('(?i)the'): >>> print(word)  InterestArea[0:0:3, The]  InterestArea[0:32:35, the]   You can also collate a bunch of interest areas into a list for convenient access later on. For example, if you wanted to do some analysis on all the three-letter words, you might extract them and assign them to a variable like so:   >>> three_letter_words = list(txt.words('.{3}' >>> print(three_letter_words)  [InterestArea[0:0:3, The], InterestArea[0:16:19, fox], InterestArea[0:32:35, the], InterestArea[0:41:44, dog   You can also slice out arbitrary interest areas by using the row and column indices of a section of text. Here, for example, we are extracting a two-word section of text from line 0 (the first and only line) and characters 10 through 18:   >>> print(txt[0:10:19])  InterestArea[0:10:19, brown fox]    The InterestArea object Once you've extracted an  text.InterestArea , you can access various properties about it:   >>> brown_fox = txt[0:10:19] >>> print(brown_fox.text)  get the string represented in this IA  brown fox >>> print(brown_fox.width)  get the pixel width of this IA  157.974609375 >>> print(brown_fox.center)  get the xy coordinates of the center of the IA  (328.4365234375, 491.94921875) >>> print(brown_fox.onset)  get the x coordinate of the IA onset  253.94921875 >>> print(brown_fox.location)  get the location of the IA in its parent TextBlock  (0, 10, 19) >>> print(brown_fox.id)  get the ID of the IA  0:10:19   By default, an  text.InterestArea will have an ID of the form  0:10:19 , which refers to the unique position that it occupies in the text. However, you can also change the IDs to something more descriptive, if you wish. For example, you could enumerate the words in the text and give each one a number:   >>> for i, word in enumerate(txt.words( : >>> word.id = f'word{i}'   and, since  text.InterestArea s are passed around by reference, the IDs will update everywhere. For example, it we print the  three_letter_words list we created earlier, we find that it now reflects the new IDs:   >>> print(three_letter_words)  [InterestArea[word0, The], InterestArea[word3, fox], InterestArea[word6, the], InterestArea[word8, dog   The  text.InterestArea defines the  in operator in a special way so that you can conveniently check if a fixation falls inside its bounding box. For example:   >>> for fixation in seq: >>> if fixation in brown_fox: >>> print(fixation)  Fixation[298,490]  Fixation[361,497]     >>> for fixation in seq: >>> for zone in txt.zones(): >>> if fixation in zone: >>> print(f'{fixation} is inside {zone}')  Fixation[430,489] is inside InterestArea[stem, jump]  Fixation[450,505] is inside InterestArea[stem, jump]  Fixation[492,491] is inside InterestArea[suffix, ed]   The  text.TextBlock also provides some more convenient methods for asking these kinds of questions, for example:   >>> print(txt.which_word(seq[3]  which word is fixation 3 inside?  InterestArea[word2, brown] >>> print(txt.which_character(seq[3]  which character specifically?  InterestArea[0:12:13, o]   An  text.InterestArea can be any sequence of consecutive characters, and, as you can see, it's possible to define several overlapping  text.InterestArea s at the same time:  txt['word4'] ( jumped ),  txt['stem'] ( jump ),  txt['suffix'] ( ed ), and  txt[0:24:25] (the  p in  jumped ) can all coexist. Visualization       - Now that we've created a  fixation.FixationSequence and  text.TextBlock , it would be useful to visualize how they relate to each other. To create a visualization, we begin by creating an  vis.Image object, specifying the pixel dimensions of the screen:   >>> img = eyekit.vis.Image(1920, 1080)   Next we render our text and fixations onto this image:   >>> img.draw_text_block(txt) >>> img.draw_fixation_sequence(seq)   Note that the elements of the image will be layered in the order in which these methods are called \u2013 in this case, the fixations will be rendered on top of the text. Finally, we save the image (Eyekit supports PDF, EPS, SVG, or PNG):   >>> img.save('quick_brown.pdf')    Sometimes it's useful to see the text in the context of the entire screen, as is the case here; other times, we'd like to remove all that excess white space and focus in on the text. To do this, you need to specify a crop margin; the image will then be cropped to the size of the text block plus the specified margin:   >>> img.save('quick_brown_cropped.pdf', crop_margin=1)    There are many other options for creating custom visualizations, which you can explore in the  vis module. For example, if you wanted to depict the bounding boxes around the two zoned interest areas we defined earlier, you might do this:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> img.draw_rectangle(txt['stem'], color='crimson') >>> img.draw_rectangle(txt['suffix'], color='cadetblue') >>> img.draw_fixation_sequence(seq) >>> img.save('quick_brown_with_zones.pdf', crop_margin=1)    Colors can be specified as a tuple of RGB values (e.g.  (220, 20, 60) ), a hex triplet (e.g.  DC143C ), or any [standard HTML color name](https: www.w3schools.com/colors/colors_names.asp) (e.g.  crimson ). Similarly, we can do the same thing with the list of three-letter words we created earlier:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> for word in three_letter_words: >>> img.draw_rectangle(word, color='slateblue') >>> img.draw_fixation_sequence(seq) >>> img.save('quick_brown_with_3letter_words.pdf', crop_margin=1)    Or, indeed, all words in the text:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> for word in txt.words(): >>> img.draw_rectangle(word, color='hotpink') >>> img.draw_fixation_sequence(seq) >>> img.save('quick_brown_with_all_words.pdf', crop_margin=1)    Note that, by default, each  text.InterestArea 's bounding box is slightly padded by, at most, half of the width of a space character. This ensures that, even if a fixation falls between two words, it will still be assigned to one of them. Padding is only applied to an  text.InterestArea 's edge if that edge adjoins a non-alphabetical character (i.e. spaces and punctuation). Thus, when  jumped was divided into separate stem and suffix areas above, no padding was applied word-internally. If desired, automatic padding can be turned off by setting the  autopad argument to  False during the creation of the  text.TextBlock , or it can be controlled manually using the  text.InterestArea.adjust_padding() method. Performing Analyses          - At the moment, Eyekit has a fairly limited set of analysis functions, which you can explore in the  analysis module. These functions take as input a collection of  text.InterestArea objects and a  fixation.FixationSequence , and they return as output a dictionary in which the keys are the  text.InterestArea IDs and the values are the relevant measure. For example, if we wanted to calculate the initial fixation duration on the three-letter words we extracted earlier, we can do this:   >>> results = eyekit.analysis.initial_fixation_duration(three_letter_words, seq) >>> print(results)  {'word0': 100, 'word3': 100, 'word6': 100, 'word8': 100}   In this case, we see that the initial fixation on each of the three-letter words lasted 100ms. Or, if we wanted to know the total fixation duration on all words:   >>> results = eyekit.analysis.total_fixation_duration(txt.words(), seq) >>> print(results)  {'word0': 100, 'word1': 200, 'word2': 100, 'word3': 100, 'word4': 300, 'word5': 100, 'word6': 100, 'word7': 100, 'word8': 100}   Here we see that the total fixation duration on  word4 ( jumped ) was 300ms. Another thing we can measure is the initial landing position:   >>> results = eyekit.analysis.initial_landing_position(txt.zones(), seq) >>> print(results)  {'stem': 2, 'suffix': 1}   Here we see that the initial fixation on  stem ( jump ) landed in position 2, and the initial fixation on  suffix ( ed ) landed in position 1. Multiline Passages          So far, we've only looked at a single line  text.TextBlock , but handling multiline passages works in largely the same way. The principal difference is that when you instantiate your  text.TextBlock object, you must pass a  list of strings (one for each line of text):   >>> txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], position=(100, 500), font_face='Helvetica', font_size=24)   To see an example, we'll load in some real multiline passage data from [Pescuma et al.](https: osf.io/hx2sj/) which is included in the [Eyekit GitHub repository](https: github.com/jwcarr/eyekit):   >>> example_data = eyekit.io.read('example/example_data.json') >>> example_texts = eyekit.io.read('example/example_texts.json')   and in particular we'll extract the fixation sequence for trial 0 and its associated text:   >>> seq = example_data['trial_0']['fixations'] >>> pid = example_data['trial_0']['passage_id'] >>> txt = example_texts[pid]['text']   As before, we can plot the fixation sequence over the passage of text to see what the data looks like:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> img.draw_rectangle(txt[0:32:40], color='orange') >>> img.draw_rectangle(txt[1:34:38], color='orange') >>> img.draw_fixation_sequence(seq) >>> img.save('multiline_passage.pdf', crop_margin=4)    First, we might decide that we want to discard that final fixation, where the participant jumped a few lines up right at the end:   >>> seq[-1].discard()  discard the final fixation   A second problem we can see here is that fixations on one line sometimes appear slightly closer to another line due to imperfect eyetracker calibration. For example, the fixation on the word  voce on line two actually falls into the bounding box of the word  vivevano on line one. Obviously, this will cause issues in your analysis further downstream, so it can be useful to first clean up the data by snapping every fixation to its appropriate line. Eyekit implements several different line assignment algorithms, which can be applied using the  tools.snap_to_lines() function from the  tools module:   >>> original_seq = seq.copy()  keep a copy of the original sequence >>> eyekit.tools.snap_to_lines(seq, txt)   This process only affects the y-coordinate of each fixation (the x-coordinate is always left unchanged). To compare the corrected fixation sequence to the original, we can make two images and then combine them in a single  vis.Figure :   >>> img1 = eyekit.vis.Image(1920, 1080) >>> img1.draw_text_block(txt) >>> img1.draw_rectangle(txt[0:32:40], color='orange') >>> img1.draw_rectangle(txt[1:34:38], color='orange') >>> img1.draw_fixation_sequence(original_seq) >>> img1.set_caption('Before correction') >>> >>> img2 = eyekit.vis.Image(1920, 1080) >>> img2.draw_text_block(txt) >>> img2.draw_rectangle(txt[0:32:40], color='orange') >>> img2.draw_rectangle(txt[1:34:38], color='orange') >>> img2.draw_fixation_sequence(seq) >>> img2.set_caption('After correction') >>> >>> fig = eyekit.vis.Figure(1, 2)  one row, two columns >>> fig.add_image(img1) >>> fig.add_image(img2) >>> fig.set_crop_margin(3) >>> fig.save('multiline_passage_corrected.pdf')    The fixation on  voce is now clearly associated with that word. It is important to note, however, that drift correction should be applied with care, especially if the fixation data is very noisy or if the passage is being read nonlinearly. Just like single-line texts, we can extract interest areas from the passage and apply analysis functions in the same way. For example, if we were interested in the word  piccolo / piccola in this passage, we could extract all occurrences of this word and calculate the total fixation duration:   >>> piccol_words = list(txt.words('piccol[oa]' >>> durations = eyekit.analysis.total_fixation_duration(piccol_words, seq) >>> print(durations)  {'2:64:71': 253, '3:0:7': 347, '3:21:28': 246, '3:29:36': 319, '7:11:18': 268, '10:43:50': 178}   Furthermore, we could make a visualization to show this information:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> for word in piccol_words: >>> img.draw_rectangle(word, color='lightseagreen') >>> x = word.onset >>> y = word.y_br - 3 >>> label = f'{durations[word.id]}ms' >>> img.draw_annotation(x, y, label, color='lightseagreen', font_face='Arial bold', font_size=4) >>> img.draw_fixation_sequence(seq, color='gray') >>> img.save('multiline_passage_piccol.pdf', crop_margin=4)    Another way to look at the data is to distribute the fixations across the characters of the passage probabilistically, under the assumption that the closer a character is to a fixation point, the more likely it is that the reader is perceiving that character. This can be performed with the  analysis.duration_mass function and plotted in a heatmap like so:   >>> mass = eyekit.analysis.duration_mass(txt, seq) >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block_heatmap(txt, mass, color='green') >>> img.save('multiline_passage_mass.pdf', crop_margin=4)    Input\u2013Output       Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, a start time, and an end time for each fixation, you are free to store data in whatever format you choose. However, as we have seen briefly above, Eyekit provides built-in support for JSON, where a typical data file might look something like this:   { \"trial_0\" : { \"participant_id\": \"John\", \"passage_id\": \"passage_a\", \"fixations\": { \"__FixationSequence__\" :  412, 142, 770, 900],  ., [655, 653, 46483, 46532 } }, \"trial_1\" : { \"participant_id\": \"Mary\", \"passage_id\": \"passage_b\", \"fixations\": { \"__FixationSequence__\" :  368, 146, 7, 197],  ., [725, 681, 30331, 31260 } }, \"trial_2\" : { \"participant_id\": \"Jack\", \"passage_id\": \"passage_c\", \"fixations\": { \"__FixationSequence__\" :  374, 147, 7, 283],  ., [890, 267, 31931, 32153 } } }   This format is compact, structured, human-readable, and flexible. With the exception of the  __FixationSequence__ object, you can freely store whatever key-value pairs you want and you can organize the hierarchy of the data structure in any way that makes sense for your project. JSON files can be loaded using the  io.read() function from the  io module:   >>> data = eyekit.io.read('example/example_data.json')   which automatically instantiates any  fixation.FixationSequence objects. Similarly, an arbitrary dictionary or list can be written out using the  io.write() function:   >>> eyekit.io.write(data, 'output_data.json', compress=True)   If  compress is set to  True , files are written in the most compact way; if  False , the file will be larger but more human-readable (like the example above). JSON can also be used to store  text.TextBlock objects \u2013 see  example_texts.json for an example \u2013 and you can even store  fixation.FixationSequence and  text.TextBlock objects in the same file if you like to keep things organized together. The  io module also provides functions for importing data from other formats:  io.import_asc() and  io.import_csv() . Once data has been imported this way, it may then be written out to Eyekit's native JSON format for quick access in the future. In time, I hope to add more functions to import data from common eyetracking formats. Getting Texts into Eyekit             - Getting texts into Eyekit can be a little tricky because their precise layout will be highly dependent on many different factors \u2013 not just the font and its size, but also the peculiarities of the presentation software and its text rendering engine. Ideally, all of your texts will be presented in some consistent way. For example, they might be centralized on the screen or they might have a consistent left edge. Once you specify how a text is positioned on screen, Eyekit calculates the location and bounding box of every character based on the particular font and font size you are using. This process is somewhat imperfect, however, especially if you are using a proportional font that makes use of advanced typographical features such as kerning and ligatures, as is the case in the example below. The best way to check that the  text.TextBlock is set up correctly is to check it against a screenshot from your actual experiment. Eyekit provides the  tools.align_to_screenshot() tool to help you do this. First, set up your text block with parameters that you think are correct:   >>> txt = eyekit.TextBlock(saramago_text, position=(300, 100), font_face='Baskerville', font_size=30, line_height=60, align='left', anchor='left')   Then pass it to the  tools.align_to_screenshot() function along with the path to a PNG screenshot file:   >>> eyekit.tools.align_to_screenshot(txt, 'screenshot.png')    This will create a new image file ending  _eyekit.png (e.g.  screenshot_eyekit.png ). In this file, Eyekit's rendering of the text is presented in green overlaying the original screenshot image. The point where the two solid green lines intersect corresponds to the  text.TextBlock 's  position argument, and the dashed green lines show the baselines of subsequent lines of text, which is based on the  line_height argument. You can use this output image to adjust the parameters of the  text.TextBlock accordingly. If all of your texts are presented in a consistent way, you should only need to establish these parameters once. An alternative strategy would be to produce your experimental stimuli using Eyekit. For example, you could export images of your TextBlocks, and then display them full-size in some experimental presentation software of your choice. Contributing       Eyekit is still in an early stage of development, but I am very happy to receive bug reports and suggestions via the [GitHub Issues page](https: github.com/jwcarr/eyekit/issues). If you'd like to work on new features or fix stuff that's currently broken, please feel free to fork the repo and/or raise an issue to discuss details. Before sending a pull request, you should check that the unit tests pass using [Pytest](https: pytest.org):   $ pytest tests/   and run [Black](https: black.readthedocs.io) over the codebase to normalize the style:   $ black eyekit/   Here are some areas of Eyekit that are currently underdeveloped: - Additional analytical measures (e.g. of saccades and regressions) - Awareness of different experimental paradigms - Creation of animations/videos - More convenient methods for collating results into dataframes etc. - Importing data from other eyetracker data formats - Synchronization of fixation data with other types of experimental event - Support for nontextual objects, such as images or shapes - Interactive tools to help you clean up your data"
},
{
"ref":"eyekit.fixation",
"url":1,
"doc":"Defines the  Fixation and  FixationSequence objects, which are used to represent fixation data."
},
{
"ref":"eyekit.fixation.Fixation",
"url":1,
"doc":"Representation of a single fixation event. It is not usually necessary to create  Fixation objects manually; they are created automatically during the instantiation of a  FixationSequence ."
},
{
"ref":"eyekit.fixation.Fixation.x",
"url":1,
"doc":"X-coordinate of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.y",
"url":1,
"doc":"Y-coordinate of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.xy",
"url":1,
"doc":"XY-coordinates of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.start",
"url":1,
"doc":"Start time of the fixation in milliseconds."
},
{
"ref":"eyekit.fixation.Fixation.end",
"url":1,
"doc":"End time of the fixation in milliseconds."
},
{
"ref":"eyekit.fixation.Fixation.duration",
"url":1,
"doc":"Duration of the fixation in milliseconds."
},
{
"ref":"eyekit.fixation.Fixation.discarded",
"url":1,
"doc":" True if the fixation has been discarded,  False otherwise."
},
{
"ref":"eyekit.fixation.Fixation.discard",
"url":1,
"doc":"Mark this fixation as discarded. To completely remove the fixation, you should also call  FixationSequence.purge() .",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence",
"url":1,
"doc":"Representation of a sequence of consecutive fixations, typically from a single trial. Initialized with: -  sequence List of tuples of ints, or something similar, that conforms to the following structure:  [(106, 540, 100, 200), (190, 536, 200, 300),  ., (763, 529, 1000, 1100)] , where each tuple contains the X-coordinate, Y-coordinate, start time, and end time of a fixation."
},
{
"ref":"eyekit.fixation.FixationSequence.start",
"url":1,
"doc":"Start time of the fixation sequence (in milliseconds)."
},
{
"ref":"eyekit.fixation.FixationSequence.end",
"url":1,
"doc":"End time of the fixation sequence (in milliseconds)."
},
{
"ref":"eyekit.fixation.FixationSequence.duration",
"url":1,
"doc":"Duration of the fixation sequence, incuding any gaps between fixations (in milliseconds)."
},
{
"ref":"eyekit.fixation.FixationSequence.append",
"url":1,
"doc":"Append a fixation to the end of the sequence.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.copy",
"url":1,
"doc":"Returns a copy of the fixation sequence.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.purge",
"url":1,
"doc":"Permanently removes all discarded fixations from the fixation sequence.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.iter_with_discards",
"url":1,
"doc":"Iterates over the fixation sequence including any discarded fixations. This is also the default behavior when iterating over a  FixationSequence directly.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.iter_without_discards",
"url":1,
"doc":"Iterates over the fixation sequence without any discarded fixations.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.iter_pairs",
"url":1,
"doc":"Iterate over fixations in consecutive pairs. This is useful if you want to compare consecutive fixations in some way. For example, if you wanted to detect when a fixation leaves an interest area, you might do something like this:   for curr_fxn, next_fxn in seq.iter_pairs(): if curr_fxn in interest_area and next_fxn not in interest_area: print('A fixation has left the interest area')  ",
"func":1
},
{
"ref":"eyekit.analysis",
"url":2,
"doc":"Functions for calculating common analysis measures, such as total fixation duration or initial landing position."
},
{
"ref":"eyekit.analysis.number_of_fixations",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the total number of fixations on each interest area. Returns a dictionary in which the keys are interest area IDs and the values are counts.",
"func":1
},
{
"ref":"eyekit.analysis.initial_fixation_duration",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the duration of the initial fixation on each interest area. Returns a dictionary in which the keys are interest area IDs and the values are initial fixation durations.",
"func":1
},
{
"ref":"eyekit.analysis.total_fixation_duration",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the total fixation duration on each interest area. Returns a dictionary in which the keys are interest area IDs and the values are total fixation durations.",
"func":1
},
{
"ref":"eyekit.analysis.gaze_duration",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the gaze duration on each interest area. Gaze duration is the sum duration of all fixations inside an interest area until the area is exited for the first time. Returns a dictionary in which the keys are interest area IDs and the values are gaze durations.",
"func":1
},
{
"ref":"eyekit.analysis.initial_landing_position",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the initial landing position (expressed in character positions) on each interest area. Counting is from 1, so a 1 indicates that the fixation landed on the first character and so forth. If the interest area represents right-to-left text, the first character is the rightmost one. Returns a dictionary in which the keys are interest area IDs and the values are initial landing positions.",
"func":1
},
{
"ref":"eyekit.analysis.initial_landing_distance",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the initial landing distance on each interest area. The initial landing distance is the pixel distance between the first fixation to land in an interest area and the left edge of that interest area (or, in the case of right-to-left text, the right edge). Returns a dictionary in which the keys are interest area IDs and the values are initial landing distances.",
"func":1
},
{
"ref":"eyekit.analysis.duration_mass",
"url":2,
"doc":"Given a  eyekit.text.TextBlock and  eyekit.fixation.FixationSequence , distribute the durations of the fixations probabilistically across the  eyekit.text.TextBlock . Specifically, the duration of fixation  f is distributed over all characters  C in its line according to the probability that the reader is \"seeing\" each character (see  p_characters_fixation() ), and this is summed over all fixations:  \\sum_{f \\in F} p(C|f) \\cdot f_\\mathrm{dur} Returns a 2D Numpy array, the sum of which is equal to the total duration of all fixations. This can be passed to  eyekit.vis.Image.draw_text_block_heatmap() for visualization. Duration mass reveals the parts of the text that received the most attention. Optionally, this can be performed over higher-level ngrams by setting  n > 1.",
"func":1
},
{
"ref":"eyekit.analysis.p_characters_fixation",
"url":2,
"doc":"Given a  eyekit.text.TextBlock and  eyekit.fixation.Fixation , calculate the probability that the reader is \"seeing\" each character in the text. We assume that the closer a character is to the fixation point, the greater the probability that the participant is \"seeing\" (i.e., processing) that character. Specifically, for a given fixation  f , we compute a Gaussian distribution over all characters in the line according to:  p(c|f) \\propto \\mathrm{exp} \\frac{ -\\mathrm{ED}(f_\\mathrm{pos}, c_\\mathrm{pos})^2 }{2\\gamma^2} where  \u03b3 ( gamma ) is a free parameter controlling the rate at which probability decays with the Euclidean distance (ED) between the position of fixation  f and the position of character  c . Returns a 2D Numpy array representing a probability distribution over all characters, with all its mass confined to the line that the fixation occurred inside, and with greater mass closer to fixation points. This array can be passed to  eyekit.vis.Image.draw_text_block_heatmap() for visualization. Optionally, this calculation can be performed over higher-level ngrams by setting  n > 1.",
"func":1
},
{
"ref":"eyekit.tools",
"url":3,
"doc":"Functions for performing common procedures, such as discarding out of bounds fixations and snapping fixations to the lines of text."
},
{
"ref":"eyekit.tools.discard_short_fixations",
"url":3,
"doc":"Given a  eyekit.fixation.FixationSequence , discard all fixations that are shorter than some threshold value. Operates directly on the sequence and does not return a copy.",
"func":1
},
{
"ref":"eyekit.tools.discard_out_of_bounds_fixations",
"url":3,
"doc":"Given a  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock , discard all fixations that do not fall within some threshold distance of any character in the text. Operates directly on the sequence and does not return a copy.",
"func":1
},
{
"ref":"eyekit.tools.snap_to_lines",
"url":3,
"doc":"Given a  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock , snap each fixation to the line that it most likely belongs to, eliminating any y-axis variation or drift. Operates directly on the sequence and does not return a copy. Several methods are available, some of which take optional parameters or require SciPy to be installed. For a full description and evaluation of these methods, see [Carr et al. (2020)](https: osf.io/jg3nc/). In right-to-left TextBlocks, reading is assumed to be progressing from right to left. In single-line TextBlocks, the  method parameter has no effect: all fixations will be snapped to the one line. -  chain : Chain consecutive fixations that are sufficiently close to each other, and then assign chains to their closest text lines. Default params:  x_thresh=192 ,  y_thresh=32 . -  cluster : Classify fixations into  m clusters based on their Y-values, and then assign clusters to text lines in positional order. Requires SciPy. -  merge : Form a set of progressive sequences and then reduce the set to  m by repeatedly merging those that appear to be on the same line. Merged sequences are then assigned to text lines in positional order. Default params:  y_thresh=32 ,  gradient_thresh=0.1 ,  error_thresh=20 . -  regress : Find  m regression lines that best fit the fixations and group fixations according to best fit regression lines, and then assign groups to text lines in positional order. Default params:  slope_bounds=(-0.1, 0.1) ,  offset_bounds=(-50, 50) ,  std_bounds=(1, 20) . Requires SciPy. -  segment : Segment fixation sequence into  m subsequences based on  m \u20131 most-likely return sweeps, and then assign subsequences to text lines in chronological order. -  split : Split fixation sequence into subsequences based on best candidate return sweeps, and then assign subsequences to closest text lines. Requires SciPy. -  stretch : Find a stretch factor and offset that results in a good alignment between the fixations and lines of text, and then assign the transformed fixations to the closest text lines. Default params:  stretch_bounds=(0.9, 1.1) ,  offset_bounds=(-50, 50) . Requires SciPy. -  warp : Map fixations to word centers using [Dynamic Time Warping](https: en.wikipedia.org/wiki/Dynamic_time_warping). This finds a monotonically increasing mapping between fixations and words with the shortest overall distance, effectively resulting in  m subsequences. Fixations are then assigned to the lines that their mapped words belong to, effectively assigning subsequences to text lines in chronological order.",
"func":1
},
{
"ref":"eyekit.tools.align_to_screenshot",
"url":3,
"doc":"Given a  eyekit.text.TextBlock and the path to a PNG screenshot file, produce an image showing the original screenshot overlaid with the text block (shown in green). If no output path is provided, the output image is written to the same directory as the screenshot file. This is useful for establishing  eyekit.text.TextBlock parameters (position, font size, etc.) that match what participants actually saw in your experiment.",
"func":1
},
{
"ref":"eyekit.tools.font_size_at_72dpi",
"url":3,
"doc":"Convert a font size at some dpi to the equivalent font size at 72dpi. Typically, this can be used to convert a Windows-style 96dpi font size to the equivalent size at 72dpi.",
"func":1
},
{
"ref":"eyekit.io",
"url":4,
"doc":"Functions for reading and writing data."
},
{
"ref":"eyekit.io.read",
"url":4,
"doc":"Read in a JSON file.  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock objects are automatically decoded and instantiated.",
"func":1
},
{
"ref":"eyekit.io.write",
"url":4,
"doc":"Write arbitrary data to a JSON file. If  compress is  True , the file is written in the most compact way; if  False , the file will be more human readable.  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock objects are automatically encoded.",
"func":1
},
{
"ref":"eyekit.io.import_asc",
"url":4,
"doc":"Import data from an ASC file produced from an SR Research EyeLink device (you will first need to use SR Research's Edf2asc tool to convert your original EDF files to ASC). The importer will extract all trials from the ASC file, where a trial is defined as a sequence of fixations (EFIX lines) that occur inside a START\u2013END block. Optionally, the importer can extract user-defined variables from the ASC file and associate them with the appropriate trial. For example, if your ASC file contains messages like this:   MSG 4244101 !V TRIAL_VAR trial_type practice MSG 4244101 !V TRIAL_VAR passage_id 1   then you could extract the variables  \"trial_type\" and  \"passage_id\" . A variable is some string that is followed by a space; anything that follows this space is the variable's value. By default, the importer looks for variables that follow the END tag. However, if your variables are placed before the START tag, then set the  placement_of_variables argument to  \"before_start\" . If unsure, you should first inspect your ASC file to see what messages you wrote to the data stream and where they are placed. The importer will return a list of dictionaries, where each dictionary represents a single trial and contains the fixations along with any other extracted variables. For example:   [ { \"trial_type\" : \"practice\", \"passage_id\" : \"1\", \"fixations\" : FixationSequence[ .] }, { \"trial_type\" : \"test\", \"passage_id\" : \"2\", \"fixations\" : FixationSequence[ .] } ]  ",
"func":1
},
{
"ref":"eyekit.io.import_csv",
"url":4,
"doc":"Import data from a CSV file (requires Pandas to be installed). By default, the importer expects the CSV file to contain the column headers,  x ,  y ,  start , and  end , but this can be customized by setting the relevant arguments to whatever column headers your CSV file contains. Each row of the CSV file is expected to represent a single fixation. If your CSV file contains data from multiple trials, you should also specify the column header of a trial identifier, so that the data can be segmented into trials. The importer will return a list of dictionaries, where each dictionary represents a single trial and contains the fixations along with the trial identifier (if specified). For example:   [ { \"trial_id\" : 1, \"fixations\" : FixationSequence[ .] }, { \"trial_id\" : 2, \"fixations\" : FixationSequence[ .] } ]  ",
"func":1
},
{
"ref":"eyekit.vis",
"url":5,
"doc":"Defines the  Image ,  Figure , and  Booklet objects, which are used to create visualizations."
},
{
"ref":"eyekit.vis.set_default_font",
"url":5,
"doc":"Set the default font face and/or size that will be used in figure captions and image annotations. This selection can be overridden on a per-image or per-figure basis. If no font is set, Eyekit defaults to 8pt Arial.",
"func":1
},
{
"ref":"eyekit.vis.Image",
"url":5,
"doc":"The Image class is used to create visualizations of text blocks and fixation sequences, and it provides methods for drawing various kinds of annotation. The general usage pattern is:   img = eyekit.vis.Image(1920, 1080) img.draw_text_block(txt) img.draw_fixation_sequence(seq) img.save('image.pdf')   Initialized with: -  screen_width Width of the screen in pixels. -  screen_height Height of the screen in pixels."
},
{
"ref":"eyekit.vis.Image.set_caption",
"url":5,
"doc":"Set the image's caption, which will be shown above the image if you place it inside a  Figure .",
"func":1
},
{
"ref":"eyekit.vis.Image.set_background_color",
"url":5,
"doc":"Set the background color of the image. By default the background color is white. If  color is set to  None , the background will be transparent.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_text_block",
"url":5,
"doc":"Draw a  eyekit.text.TextBlock on the image.  color sets the color of the text.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_text_block_heatmap",
"url":5,
"doc":"Draw a  eyekit.text.TextBlock on the image along with an associated distribution, which is represented in heatmap form. This is can be used to visualize the output from  eyekit.analysis.duration_mass() .  color determines the color of the heatmap.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_fixation_sequence",
"url":5,
"doc":"Draw a  eyekit.fixation.FixationSequence on the image. Optionally, you can choose whether or not to display saccade lines and discarded fixations, and which colors to use.  number_fixations is not yet implemented.  fixation_radius can be used to set a constant radius for all fixations (rather than a radius that is proportional to duration).",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_sequence_comparison",
"url":5,
"doc":"Draw a  eyekit.fixation.FixationSequence on the image with the fixations colored according to whether or not they match a reference sequence in terms of the y-coordinate. This is mostly useful for comparing the outputs of two different drift correction algorithms.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_line",
"url":5,
"doc":"Draw an arbitrary line on the image from  start_xy to  end_xy .  stroke_width is set in points for vector output or pixels for PNG output.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_circle",
"url":5,
"doc":"Draw an arbitrary circle on the image centered at  x ,  y and with some  radius .  stroke_width is set in points for vector output or pixels for PNG output.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_rectangle",
"url":5,
"doc":"Draw a rectangle on the image. You can pass in some box-like object, such as an  text.InterestArea , or you can specify an x, y, width, and height to draw an arbitrary rectangle.  stroke_width is set in points for vector output or pixels for PNG output.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_annotation",
"url":5,
"doc":"Draw arbitrary text on the image located at  x ,  y .  font_size is set in points for vector output or pixels for PNG output.",
"func":1
},
{
"ref":"eyekit.vis.Image.save",
"url":5,
"doc":"Save the image to some  output_path . Images can be saved as .pdf, .eps, .svg, or .png.  width only applies to the vector formats and determines the millimeter width of the output file; PNG images are saved at actual pixel size. If you set a crop margin, the image will be cropped to the size of the  eyekit.text.TextBlock plus the specified margin. Margins are specified in millimeters (PDF, EPS, SVG) or pixels (PNG).",
"func":1
},
{
"ref":"eyekit.vis.Figure",
"url":5,
"doc":"The Figure class is used to combine one or more images into a publication-ready figure. The general usage pattern is:   fig = eyekit.vis.Figure(1, 2) fig.add_image(img1) fig.add_image(img2) fig.save('figure.pdf')   Initialized with: -  n_rows Number of rows in the figure. -  n_cols Number of columns in the figure."
},
{
"ref":"eyekit.vis.Figure.set_crop_margin",
"url":5,
"doc":"Set the crop margin of the embedded images. Each image in the figure will be cropped to the size and positioning of the most extreme text block extents, plus the specified margin. This has the effect of zooming in to all images in a consistent way \u2013 maintaining the aspect ratio and relative positioning of the text blocks across images. Margins are specified in figure millimeters.",
"func":1
},
{
"ref":"eyekit.vis.Figure.set_lettering",
"url":5,
"doc":"By default, each image caption is prefixed with a letter,  (A) ,  (B) ,  (C) , etc. If you want to turn this off, call  Figure.set_lettering(False) prior to saving.",
"func":1
},
{
"ref":"eyekit.vis.Figure.set_padding",
"url":5,
"doc":"Set the vertical or horizontal padding between images or the padding around the edge of the figure. Padding is expressed in millimeters. By default, the vertical and horizontal padding between images is 4mm and the edge padding is 1mm.",
"func":1
},
{
"ref":"eyekit.vis.Figure.add_image",
"url":5,
"doc":"Add an  Image to the figure. If a row and column index is specified, the image is placed in that position. Otherwise,  image is placed in the next available position.",
"func":1
},
{
"ref":"eyekit.vis.Figure.save",
"url":5,
"doc":"Save the figure to some  output_path . Figures can be saved as .pdf, .eps, or .svg.  width determines the millimeter width of the output file.",
"func":1
},
{
"ref":"eyekit.vis.Booklet",
"url":5,
"doc":"The Booklet class is used to combine one or more figures into a multipage PDF booklet. The general usage pattern is:   booklet = eyekit.vis.Booklet() booklet.add_figure(fig1) booklet.add_figure(fig2) booklet.save('booklet.pdf')  "
},
{
"ref":"eyekit.vis.Booklet.add_figure",
"url":5,
"doc":"Add a  Figure to a new page in the booklet.",
"func":1
},
{
"ref":"eyekit.vis.Booklet.save",
"url":5,
"doc":"Save the booklet to some  output_path . Booklets can only be saved as .pdf.  width and  height determine the millimeter sizing of the booklet pages, which defaults to A4 (210x297mm).",
"func":1
},
{
"ref":"eyekit.text",
"url":6,
"doc":"Defines the  TextBlock and  InterestArea objects for handling texts."
},
{
"ref":"eyekit.text.Box",
"url":6,
"doc":"Representation of a bounding box, which provides an underlying framework for  Character ,  InterestArea , and  TextBlock ."
},
{
"ref":"eyekit.text.Box.x",
"url":6,
"doc":"X-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.Box.y",
"url":6,
"doc":"Y-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.Box.x_tl",
"url":6,
"doc":"X-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.Box.y_tl",
"url":6,
"doc":"Y-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.Box.x_br",
"url":6,
"doc":"X-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.Box.y_br",
"url":6,
"doc":"Y-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.Box.width",
"url":6,
"doc":"Width of the bounding box"
},
{
"ref":"eyekit.text.Box.height",
"url":6,
"doc":"Height of the bounding box"
},
{
"ref":"eyekit.text.Box.box",
"url":6,
"doc":"The bounding box represented as x_tl, y_tl, width, and height"
},
{
"ref":"eyekit.text.Box.center",
"url":6,
"doc":"XY-coordinates of the center of the bounding box"
},
{
"ref":"eyekit.text.Character",
"url":6,
"doc":"Representation of a single character of text. A  Character object is essentially a one-letter string that occupies a position in space and has a bounding box. It is not usually necessary to create  Character objects manually; they are created automatically during the instantiation of a  TextBlock ."
},
{
"ref":"eyekit.text.Character.baseline",
"url":6,
"doc":"The y position of the character baseline"
},
{
"ref":"eyekit.text.Character.midline",
"url":6,
"doc":"The y position of the character midline"
},
{
"ref":"eyekit.text.Character.x",
"url":6,
"doc":"X-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.Character.y",
"url":6,
"doc":"Y-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.Character.x_tl",
"url":6,
"doc":"X-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.Character.y_tl",
"url":6,
"doc":"Y-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.Character.x_br",
"url":6,
"doc":"X-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.Character.y_br",
"url":6,
"doc":"Y-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.Character.width",
"url":6,
"doc":"Width of the bounding box"
},
{
"ref":"eyekit.text.Character.height",
"url":6,
"doc":"Height of the bounding box"
},
{
"ref":"eyekit.text.Character.box",
"url":6,
"doc":"The bounding box represented as x_tl, y_tl, width, and height"
},
{
"ref":"eyekit.text.Character.center",
"url":6,
"doc":"XY-coordinates of the center of the bounding box"
},
{
"ref":"eyekit.text.InterestArea",
"url":6,
"doc":"Representation of an interest area \u2013 a portion of a  TextBlock object that is of potential interest. It is not usually necessary to create  InterestArea objects manually; they are created automatically when you slice a  TextBlock object or when you iterate over lines, words, characters, ngrams, or zones parsed from the raw text."
},
{
"ref":"eyekit.text.InterestArea.x_tl",
"url":6,
"doc":"X-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.x_br",
"url":6,
"doc":"X-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.location",
"url":6,
"doc":"Location of the interest area in its parent TextBlock (row, start, end)"
},
{
"ref":"eyekit.text.InterestArea.id",
"url":6,
"doc":"Interest area ID. By default, these ID's have the form 1:5:10, which represents the line number and column indices of the  InterestArea in its parent  TextBlock . However, IDs can also be changed to any arbitrary string."
},
{
"ref":"eyekit.text.InterestArea.right_to_left",
"url":6,
"doc":" True if interest area represents right-to-left text"
},
{
"ref":"eyekit.text.InterestArea.text",
"url":6,
"doc":"String representation of the interest area"
},
{
"ref":"eyekit.text.InterestArea.display_text",
"url":6,
"doc":"Same as  text except right-to-left text is output in display form"
},
{
"ref":"eyekit.text.InterestArea.baseline",
"url":6,
"doc":"The y position of the text baseline"
},
{
"ref":"eyekit.text.InterestArea.midline",
"url":6,
"doc":"The y position of the text midline"
},
{
"ref":"eyekit.text.InterestArea.onset",
"url":6,
"doc":"The x position of the onset of the interest area. The onset is the left edge of the interest area text without any bounding box padding (or the right edge in the case of right-to-left text)."
},
{
"ref":"eyekit.text.InterestArea.padding",
"url":6,
"doc":"Bounding box padding on the left and right edge"
},
{
"ref":"eyekit.text.InterestArea.set_padding",
"url":6,
"doc":"Set the amount of bounding box padding on the left and/or right edge.",
"func":1
},
{
"ref":"eyekit.text.InterestArea.adjust_padding",
"url":6,
"doc":"Adjust the current amount of bounding box padding on the left and/or right edge. Positive values increase the padding, and negative values decrease the padding.",
"func":1
},
{
"ref":"eyekit.text.InterestArea.x",
"url":6,
"doc":"X-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.y",
"url":6,
"doc":"Y-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.y_tl",
"url":6,
"doc":"Y-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.y_br",
"url":6,
"doc":"Y-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.width",
"url":6,
"doc":"Width of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.height",
"url":6,
"doc":"Height of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.box",
"url":6,
"doc":"The bounding box represented as x_tl, y_tl, width, and height"
},
{
"ref":"eyekit.text.InterestArea.center",
"url":6,
"doc":"XY-coordinates of the center of the bounding box"
},
{
"ref":"eyekit.text.TextBlock",
"url":6,
"doc":"Representation of a piece of text, which may be a word, sentence, or entire multiline passage. Initialized with: -  text The line of text (string) or lines of text (list of strings). Optionally, these can be marked up with arbitrary interest areas (zones); for example,  The quick brown fox jump[ed]{past-suffix} over the lazy dog . -  position XY-coordinates describing the position of the TextBlock on the screen. The x-coordinate should be either the left edge, right edge, or center point of the TextBlock, depending on how the  anchor argument has been set (see below). The y-coordinate should always correspond to the baseline of the first (or only) line of text. -  font_face Name of a font available on your system. The keywords  italic and/or  bold can also be included to select the desired style, e.g.,  Minion Pro bold italic . -  font_size Font size in pixels. At 72dpi, this is equivalent to the font size in points. To convert a font size from some other dpi, use  eyekit.tools.font_size_at_72dpi() . -  line_height Distance between lines of text in pixels. In general, for single line spacing, the line height is equal to the font size; for double line spacing, the line height is equal to 2 \u00d7 the font size, etc. By default, the line height is assumed to be the same as the font size (single line spacing). This parameter also effectively determines the height of the bounding boxes around interest areas. -  align Alignment of the text within the TextBlock. Must be set to  left ,  center , or  right , and defaults to  left (unless  right_to_left is set to  True , in which case  align defaults to  right ). -  anchor Anchor point of the TextBlock. This determines the interpretation of the  position argument (see above). Must be set to  left ,  center , or  right , and defaults to the same as the  align argument. For example, if  position was set to the center of the screen, the  align and  anchor arguments would have the following effects:  -  right_to_left Set to  True if the text is in a right-to-left script (Arabic, Hebrew, Urdu, etc.). If you are working with the Arabic script, you should reshape the text prior to passing it into Eyekit by using, for example, the Arabic-reshaper package. -  alphabet A string of characters that are to be considered alphabetical, which determines what counts as a word. By default, this includes any character defined as a letter or number in unicode, plus the underscore character. However, if you need to modify Eyekit's default behavior, you can set a specific alphabet here. For example, if you wanted to treat apostrophes and hyphens as alphabetical, you might use  alphabet=\"A-Za-z'-\" . This would allow a sentence like \"Where's the orang-utan?\" to be treated as three words rather than five. -  autopad If  True (the default), a small amount of padding (half of the width of a space character) is added to each side of an interest area. Fixations that are very close to, but technically outside of, an interest area will therefore still be considered to be inside that interest area. If the character to the left or right of the interest area is alphabetical (i.e. if the interest area is word-internal), padding will not be added on that side.  "
},
{
"ref":"eyekit.text.TextBlock.defaults",
"url":6,
"doc":"Set default  TextBlock parameters. If you plan to create several  TextBlock s with the same parameters, it may be useful to set the default parameters at the top of your script or at the start of your session:   import eyekit eyekit.TextBlock.defaults(font_face='Helvetica') txt = eyekit.TextBlock('The quick brown fox') print(txt.font_face)  'Helvetica'  ",
"func":1
},
{
"ref":"eyekit.text.TextBlock.text",
"url":6,
"doc":"Original input text"
},
{
"ref":"eyekit.text.TextBlock.position",
"url":6,
"doc":"Position of the  TextBlock "
},
{
"ref":"eyekit.text.TextBlock.font_face",
"url":6,
"doc":"Name of the font"
},
{
"ref":"eyekit.text.TextBlock.font_size",
"url":6,
"doc":"Font size in points"
},
{
"ref":"eyekit.text.TextBlock.line_height",
"url":6,
"doc":"Line height in points"
},
{
"ref":"eyekit.text.TextBlock.align",
"url":6,
"doc":"Alignment of the text (either  left ,  center , or  right )"
},
{
"ref":"eyekit.text.TextBlock.anchor",
"url":6,
"doc":"Anchor point of the text (either  left ,  center , or  right )"
},
{
"ref":"eyekit.text.TextBlock.right_to_left",
"url":6,
"doc":"Right-to-left text"
},
{
"ref":"eyekit.text.TextBlock.alphabet",
"url":6,
"doc":"Characters that are considered alphabetical"
},
{
"ref":"eyekit.text.TextBlock.autopad",
"url":6,
"doc":"Whether or not automatic padding is switched on"
},
{
"ref":"eyekit.text.TextBlock.n_rows",
"url":6,
"doc":"Number of rows in the text (i.e. the number of lines)"
},
{
"ref":"eyekit.text.TextBlock.n_cols",
"url":6,
"doc":"Number of columns in the text (i.e. the number of characters in the widest line)"
},
{
"ref":"eyekit.text.TextBlock.n_lines",
"url":6,
"doc":"Number of lines in the text (i.e. alias of  n_rows )"
},
{
"ref":"eyekit.text.TextBlock.baselines",
"url":6,
"doc":"Y-coordinate of the baseline of each line of text"
},
{
"ref":"eyekit.text.TextBlock.midlines",
"url":6,
"doc":"Y-coordinate of the midline of each line of text"
},
{
"ref":"eyekit.text.TextBlock.zones",
"url":6,
"doc":"Iterate over each marked up zone as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_zone",
"url":6,
"doc":"Return the marked-up zone that the fixation falls inside as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.lines",
"url":6,
"doc":"Iterate over each line as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_line",
"url":6,
"doc":"Return the line that the fixation falls inside as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.words",
"url":6,
"doc":"Iterate over each word as an  InterestArea . Optionally, you can supply a regex pattern to pick out specific words. For example,  '(?i)the' gives you case-insensitive occurrences of the word  the or  '[a-z]+ing' gives you lower-case words ending with  -ing .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_word",
"url":6,
"doc":"Return the word that the fixation falls inside as an  InterestArea . For the meaning of  pattern see  TextBlock.words() .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.characters",
"url":6,
"doc":"Iterate over each character as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_character",
"url":6,
"doc":"Return the character that the fixation falls inside as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.ngrams",
"url":6,
"doc":"Iterate over each ngram, for given n, as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.word_centers",
"url":6,
"doc":"Return the XY-coordinates of the center of each word.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.x",
"url":6,
"doc":"X-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.y",
"url":6,
"doc":"Y-coordinate of the center of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.x_tl",
"url":6,
"doc":"X-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.y_tl",
"url":6,
"doc":"Y-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.x_br",
"url":6,
"doc":"X-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.y_br",
"url":6,
"doc":"Y-coordinate of the bottom-right corner of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.width",
"url":6,
"doc":"Width of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.height",
"url":6,
"doc":"Height of the bounding box"
},
{
"ref":"eyekit.text.TextBlock.box",
"url":6,
"doc":"The bounding box represented as x_tl, y_tl, width, and height"
},
{
"ref":"eyekit.text.TextBlock.center",
"url":6,
"doc":"XY-coordinates of the center of the bounding box"
}
]