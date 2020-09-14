URLS=[
"index.html",
"fixation.html",
"analysis.html",
"tools.html",
"io.html",
"text.html",
"image.html"
];
INDEX=[
{
"ref":"eyekit",
"url":0,
"doc":"Eyekit is a Python package for handling, analyzing, and visualizing eyetracking data from reading experiments. Eyekit is currently in the pre-alpha stage and is licensed under the terms of the MIT License. Philosophy      Eyekit is a lightweight tool for doing open, transparent, reproducible science on reading behavior. Eyekit is entirely independent of any particular eyetracker hardware, presentation software, or data formats, and has a minimal set of Python dependencies. It has an object-oriented style that defines two core objects \u2013 the TextBlock and the FixationSequence \u2013 that you bring into contact with a bit of coding. Is Eyekit the Right Tool for Me?                 - You basically just want to analyze which parts of a text someone is looking at by defining areas of interest. - You are interested in a fixation-level analysis, as opposed to, for example, saccades or millisecond-by-millisecond eye movements. - You don't mind doing a little bit of legwork to transform your raw fixation data and texts into something Eyekit can understand. - You need support for arbitrary fonts that may be monospaced or proportional. - You want the flexibility to define custom measures and to build your own reproducible processing pipeline. - You would like tools for dealing with noise and calibration issues, such as vertical drift, and for discarding fixations according to your own criteria. - You want to produce publication-ready visualizations and to share your data in a standard and open format. Installation       The latest version of Eyekit can be installed using  pip :   $ pip install eyekit   Eyekit is compatible with Python 3.6 and up and has four dependencies: - [NumPy](https: numpy.org) - [matplotlib](https: matplotlib.org) - [fontTools](https: pypi.org/project/fonttools/) - [CairoSVG](https: cairosvg.org) [SciPy](https: www.scipy.org) and [scikit-learn](https: scikit-learn.org) are required by certain tools but can be installed later if needed. Getting Started        - Once installed, import Eyekit in the normal way:   >>> import eyekit   Eyekit makes use of two core objects: the  text.TextBlock object and the  fixation.FixationSequence object. Much of Eyekit's functionality involves bringing these two objects into contact. Typically, you define particular areas of the  text.TextBlock that are of interest (phrases, words, morphemes, letters .) and check to see which fixations from the  fixation.FixationSequence fall in those areas and for how long.  The  text.TextBlock object A  text.TextBlock can represent a word, sentence, or passage of text. When you create a  text.TextBlock object, it is necessary to specify the pixel position of the top-left corner, the font, and the font size. Optionally, you can also specify the line spacing (1 for single line spacing, 2 for double line spacing, etc.). Let's begin by creating a  text.TextBlock representing a single sentence:   >>> sentence = 'The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.' >>> txt = eyekit.TextBlock(sentence, position=(100, 500), font_name='Times New Roman', font_size=36) >>> print(txt)  TextBlock[The quick brown  .]   Eyekit has a simple scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case  jump and  ed ) and curly braces are used to provide a unique label for each interest area (in this case  stem_1 and  suffix_1 ). We can iterate over these interest areas using the  text.TextBlock.interest_areas() iterator method:   >>> for interest_area in txt.interest_areas(): >>> print(interest_area.label, interest_area.text, interest_area.box)  stem_1 jump (411.923828125, 500.0, 74.00390625, 36.0)  suffix_1 ed (485.927734375, 500.0, 33.978515625, 36.0)   In this case, we are printing each interest area's label, its textual representation, and its bounding box (x, y, width, and height). Various other methods are available for treating all lines, words, characters, or ngrams as interest areas. If, for example, you were interested in every word, you could use the  text.TextBlock.words() iterator without needing to explicitly mark up every word as an interest area:   >>> for word in txt.words(): >>> print(word.label, word.text, word.box)  word_0 The (95.5, 500.0, 64.96875, 36.0)  word_1 quick (160.46875, 500.0, 88.98046875, 36.0)  word_2 brown (249.44921875, 500.0, 100.986328125, 36.0)  word_3 fox (350.435546875, 500.0, 56.98828125, 36.0)  word_4 jumped (407.423828125, 500.0, 116.982421875, 36.0)  word_5 over (524.40625, 500.0, 72.966796875, 36.0)  word_6 the (597.373046875, 500.0, 52.98046875, 36.0)  word_7 lazy (650.353515625, 500.0, 68.958984375, 36.0)  word_8 dog (719.3125, 500.0, 63.0, 36.0)   You can also slice out arbitrary interest areas by using the row and column indices of a section of text. Here, for example, we are taking a slice from row 0 (the first and only line) and columns 10 through 18:   >>> arbitrary_interest_area = txt[0, 10:19] >>> print(arbitrary_interest_area.text, arbitrary_interest_area.box)  brown fox (253.94921875, 500.0, 148.974609375, 36.0)   This could be useful if you wanted to slice up the text in some programmatic way, creating interest areas from each three-letter chunk, for example.  The  fixation.FixationSequence object Fixation data is represented in a  fixation.FixationSequence object. Let's create some pretend data to play around with:   >>> seq = eyekit.FixationSequence( 106, 520, 100], [190, 516, 100], [230, 535, 100], [298, 520, 100], [361, 527, 100], [430, 519, 100], [450, 535, 100], [492, 521, 100], [562, 535, 100], [637, 523, 100], [712, 517, 100], [763, 517, 100 )   Each fixation is represented by three numbers: its x-coordinate, its y-coordinate, and its duration (in this example, they're all 100ms). Once created, a  fixation.FixationSequence can be traversed, indexed, and sliced as you'd expect. For example,   >>> print(seq[5:10])  FixationSequence[Fixation[430,519],  ., Fixation[637,523   slices out fixations 5 through 9 into a new  fixation.FixationSequence object. This could be useful, for example, if you wanted to remove superfluous fixations from the start and end of the sequence. A basic question we might have at this point is: Do any of these fixations fall inside my interest areas? We can write some simple code to answer this, using one of the  which_ methods:   >>> for fixation in seq: >>> ia = txt.which_interest_area(fixation) >>> if ia is not None: >>> print(f'There was a fixation inside interest area {ia.label}, which is \"{ia.text}\".')  There was a fixation inside interest area stem_1, which is \"jump\".  There was a fixation inside interest area stem_1, which is \"jump\".  There was a fixation inside interest area suffix_1, which is \"ed\".   Analysis     At the moment, Eyekit has a fairly limited set of analysis functions; in general, you are expected to write code to calculate whatever you are interested in measuring. The functions that are currently available can be explored in the  analysis module, but two common eyetracking measures that  are implemented are  analysis.initial_fixation_duration() and  analysis.total_fixation_duration() , which may be used like this:   >>> tot_durations = eyekit.analysis.total_fixation_duration(txt.interest_areas(), seq) >>> print(tot_durations)  {'stem_1': 200, 'suffix_1': 100} >>> init_durations = eyekit.analysis.initial_fixation_duration(txt.interest_areas(), seq) >>> print(init_durations)  {'stem_1': 100, 'suffix_1': 100}   In this case, we see that the total time spent inside the  stem_1 interest area was 200ms, while the duration of the initial fixation on that interest area was 100ms. Similarly, these analysis functions can be applied to other kinds of interest areas, such as words:   >>> tot_durations_on_words = eyekit.analysis.total_fixation_duration(txt.words(), seq) >>> print(tot_durations_on_words)  {'word_0': 100, 'word_1': 200, 'word_2': 100, 'word_3': 100, 'word_4': 300, 'word_5': 100, 'word_6': 100, 'word_7': 100, 'word_8': 100}   Here we see that a total of 300ms was spent on  word_4 , \"jumped\". Visualization       - Eyekit has some basic tools to help you create visualizations of your data. We begin by creating an  image.Image object, specifying the pixel dimensions of the screen:   >>> img = eyekit.Image(1920, 1080)   Next we render our text and fixations:   >>> img.render_text(txt) >>> img.render_fixations(seq)   Note that the elements of the image will be layered in the order in which these methods are called \u2013 in this case, the fixations will be rendered on top of the text. Finally, we save the image. Eyekit natively creates images in the SVG format, but the images can be converted to PDF, EPS, or PNG on the fly by using the appropriate file extension:   >>> img.save('quick_brown.pdf')    Sometimes it's useful to see the text in the context of the entire screen, as is the case here; other times, we'd like to remove all that excess white space and focus on the text. To do this, you can call the  crop_to_text() method prior to saving, optionally specifying some amount of margin:   >>> img.crop_to_text(margin=5) >>> img.save('quick_brown_cropped.pdf')    There are many other options for creating custom visualizations, which you can explore in the  image module. For example, if you wanted to depict the bounding boxes around the two interest areas, with different colors for stems and suffixes, you might do this:   >>> img = eyekit.Image(1920, 1080) >>> img.render_text(txt, font='Courier New', fontsize=28) >>> for interest_area in txt.interest_areas(): >>> if interest_area.label.startswith('stem'): >>> img.draw_rectangle(interest_area.bounding_box, color='red') >>> elif interest_area.label.startswith('suffix'): >>> img.draw_rectangle(interest_area.bounding_box, color='blue') >>> img.render_fixations(seq) >>> img.crop_to_text(margin=5) >>> img.save('quick_brown_with_IAs.pdf')    Multiline Passages          So far, we've only looked at a single line  text.TextBlock , but handling multiline passages works in largely the same way. The principal difference is that when you instantiate your  text.TextBlock object, you must pass a  list of strings (one for each line of text):   >>> txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], position=(100, 500), font_name='Arial', font_size=24)   To see an example, we'll load in some multiline passage data that is included in this repository:   >>> example_data = eyekit.io.read('example/example_data.json') >>> example_texts = eyekit.io.read('example/example_texts.json')   and in particular we'll extract the fixation sequence for trial 0 and its associated text:   >>> seq = example_data['trial_0']['fixations'] >>> pid = example_data['trial_0']['passage_id'] >>> txt = example_texts[pid]['text']   As before, we can plot the fixation sequence over the passage of text to see what the data looks like:   >>> img = eyekit.Image(1920, 1080) >>> img.render_text(txt) >>> for interest_area in txt.interest_areas(): >>> img.draw_rectangle(interest_area.box, color='orange') >>> img.render_fixations(seq) >>> img.crop_to_text(margin=50) >>> img.save('multiline_passage.pdf')    A common issue with multiline passage reading is that fixations on one line may appear closer to another line due to imperfect eyetracker calibration or general noise. For example, the fixation on \"voce\" on line two actually falls into the bounding box of the word \"vivevano\" on line one. Likewise, the fixation on \"passeggiata\" in the middle of the text is closer to \"Mamma\" on the line above. Obviously, such \"vertical drift\" will cause issues in your analysis further downstream, so it may be useful to first clean up the data by snapping every fixation to its appropriate line. Eyekit implements several vertical drift correction algorithms, which can be applied using the  tools.snap_to_lines() function from the  tools module:   >>> clean_seq = eyekit.tools.snap_to_lines(seq, txt, method='warp')   This process only affects the y-coordinate of each fixation; the x-coordinate is always left unchanged. The default method is  warp , but you can also use  chain ,  cluster ,  merge ,  regress ,  segment , and  split . For a full description and evaluation of these methods, see [Carr et al. (2020)](https: osf.io/jg3nc/). Let's have a look at the fixation sequence after applying this cleaning step:   >>> img = eyekit.Image(1920, 1080) >>> img.render_text(txt) >>> img.render_fixations(clean_seq) >>> img.crop_to_text(50) >>> img.save('multiline_passage_corrected.pdf')    The fixations on \"voce\" and \"passeggiata\", for example, are now clearly associated with the correct words, allowing us to proceed with our analysis. It is important to note, however, that drift correction should be applied with care, especially if the fixation data is very noisy or if the passage is being read nonlinearly. Input\u2013Output       Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, and a duration for each fixation, you are free to store data in whatever format you choose. However, as we have seen briefly above, Eyekit provides built-in support for JSON, where a typical data file might look somthing like this:   { \"trial_0\" : { \"participant_id\": \"John\", \"passage_id\": \"passage_a\", \"fixations\": { \"__FixationSequence__\" :  412, 142, 131],  ., [588, 866, 224 } }, \"trial_1\" : { \"participant_id\": \"Mary\", \"passage_id\": \"passage_b\", \"fixations\": { \"__FixationSequence__\" :  368, 146, 191],  ., [725, 681, 930 } }, \"trial_2\" : { \"participant_id\": \"Jack\", \"passage_id\": \"passage_c\", \"fixations\": { \"__FixationSequence__\" :  374, 147, 277],  ., [1288, 804, 141 } } }   This format is open, human-readable, and flexible. With the exception of the  __FixationSequence__ object, you can freely store whatever key-value pairs you want and you can organize the hierarchy of the data structure in any way that makes sense for your project. JSON files can be loaded using the  io.read() function from the  io module:   >>> data = eyekit.io.read('example/example_data.json') >>> print(data)  {'trial_0': {'participant_id': 'John', 'passage_id': 'passage_a', 'fixations': FixationSequence[Fixation[412,142],  ., Fixation[588,866 }, 'trial_1': {'participant_id': 'Mary', 'passage_id': 'passage_b', 'fixations': FixationSequence[Fixation[368,146],  ., Fixation[725,681 }, 'trial_2': {'participant_id': 'Jack', 'passage_id': 'passage_c', 'fixations': FixationSequence[Fixation[374,147],  ., Fixation[1288,804    which automatically instantiates any  fixation.FixationSequence objects. Similarly, an arbitrary dictionary of data can be written out using the  io.write() function:   >>> eyekit.io.write(data, 'output_data.json', compress=True)   If  compress is set to  True (the default), files are written in the most compact way; if  False , the file will be larger but more human-readable (like the example above). JSON can also be used to store  text.TextBlock objects \u2013 see  example_texts.json for an example \u2013 and you can even store  fixation.FixationSequence and  text.TextBlock objects in the same file if you like to keep things together. Getting Your Data into Eyekit               - Currently, the options for converting your raw data into something Eyekit can understand are quite limited. In time, I hope to add more functions that convert from common formats.  Fixation data If you have your fixation data in CSV files, you could load the data into a  fixation.FixationSequence by doing something along these lines (assuming you have columns  x ,  y , and  duration ):   >>> import pandas >>> data = pandas.read_csv('mydata.csv') >>> fixations = [fxn for fxn in zip(data['x'], data['y'], data['duration'])] >>> seq = eyekit.FixationSequence(fixations)   Eyekit has rudimentary support for importing data from ASC files. When importing data this way, you must specify the name of a trial variable and its possible values so that the importer can determine when a new trial begins:   >>> data = eyekit.io.import_asc('mydata.asc', 'trial_type', ['Experimental'], extract_vars=['passage_id', 'response'])   In this case, when parsing the ASC file, the importer would consider   MSG 4244100 !V TRIAL_VAR trial_type Experimental   to mark the beginning of a new trial and will extract all  EFIX lines that occur within the subsequent  START \u2013 END block. Optionally, you can specify other variables that you want to extract (in this case  passage_id and  response ), resulting in imported data that looks like this:   { \"trial_0\" : { \"trial_type\" : \"Experimental\", \"passage_id\" : \"passage_a\", \"response\" : \"yes\", \"fixations\" : FixationSequence 368, 161, 208],  ., [562, 924, 115 } }   In addition, rather than load one ASC file at a time, you can also point to a directory of ASC files, all of which will then be loaded into a single dataset:   >>> data = eyekit.io.import_asc('asc_data_files/', 'trial_type', ['Experimental'], extract_variables=['passage_id', 'response'])   which could then be written out to Eyekit's native format for quick access in the future:   >>> eyekit.io.write(data, 'converted_asc_data.json')    Text data Getting texts into Eyekit can be a little tricky because their precise layout will be highly dependent on many different factors \u2013 not just the font and fontsize, but also the presentation software and its text rendering engine, the size and resolution of the display, the positioning of the text, and perhaps even the operating system itself. Ideally, all of your texts will be presented so that the top-left corner of the block of text is located in a consistent position on the screen (depending on how you set up your experiment, this may already be the case). Eyekit uses this position to figure out the precise location of characters and interest areas based on the particular font and font size you are using. However, this process is somewhat imperfect and you might need to experiment a little to get up and running. The best way to do this is to create a  text.TextBlock with values that seem to make sense and then output a PNG image, which will have the exact pixel dimensions of the screen; you can then check that this image matches up with a screenshot of what your participants are actually seeing."
},
{
"ref":"eyekit.fixation",
"url":1,
"doc":"Defines classes for dealing with fixations, most notably the  FixationSequence object."
},
{
"ref":"eyekit.fixation.Fixation",
"url":1,
"doc":"Representation of a single fixation event. It is not usually necessary to create  Fixation objects manually; they are created automatically during the instantiation of a  FixationSequence ."
},
{
"ref":"eyekit.fixation.Fixation.x",
"url":1,
"doc":" int X-coordinate of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.y",
"url":1,
"doc":" int Y-coordinate of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.xy",
"url":1,
"doc":" tuple XY-coordinates of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.duration",
"url":1,
"doc":" int Duration of the fixation in milliseconds."
},
{
"ref":"eyekit.fixation.Fixation.discarded",
"url":1,
"doc":" bool  True if the fixation has been discarded,  False otherwise."
},
{
"ref":"eyekit.fixation.Fixation.tuple",
"url":1,
"doc":"Tuple representation of the fixation."
},
{
"ref":"eyekit.fixation.FixationSequence",
"url":1,
"doc":"Representation of a sequence of consecutive fixations, typically from a single trial. Initialized with: -  sequence :  list of  tuple of  int or something similar that conforms to the following structure:  [(106, 540, 100), (190, 536, 100),  ., (763, 529, 100)] , where each tuple contains the X-coordinate, Y-coordinate, and duration of a fixation"
},
{
"ref":"eyekit.fixation.FixationSequence.append",
"url":1,
"doc":"",
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
"ref":"eyekit.fixation.FixationSequence.copy",
"url":1,
"doc":"Returns a copy of the fixation sequence. Does not include any discarded fixations by default, so this can be useful if you want to permanently remove all discarded fixations.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.tolist",
"url":1,
"doc":"Returns representation of the fixation sequence in simple list format for serialization.",
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
"doc":"Iterate over a sequence of fixations and, for each fixation, distribute its duration across the line of text it is located inside and return the sum of these distributions. More specifically, we assume that the closer a character is to the fixation point, the greater the probability that the participant is \"looking at\" (i.e., processing) that character. Specifically, for a given fixation  f , we compute a Gaussian distribution over all characters in the line according to:  p(c|f) \\propto \\mathrm{exp} \\frac{ -\\mathrm{ED}(f_\\mathrm{pos}, c_\\mathrm{pos})^2 }{2\\gamma^2} where  \u03b3 is a free parameter controlling the rate at which probability decays with the Euclidean distance (ED) between the position of fixation  f and the position of character  c . The duration of fixation  f is then distributed across the entire line probabilistically and summed over all fixations in the fixation sequence  F , yielding what we refer to as \"duration mass\".  \\sum_{f \\in F} P(c|f) \\cdot f_\\mathrm{dur} ",
"func":1
},
{
"ref":"eyekit.tools",
"url":3,
"doc":"Functions for performing common procedures, such as discarding out of bounds fixations and snapping fixations to the lines of text."
},
{
"ref":"eyekit.tools.snap_to_lines",
"url":3,
"doc":"Given a  FixationSequence and  TextBlock , snap each fixation to the line that it most likely belongs to, eliminating any y-axis variation or drift. Returns a copy of the fixation sequence. Several methods are available, some of which take optional parameters. For a full description and evaluation of these methods, see [Carr et al. (2020)](https: osf.io/jg3nc/). -  chain : Chain consecutive fixations that are sufficiently close to each other, and then assign chains to their closest text lines. Default params:  x_thresh=192 ,  y_thresh=32 -  cluster : Classify fixations into  m clusters based on their Y-values, and then assign clusters to text lines in positional order. -  merge : Form a set of progressive sequences and then reduce the set to  m by repeatedly merging those that appear to be on the same line. Merged sequences are then assigned to text lines in positional order. Default params:  y_thresh=32 ,  g_thresh=0.1 ,  e_thresh=20 -  regress : Find  m regression lines that best fit the fixations and group fixations according to best fit regression lines, and then assign groups to text lines in positional order. Default params:  k_bounds=(-0.1, 0.1) ,  o_bounds=(-50, 50) ,  s_bounds=(1, 20) -  segment : Segment fixation sequence into  m subsequences based on  m \u20131 most-likely return sweeps, and then assign subsequences to text lines in chronological order. -  split : Split fixation sequence into subsequences based on best candidate return sweeps, and then assign subsequences to closest text lines. -  warp : Map fixations to word centers by finding a monotonically increasing mapping with minimal cost, effectively resulting in  m subsequences, and then assign fixations to the lines that their mapped words belong to, effectively assigning subsequences to text lines in chronological order.",
"func":1
},
{
"ref":"eyekit.tools.discard_out_of_bounds_fixations",
"url":3,
"doc":"Given a fixation sequence and text, discard all fixations that do not fall within some threshold of any character in the text.",
"func":1
},
{
"ref":"eyekit.tools.fixation_sequence_distance",
"url":3,
"doc":"Returns Dynamic Time Warping distance between two fixation sequences.",
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
"ref":"eyekit.text",
"url":5,
"doc":"Defines classes for dealing with texts, most notably the  TextBlock and  InterestArea objects."
},
{
"ref":"eyekit.text.Character",
"url":5,
"doc":"Representation of a single character of text. A  Character object is essentially a one-letter string that occupies a position in space and has a bounding box. It is not usually necessary to create  Character objects manually; they are created automatically during the instantiation of a  TextBlock ."
},
{
"ref":"eyekit.text.Character.x",
"url":5,
"doc":" float X-coordinate of the center of the character"
},
{
"ref":"eyekit.text.Character.y",
"url":5,
"doc":" float Y-coordinate of the center of the character"
},
{
"ref":"eyekit.text.Character.x_tl",
"url":5,
"doc":" float X-coordinate of the top-left corner of character's bounding box"
},
{
"ref":"eyekit.text.Character.y_tl",
"url":5,
"doc":" float Y-coordinate of the top-left corner of character's bounding box"
},
{
"ref":"eyekit.text.Character.x_br",
"url":5,
"doc":" float X-coordinate of the bottom-right corner of character's bounding box"
},
{
"ref":"eyekit.text.Character.y_br",
"url":5,
"doc":" float Y-coordinate of the bottom-right corner of character's bounding box"
},
{
"ref":"eyekit.text.Character.width",
"url":5,
"doc":" float Width of the character"
},
{
"ref":"eyekit.text.Character.height",
"url":5,
"doc":" float Height of the character (i.e., the line height inherited from the  TextBlock )"
},
{
"ref":"eyekit.text.Character.box",
"url":5,
"doc":" tuple The character's bounding box: x, y, width, and height"
},
{
"ref":"eyekit.text.Character.center",
"url":5,
"doc":" tuple XY-coordinates of center of character"
},
{
"ref":"eyekit.text.Character.non_word_character",
"url":5,
"doc":" bool True if the character is non-alphabetical"
},
{
"ref":"eyekit.text.InterestArea",
"url":5,
"doc":"Representation of an interest area \u2013 a portion of a  TextBlock object that is of potenital interest. It is not usually necessary to create  InterestArea objects manually; they are created automatically when you slice a  TextBlock object or when you iterate over lines, words, characters, ngrams, or parsed interest areas."
},
{
"ref":"eyekit.text.InterestArea.x",
"url":5,
"doc":" float X-coordinate of the center of the interest area"
},
{
"ref":"eyekit.text.InterestArea.y",
"url":5,
"doc":" float Y-coordinate of the center of the interest area"
},
{
"ref":"eyekit.text.InterestArea.x_tl",
"url":5,
"doc":" float X-coordinate of the top-left corner of the interest area's bounding box"
},
{
"ref":"eyekit.text.InterestArea.y_tl",
"url":5,
"doc":" float Y-coordinate of the top-left corner of the interest area's bounding box"
},
{
"ref":"eyekit.text.InterestArea.x_br",
"url":5,
"doc":" float X-coordinate of the bottom-right corner of the interest area's bounding box"
},
{
"ref":"eyekit.text.InterestArea.y_br",
"url":5,
"doc":" float Y-coordinate of the bottom-right corner of the interest area's bounding box"
},
{
"ref":"eyekit.text.InterestArea.width",
"url":5,
"doc":" float Width of the interest area"
},
{
"ref":"eyekit.text.InterestArea.height",
"url":5,
"doc":" float Height of the interest area"
},
{
"ref":"eyekit.text.InterestArea.box",
"url":5,
"doc":" tuple The interest area's bounding box: x, y, width, and height"
},
{
"ref":"eyekit.text.InterestArea.center",
"url":5,
"doc":" tuple XY-coordinates of center of interest area"
},
{
"ref":"eyekit.text.InterestArea.text",
"url":5,
"doc":" str String represention of the interest area. Same as calling  str() on an  InterestArea ."
},
{
"ref":"eyekit.text.InterestArea.label",
"url":5,
"doc":" str Arbitrary label for the interest area"
},
{
"ref":"eyekit.text.TextBlock",
"url":5,
"doc":"Representation of a piece of text, which may be a word, sentence, or entire multiline passage. Initialized with: -  text  str (single line) |  list of  str (multiline) : The line or lines of text -  position  tuple [ float ,  float ] : XY-coordinates of the top left corner of the  TextBlock 's bounding box -  font_name  str : Name of a font available on your system. Matplotlib's FontManager is used to discover available fonts. -  font_size  float : Font size in points. -  line_spacing  float : Amount of line spacing (1 for single line spacing, 2 for double line spacing, etc.)"
},
{
"ref":"eyekit.text.TextBlock.x",
"url":5,
"doc":" float X-coordinate of the center of the TextBlock"
},
{
"ref":"eyekit.text.TextBlock.y",
"url":5,
"doc":" float Y-coordinate of the center of the TextBlock"
},
{
"ref":"eyekit.text.TextBlock.x_tl",
"url":5,
"doc":" float X-coordinate of the top-left corner of the TextBlock"
},
{
"ref":"eyekit.text.TextBlock.y_tl",
"url":5,
"doc":" float Y-coordinate of the top-left corner of the TextBlock"
},
{
"ref":"eyekit.text.TextBlock.x_br",
"url":5,
"doc":" float X-coordinate of the bottom-right corner of TextBlock"
},
{
"ref":"eyekit.text.TextBlock.y_br",
"url":5,
"doc":" float Y-coordinate of the bottom-right corner of TextBlock"
},
{
"ref":"eyekit.text.TextBlock.width",
"url":5,
"doc":" float Width of the TextBlock (i.e. the width of the widest line)"
},
{
"ref":"eyekit.text.TextBlock.height",
"url":5,
"doc":" float Height of the TextBlock"
},
{
"ref":"eyekit.text.TextBlock.box",
"url":5,
"doc":" tuple The interest area's bounding box: x, y, width, and height"
},
{
"ref":"eyekit.text.TextBlock.center",
"url":5,
"doc":" tuple XY-coordinates of center of interest area"
},
{
"ref":"eyekit.text.TextBlock.font_name",
"url":5,
"doc":" str Name of the font"
},
{
"ref":"eyekit.text.TextBlock.font_size",
"url":5,
"doc":" float Font size in points"
},
{
"ref":"eyekit.text.TextBlock.line_spacing",
"url":5,
"doc":" float Line spacing (single, double, etc.)"
},
{
"ref":"eyekit.text.TextBlock.line_height",
"url":5,
"doc":" float Pixel distance between lines"
},
{
"ref":"eyekit.text.TextBlock.n_rows",
"url":5,
"doc":" int Number of rows in the text (i.e. the number of lines)"
},
{
"ref":"eyekit.text.TextBlock.n_cols",
"url":5,
"doc":" int Number of columns in the text (i.e. the number of characters in the widest line)"
},
{
"ref":"eyekit.text.TextBlock.line_positions",
"url":5,
"doc":" int-array Y-coordinates of the center of each line of text"
},
{
"ref":"eyekit.text.TextBlock.word_centers",
"url":5,
"doc":" int-array XY-coordinates of the center of each word"
},
{
"ref":"eyekit.text.TextBlock.interest_areas",
"url":5,
"doc":"Iterate over each  InterestArea parsed from the raw text during initialization.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_interest_area",
"url":5,
"doc":"Returns the parsed  InterestArea that the fixation falls inside",
"func":1
},
{
"ref":"eyekit.text.TextBlock.get_interest_area",
"url":5,
"doc":"Retrieve a parsed  InterestArea by its label.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.lines",
"url":5,
"doc":"Iterate over each line as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_line",
"url":5,
"doc":"Returns the line  InterestArea that the fixation falls inside",
"func":1
},
{
"ref":"eyekit.text.TextBlock.words",
"url":5,
"doc":"Iterate over each word as an  InterestArea .  add_padding adds a little extra width to each word's bounding box, so that they cover the adjoining spaces or punctuation.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_word",
"url":5,
"doc":"Returns the word  InterestArea that the fixation falls inside.  add_padding adds a little extra width to each word's bounding box, so that they cover the adjoining spaces or punctuation.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.characters",
"url":5,
"doc":"Iterate over each character as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_character",
"url":5,
"doc":"Returns the character  InterestArea that the fixation falls inside",
"func":1
},
{
"ref":"eyekit.text.TextBlock.ngrams",
"url":5,
"doc":"Iterate over each ngram, for given n, as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.in_bounds",
"url":5,
"doc":"Returns  True if the given fixation is within a certain threshold of any character in the text. Returns  False otherwise.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.p_ngrams_fixation",
"url":5,
"doc":"Given a fixation, return probability distribution over ngrams in the text (or, optionally, just the line), representing the probability that each ngram is being \"seen\".",
"func":1
},
{
"ref":"eyekit.text.TextBlock.todict",
"url":5,
"doc":"Returns the  TextBlock 's ininialization arguments as a dictionary for serialization.",
"func":1
},
{
"ref":"eyekit.image",
"url":6,
"doc":"Defines the  Image object, which is used to create visualizations, and other functions for handling images."
},
{
"ref":"eyekit.image.Image",
"url":6,
"doc":"Visualization of texts and fixation sequences."
},
{
"ref":"eyekit.image.Image.render_text",
"url":6,
"doc":"Render a  eyekit.text.TextBlock on the image.",
"func":1
},
{
"ref":"eyekit.image.Image.render_fixations",
"url":6,
"doc":"Render a  eyekit.fixation.FixationSequence on the image.",
"func":1
},
{
"ref":"eyekit.image.Image.render_fixation_comparison",
"url":6,
"doc":"Render a  eyekit.fixation.FixationSequence on the image with the fixations colored according to whether or not they match a reference sequence in terms of the y-coordinate. This is mostly useful for comparing the outputs of two different drift correction algorithms.",
"func":1
},
{
"ref":"eyekit.image.Image.render_heatmap",
"url":6,
"doc":"Render a heatmap on the image. This is typically useful for visualizing the output from  eyekit.analysis.duration_mass() .",
"func":1
},
{
"ref":"eyekit.image.Image.draw_line",
"url":6,
"doc":"Draw an arbitrary line on the image from  start_xy to  end_xy .",
"func":1
},
{
"ref":"eyekit.image.Image.draw_circle",
"url":6,
"doc":"Draw an arbitrary circle on the image with center  xy and given  radius .",
"func":1
},
{
"ref":"eyekit.image.Image.draw_rectangle",
"url":6,
"doc":"Draw an arbitrary rectangle on the image located at x,y with some width and height. Also accepts a tuple of four ints as the first argument.",
"func":1
},
{
"ref":"eyekit.image.Image.draw_text",
"url":6,
"doc":"Draw arbitrary text on the image located at x,y.  align determines the anchor of the given position. Some CSS styling can also be provided to customize the text.",
"func":1
},
{
"ref":"eyekit.image.Image.crop_to_text",
"url":6,
"doc":"Once a  eyekit.text.TextBlock has been rendered using  Image.render_text() , this method can be called to crop the image to the size of the text with some  margin .",
"func":1
},
{
"ref":"eyekit.image.Image.set_label",
"url":6,
"doc":"Give the image a label which will be shown if you place the image in a combined image using  combine_images() .",
"func":1
},
{
"ref":"eyekit.image.Image.save",
"url":6,
"doc":"Save the image to some  output_path . The format (SVG, PDF, EPS, or PNG) is determined from the filename extension.  image_width only applies to SVG, PDF, and EPS where it determines the mm width. PNGs are rendered at actual pixel size. PDF, EPS, and PNG require [CairoSVG](https: cairosvg.org/):  pip install cairosvg ",
"func":1
},
{
"ref":"eyekit.image.convert_svg",
"url":6,
"doc":"Convert an SVG file into PDF, EPS, or PNG. This function is essentially a wrapper around [CairoSVG](https: cairosvg.org/).",
"func":1
},
{
"ref":"eyekit.image.combine_images",
"url":6,
"doc":"Combine image objects together into one larger image.  images should be a  list of  list of  Image structure. For example,   img1, img2], [img3, img4  results in a 2x2 grid of images.  image_width is the desired mm (SVG, PDF, EPS) or pixel (PNG) width of the combined image. If  auto_letter is set to  True , each image will be given a letter label.",
"func":1
}
]