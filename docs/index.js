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
"doc":"Eyekit is a Python package for analyzing reading behavior using eyetracking data. Eyekit is entirely independent of any particular eyetracker hardware, presentation software, or data formats, and has a minimal set of dependencies. It has an object-oriented style that defines two core objects \u2013 the TextBlock and the FixationSequence \u2013 that you bring into contact with a bit of coding. Eyekit is currently in the pre-alpha stage and is licensed under the terms of the MIT License. Is Eyekit the Right Tool for Me?                 - You basically just want to analyze which parts of a text someone is looking at by defining areas of interest. - You are interested in a fixation-level analysis, as opposed to, for example, saccades or millisecond-by-millisecond eye movements. - You don't mind doing a little bit of legwork to transform your raw fixation data and texts into something Eyekit can understand. - You need support for arbitrary fonts that may be monospaced or proportional. - You want the flexibility to define custom measures and to build your own reproducible processing pipeline. - You would like tools for dealing with noise and calibration issues, and for discarding fixations according to your own criteria. - You want to share your data in an open format and produce publication-ready vector graphics. Installation       The latest version of Eyekit can be installed using  pip :   $ pip install eyekit   Eyekit is compatible with Python 3.6+ and has two dependencies: - [NumPy](https: numpy.org) - [Cairocffi](https: github.com/Kozea/cairocffi) Cairocffi is a Python wrapper around the graphics library [Cairo](https: cairographics.org), which you will also need to install if you don't already have it. Many Linux distributions have Cairo built in. On a Mac, it can be installed using [Homebrew](https: brew.sh):  brew install cairo . On Windows, your best bet might be [Anaconda](https: anaconda.org/anaconda/cairo). Getting Started        - Once installed, import Eyekit in the normal way:   >>> import eyekit   Eyekit makes use of two core objects: the  text.TextBlock and the  fixation.FixationSequence . Much of Eyekit's functionality involves bringing these two objects into contact. Typically, you define particular areas of the  text.TextBlock that are of interest (phrases, words, morphemes, letters .) and check to see which fixations from the  fixation.FixationSequence fall in those areas and for how long.  The TextBlock object A  text.TextBlock can represent a word, sentence, or passage of text. When you create a  text.TextBlock object, it is necessary to specify the pixel position of the top-left corner, the font, and the font size. Let's begin by creating a  text.TextBlock representing a single sentence:   >>> sentence = 'The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.' >>> txt = eyekit.TextBlock(sentence, position=(100, 500), font_face='Times New Roman', font_size=36) >>> print(txt)  TextBlock[The quick brown  .]   Eyekit has a simple scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case  jump and  ed ) and curly braces are used to provide a unique ID for each interest area (in this case  stem_1 and  suffix_1 ). These interest areas that have been specifically marked up in the raw text are called \"zones\". We can iterate over the zones using the  text.TextBlock.zones() iterator:   >>> for zone in txt.zones(): >>> print(zone.id, zone.text, zone.box)  stem_1 jump (411.923828125, 473.94921875, 74.00390625, 36.0)  suffix_1 ed (485.927734375, 473.94921875, 33.978515625, 36.0)   In this case, we are printing each zone's ID, the string of text it represents, and its bounding box (x, y, width, and height). In addition to manually marked-up zones, you can also create interest areas automatically based on the lines, words, characters, or ngrams of the text. If, for example, you were interested in all words, you could use  text.TextBlock.words() to iterate over every word as an interest area without needing to explicitly mark each of them up in the raw text:   >>> for word in txt.words(): >>> print(word.text, word.box)  The (95.5, 473.94921875, 64.96875, 36.0)  quick (160.46875, 473.94921875, 88.98046875, 36.0)  brown (249.44921875, 473.94921875, 100.986328125, 36.0)  fox (350.435546875, 473.94921875, 56.98828125, 36.0)  jumped (407.423828125, 473.94921875, 116.982421875, 36.0)  over (524.40625, 473.94921875, 72.966796875, 36.0)  the (597.373046875, 473.94921875, 52.98046875, 36.0)  lazy (650.353515625, 473.94921875, 68.958984375, 36.0)  dog (719.3125, 473.94921875, 63.0, 36.0)   You can also slice out arbitrary interest areas by using the row and column indices of a section of text. Here, for example, we are taking a slice from row 0 (the first and only line) and characters 10 through 18:   >>> arbitrary_IA = txt[0:10:19] >>> print(arbitrary_IA.text, arbitrary_IA.box)  brown fox (253.94921875, 473.94921875, 148.974609375, 36.0)   This could be useful if you wanted to slice up the text in some programmatic way, creating interest areas from each three-letter chunk, for example.  The FixationSequence object Fixation data is represented in a  fixation.FixationSequence object. Let's create some pretend data to play around with:   >>> seq = eyekit.FixationSequence( 106, 490, 100], [190, 486, 100], [230, 505, 100], [298, 490, 100], [361, 497, 100], [430, 489, 100], [450, 505, 100], [492, 491, 100], [562, 505, 100], [637, 493, 100], [712, 497, 100], [763, 487, 100 )   Each fixation is represented by three numbers: its x-coordinate, its y-coordinate, and its duration (in this example, they're all 100ms). Once created, a  fixation.FixationSequence can be traversed, indexed, and sliced as you'd expect. For example,   >>> print(seq[5:10])  FixationSequence[Fixation[430,489],  ., Fixation[637,493   slices out fixations 5 through 9 into a new  fixation.FixationSequence object. This could be useful, for example, if you wanted to remove superfluous fixations from the start and end of the sequence. A basic question we might have at this point is: Do any of these fixations fall inside the zones I marked up? We can write some simple code to answer this:   >>> for fixation in seq: >>> for zone in txt.zones(): >>> if fixation in zone: >>> print(f'There was a fixation inside {zone.id}, which is \"{zone.text}\".')  There was a fixation inside stem_1, which is \"jump\".  There was a fixation inside stem_1, which is \"jump\".  There was a fixation inside suffix_1, which is \"ed\".   Visualization       - Now that we've defined a  text.TextBlock and  fixation.FixationSequence , it would be useful to visualize how they relate to each other. We begin by creating an  vis.Image object, specifying the pixel dimensions of the screen:   >>> img = eyekit.vis.Image(1920, 1080)   Next we render our text and fixations:   >>> img.draw_text_block(txt) >>> img.draw_fixation_sequence(seq)   Note that the elements of the image will be layered in the order in which these methods are called \u2013 in this case, the fixations will be rendered on top of the text. Finally, we save the image (Eyekit supports PDF, EPS, SVG, or PNG):   >>> img.save('quick_brown.pdf')    Sometimes it's useful to see the text in the context of the entire screen, as is the case here; other times, we'd like to remove all that excess white space and focus in on the text. To do this, you need to specify a crop margin; the image will then be cropped to the size of the text block plus the specified margin:   >>> img.save('quick_brown_cropped.pdf', crop_margin=1)    There are many other options for creating custom visualizations, which you can explore in the  image module. For example, if you wanted to depict the bounding boxes around the two zoned interest areas we defined earlier, with different colors for stems and suffixes, you might do this:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> for zone in txt.zones(): >>> if zone.id.startswith('stem'): >>> img.draw_rectangle(zone.box, color='crimson') >>> elif zone.id.startswith('suffix'): >>> img.draw_rectangle(zone.box, color='cadetblue') >>> img.draw_fixation_sequence(seq) >>> img.save('quick_brown_with_zones.pdf', crop_margin=1)    Colors can be specified as a tuple of RGB values (e.g.  (220, 20, 60) ), a hex triplet (e.g.  DC143C ), or any [standard HTML color name](https: www.w3schools.com/colors/colors_names.asp) (e.g.  crimson ). Performing Analyses          - At the moment, Eyekit has a fairly limited set of analysis functions; in general, you are expected to write code to calculate whatever you are interested in measuring. The functions that are currently available can be explored in the  analysis module, but two common eyetracking measures that  are implemented are  analysis.initial_fixation_duration() and  analysis.total_fixation_duration() , which may be used like this:   >>> tot_durations = eyekit.analysis.total_fixation_duration(txt.zones(), seq) >>> print(tot_durations)  {'stem_1': 200, 'suffix_1': 100} >>> init_durations = eyekit.analysis.initial_fixation_duration(txt.zones(), seq) >>> print(init_durations)  {'stem_1': 100, 'suffix_1': 100}   In this case, we see that the total time spent inside the  stem_1 interest area was 200ms, while the duration of the initial fixation on that interest area was 100ms. Similarly, these analysis functions can be applied to other kinds of interest areas, such as words:   >>> tot_durations_on_words = eyekit.analysis.total_fixation_duration(txt.words(), seq) >>> print(tot_durations_on_words)  {'0:0:3': 100, '0:4:9': 200, '0:10:15': 100, '0:16:19': 100, '0:20:26': 300, '0:27:31': 100, '0:32:35': 100, '0:36:40': 100, '0:41:44': 100}   Here we see that a total of 300ms was spent on the word with ID  0:20:26 , which is \"jumped\". Each word ID refers to the unique position that word occupies in the text \u2013 in this case, row 0, characters 20 through 25). If you want to perform further operations on a particular interest area, you can slice it out from the text, assign it to a variable, and change its ID to something more useful:   >>> jumped_IA = txt[0:20:26] >>> jumped_IA.id = 'verb_jumped' >>> landing_pos = eyekit.analysis.initial_landing_position(jumped_IA, seq) >>> print(landing_pos)  {'verb_jumped': 2}   The initial fixation on \"jumped\" landed on character 2. Multiline Passages          So far, we've only looked at a single line  text.TextBlock , but handling multiline passages works in largely the same way. The principal difference is that when you instantiate your  text.TextBlock object, you must pass a  list of strings (one for each line of text):   >>> txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], position=(100, 500), font_face='Helvetica', font_size=24)   To see an example, we'll load in some real multiline passage data from [Pescuma et al.](https: osf.io/hx2sj/) which is included in the [Eyekit GitHub repository](https: github.com/jwcarr/eyekit):   >>> example_data = eyekit.io.read('example/example_data.json') >>> example_texts = eyekit.io.read('example/example_texts.json')   and in particular we'll extract the fixation sequence for trial 0 and its associated text:   >>> seq = example_data['trial_0']['fixations'] >>> pid = example_data['trial_0']['passage_id'] >>> txt = example_texts[pid]['text']   As before, we can plot the fixation sequence over the passage of text to see what the data looks like:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> img.draw_rectangle(txt[0:32:40].box, color='orange') >>> img.draw_rectangle(txt[4:12:17].box, color='orange') >>> img.draw_fixation_sequence(seq) >>> img.save('multiline_passage.pdf', crop_margin=4)    A common issue with multiline passage reading is that fixations on one line may appear closer to another line due to imperfect eyetracker calibration or general noise. For example, the fixation on \"voce\" on line two actually falls into the bounding box of the word \"vivevano\" on line one. Likewise, the fixation on \"passeggiata\" in the middle of the text is closer to \"Mamma\" on the line above. Obviously, this noise will cause issues in your analysis further downstream, so it may be useful to first clean up the data by snapping every fixation to its appropriate line. Eyekit implements several drift correction algorithms, which can be applied using the  tools.snap_to_lines() function from the  tools module:   >>> original_seq = seq.copy()  Keep a copy of the original sequence >>> eyekit.tools.snap_to_lines(seq, txt)   This process only affects the y-coordinate of each fixation; the x-coordinate is always left unchanged. Various correction methods are available \u2013 see the  tools.snap_to_lines() documentation and [Carr et al. (2020)](https: osf.io/jg3nc/) for a more complete description and evaluation. To compare the corrected fixation sequence to the original, we'll make two images and then combine them in a single  vis.Figure :   >>> img1 = eyekit.vis.Image(1920, 1080) >>> img1.draw_text_block(txt) >>> img1.draw_fixation_sequence(original_seq) >>> img1.set_caption('Before correction') >>> >>> img2 = eyekit.vis.Image(1920, 1080) >>> img2.draw_text_block(txt) >>> img2.draw_fixation_sequence(seq) >>> img2.set_caption('After correction') >>> >>> fig = eyekit.vis.Figure(1, 2)  one row, two columns >>> fig.add_image(img1) >>> fig.add_image(img2) >>> fig.set_crop_margin(3) >>> fig.save('multiline_passage_corrected.pdf')    The fixations on \"voce\" and \"passeggiata\", for example, are now clearly associated with the correct words, allowing us to proceed with our analysis. It is important to note, however, that drift correction should be applied with care, especially if the fixation data is very noisy or if the passage is being read nonlinearly. Just as with single-line texts, we can iterate over lines, words, characters, and ngrams using the appropriate methods and apply the same kinds of analysis functions. For example, if we were interested in the word \"piccolo\"/\"piccola\" in this passage, we could do this:   >>> img = eyekit.vis.Image(1920, 1080) >>> img.draw_text_block(txt) >>> img.draw_fixation_sequence(seq, color='gray') >>> for word in txt.words('piccol[oa]'): >>> tot_dur = eyekit.analysis.total_fixation_duration(word, seq) >>> img.draw_rectangle(word.box, color='lightseagreen') >>> img.draw_annotation(word.x_tl+2, word.y_br-3, f'{tot_dur[word.id]}ms', color='lightseagreen', font_face='Arial bold', font_size=4) >>> img.save('multiline_passage_piccol.pdf', crop_margin=4)    Input\u2013Output       Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, and a duration for each fixation, you are free to store data in whatever format you choose. However, as we have seen briefly above, Eyekit provides built-in support for JSON, where a typical data file might look something like this:   { \"trial_0\" : { \"participant_id\": \"John\", \"passage_id\": \"passage_a\", \"fixations\": { \"__FixationSequence__\" :  412, 142, 131],  ., [588, 866, 224 } }, \"trial_1\" : { \"participant_id\": \"Mary\", \"passage_id\": \"passage_b\", \"fixations\": { \"__FixationSequence__\" :  368, 146, 191],  ., [725, 681, 930 } }, \"trial_2\" : { \"participant_id\": \"Jack\", \"passage_id\": \"passage_c\", \"fixations\": { \"__FixationSequence__\" :  374, 147, 277],  ., [1288, 804, 141 } } }   This format is open, human-readable, and flexible. With the exception of the  __FixationSequence__ object, you can freely store whatever key-value pairs you want and you can organize the hierarchy of the data structure in any way that makes sense for your project. JSON files can be loaded using the  io.read() function from the  io module:   >>> data = eyekit.io.read('example/example_data.json') >>> print(data)  {'trial_0': {'participant_id': 'John', 'passage_id': 'passage_a', 'fixations': FixationSequence[Fixation[412,142],  ., Fixation[588,866 }, 'trial_1': {'participant_id': 'Mary', 'passage_id': 'passage_b', 'fixations': FixationSequence[Fixation[368,146],  ., Fixation[725,681 }, 'trial_2': {'participant_id': 'Jack', 'passage_id': 'passage_c', 'fixations': FixationSequence[Fixation[374,147],  ., Fixation[1288,804    which automatically instantiates any  fixation.FixationSequence objects. Similarly, an arbitrary dictionary of data can be written out using the  io.write() function:   >>> eyekit.io.write(data, 'output_data.json', compress=True)   If  compress is set to  True (the default), files are written in the most compact way; if  False , the file will be larger but more human-readable (like the example above). JSON can also be used to store  text.TextBlock objects \u2013 see  example_texts.json for an example \u2013 and you can even store  fixation.FixationSequence and  text.TextBlock objects in the same file if you like to keep things organized together. Getting Data into Eyekit             Currently, the options for converting your raw data into something Eyekit can understand are quite limited. In time, I hope to add more functions that convert from common formats.  Fixation data If you have your fixation data in CSV files, you could load the data into a  fixation.FixationSequence by doing something along these lines (assuming you have columns  x ,  y , and  duration ):   >>> import pandas >>> data = pandas.read_csv('mydata.csv') >>> fixations = [fxn for fxn in zip(data['x'], data['y'], data['duration'])] >>> seq = eyekit.FixationSequence(fixations)   Eyekit has rudimentary support for importing data from ASC files. When importing data this way, you must specify the name of a trial variable and its possible values so that the importer can determine when a new trial begins:   >>> data = eyekit.io.import_asc('mydata.asc', 'trial_type', ['Experimental'], extract_vars=['passage_id', 'response'])   In this case, when parsing the ASC file, the importer would consider   MSG 4244100 !V TRIAL_VAR trial_type Experimental   to mark the beginning of a new trial and will extract all  EFIX lines that occur within the subsequent  START \u2013 END block. Optionally, you can specify other variables that you want to extract (in this case  passage_id and  response ), resulting in imported data that looks like this:   { \"trial_0\" : { \"trial_type\" : \"Experimental\", \"passage_id\" : \"passage_a\", \"response\" : \"yes\", \"fixations\" : FixationSequence 368, 161, 208],  ., [562, 924, 115 } }   In addition, rather than load one ASC file at a time, you can also point to a directory of ASC files, all of which will then be loaded into a single dataset:   >>> data = eyekit.io.import_asc('asc_data_files/', 'trial_type', ['Experimental'], extract_variables=['passage_id', 'response'])   which could then be written out to Eyekit's native format for quick access in the future:   >>> eyekit.io.write(data, 'converted_asc_data.json')    Text data Getting texts into Eyekit can be a little tricky because their precise layout will be highly dependent on many different factors \u2013 not just the font and its size, but also the peculiarities of the presentation software and its text rendering engine. Ideally, all of your texts will be presented so that the top-left corner of the block of text is located in a consistent position on the screen (depending on how you set up your experiment, this may already be the case). Eyekit uses this position to estimate the location of every character in the text based on the particular font and font size you are using. This process is somewhat imperfect, however, especially if you are using a proportional font that makes use of advanced typographical features such as kerning and ligatures, as is the case below. The best way to check that the  text.TextBlock is set up correctly is to pass it to  tools.align_to_screenshot() from the  eyekit.tools module, along with the path to a screenshot of the text as displayed to the participant:   >>> txt = eyekit.TextBlock(saramago_text, position=(300, 100), font_face='Baskerville', font_size=30, line_height=60) >>> eyekit.tools.align_to_screenshot(txt, 'screenshot.png')    This will create a new file  'screenshot_eyekit.png' . In this file, Eyekit's rendering of the text is presented in green overlaying the original screenshot image. The point where the two solid green lines intersect is the  text.TextBlock 's  position argument, and the dashed green lines show the baselines of each subsequent line, which is based on the  line_height argument. You can use this output to adjust the parameters of the  text.TextBlock accordingly. Alternatively, instead of overlaying the text, you can overlay the word bounding boxes that Eyekit has identified to check how reliable they are:   >>> eyekit.tools.align_to_screenshot(txt, 'screenshot.png', show_text=False, show_bounding_boxes=True)    As you can see, although the identified bounding boxes are imperfect in some cases, they are certainly good enough for a word-level analysis. Contributing       Eyekit is still in an early stage of development, but I am very happy to receive bug reports and suggestions via the [GitHub Issues page](https: github.com/jwcarr/eyekit/issues). If you'd like to work on new features or fix stuff that's currently broken, please feel free to fork the repo and/or raise an issue to discuss details. Before sending a pull request, you should check that the unit tests pass using [Pytest](https: pytest.org):   $ pytest tests/   and run [Black](https: black.readthedocs.io) over the codebase to normalize the style:   $ black eyekit/  "
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
"ref":"eyekit.fixation.Fixation.tuple",
"url":1,
"doc":"Tuple representation of the fixation."
},
{
"ref":"eyekit.fixation.FixationSequence",
"url":1,
"doc":"Representation of a sequence of consecutive fixations, typically from a single trial. Initialized with: -  sequence List of tuples of ints, or something similar, that conforms to the following structure:  [(106, 540, 100), (190, 536, 100),  ., (763, 529, 100)] , where each tuple contains the X-coordinate, Y-coordinate, and duration of a fixation"
},
{
"ref":"eyekit.fixation.FixationSequence.append",
"url":1,
"doc":"",
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
"ref":"eyekit.fixation.FixationSequence.XYarray",
"url":1,
"doc":"Returns a Numpy array containing the XY-coordinates of the fixations.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.Xarray",
"url":1,
"doc":"Returns a Numpy array containing the X-coordinates of the fixations.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.Yarray",
"url":1,
"doc":"Returns a Numpy array containing the Y-coordinates of the fixations.",
"func":1
},
{
"ref":"eyekit.analysis",
"url":2,
"doc":"Functions for calculating common analysis measures, such as total fixation duration or initial landing position."
},
{
"ref":"eyekit.analysis.initial_fixation_duration",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the duration of the initial fixation on each interest area.",
"func":1
},
{
"ref":"eyekit.analysis.total_fixation_duration",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the total fixation duration on each interest area.",
"func":1
},
{
"ref":"eyekit.analysis.gaze_duration",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the gaze duration on each interest area. Gaze duration is the sum duration of all fixations inside an interest area until the area is exited for the first time.",
"func":1
},
{
"ref":"eyekit.analysis.initial_landing_position",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the initial landing position (expressed in character positions) on each interest area. Counting is from 1, so a 1 indicates the initial fixation landed on the first character and so forth.",
"func":1
},
{
"ref":"eyekit.analysis.initial_landing_x",
"url":2,
"doc":"Given an interest area or collection of interest areas, return the initial landing position (expressed in pixel distance from the start of the interest area) on each interest area.",
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
"doc":"Given a  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock , snap each fixation to the line that it most likely belongs to, eliminating any y-axis variation or drift. Operates directly on the sequence and does not return a copy. Several methods are available, some of which take optional parameters or require SciPy to be installed. For a full description and evaluation of these methods, see [Carr et al. (2020)](https: osf.io/jg3nc/). -  chain : Chain consecutive fixations that are sufficiently close to each other, and then assign chains to their closest text lines. Default params:  x_thresh=192 ,  y_thresh=32 . -  cluster : Classify fixations into  m clusters based on their Y-values, and then assign clusters to text lines in positional order. Requires SciPy. -  merge : Form a set of progressive sequences and then reduce the set to  m by repeatedly merging those that appear to be on the same line. Merged sequences are then assigned to text lines in positional order. Default params:  y_thresh=32 ,  gradient_thresh=0.1 ,  error_thresh=20 . -  regress : Find  m regression lines that best fit the fixations and group fixations according to best fit regression lines, and then assign groups to text lines in positional order. Default params:  slope_bounds=(-0.1, 0.1) ,  offset_bounds=(-50, 50) ,  std_bounds=(1, 20) . Requires SciPy. -  segment : Segment fixation sequence into  m subsequences based on  m \u20131 most-likely return sweeps, and then assign subsequences to text lines in chronological order. -  split : Split fixation sequence into subsequences based on best candidate return sweeps, and then assign subsequences to closest text lines. Requires SciPy. -  stretch : Find a stretch factor and offset that results in a good alignment between the fixations and lines of text, and then assign the transformed fixations to the closest text lines. Default params:  stretch_bounds=(0.9, 1.1) ,  offset_bounds=(-50, 50) . Requires SciPy. -  warp : Map fixations to word centers using [Dynamic Time Warping](https: en.wikipedia.org/wiki/Dynamic_time_warping). This finds a monotonically increasing mapping between fixations and words with the shortest overall distance, effectively resulting in  m subsequences. Fixations are then assigned to the lines that their mapped words belong to, effectively assigning subsequences to text lines in chronological order.",
"func":1
},
{
"ref":"eyekit.tools.align_to_screenshot",
"url":3,
"doc":"Create an image depicting a PNG screenshot overlaid with a  eyekit.text.TextBlock in green. If no output path is provided, the output is written to the same directory as the screenshot file. This is useful for establishing the correct  eyekit.text.TextBlock parameters to match what participants are actually seeing.",
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
"doc":"Write arbitrary data to a JSON file. If  compress is  True , the file is written in the most compact way; if  False , the file will be larger but more human-readable.  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock objects are automatically serialized.",
"func":1
},
{
"ref":"eyekit.io.import_asc",
"url":4,
"doc":"Import a single ASC file or a directory of ASC files. The importer looks for a  trial_begin_var that is set to one of the  trial_begin_vals , and then extracts all  EFIX lines that occur within the subsequent  START \u2013 END block. Optionally, you can specify other variables that you want to extract, resulting in imported data that looks like this:   { \"trial_0\" : { \"trial_type\" : \"Experimental\", \"passage_id\" : \"passage_a\", \"response\" : \"yes\", \"fixations\" : FixationSequence 368, 161, 208],  ., [562, 924, 115 } }  ",
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
"doc":"Draw a  eyekit.fixation.FixationSequence on the image. Optionally, you can choose whether or not to display saccade lines and discarded fixations, and which colors to use.  number_fixations is not yet implemented.",
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
"doc":"Draw an arbitrary rectangle on the image.  rect should be a tuple specifying x, y, width, and height, or these four values can be passed in separately as the first four arguments.  stroke_width is set in points for vector output or pixels for PNG output.",
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
"ref":"eyekit.text.InterestArea.id",
"url":6,
"doc":"Interest area ID. By default, these ID's have the form 1:5:10, which represents the line number and column indices of the  InterestArea in its parent  TextBlock . However, IDs can also be changed to any arbitrary string."
},
{
"ref":"eyekit.text.InterestArea.baseline",
"url":6,
"doc":"The y position of the text baseline"
},
{
"ref":"eyekit.text.InterestArea.text",
"url":6,
"doc":"String representation of the interest area"
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
"ref":"eyekit.text.InterestArea.x_tl",
"url":6,
"doc":"X-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.y_tl",
"url":6,
"doc":"Y-coordinate of the top-left corner of the bounding box"
},
{
"ref":"eyekit.text.InterestArea.x_br",
"url":6,
"doc":"X-coordinate of the bottom-right corner of the bounding box"
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
"doc":"Representation of a piece of text, which may be a word, sentence, or entire multiline passage. Initialized with: -  text The line of text (string) or lines of text (list of strings). Optionally, these can be marked up with arbitrary interest areas (zones); for example,  The quick brown fox jump[ed]{past-suffix} over the lazy dog . -  position XY-coordinates of the left edge of the first baseline of the block of text. -  font_face Name of a font available on your system. The keywords  italic and/or  bold can also be included to select the desired style, e.g.,  Minion Pro bold italic . -  font_size Font size in points (at 72dpi). To convert a font size from some other dpi, use  eyekit.tools.font_size_at_72dpi() . -  line_height Height of a line of text in points. Generally speaking, for single line spacing, the line height is equal to the font size, for double line spacing, the line height is equal to 2 \u00d7 the font size, etc. By default, the line height is assumed to be the same as the font size (single line spacing). This parameter also effectively determines the height of the bounding boxes around interest areas. -  alphabet A string of characters that are to be considered alphabetical, which determines, for example, what is considered a word. By default, Eyekit considers the standard Latin, Greek, and Cyrillic alphabets to be alphabetical, plus the special and accented characters from most European languages. However, if you need support for some other alphabet, or if you want to modify Eyekit's default behavior, you can set an alternative alphabet here. This parameter is case sensitive, so you must supply upper- and lower-case variants. For example, if you wanted to treat apostrophes and hyphens as alphabetical, you might use  alphabet=\"A-Za-z'-\" . This would allow, for example, \"Where's the orang-utan?\" to be treated as three words rather than five."
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
"doc":"String representation of the text"
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
"ref":"eyekit.text.TextBlock.alphabet",
"url":6,
"doc":"Characters that are considered alphabetical"
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
"ref":"eyekit.text.TextBlock.line_positions",
"url":6,
"doc":"Y-coordinates of the center of each line of text"
},
{
"ref":"eyekit.text.TextBlock.word_centers",
"url":6,
"doc":"XY-coordinates of the center of each word"
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
"doc":"Iterate over each word as an  InterestArea . Optionally, you can supply a regex pattern to define what constitutes a word or to pick out specific words. For example,  r'\\b[Tt]he\\b' gives you all occurrences of the word  the or  '[a-z]+ing' gives you all words ending with  -ing .  add_padding adds half of the width of a space character to the left and right edges of the word's bounding box, so that fixations that fall on a space between two words will at least fall into one of the two words' bounding boxes.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_word",
"url":6,
"doc":"Return the word that the fixation falls inside as an  InterestArea . For the meaning of  pattern and  add_padding see  TextBlock.words() .",
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