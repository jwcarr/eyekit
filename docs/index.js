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
"doc":"Eyekit is a Python package for handling, analyzing, and visualizing eyetracking data, with a particular emphasis on the reading of sentences and multiline passages presented in a fixed-width font. Eyekit is currently in the pre-alpha stage and is licensed under the terms of the MIT License. Installation       The latest version of Eyekit can be installed using  pip :   $ pip install eyekit   Eyekit is compatible with Python 3.5 and up. The only required dependency is [Numpy](https: numpy.org), which will be installed automatically by pip if necessary. [CairoSVG](https: cairosvg.org) is required if you want to export visualizations into formats other than SVG. [Scipy](https: www.scipy.org) and [Scikit-learn](https: scikit-learn.org) are required by certain tools. Getting Started        - Once installed, import Eyekit in the normal way:   >>> import eyekit   Eyekit makes use of two core types of object: the  TextBlock object and the  FixationSequence object. Much of Eyekit's functionality involves bringing these two objects into contact; typically, we have a passage of text and we want to analyze which parts of the text a participant is looking at.  The  TextBlock object A  TextBlock object can represent a word, sentence, or passage of text. When you create a  TextBlock object, it is necessary to specify the pixel position of the first character, the pixel spacing between characters, the pixel spacing between lines, and the fontsize. Since Eyekit assumes a fixed-width font, it uses these details to establish the position of every character. Let's begin by creating a single sentence  TextBlock object:   >>> sentence = 'The quick brown fox [jump]{stem_1}[ed]{suffix_1} over the lazy dog.' >>> txt = eyekit.TextBlock(sentence, first_character_position=(100, 540), character_spacing=16, line_spacing=64, fontsize=28) >>> print(txt)  TextBlock[The quick brown  .]   Often we are only interested in certain parts of the sentence, or so-called \"interest areas\". Eyekit has a simple markup scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case  jump and  ed ) and curly braces are used to provide a unique label for each interest area (in this case  stem_1 and  suffix_1 ). We can iterate over them using the  TextBlock.interest_areas() iterator method:   >>> for interest_area in txt.interest_areas(): >>> print(interest_area.label, interest_area.text, interest_area.bounding_box)  stem_1 jump (412, 508, 64, 64)  suffix_1 ed (476, 508, 32, 64)   In this case, we are printing each interest area's label, its textual representation, and its bounding box (x, y, width, and height). Various other methods are available for treating all words, characters, or ngrams as interest areas. If, for example, you wanted to treat each word as an interest area, you could do the following without needing to explicitly mark up every word as an interest area:   >>> for word in txt.words(): >>> print(word.label, word.text, word.bounding_box)  word_0 The (92, 508, 48, 64)  word_1 quick (156, 508, 80, 64)  word_2 brown (252, 508, 80, 64)  word_3 fox (348, 508, 48, 64)  word_4 jumped (412, 508, 96, 64)  word_5 over (524, 508, 64, 64)  word_6 the (604, 508, 48, 64)  word_7 lazy (668, 508, 64, 64)  word_8 dog (748, 508, 48, 64)    The  FixationSequence object Fixation data is represented in a  FixationSequence object. Let's create some fake data to play around with:   >>> seq = eyekit.FixationSequence( 106, 540, 100], [190, 536, 100], [230, 555, 100], [298, 540, 100], [361, 547, 100], [430, 539, 100], [450, 539, 100], [492, 540, 100], [562, 555, 100], [637, 541, 100], [712, 539, 100], [763, 529, 100 )   Each fixation is represented by three numbers: its x-coordinate, its y-coordinate, and its duration (in this example, they're all 100ms). Once created, a  FixationSequence can be traversed, indexed, and sliced as you'd expect. For example,   >>> print(seq[5:10])  FixationSequence[Fixation[430,539],  ., Fixation[637,541   slices out fixations 5 through 9 into a new  FixationSequence object. This could be useful, for example, if you wanted to remove superfluous fixations from the start and end of the sequence. A basic question we might have is: Do any of these fixations fall inside my interest areas? We can write some simple code to answer this:   >>> for fixation in seq: >>> ia = txt.which_interest_area(fixation) >>> if ia is not None: >>> print('There was a fixation inside interest area {}, which is \"{}\".'.format(ia.label, ia.text  There was a fixation inside interest area stem_1, which is \"jump\".  There was a fixation inside interest area stem_1, which is \"jump\".  There was a fixation inside interest area suffix_1, which is \"ed\".   Analysis     At the moment, Eyekit has a fairly limited set of analysis functions; in general, you are expected to write code to calculate whatever you are interested in measuring. The available functions can be explored in the  analysis module, but two common functions that are currently available are  analysis.initial_fixation_duration() and  analysis.total_fixation_duration() , which may be used like this:   >>> tot_durations = eyekit.analysis.total_fixation_duration(txt.interest_areas(), seq) >>> init_durations = eyekit.analysis.initial_fixation_duration(txt.interest_areas(), seq) >>> print(tot_durations)  {'stem_1': 200, 'suffix_1': 100} >>> print(init_durations)  {'stem_1': 100, 'suffix_1': 100}   In this case, we see that the total duration spent inside the  stem_1 bounding box was 200ms, while the duration of the initial fixation on that interest area was 100ms. Similarly, these functions can be applied to other kinds of interest areas, such as words:   >>> tot_durations_on_words = eyekit.analysis.total_fixation_duration(txt.words(), seq) >>> print(tot_durations_on_words)  {'word_0': 100, 'word_1': 200, 'word_2': 100, 'word_3': 100, 'word_4': 300, 'word_5': 100, 'word_6': 100, 'word_7': 100, 'word_8': 100}   Here we see that a total of 300ms was spent on  word_4 , \"jumped\". Visualization       - Eyekit has some basic tools to help you create visualizations of your data. In general, we begin by creating an  image.Image object, specifying the pixel dimensions of the screen:   >>> img = eyekit.Image(1920, 1080)   Next we render our text and fixations:   >>> img.render_text(txt) >>> img.render_fixations(seq)   And finally, we save the image (Eyekit supports SVG, PDF, EPS, and PNG):   >>> img.save('quick_brown.pdf')    Sometimes it's useful to see the text in the context of the entire screen; other times, we'd like to remove all that excess white space and focus on the text. To do this, you can call the  crop_to_text() method prior to saving, optionally specifying some amount of margin:   >>> img.crop_to_text(margin=5) >>> img.save('quick_brown_cropped.pdf')    There are many other options for creating custom visualizations. For example, if we wanted to depict the bounding boxes around our two interest areas, with different colors for stems and suffixes, we might do this:   >>> img = eyekit.Image(1920, 1080) >>> img.render_text(txt) >>> for interest_area in txt.interest_areas(): >>> if interest_area.label.startswith('stem'): >>> img.draw_rectangle(interest_area.bounding_box, color='red') >>> elif interest_area.label.startswith('suffix'): >>> img.draw_rectangle(interest_area.bounding_box, color='blue') >>> img.render_fixations(seq) >>> img.crop_to_text(margin=5) >>> img.save('quick_brown_with_IAs.pdf')    Multiline Passages          Handling multiline passages works in largely the same way as described above. The principal difference is that when you instantiate a  TextBlock object, you must pass a list of strings (one for each line of text):   >>> txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], first_character_position=(100, 540), character_spacing=16, line_spacing=64, fontsize=28)   To see an example, we'll first load in some multiline passage data that is included in this repo:   >>> example_data = eyekit.io.read('example_data.json') >>> example_texts = eyekit.io.load_texts('example_texts.json')   and in particular we'll extract the fixation sequence for trial 0 and its associated text:   >>> seq = example_data['trial_0']['fixations'] >>> txt = example_texts[example_data['trial_0']['passage_id'   As before, we can plot the fixation sequence over the passage of text to see what the data looks like:   >>> img = eyekit.Image(1920, 1080) >>> img.render_text(txt) >>> img.render_fixations(seq) >>> img.crop_to_text(margin=50) >>> img.save('multiline_passage.pdf')    A common issue with multiline passage reading is that fixations on one line may appear closer to another line due to imperfect eyetracker calibration or general noise. For example, the fixation on \"voce\" on line two actually falls into the bounding box of the word \"vivevano\" on line one. Likewise, the fixation on \"passeggiata\" in the middle of the text is closer to \"Mamma\" on the line above. Obviously, such \"vertical drift\" will cause issues in your analysis further downstream, so it may be useful to first clean up the data by snapping every fixation to its appropriate line. Eyekit implements several vertical drift correction algorithms, which can be applied using the  tools.snap_to_lines() function from the  tools module:   >>> clean_seq = eyekit.tools.snap_to_lines(seq, txt, method='warp')   The default method is  warp , but you can also use  chain ,  cluster ,  merge ,  regress ,  segment , and  split . For a full description and evaluation of these methods, see [Carr et al. (2020)](https: osf.io/jg3nc/). This process only affects the y-coordinate of each fixation; the x-coordinate is always left unchanged. Let's have a look at the fixation sequence after applying this cleaning step:   >>> img = eyekit.Image(1920, 1080) >>> img.render_text(txt) >>> img.render_fixations(clean_seq) >>> img.crop_to_text(50) >>> img.save('multiline_passage_corrected.pdf')    The fixations on \"voce\" and \"passeggiata\", for example, are now clearly associated with the correct words, allowing us to proceed with our analysis. It is important to note, however, that drift correction should be applied with care, especially if the fixation data is very noisy or if the passage is being read nonlinearly. Input\u2013Output       Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, and a duration for each fixation, you are free to store data in whatever format you choose. However, as we have seen above, Eyekit provides built-in support for a JSON-based format, where a typical data file looks like this:   { \"trial_0\" : { \"participant_id\": \"John\", \"passage_id\": \"passage_a\", \"fixations\":  412, 142, 131], [459, 163, 112], [551, 160, 334],  ., [588, 866, 224 }, \"trial_1\" : { \"participant_id\": \"Mary\", \"passage_id\": \"passage_b\", \"fixations\":  368, 146, 191], [431, 154, 246], [512, 150, 192],  ., [725, 681, 930 }, \"trial_2\" : { \"participant_id\": \"Jack\", \"passage_id\": \"passage_c\", \"fixations\":  374, 147, 277], [495, 151, 277], [542, 155, 138],  ., [1288, 804, 141 } }   This format is open, human-readable, and fairly flexible. Each trial object should contain a key called  fixations that maps to an array containing x, y, and duration for each fixation. Aside from this, you can freely add other key\u2013value pairs (e.g., participant IDs, trial IDs, timestamps, etc.). These data files can be loaded using the  io.read() function from the  io module:   >>> data = eyekit.io.read('example_data.json')   and written using the  io.write() function:   >>> eyekit.io.write(data, 'example_data.json', indent=2)   Optionally, the  indent parameter specifies how much indentation to use in the files \u2013 indentation results in larger files, but they are more human-readable. If you store your fixation data in CSV files, you could load the data into a  FixationSequence by doing something along these lines (assuming you have columns  x ,  y , and  duration ):   >>> import pandas >>> data = pandas.read_csv('mydata.csv') >>> seq = eyekit.FixationSequence([fxn for fxn in zip(data['x'], data['y'], data['duration'])])   Eyekit also has rudimentary support for importing data from ASC files. When importing data this way, you must specify the name of a trial variable and its possible values so that the importer can determine when a new trial begins:   >>> data = eyekit.io.import_asc('mydata.asc', 'trial_type', ['Experimental'], extract_vars=['passage_id', 'response'])   In this case, when parsing the ASC file, the importer would consider   MSG 4244100 !V TRIAL_VAR trial_type Experimental   to mark the beginning of a new trial and will extract all  EFIX lines that occur within the subsequent  START \u2013 END block. Optionally, you can specify other variables that you want to extract (in this case  passage_id and  response ), resulting in imported data that looks like this:   { \"trial_0\" : { \"trial_type\" : \"Experimental\", \"passage_id\" : \"passage_a\", \"response\" : \"yes\", \"fixations\" : FixationSequence 368, 161, 208],  ., [562, 924, 115 } }   In addition, rather than load one ASC file at a time, you can also point to a directory of ASC files, all of which will then be loaded into a single dataset:   >>> data = eyekit.io.import_asc('asc_data_files/', 'trial_type', ['Experimental'], extract_variables=['passage_id', 'response'])   which could then be written out to Eyekit's native format:   >>> eyekit.io.write(data, 'converted_asc_data.json')  "
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
"doc":"Read in an Eyekit JSON file with the following structure:   { \"trial_0\" : { \"participant_id\" : \"John\", \"passage_id\" : \"passage_a\", \"fixations\" :  412, 142, 131],  ., [588, 866, 224 }, \"trial_1\" : { \"participant_id\" : \"Mary\", \"passage_id\" : \"passage_b\", \"fixations\" :  368, 146, 191],  ., [725, 681, 930 } }   Lists of fixations are automatically converted into  FixationSequence objects.",
"func":1
},
{
"ref":"eyekit.io.write",
"url":4,
"doc":"Write out to an Eyekit JSON file.  FixationSequence objects are automatically serialized. Optionally, the  indent parameter specifies how much indentation to use in the files.",
"func":1
},
{
"ref":"eyekit.io.load_texts",
"url":4,
"doc":"Load texts from a JSON file with the following structure:   { \"sentence_0\" : { \"first_character_position\" : [368, 155], \"character_spacing\" : 16, \"line_spacing\" : 64, \"fontsize\" : 28, \"text\" : \"The quick brown fox jumped over the lazy dog.\" }, \"sentence_1\" : { \"first_character_position\" : [368, 155], \"character_spacing\" : 16, \"line_spacing\" : 64, \"fontsize\" : 28, \"text\" : \"Lorem ipsum dolor sit amet, consectetur adipiscing elit.\" } }    TextBlock objects are created automatically, resulting in the dictionary:   { \"sentence_0\" : TextBlock[The quick brown  .], \"sentence_1\" : TextBlock[Lorem ipsum dolo .] }  ",
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
"doc":"Representation of a single character of text. It is not usually necessary to create  Character objects manually; they are created automatically during the instantiation of a  TextBlock ."
},
{
"ref":"eyekit.text.Character.x",
"url":5,
"doc":" int X-coordinate of the character"
},
{
"ref":"eyekit.text.Character.y",
"url":5,
"doc":" int Y-coordinate of the character"
},
{
"ref":"eyekit.text.Character.xy",
"url":5,
"doc":" tuple XY-coordinates of the character"
},
{
"ref":"eyekit.text.Character.rc",
"url":5,
"doc":" tuple Row,column index of the character"
},
{
"ref":"eyekit.text.Character.non_word_character",
"url":5,
"doc":" bool True if the character is non-alphabetical"
},
{
"ref":"eyekit.text.Character.x_tl",
"url":5,
"doc":"X-coordinate of top-left corner of bounding box"
},
{
"ref":"eyekit.text.Character.y_tl",
"url":5,
"doc":"Y-coordinate of top-left corner of bounding box"
},
{
"ref":"eyekit.text.Character.x_br",
"url":5,
"doc":"X-coordinate of bottom-right corner of bounding box"
},
{
"ref":"eyekit.text.Character.y_br",
"url":5,
"doc":"Y-coordinate of bottom-right corner of bounding box"
},
{
"ref":"eyekit.text.Character.bounding_box",
"url":5,
"doc":"Bounding box around the character; x, y, width, and height.  Fixation in Character returns  True if the fixation is inside this bounding box."
},
{
"ref":"eyekit.text.InterestArea",
"url":5,
"doc":"Representation of an interest area \u2013 a portion of a  TextBlock object that is of potenital interest. It is not usually necessary to create  InterestArea objects manually; they are created automatically when you slice a  TextBlock object or when you iterate over lines, words, characters, ngrams, or parsed interest areas."
},
{
"ref":"eyekit.text.InterestArea.x_tl",
"url":5,
"doc":"X-coordinate of top-left corner of bounding box"
},
{
"ref":"eyekit.text.InterestArea.y_tl",
"url":5,
"doc":"Y-coordinate of top-left corner of bounding box"
},
{
"ref":"eyekit.text.InterestArea.x_br",
"url":5,
"doc":"X-coordinate of bottom-right corner of bounding box"
},
{
"ref":"eyekit.text.InterestArea.y_br",
"url":5,
"doc":"Y-coordinate of bottom-right corner of bounding box"
},
{
"ref":"eyekit.text.InterestArea.width",
"url":5,
"doc":"Width of the  text.InterestArea "
},
{
"ref":"eyekit.text.InterestArea.height",
"url":5,
"doc":"Height of the interest area"
},
{
"ref":"eyekit.text.InterestArea.chars",
"url":5,
"doc":"Characters in the interest area"
},
{
"ref":"eyekit.text.InterestArea.text",
"url":5,
"doc":"String represention of the interest area"
},
{
"ref":"eyekit.text.InterestArea.bounding_box",
"url":5,
"doc":"Bounding box around the interest area; x, y, width, and height.  Fixation in InterestArea returns  True if the fixation is inside this bounding box."
},
{
"ref":"eyekit.text.InterestArea.center",
"url":5,
"doc":"XY-coordinates of center of interest area"
},
{
"ref":"eyekit.text.InterestArea.label",
"url":5,
"doc":"Arbitrary label for the interest area"
},
{
"ref":"eyekit.text.TextBlock",
"url":5,
"doc":"Representation of a piece of text, which may be a word, sentence, or entire multiline passage. Initialized with: -  text :  str (single line) or  list of  str (multiline) representing the text -  first_character_position :  tuple providing the XY-coordinates of the center of the first character in the text -  character_spacing :  int Pixel distance between characters -  line_spacing :  int Pixel distance between lines -  fontsize :  int Fontsize (this only affects how images are rendered and is not used in any internal calculations)"
},
{
"ref":"eyekit.text.TextBlock.first_character_position",
"url":5,
"doc":" tuple XY-coordinates of the center of the first character in the text"
},
{
"ref":"eyekit.text.TextBlock.character_spacing",
"url":5,
"doc":" int Pixel distance between characters"
},
{
"ref":"eyekit.text.TextBlock.line_spacing",
"url":5,
"doc":" int Pixel distance between lines"
},
{
"ref":"eyekit.text.TextBlock.fontsize",
"url":5,
"doc":" int Fontsize"
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
"doc":"Iterate over each  text.InterestArea parsed from the raw text during initialization.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_interest_area",
"url":5,
"doc":"Returns the parsed  text.InterestArea that the fixation falls inside",
"func":1
},
{
"ref":"eyekit.text.TextBlock.get_interest_area",
"url":5,
"doc":"Retrieve a parsed  text.InterestArea by its label.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.lines",
"url":5,
"doc":"Iterate over each line as an  text.InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_line",
"url":5,
"doc":"Returns the line  text.InterestArea that the fixation falls inside",
"func":1
},
{
"ref":"eyekit.text.TextBlock.words",
"url":5,
"doc":"Iterate over each word as an  text.InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_word",
"url":5,
"doc":"Returns the word  text.InterestArea that the fixation falls inside",
"func":1
},
{
"ref":"eyekit.text.TextBlock.characters",
"url":5,
"doc":"Iterate over each character as an  text.InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_character",
"url":5,
"doc":"Returns the character  text.InterestArea that the fixation falls inside",
"func":1
},
{
"ref":"eyekit.text.TextBlock.ngrams",
"url":5,
"doc":"Iterate over each ngram, for given n, as an  text.InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.rc_to_xy",
"url":5,
"doc":"Returns x and y coordinates from row and column indices.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.xy_to_rc",
"url":5,
"doc":"Returns row and column indices from x and y coordinates.",
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
"doc":"Render a  TextBlock on the image.",
"func":1
},
{
"ref":"eyekit.image.Image.render_fixations",
"url":6,
"doc":"Render a  FixationSequence on the image.",
"func":1
},
{
"ref":"eyekit.image.Image.render_fixation_comparison",
"url":6,
"doc":"Render a  FixationSequence on the image with the fixations colored according to whether or not they match a reference sequence in terms of the y-coordinate. This is mostly useful for comparing the outputs of two different drift correction algorithms.",
"func":1
},
{
"ref":"eyekit.image.Image.render_heatmap",
"url":6,
"doc":"Render a heatmap on the image. This is typically useful for visualizing the output from  analysis.duration_mass .",
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
"doc":"Draw arbitrary text on the image located at x,y.  align determines the anchor of the given position. Some CSS srtyling can also be provided to customize the text styling.",
"func":1
},
{
"ref":"eyekit.image.Image.crop_to_text",
"url":6,
"doc":"Once a  TextBlock has been rendered using  render_text() , this method can be called to crop the image to the size of the text block with some  margin .",
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