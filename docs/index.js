URLS=[
"index.html",
"measure.html",
"fixation.html",
"tools.html",
"io.html",
"vis.html",
"text.html"
];
INDEX=[
{
"ref":"eyekit",
"url":0,
"doc":"Eyekit is a Python package for analyzing reading behavior using eyetracking data. Eyekit aims to be entirely independent of any particular eyetracker hardware, experiment software, or data formats. It has an object-oriented style that defines three core objects \u2013 the TextBlock, InterestArea, and FixationSequence \u2013 that you bring into contact with a bit of coding.  Is Eyekit the Right Tool for Me?                 - You want to analyze which parts of a text someone is looking at and for how long. - You need convenient tools for extracting areas of interest from texts, such as specific words, phrases, or letter combinations. - You want to calculate common reading measures, such as gaze duration or initial landing position. - You need support for arbitrary fonts, multiline passages, right-to-left text, or non-alphabetical scripts. - You want the flexibility to define custom reading measures and to build your own reproducible processing pipeline. - You would like tools for dealing with noise and calibration issues, and for discarding fixations according to your own criteria. - You want to share your data in an open format and produce publication-ready vector graphics. Installation       Eyekit may be installed using  pip :   pip install eyekit   Eyekit is compatible with Python 3.8+. Its main dependency is the graphics library [Cairo](https: cairographics.org), which you might also need to install if it's not already on your system. Many Linux distributions have Cairo built in. On a Mac, it can be installed using [Homebrew](https: brew.sh):  brew install cairo . On Windows, it can be installed using [Anaconda](https: anaconda.org/anaconda/cairo):  conda install -c anaconda cairo . Getting Started        - Once installed, import Eyekit in the normal way:   import eyekit   Eyekit makes use of three core objects: the  fixation.FixationSequence ,  text.TextBlock , and  text.InterestArea . Much of Eyekit's functionality involves bringing these objects into contact. Typically, you define particular areas of the  text.TextBlock that are of interest (phrases, words, morphemes, letters .) and check to see which fixations from the  fixation.FixationSequence fall in those  text.InterestArea s and for how long.  The FixationSequence object Fixation data is represented in a  fixation.FixationSequence . Usually you will import fixation data from some raw data files, but for now let's just create some pretend data to play around with:   seq = eyekit.FixationSequence( 106, 490, 0, 100], [190, 486, 100, 200], [230, 505, 200, 300], [298, 490, 300, 400], [361, 497, 400, 500], [430, 489, 500, 600], [450, 505, 600, 700], [492, 491, 700, 800], [562, 505, 800, 900], [637, 493, 900, 1000], [712, 497, 1000, 1100], [763, 487, 1100, 1200 )   At a minimum, each fixation is represented by four numbers: its x-coordinate, its y-coordinate, its start time, and its end time (so, in this example, they all last 100ms). Once created, a  fixation.FixationSequence can be traversed, indexed, and sliced just like an ordinary  list . For example,   print(seq[5:10])  FixationSequence[Fixation[430,489],  ., Fixation[637,493   slices out fixations 5 through 9 into a new  fixation.FixationSequence object. A  fixation.FixationSequence (and the  fixation.Fixation objects it contains) has various properties that you can query:   print(len(seq  Number of fixations  12 print(seq.duration)  Duration of whole sequence  1200 print(seq[0].duration)  Duration of first fixation  100 print(seq[-1].xy)  xy coordinates of final fixation  (763, 487) print(seq[1].x)  x coordinate of second fixation  190    The TextBlock object A  text.TextBlock can represent a word, sentence, or passage of text. When you create a  text.TextBlock object, it is necessary to specify various details such as its position on the screen and the font:   sentence = 'The quick brown fox [jump]{stem}[ed]{suffix} over the lazy dog.' txt = eyekit.TextBlock(sentence, position=(100, 500), font_face='Times New Roman', font_size=36) print(txt)  TextBlock[The quick brown f .]   Eyekit has a simple scheme for marking up interest areas, as you can see in the above sentence. Square brackets are used to mark the interest area itself (in this case  jump and  ed ) and curly braces are used to provide a unique ID for each interest area (in this case  stem and  suffix ). We can extract a particular interest area by using its ID:   print(txt['stem'])  InterestArea[stem, jump]   Manually marking up interest areas in the raw text is typically useful if you have a small number of known interest areas. However, Eyekit also provides more powerful tools for extracting interest areas programmatically. For example, you can use  text.TextBlock.words() to iterate over every word in the text as an  text.InterestArea without needing to explicitly mark each of them up in the raw text:   for word in txt.words(): print(word)  InterestArea[0:0:3, The]  InterestArea[0:4:9, quick]  InterestArea[0:10:15, brown]  InterestArea[0:16:19, fox]  InterestArea[0:20:26, jumped]  InterestArea[0:27:31, over]  InterestArea[0:32:35, the]  InterestArea[0:36:40, lazy]  InterestArea[0:41:44, dog]   You can also supply a regular expression to iterate over words that match a certain pattern; words that end in  ed for example:   for word in txt.words('.+ed'): print(word)  InterestArea[0:20:26, jumped]   or just the four-letter words:   for word in txt.words('.{4}'): print(word)  InterestArea[0:27:31, over]  InterestArea[0:36:40, lazy]   or case-insensitive occurrences of the word  the :   for word in txt.words('(?i)the'): print(word)  InterestArea[0:0:3, The]  InterestArea[0:32:35, the]   You can collate a bunch of interest areas into a list for convenient access later on. For example, if you wanted to do some analysis on all the three-letter words, you might extract them and assign them to a variable like so:   three_letter_words = list(txt.words('.{3}' print(three_letter_words)  [InterestArea[0:0:3, The], InterestArea[0:16:19, fox], InterestArea[0:32:35, the], InterestArea[0:41:44, dog   You can also slice out arbitrary interest areas by using the row and column indices of a section of text. Here, for example, we are extracting a two-word section of text from line 0 (the first and only line) and characters 10 through 18:   brown_fox_ia = txt[0:10:19] print(brown_fox_ia)  InterestArea[0:10:19, brown fox]    The InterestArea object Once you've extracted an  text.InterestArea , you can access various properties about it:   print(brown_fox_ia.text)  get the string represented in this IA  brown fox print(brown_fox_ia.width)  get the pixel width of this IA  160.2421875 print(brown_fox_ia.center)  get the xy coordinates of the center of the IA  (329.5703125, 491.94921875) print(brown_fox_ia.onset)  get the x coordinate of the IA onset  253.94921875 print(brown_fox_ia.location)  get the location of the IA in its parent TextBlock  (0, 10, 19) print(brown_fox_ia.id)  get the ID of the IA  0:10:19   By default, an  text.InterestArea will have an ID of the form  0:10:19 , which refers to the unique position that it occupies in the text. However, you can also change the IDs to something more descriptive, if you wish. For example, you could enumerate the words in the text and give each one a number:   for i, word in enumerate(txt.words( : word.id = f'word{i}'   and, since  text.InterestArea s are passed around by reference, the IDs will update everywhere. For example, it we print the  three_letter_words list we created earlier, we find that it now reflects the new IDs:   print(three_letter_words)  [InterestArea[word0, The], InterestArea[word3, fox], InterestArea[word6, the], InterestArea[word8, dog   The  text.InterestArea defines the  in operator in a special way so that you can conveniently check if a fixation falls inside its bounding box. For example:   for fixation in seq: if fixation in brown_fox_ia: print(fixation)  Fixation[298,490]  Fixation[361,497]   An  text.InterestArea can be any sequence of consecutive characters, and, as you can see, it's possible to define several overlapping  text.InterestArea s at the same time:  txt['word4'] ( jumped ),  txt['stem'] ( jump ),  txt['suffix'] ( ed ), and  txt[0:24:25] (the  p in  jumped ) can all coexist. Visualization       - Now that we've created a  fixation.FixationSequence and  text.TextBlock , and we've extracted some  text.InterestArea s, it would be useful to visualize how these things relate to each other. To create a visualization, we begin by creating an  vis.Image object, specifying the pixel dimensions of the screen:   img = eyekit.vis.Image(1920, 1080)   Next we render our text and fixations onto this image:   img.draw_text_block(txt) img.draw_fixation_sequence(seq)   Note that the elements of the image will be layered in the order in which these methods are called \u2013 in this case, the fixations will be rendered on top of the text. Finally, we save the image (Eyekit supports PDF, EPS, SVG, or PNG):   img.save('quick_brown.svg')    Sometimes it's useful to see the text in the context of the entire screen, as is the case here; other times, we'd like to remove all that excess white space and focus in on the text. To do this, you need to specify a crop margin; the image will then be cropped to the size of the text block plus the specified margin:   img.save('quick_brown_cropped.svg', crop_margin=2)    There are many other options for creating custom visualizations, which you can explore in the  vis module. For example, if you wanted to depict the bounding boxes around the two interest areas we manually marked-up in the raw text, you might do this:   img = eyekit.vis.Image(1920, 1080) img.draw_text_block(txt) img.draw_rectangle(txt['stem'], color='crimson') img.draw_rectangle(txt['suffix'], color='cadetblue') img.draw_fixation_sequence(seq) img.save('quick_brown_with_zones.svg', crop_margin=2)    Colors can be specified as a tuple of RGB values (e.g.  (220, 20, 60) ), a hex triplet (e.g.  DC143C ), or any [standard HTML color name](https: www.w3schools.com/colors/colors_names.asp) (e.g.  crimson ). Similarly, we can do the same thing with the list of three-letter words we created earlier:   img = eyekit.vis.Image(1920, 1080) img.draw_text_block(txt) for word in three_letter_words: img.draw_rectangle(word, fill_color='slateblue', opacity=0.5) img.draw_fixation_sequence(seq) img.save('quick_brown_with_3letter_words.svg', crop_margin=2)    Or, indeed, all words in the text:   img = eyekit.vis.Image(1920, 1080) img.draw_text_block(txt) for word in txt.words(): img.draw_rectangle(word, color='hotpink') img.draw_fixation_sequence(seq) img.save('quick_brown_with_all_words.svg', crop_margin=2)    Note that, by default, each  text.InterestArea 's bounding box is slightly padded by, at most, half of the width of a space character. This ensures that, even if a fixation falls between two words, it will still be assigned to one of them. Padding is only applied to an  text.InterestArea 's edge if that edge adjoins a non-alphabetical character (i.e. spaces and punctuation). Thus, when  jumped was divided into separate stem and suffix areas above, no padding was applied word-internally. If desired, automatic padding can be turned off by setting the  autopad argument to  False during the creation of the  text.TextBlock , or it can be controlled manually using the  text.InterestArea.adjust_padding() method. Taking Measurements          - The  measure module provides various functions for computing common reading measures, including, for example: -  measure.gaze_duration -  measure.initial_fixation_duration -  measure.initial_landing_position These functions take an  text.InterestArea and  fixation.FixationSequence as input, and return the measure of interest. For example, if we wanted to measure the initial landing position on the  stem interest area, we can apply the function like this:   print(eyekit.measure.initial_landing_position(txt['stem'], seq  2   The initial fixation on  jump landed on character 2. You can also apply these functions to a collection of interest areas. This will return a dictionary of results in which the keys are the  text.InterestArea IDs. For example, if we wanted to calculate the initial fixation duration on the three-letter words we extracted earlier, we can do this:   print(eyekit.measure.initial_fixation_duration(three_letter_words, seq  {'word0': 100, 'word3': 100, 'word6': 100, 'word8': 100}   In this case, we see that the initial fixation on each of the three-letter words lasted 100ms. Typically, you will want to apply multiple measures to several interest areas across many trials, generating what is sometimes known as an \"interest area report.\" The  eyekit.measure.interest_area_report() function can help you do this, outputting a Pandas dataframe that can then be used in your downstream statistical analyses.  eyekit.measure.interest_area_report() expects a list of trials and a list of measurement functions. Each trial should be a dictionary containing at least two keys:  fixations , which will map to a  eyekit.fixation.FixationSequence , and  interest_areas , which will map to a list of interest areas extracted from a  eyekit.text.TextBlock . Any other keys in the dictionary (e.g., subject or trial identifiers) will be included as separate columns in the resulting dataframe. For example, here we are creating an interest area report (for all words) using the dummy data created above:   trials = [ { 'trial_id': 'dummy_trial', 'fixations': seq, 'interest_areas': txt.words(), } ] df = eyekit.measure.interest_area_report(trials, measures=['gaze_duration', 'total_fixation_duration']) print(df)  trial_id interest_area_id interest_area_text initial_fixation_duration total_fixation_duration  0 dummy_trial 0:0:3 The 100 100  1 dummy_trial 0:4:9 quick 100 200  2 dummy_trial 0:10:15 brown 100 100  3 dummy_trial 0:16:19 fox 100 100  4 dummy_trial 0:20:26 jumped 100 300  5 dummy_trial 0:27:31 over 100 100  6 dummy_trial 0:32:35 the 100 100  7 dummy_trial 0:36:40 lazy 100 100  8 dummy_trial 0:41:44 dog 100 100   Since this outputs a Pandas dataframe, you can interact with the data using standard Pandas methods, including, for example, saving the dataframe to a CSV file:   df.to_csv('path/to/results.csv')   The measurement functions provided by Eyekit can be used as-is or you can take a look at the underlying code and adapt them for your own purposes. For example, say \u2013 for some reason \u2013 you wanted to measure total fixation duration but double the duration if the word begins with a vowel, you could define your own custom measurement function like so:   def my_special_measure(interest_area, fixation_sequence): total_duration = 0 for fixation in fixation_sequence: if fixation in interest_area: if interest_area.text.startswith 'a', 'e', 'i', 'o', 'u' : total_duration += fixation.duration  2 else: total_duration += fixation.duration return total_duration   and then apply your function to some data:   print(my_special_measure(txt['suffix'], seq  200   Multiline Passages          So far, we've only looked at a single line  text.TextBlock , but handling multiline passages works in largely the same way. The principal difference is that when you instantiate your  text.TextBlock object, you must pass a  list of strings (one for each line of text):   txt = eyekit.TextBlock(['This is line 1', 'This is line 2'], position=(100, 500), font_face='Helvetica', font_size=24)   To see an example, we'll load in some real multiline passage data from [Pescuma et al.](https: osf.io/hx2sj/) which is included in the [Eyekit GitHub repository](https: github.com/jwcarr/eyekit):   example_data = eyekit.io.load('example/example_data.json') example_texts = eyekit.io.load('example/example_texts.json')   and in particular we'll extract the fixation sequence for trial 0 and its associated text:   seq = example_data['trial_0']['fixations'] pid = example_data['trial_0']['passage_id'] txt = example_texts[pid]['text']   As before, we can plot the fixation sequence over the passage of text to see what the data looks like:   img = eyekit.vis.Image(1920, 1080) img.draw_text_block(txt) img.draw_rectangle(txt[0:32:40], color='orange') img.draw_rectangle(txt[1:34:38], color='orange') img.draw_fixation_sequence(seq) img.save('multiline_passage.svg', crop_margin=4)    First, we might decide that we want to discard that final fixation, where the participant jumped a few lines up right at the end:   seq[-1].discard()  discard the final fixation   A second problem we can see here is that fixations on one line sometimes appear slightly closer to another line due to imperfect eyetracker calibration. For example, the fixation on the word  voce on line two actually falls into the bounding box of the word  vivevano on line one. Obviously, this will cause issues in your analysis further downstream, so it can be useful to first clean up the data by snapping every fixation to its appropriate line. Eyekit implements several different line assignment algorithms, which can be applied using the  fixation.FixationSequence.snap_to_lines() method:   original_seq = seq.copy()  keep a copy of the original sequence seq.snap_to_lines(txt)   This process adjusts the y-coordinate of each fixation so that it matches the midline of its assigned line. To compare the corrected fixation sequence to the original, we could make two images and then combine them in a single  vis.Figure , like so:   img1 = eyekit.vis.Image(1920, 1080) img1.draw_text_block(txt) img1.draw_rectangle(txt[0:32:40], color='orange') img1.draw_rectangle(txt[1:34:38], color='orange') img1.draw_fixation_sequence(original_seq) img1.set_caption('Before correction') img2 = eyekit.vis.Image(1920, 1080) img2.draw_text_block(txt) img2.draw_rectangle(txt[0:32:40], color='orange') img2.draw_rectangle(txt[1:34:38], color='orange') img2.draw_fixation_sequence(seq) img2.set_caption('After correction') fig = eyekit.vis.Figure(1, 2)  one row, two columns fig.add_image(img1) fig.add_image(img2) fig.set_crop_margin(3) fig.save('multiline_passage_corrected.svg')    The fixation on  voce is now clearly associated with the correct word. Nevertheless,  snap_to_lines() should be applied with care, especially if the fixation data is very noisy or if the passage is being read nonlinearly. For advice on which method to use, see [Carr et al. (2021)](https: doi.org/10.3758/s13428-021-01554-0). Just like single-line texts, we can extract interest areas from the passage and take measurements in the same way. For example, if we were interested in the word  piccolo / piccola in this passage, we could extract all occurrences of this word and calculate the total fixation duration:   piccol_words = list(txt.words('piccol[oa]' durations = eyekit.measure.total_fixation_duration(piccol_words, seq) print(durations)  {'2:64:71': 253, '3:0:7': 347, '3:21:28': 246, '3:29:36': 319, '7:11:18': 268, '10:43:50': 178}   Furthermore, we could make a visualization to show this information:   img = eyekit.vis.Image(1920, 1080) img.draw_text_block(txt) for word in piccol_words: img.draw_rectangle(word, color='lightseagreen') x = word.onset y = word.y_br - 3 label = f'{durations[word.id]}ms' img.draw_annotation x, y), label, color='lightseagreen', font_face='Arial bold', font_size=4) img.draw_fixation_sequence(seq, color='gray') img.save('multiline_passage_piccol.svg', crop_margin=4)    Another way to look at the data is to distribute the fixations across the characters of the passage probabilistically, under the assumption that the closer a character is to a fixation point, the more likely it is that the reader is perceiving that character. This can be performed with the  measure.duration_mass function and plotted in a heatmap like so:   mass = eyekit.measure.duration_mass(txt, seq) img = eyekit.vis.Image(1920, 1080) img.draw_heatmap(txt, mass, color='green') img.save('multiline_passage_mass.svg', crop_margin=4)    Input\u2013Output       Eyekit is not especially committed to any particular file format; so long as you have an x-coordinate, a y-coordinate, a start time, and an end time for each fixation, you are free to store data in whatever format you choose. However, as we have seen briefly above, Eyekit provides built-in support for JSON, where a typical data file might look something like this:   { \"trial_0\" : { \"participant_id\": \"John\", \"passage_id\": \"passage_a\", \"fixations\": { \"__FixationSequence__\": [ { \"x\": 412, \"y\": 142, \"start\": 770, \"end\": 900 }, { \"x\": 459, \"y\": 163, \"start\": 924, \"end\": 1035 }, { \"x\": 551, \"y\": 160, \"start\": 1062, \"end\": 1395 } ] } }, \"trial_1\" : { \"participant_id\": \"Mary\", \"passage_id\": \"passage_b\", \"fixations\": { \"__FixationSequence__\": [ { \"x\": 368, \"y\": 146, \"start\": 7, \"end\": 197 }, { \"x\": 431, \"y\": 154, \"start\": 415, \"end\": 660 }, { \"x\": 512, \"y\": 150, \"start\": 685, \"end\": 876 } ] } } }   This format is compact, structured, human-readable, and flexible. With the exception of the  __FixationSequence__ object, you can freely store whatever key-value pairs you want and you can organize the hierarchy of the data structure in any way that makes sense for your project. JSON files can be loaded using the  io.load() function from the  io module:   data = eyekit.io.load('example/example_data.json')   which automatically instantiates any  fixation.FixationSequence objects. Similarly, an arbitrary dictionary or list can be written out using the  io.save() function:   eyekit.io.save(data, 'output_data.json', compress=True)   If  compress is set to  True , files are written in the most compact way; if  False , the file will be larger but more human-readable (like the example above). JSON can also be used to store  text.TextBlock objects \u2013 see  example_texts.json for an example \u2013 and you can even store  fixation.FixationSequence and  text.TextBlock objects in the same file if you like to keep things organized together. The  io module also provides functions for importing data from other formats:  io.import_asc() and  io.import_csv() . Once data has been imported this way, it may then be written out to Eyekit's native JSON format for quick access in the future. In time, I hope to add more functions to import data from common eyetracker formats. Creating Experimental Stimuli               - Eyekit is primarily intended for use at the analysis stage. However, it is possible to create basic experimental stimuli that can be presented in software of your choice. This can be achieved with the  tools.create_stimuli() function. For example, you can specify a path to some .txt files, along with an output path and various details about the presentation of the texts:   eyekit.tools.create_stimuli( 'path/to/my/raw/texts/', 'path/to/save/my/stimuli/', screen_width=1920, screen_height=1080, position=(400, 200), font_face='Consolas', font_size=20, line_height=40, color='black', background_color='white', )   This will output a PNG image for each text file, plus a file called  stimuli.json that contains each text as a  text.TextBlock object (for use at the analysis stage). The PNG images may then be presented at full size on the experimental computer (e.g. 1920\u00d71080). Getting Texts into Eyekit             - For more complex experimental designs or if you used other software to create your stimuli, you will need to recreate the stimuli as Eyekit  text.TextBlock s based on what you know about how they were presented. This can be a little tricky because the precise layout of the texts will be dependent on many different factors \u2013 not just the font and its size, but also the peculiarities of the experiment software and its text rendering engine. Ideally, all of your texts will have been presented in some consistent way. For example, they might be centralized on the screen or they might have a consistent left edge. The best way to check that a  text.TextBlock is set up correctly is to check it against a screenshot from your actual experiment. Eyekit provides the  tools.align_to_screenshot() tool to help you do this. First, set up your text block with parameters that you think are correct:   txt = eyekit.TextBlock( saramago_text, position=(300, 100), font_face='Baskerville', font_size=30, line_height=60, align='left', anchor='left' )   Then pass it to the  tools.align_to_screenshot() function along with the path to a PNG screenshot file:   eyekit.tools.align_to_screenshot(txt, 'screenshot.png')    This will create a new image file ending  _eyekit.png (e.g.  screenshot_eyekit.png ). In this file, Eyekit's rendering of the text is presented in green overlaying the original screenshot image. The point where the two solid green lines intersect corresponds to the  text.TextBlock 's  position argument, and the dashed green lines show the baselines of subsequent lines of text, which is based on the  line_height argument. You can use this output image to adjust the parameters of the  text.TextBlock accordingly. In this example case, we see that the  text.TextBlock is positioned slightly too high up. If all of your texts are presented in a consistent way, you should only need to establish these parameters once. Multilingual Support           Eyekit aims to offer good multilingual support, and the most common scripts \u2013 Arabic, Chinese, Cyrillic, Greek, Hebrew, Japanese, Korean, Latin \u2013 should all work out of the box. Right-to-left text (and bidirectional text in general) is supported \u2013 all you need to do is set  right_to_left=True when creating a  text.TextBlock . This ensures that the text will be rendered correctly and that functions like  measure.initial_landing_position and  fixation.FixationSequence.snap_to_lines will process the text in right-to-left direction. If you are working with the Arabic script, the text should be shaped prior to passing it into Eyekit using, for example, the [Arabic-reshaper](https: github.com/mpcabd/python-arabic-reshaper) package. Eyekit uses Cairo's \"toy font\" API to extract character metrics from the fonts available on your system. This API can be somewhat imperfect, especially if you are working with a particularly complex script or advanced typographical features, such as ligatures and kerning. However, in most cases it should be more than sufficient to extract areas of interest fairly accurately. When choosing a font for your experiment, the key thing to do is to make sure it supports all the glyphs in the language you're working with (some software, for example, may fall back to an alternative font in cases where a glyph is missing). Contributing       Eyekit is still in an early stage of development, but I am very happy to receive bug reports and suggestions via the [GitHub Issues page](https: github.com/jwcarr/eyekit/issues). If you'd like to work on new features or fix stuff that's currently broken, please feel free to fork the repo and/or raise an issue to discuss details. Before sending a pull request, you should check that the unit tests pass using [Pytest](https: pytest.org):   pytest tests/   and run [Black](https: black.readthedocs.io) over the codebase to normalize the style:   black eyekit/   Here are some areas of Eyekit that are currently underdeveloped: - Additional reading measures (e.g. of saccades and regressions) - Awareness of different experimental paradigms - Creation of animations/videos - More convenient methods for collating results into dataframes etc. - Importing data from other eyetracker data formats - Synchronization of fixation data with other types of experimental event - Support for nontextual objects, such as images or shapes - Interactive tools for cleaning up raw data - General testing and the addition of more unit tests"
},
{
"ref":"eyekit.measure",
"url":1,
"doc":"Functions for calculating common reading measures, such as gaze duration or initial landing position."
},
{
"ref":"eyekit.measure.interest_area_report",
"url":1,
"doc":"Given one or more trials and one or more measures, apply each measure to all interest areas associated with each trial and return a Pandas dataframe with the collated results. The  trials argument should be a list of dictionaries, where each dictionary contains minimally a  fixations key that maps to a  eyekit.fixation.FixationSequence and an  interest_areas key that maps to a list of interest areas extracted from a  eyekit.text.TextBlock . Any other keys in the dictionary (e.g., trial/subject identifiers) will be included as separate columns in the resulting dataframe. The  measures argument should be a list of built-in measures from the  eyekit.measure module or your own custom measurement functions. For example:   trials = [ { 'trial_id': 'trial1', 'fixations': FixationSequence( .), 'interest_areas': text_block.words() } ] measures = ['total_fixation_duration', 'gaze_duration'] dataframe = eyekit.measure.interest_area_report(trials, measures) dataframe.to_csv('path/to/output.csv')  write dateframe to CSV  ",
"func":1
},
{
"ref":"eyekit.measure.number_of_fixations",
"url":1,
"doc":"Given an interest area and fixation sequence, return the number of fixations on that interest area. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.initial_fixation_duration",
"url":1,
"doc":"Given an interest area and fixation sequence, return the duration of the initial fixation on that interest area. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.first_of_many_duration",
"url":1,
"doc":"Given an interest area and fixation sequence, return the duration of the initial fixation on that interest area, but only if there was more than one fixation on the interest area (otherwise return  None ). This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.total_fixation_duration",
"url":1,
"doc":"Given an interest area and fixation sequence, return the sum duration of all fixations on that interest area. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.gaze_duration",
"url":1,
"doc":"Given an interest area and fixation sequence, return the gaze duration on that interest area. Gaze duration is the sum duration of all fixations inside an interest area until the area is exited for the first time. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.go_past_duration",
"url":1,
"doc":"Given an interest area and fixation sequence, return the go-past time on that interest area. Go-past time is the sum duration of all fixations from when the interest area is first entered until when it is first exited to the right, including any regressions to the left that occur during that time period (and vice versa in the case of right-to-left text). This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.second_pass_duration",
"url":1,
"doc":"Given an interest area and fixation sequence, return the second pass duration on that interest area. Second pass duration is the sum duration of all fixations inside an interest area during the second pass over that interest area. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.initial_landing_position",
"url":1,
"doc":"Given an interest area and fixation sequence, return the initial landing position (expressed in character positions) on that interest area. Counting is from 1. If the interest area represents right-to-left text, the first character is the rightmost one. Returns  None if no fixation landed on the interest area. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.initial_landing_distance",
"url":1,
"doc":"Given an interest area and fixation sequence, return the initial landing distance on that interest area. The initial landing distance is the pixel distance between the first fixation to land in an interest area and the left edge of that interest area (or, in the case of right-to-left text, the right edge). Technically, the distance is measured from the text onset without including any padding. Returns  None if no fixation landed on the interest area. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.landing_distances",
"url":1,
"doc":"Deprecated in 0.5.4. Given an interest area and fixation sequence, return a list of landing distances on that interest area. Each landing distance is the pixel distance between the fixation and the left edge of the interest area(or, in the case of right-to-left text, the right edge). The distance is measured from the text onset without including any padding. Returns an empty list if no fixation landed on the interest area. This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.number_of_regressions_in",
"url":1,
"doc":"Given an interest area and fixation sequence, return the number of regressions back to that interest area after the interest area was read for the first time. In other words, find the first fixation to exit the interest area and then count how many times the reader returns to the interest area from the right (or from the left in the case of right-to-left text). This function may also be applied to a collection of interest areas, in which case a dictionary of results is returned.",
"func":1
},
{
"ref":"eyekit.measure.duration_mass",
"url":1,
"doc":"Given a  eyekit.text.TextBlock and  eyekit.fixation.FixationSequence , distribute the durations of the fixations probabilistically across the  eyekit.text.TextBlock . Specifically, the duration of fixation  f is distributed over all characters  C in its line according to the probability that the reader is \"seeing\" each character (see  p_characters_fixation() ), and this is summed over all fixations:  \\sum_{f \\in F} p(C|f) \\cdot f_\\mathrm{dur} For a given fixation  f , we compute a Gaussian distribution over all characters in the line according to:  p(c|f) \\propto \\mathrm{exp} \\frac{ -\\mathrm{ED}(f_\\mathrm{pos}, c_\\mathrm{pos})^2 }{2\\gamma^2} where  \u03b3 ( gamma ) is a free parameter controlling the rate at which probability decays with the Euclidean distance (ED) between the position of fixation  f and the position of character  c . Returns a 2D Numpy array, the sum of which is equal to the total duration of all fixations. This can be passed to  eyekit.vis.Image.draw_heatmap() for visualization. Duration mass reveals the parts of the text that received the most attention. Optionally, this can be performed over higher-level ngrams by setting  ngram_width > 1.",
"func":1
},
{
"ref":"eyekit.fixation",
"url":2,
"doc":"Defines the  Fixation and  FixationSequence objects, which are used to represent fixation data."
},
{
"ref":"eyekit.fixation.Fixation",
"url":2,
"doc":"Representation of a single fixation event. It is not usually necessary to create  Fixation objects manually; they are created automatically during the instantiation of a  FixationSequence ."
},
{
"ref":"eyekit.fixation.Fixation.index",
"url":2,
"doc":"Index of the fixation in its parent  FixationSequence "
},
{
"ref":"eyekit.fixation.Fixation.x",
"url":2,
"doc":"X-coordinate of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.y",
"url":2,
"doc":"Y-coordinate of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.xy",
"url":2,
"doc":"XY-coordinates of the fixation."
},
{
"ref":"eyekit.fixation.Fixation.start",
"url":2,
"doc":"Start time of the fixation in milliseconds."
},
{
"ref":"eyekit.fixation.Fixation.end",
"url":2,
"doc":"End time of the fixation in milliseconds."
},
{
"ref":"eyekit.fixation.Fixation.duration",
"url":2,
"doc":"Duration of the fixation in milliseconds."
},
{
"ref":"eyekit.fixation.Fixation.pupil_size",
"url":2,
"doc":"Size of the pupil.  None if no pupil size is recorded."
},
{
"ref":"eyekit.fixation.Fixation.discarded",
"url":2,
"doc":" True if the fixation has been discarded,  False otherwise."
},
{
"ref":"eyekit.fixation.Fixation.tags",
"url":2,
"doc":"Tags applied to this fixation."
},
{
"ref":"eyekit.fixation.Fixation.discard",
"url":2,
"doc":"Mark this fixation as discarded. To completely remove the fixation, you should also call  FixationSequence.purge() .",
"func":1
},
{
"ref":"eyekit.fixation.Fixation.add_tag",
"url":2,
"doc":"Tag this fixation with some arbitrary tag and (optionally) a value.",
"func":1
},
{
"ref":"eyekit.fixation.Fixation.has_tag",
"url":2,
"doc":"Returns  True if the fixation has a given tag.",
"func":1
},
{
"ref":"eyekit.fixation.Fixation.shift_x",
"url":2,
"doc":"Shift the fixation's x-coordinate to the right (+) or left (-) by some amount (in pixels).",
"func":1
},
{
"ref":"eyekit.fixation.Fixation.shift_y",
"url":2,
"doc":"Shift the fixation's y-coordinate down (+) or up (-) by some amount (in pixels).",
"func":1
},
{
"ref":"eyekit.fixation.Fixation.shift_time",
"url":2,
"doc":"Shift this fixation forwards (+) or backwards (-) in time by some amount (in milliseconds).",
"func":1
},
{
"ref":"eyekit.fixation.Fixation.serialize",
"url":2,
"doc":"Returns representation of the fixation as a dictionary for serialization.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence",
"url":2,
"doc":"Representation of a sequence of consecutive fixations, typically from a single trial. Initialized with: -  sequence List of tuples of ints, or something similar, that conforms to the following structure:  [(106, 540, 100, 200), (190, 536, 200, 300),  ., (763, 529, 1000, 1100)] , where each tuple contains the X-coordinate, Y-coordinate, start time, and end time of a fixation. Alternatively,  sequence may be a list of dicts, where each dict is something like  {'x': 106, 'y': 540, 'start': 100, 'end': 200} ."
},
{
"ref":"eyekit.fixation.FixationSequence.start",
"url":2,
"doc":"Start time of the fixation sequence (in milliseconds)."
},
{
"ref":"eyekit.fixation.FixationSequence.end",
"url":2,
"doc":"End time of the fixation sequence (in milliseconds)."
},
{
"ref":"eyekit.fixation.FixationSequence.duration",
"url":2,
"doc":"Duration of the fixation sequence, incuding any gaps between fixations (in milliseconds)."
},
{
"ref":"eyekit.fixation.FixationSequence.copy",
"url":2,
"doc":"Returns a copy of the fixation sequence.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.purge",
"url":2,
"doc":"Permanently removes all discarded fixations from the sequence, and reindexes the fixations.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.iter_with_discards",
"url":2,
"doc":"Iterates over the fixation sequence including any discarded fixations. This is also the default behavior when iterating over a  FixationSequence directly.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.iter_without_discards",
"url":2,
"doc":"Iterates over the fixation sequence without any discarded fixations.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.iter_pairs",
"url":2,
"doc":"Iterate over fixations in consecutive pairs. This is useful if you want to compare consecutive fixations in some way. For example, if you wanted to detect when a fixation leaves an interest area, you might do something like this:   for curr_fxn, next_fxn in seq.iter_pairs(): if curr_fxn in interest_area and next_fxn not in interest_area: print('A fixation has left the interest area')  ",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.shift_x",
"url":2,
"doc":"Shift all fixations' x-coordinates to the right (+) or left (-) by some amount (in pixels).",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.shift_y",
"url":2,
"doc":"Shift all fixations' y-coordinates down (+) or up (-) by some amount (in pixels).",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.shift_time",
"url":2,
"doc":"Shift all fixations forwards (+) or backwards (-) in time by some amount (in milliseconds).",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.shift_start_time_to_zero",
"url":2,
"doc":"Shift all fixations backwards in time, such that the first fixation in the sequence starts at time 0. Returns the amount (in milliseconds) by which the entire sequence was shifted.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.segment",
"url":2,
"doc":"Given a list of time intervals, segment the fixation sequence into subsequences. This may be useful if you want to split the sequence based on, for example, page turns or subtitle timings. Returns a list of  n  FixationSequence s, where  n =  len(time_intervals) . The time intervals should be specified as a list of tuples or something similarly interpretable:  [(500, 1000), (1500, 2000), (2500, 5000)] .",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.discard_short_fixations",
"url":2,
"doc":"Discard all fixations that are shorter than some threshold value (defualt: 50ms). Note that this only flags fixations as discarded and doesn't actually remove them; to remove discarded fixations, call  eyekit.fixation.FixationSequence.purge() after discarding.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.discard_long_fixations",
"url":2,
"doc":"Discard all fixations that are longer than some threshold value (defualt: 500ms). Note that this only flags fixations as discarded and doesn't actually remove them; to remove discarded fixations, call  eyekit.fixation.FixationSequence.purge() after discarding.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.discard_out_of_bounds_fixations",
"url":2,
"doc":"Given a  eyekit.text.TextBlock , discard all fixations that do not fall within some threshold distance of any character in the text. Note that this only flags fixations as discarded and doesn't actually remove them; to remove discarded fixations, call  eyekit.fixation.FixationSequence.purge() after discarding.",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.snap_to_lines",
"url":2,
"doc":"Given a  eyekit.text.TextBlock , snap each fixation to the line that it most likely belongs to, eliminating any y-axis variation. Several methods are available (see below), some of which take optional parameters or require NumPy/SciPy to be installed. See [Carr et al. (2021)](https: doi.org/10.3758/s13428-021-01554-0) for a full description and evaluation of these methods. Note that in single-line TextBlocks, the  method parameter has no effect: all fixations will be snapped to the one line. If a list of methods is passed in, each fixation will be snapped to the line with the most \"votes\" across the selection of methods (in case of ties, the left-most method takes priority). This \"wisdom of the crowd\" approach usually results in greater performance than any one algorithm individually; ideally, you should choose a selection of methods that have different general properties: for example,  ['slice', 'cluster', 'warp'] . The  snap_to_lines() method returns two values, delta and kappa, which are indicators of data quality. Delta is the average amount by which a fixation is moved in the correction. If this value is high (e.g. > 30), this may indicate that the quality of the data or the correction is low. Kappa, which is only calculated when multiple methods are applied, is a measure of agreement among the methods. If this value is low (e.g. < 0.7), this may indicate that the correction is unreliable. -  chain : Chain consecutive fixations that are sufficiently close to each other, and then assign chains to their closest text lines. Default params:  x_thresh=192 ,  y_thresh=32 . Requires NumPy. Original method implemented in [popEye](https: github.com/sascha2schroeder/popEye/). -  cluster : Classify fixations into  m clusters based on their Y-values, and then assign clusters to text lines in positional order. Requires SciPy. Original method implemented in [popEye](https: github.com/sascha2schroeder/popEye/). -  merge : Form a set of progressive sequences and then reduce the set to  m by repeatedly merging those that appear to be on the same line. Merged sequences are then assigned to text lines in positional order. Default params:  y_thresh=32 ,  gradient_thresh=0.1 ,  error_thresh=20 . Requires NumPy. Original method by [\u0160pakov et al. (2019)](https: doi.org/10.3758/s13428-018-1120-x). -  regress : Find  m regression lines that best fit the fixations and group fixations according to best fit regression lines, and then assign groups to text lines in positional order. Default params:  slope_bounds=(-0.1, 0.1) ,  offset_bounds=(-50, 50) ,  std_bounds=(1, 20) . Requires SciPy. Original method by [Cohen (2013)](https: doi.org/10.3758/s13428-012-0280-3). -  segment : Segment fixation sequence into  m subsequences based on  m \u20131 most-likely return sweeps, and then assign subsequences to text lines in chronological order. Requires NumPy. Original method by [Abdulin & Komogortsev (2015)](https: doi.org/10.1109/BTAS.2015.7358786). -  slice : Form a set of runs and then reduce the set to  m by repeatedly merging those that appear to be on the same line. Merged sequences are then assigned to text lines in positional order. Default params:  x_thresh=192 ,  y_thresh=32 ,  w_thresh=32 ,  n_thresh=90 . Requires NumPy. Original method by [Glandorf & Schroeder (2021)](https: doi.org/10.1016/j.procs.2021.09.069). -  split : Split fixation sequence into subsequences based on best candidate return sweeps, and then assign subsequences to closest text lines. Requires SciPy. Original method by [Carr et al. (2022)](https: doi.org/10.3758/s13428-021-01554-0). -  stretch : Find a stretch factor and offset that results in a good alignment between the fixations and lines of text, and then assign the transformed fixations to the closest text lines. Default params:  stretch_bounds=(0.9, 1.1) ,  offset_bounds=(-50, 50) . Requires SciPy. Original method by [Lohmeier (2015)](http: www.monochromata.de/master_thesis/ma1.3.pdf). -  warp : Map fixations to word centers using [Dynamic Time Warping](https: en.wikipedia.org/wiki/Dynamic_time_warping). This finds a monotonically increasing mapping between fixations and words with the shortest overall distance, effectively resulting in  m subsequences. Fixations are then assigned to the lines that their mapped words belong to, effectively assigning subsequences to text lines in chronological order. Requires NumPy. Original method by [Carr et al. (2022)](https: doi.org/10.3758/s13428-021-01554-0).",
"func":1
},
{
"ref":"eyekit.fixation.FixationSequence.serialize",
"url":2,
"doc":"Returns representation of the fixation sequence in simple list format for serialization.",
"func":1
},
{
"ref":"eyekit.tools",
"url":3,
"doc":"Miscellaneous utility functions."
},
{
"ref":"eyekit.tools.create_stimuli",
"url":3,
"doc":"Create PNG stimuli for a set of texts. This may be useful if you want to use Eyekit to create your experimental stimuli. If  input_texts is a string, it will be treated as a path to a directory of .txt files. If  input_texts is a list, it is assumed to be a list of texts (strings or lists of strings). If  input_texts is a dictionary, it should be of the form  {'stim_id': TextBlock,  .} .  output_stimuli must be a path to a directory. The  screen_width and  screen_height must be specified and should match the final display size of the experimental stimuli (typically, the experimental computer's screen resolution). A  color and  background_color can optionally be specified (defaulting to black on white). Additional arguments are passed to  TextBlock , and may include  position ,  font_face ,  font_size , and  line_height (see  eyekit.text.TextBlock for more info). The function will also store the texts as  TextBlock objects in  stimuli.json for use at the analysis stage.",
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
"ref":"eyekit.tools.discard_short_fixations",
"url":3,
"doc":" Deprecated in 0.4 and removed in 0.6. Use  eyekit.fixation.FixationSequence.discard_short_fixations() .",
"func":1
},
{
"ref":"eyekit.tools.discard_out_of_bounds_fixations",
"url":3,
"doc":" Deprecated in 0.4 and removed in 0.6. Use  eyekit.fixation.FixationSequence.discard_out_of_bounds_fixations() .",
"func":1
},
{
"ref":"eyekit.tools.snap_to_lines",
"url":3,
"doc":" Deprecated in 0.4 and removed in 0.6. Use  eyekit.fixation.FixationSequence.snap_to_lines() .",
"func":1
},
{
"ref":"eyekit.io",
"url":4,
"doc":"Functions for reading and writing data."
},
{
"ref":"eyekit.io.load",
"url":4,
"doc":"Read in a JSON file.  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock objects are automatically decoded and instantiated.",
"func":1
},
{
"ref":"eyekit.io.save",
"url":4,
"doc":"Write arbitrary data to a JSON file. If  compress is  True , the file is written in the most compact way; if  False , the file will be more human readable.  eyekit.fixation.FixationSequence and  eyekit.text.TextBlock objects are automatically encoded.",
"func":1
},
{
"ref":"eyekit.io.import_asc",
"url":4,
"doc":"Import data from an ASC file produced from an SR Research EyeLink device (you will first need to use SR Research's Edf2asc tool to convert your original EDF files to ASC). The importer will extract all trials from the ASC file, where a trial is defined as a sequence of fixations (EFIX lines) that occur inside a START\u2013END block. Optionally, the importer can extract user-defined variables and ms-by-ms samples. For example, if your ASC file contains messages like this:   MSG 4244101 trial_type practice MSG 4244101 passage_id 1 MSG 4244592 stim_onset   then you could extract the variables  \"trial_type\" and  \"passage_id\" . A variable is some string that is followed by a space; anything that follows this space is the variable's value. If the variable is not followed by a value (e.g.,  \"stim_onset\" above), then the time of the message is recorded as its value; this can be useful for recording the precise timing of an event. By default, the importer looks for variables that follow the END tag. However, if your variables are placed before the START tag, then set the  placement_of_variables argument to  \"before_start\" . If unsure, you should first inspect your ASC file to see what messages you wrote to the data stream and where they are placed. The importer will return a list of dictionaries, where each dictionary represents a single trial and contains the fixations along with any other extracted variables. For example:   [ { \"trial_type\": \"practice\", \"passage_id\": \"1\", \"stim_onset\": 4244592, \"fixations\": FixationSequence[ .] }, { \"trial_type\": \"test\", \"passage_id\": \"2\", \"stim_onset\": 4256311, \"fixations\": FixationSequence[ .] } ]  ",
"func":1
},
{
"ref":"eyekit.io.import_csv",
"url":4,
"doc":"Import data from a CSV file. By default, the importer expects the CSV file to contain the column headers,  x ,  y ,  start , and  end , but this can be customized by setting the relevant arguments to whatever column headers your CSV file contains. Each row of the CSV file is expected to represent a single fixation. If your CSV file contains data from multiple trials, you should also specify the column header of a trial identifier, so that the data can be segmented into trials. The importer will return a list of dictionaries, where each dictionary represents a single trial and contains the fixations along with the trial identifier (if specified). For example:   [ { \"trial_id\" : 1, \"fixations\" : FixationSequence[ .] }, { \"trial_id\" : 2, \"fixations\" : FixationSequence[ .] } ]  ",
"func":1
},
{
"ref":"eyekit.io.read",
"url":4,
"doc":" Deprecated in 0.4 and removed in 0.6. Use  eyekit.io.load() .",
"func":1
},
{
"ref":"eyekit.io.write",
"url":4,
"doc":" Deprecated in 0.4 and removed in 0.6. Use  eyekit.io.save() .",
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
"doc":"Set the default font face and/or size that will be used in figure captions and image annotations. This selection can be overridden on a per-image, per-figure, or per-annotation basis. If no font is set, Eyekit defaults to 8pt Arial.",
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
"doc":"Set the image's caption, which will be shown above the image if you place it inside a  Figure . If no font is set, the default font will be used (see  set_default_font ).",
"func":1
},
{
"ref":"eyekit.vis.Image.set_background_color",
"url":5,
"doc":"Set the background color of the image. By default the background color is white. If  color is set to  None , the background will be transparent.",
"func":1
},
{
"ref":"eyekit.vis.Image.set_background_image",
"url":5,
"doc":"Set a background image. The background image must be a PNG file that matches the dimensions of the  Image object. Note also that the resulting  Image object must be saved as a PNG (a background image cannot be combined with vector output).",
"func":1
},
{
"ref":"eyekit.vis.Image.set_crop_area",
"url":5,
"doc":"Crop the final image to a particular rectangular area of the screen.  rect should be a tuple of the form  (x, y, width, height) specifying the crop area (in screen coordinates) or a Box-like object, such as a TextBlock or InterestArea. If no crop area is set, then it defaults to the maximum extents of all TextBlocks drawn to the Image.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_text_block",
"url":5,
"doc":"Draw a  eyekit.text.TextBlock on the image.  color defaults to black if unspecified. If  mask_text is set to  True , the text will be displayed as a series of rectangles, which is useful if you want to deemphasize the linguistic content.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_fixation_sequence",
"url":5,
"doc":"Draw a  eyekit.fixation.FixationSequence on the image. Optionally, you can choose whether or not to display saccade lines and discarded fixations.  color ,  discard_color , and  saccade_color determine the colors of fixations, discarded fixations, and saccade lines respectively. If  number_fixations is  True , each fixation is superimposed with its index. By default, the radius of each fixation is calculated as  sqrt(duration/pi) , such that the area of each fixation will correspond to duration. If  fixation_radius is set to a number, all fixations will be rendered at a constant size.  stroke_width controls the thickness of saccade lines.  opacity controls the opacity of fixations. If you want to set the  color or  fixation_radius of each fixation independently, pass in a function that takes a fixation and returns a color. For example, to color code fixations that have the tag  special_fixation you could use a lambda function such as   color = lambda fxn: 'red' if fxn.has_tag('special_fixation') else 'black'   or to base the fixation size on pupil size, you could use:   fixation_radius = lambda fxn: (fxn.pupil_size / 3.14159)  0.5  ",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_heatmap",
"url":5,
"doc":"Draw a  eyekit.text.TextBlock on the image along with an associated distribution, which is represented in heatmap form. This is can be used to visualize the output from  eyekit.measure.duration_mass() .  color determines the color of the heatmap.",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_line",
"url":5,
"doc":"Draw an arbitrary line on the image from  start_xy to  end_xy .  stroke_width is set in points for vector output or pixels for PNG output. If  dashed is  True , the line will have a dashed style (or a custom dash pattern can be supplied, e.g.  dashed=(1,2,4,2) ).",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_circle",
"url":5,
"doc":"Draw an arbitrary circle on the image centered at  xy with some  radius .  stroke_width is set in points for vector output or pixels for PNG output. If  dashed is  True , the line will have a dashed style (or a custom dash pattern can be supplied, e.g.  dashed=(1,2,4,2) ). If no  color or  fill_color is provided,  color will default to black.  opacity controls the opacity of the circle's fill color and should be set between 0 (fully transparent) and 1 (fully opaque).",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_rectangle",
"url":5,
"doc":"Draw a rectangle on the image. You can pass in some Box-like object, such as an  eyekit.text.InterestArea , or you can pass a tuple of the form (x, y, width, height).  stroke_width is set in points for vector output or pixels for PNG output. If  dashed is  True , the line will have a dashed style (or a custom dash pattern can be supplied, e.g.  dashed=(1,2,4,2) ). If no  color or  fill_color is provided,  color will default to black.  opacity controls the opacity of the rectangle's fill color and should be set between 0 (fully transparent) and 1 (fully opaque).",
"func":1
},
{
"ref":"eyekit.vis.Image.draw_annotation",
"url":5,
"doc":"Draw arbitrary text on the image located at  xy . If no font is set, the default font will be used (see  set_default_font ).  font_size is set in points for vector output or pixels for PNG output.  anchor controls how the text is aligned relative to  xy and may be set to  left ,  center , or  right .",
"func":1
},
{
"ref":"eyekit.vis.Image.save",
"url":5,
"doc":"Save the image to some  output_path . Images can be saved as .pdf, .eps, .svg, or .png.  width only applies to the vector formats and determines the millimeter width of the output file; PNG images are saved at actual pixel size. If you set a crop margin, the image will be cropped to the size of the  eyekit.text.TextBlock plus the specified margin. Margins are specified in millimeters (PDF, EPS, SVG) or pixels (PNG). EPS does not support opacity effects.",
"func":1
},
{
"ref":"eyekit.vis.Image.render_frame",
"url":5,
"doc":"Render the image to PNG and return the bytestream. This can be used to build videos and animations.",
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
"ref":"eyekit.vis.Figure.set_border_style",
"url":5,
"doc":"Set the thickness and color of the image borders. By default, image border are 1pt black.",
"func":1
},
{
"ref":"eyekit.vis.Figure.set_enumeration",
"url":5,
"doc":"By default, each image caption is prefixed with a letter in parentheses:  (A) ,  (B) ,  (C) , etc. If you want to turn this off, call  Figure.set_enumeration(False) prior to saving. You can also specify a custom style using the    ,    , or    tags; for example  Figure.set_enumeration('[ ]') will result in  [1] ,  [2] ,  [3] etc. If no font is set, the default font will be used (see  set_default_font ).",
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
"doc":"Save the figure to some  output_path . Figures can be saved as .pdf, .eps, or .svg.  width determines the millimeter width of the output file. EPS does not support opacity effects.",
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
"ref":"eyekit.text.Character.serialize",
"url":6,
"doc":"",
"func":1
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
"doc":"Representation of an interest area \u2013 a portion of a  TextBlock object that is of potential interest. It is not usually necessary to create  InterestArea objects manually; they are created automatically when you extract areas of interest from a  TextBlock ."
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
"doc":"Bounding box padding on the top, bottom, left, and right edges"
},
{
"ref":"eyekit.text.InterestArea.set_padding",
"url":6,
"doc":"Set the amount of bounding box padding on the top, bottom, left and/or right edges.",
"func":1
},
{
"ref":"eyekit.text.InterestArea.adjust_padding",
"url":6,
"doc":"Adjust the current amount of bounding box padding on the top, bottom, left, and/or right edges. Positive values increase the padding, and negative values decrease the padding.",
"func":1
},
{
"ref":"eyekit.text.InterestArea.is_left_of",
"url":6,
"doc":"Returns True if the interest area is to the left of the fixation.",
"func":1
},
{
"ref":"eyekit.text.InterestArea.is_right_of",
"url":6,
"doc":"Returns True if the interest area is to the right of the fixation.",
"func":1
},
{
"ref":"eyekit.text.InterestArea.is_before",
"url":6,
"doc":"Returns True if the interest area is before the fixation. An interest area comes before a fixation if it is to the left of that fixation (or to the right in the case of right-to-left text).",
"func":1
},
{
"ref":"eyekit.text.InterestArea.is_after",
"url":6,
"doc":"Returns True if the interest area is after the fixation. An interest area comes after a fixation if it is to the right of that fixation (or to the left in the case of right-to-left text).",
"func":1
},
{
"ref":"eyekit.text.InterestArea.serialize",
"url":6,
"doc":"Returns the  InterestArea 's initialization arguments as a dictionary for serialization.",
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
"doc":"Representation of a piece of text, which may be a word, sentence, or entire multiline passage. Initialized with: -  text The line of text (string) or lines of text (list of strings). Optionally, these can be marked up with arbitrary interest areas; for example,  The quick brown fox jump[ed]{past-suffix} over the lazy dog . -  position XY-coordinates describing the position of the TextBlock on the screen. The x-coordinate should be either the left edge, right edge, or center point of the TextBlock, depending on how the  anchor argument has been set (see below). The y-coordinate should always correspond to the baseline of the first (or only) line of text. -  font_face Name of a font available on your system. The keywords  italic and/or  bold can also be included to select the desired style, e.g.,  Minion Pro bold italic . -  font_size Font size in pixels. At 72dpi, this is equivalent to the font size in points. To convert a font size from some other dpi, use  eyekit.tools.font_size_at_72dpi() . -  line_height Distance between lines of text in pixels. In general, for single line spacing, the line height is equal to the font size; for double line spacing, the line height is equal to 2 \u00d7 the font size, etc. By default, the line height is assumed to be the same as the font size (single line spacing). If  autopad is set to  True (see below), the line height also effectively determines the height of the bounding boxes around interest areas. -  align Alignment of the text within the TextBlock. Must be set to  left ,  center , or  right , and defaults to  left (unless  right_to_left is set to  True , in which case  align defaults to  right ). -  anchor Anchor point of the TextBlock. This determines the interpretation of the  position argument (see above). Must be set to  left ,  center , or  right , and defaults to the same as the  align argument. For example, if  position was set to the center of the screen, the  align and  anchor arguments would have the following effects:  -  right_to_left Set to  True if the text is in a right-to-left script (Arabic, Hebrew, Urdu, etc.). If you are working with the Arabic script, you should reshape the text prior to passing it into Eyekit by using, for example, the Arabic-reshaper package. -  alphabet A string of characters that are to be considered alphabetical, which determines what counts as a word. By default, this includes any character defined as a letter or number in unicode, plus the underscore character. However, if you need to modify Eyekit's default behavior, you can set a specific alphabet here. For example, if you wanted to treat apostrophes and hyphens as alphabetical, you might use  alphabet=\"A-Za-z'-\" . This would allow a sentence like \"Where's the orang-utan?\" to be treated as three words rather than five. -  autopad If  True (the default), padding is automatically added to  InterestArea bounding boxes to avoid horizontal gaps between words and vertical gaps between lines. Horizontal padding (half of the width of a space character) is added to the left and right edges, unless the character to the left or right of the interest area is alphabetical (e.g. if the interest area is word-internal). Vertical padding is added to the top and bottom edges, such that bounding box heights will be equal to the  line_height (see above).  "
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
"ref":"eyekit.text.TextBlock.interest_areas",
"url":6,
"doc":"Iterate over each interest area that was manually marked up in the raw text. To mark up an interest area, use brackets to mark the area itself followed immediately by braces to provide an ID (e.g.,  TextBlock(\"The quick [brown]{word_id} fox.\") ).",
"func":1
},
{
"ref":"eyekit.text.TextBlock.lines",
"url":6,
"doc":"Iterate over each line as an  InterestArea .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.words",
"url":6,
"doc":"Iterate over each word as an  InterestArea . Optionally, you can supply a regex pattern to pick out specific words. For example,  '(?i)the' gives you case-insensitive occurrences of the word  the or  '[a-z]+ing' gives you lower-case words ending with  -ing .  line_n limits the iteration to a specific line number. If  alphabetical_only is set to  True , a word is defined as a string of consecutive alphabetical characters (as defined by the TextBlock's  alphabet property); if  False , a word is defined as a string of consecutive non-whitespace characters.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.characters",
"url":6,
"doc":"Iterate over each character as an  InterestArea .  line_n limits the iteration to a specific line number. If  alphabetical_only is set to  True , the iterator will only yield alphabetical characters (as defined by the TextBlock's  alphabet property).",
"func":1
},
{
"ref":"eyekit.text.TextBlock.ngrams",
"url":6,
"doc":"Iterate over each ngram, for given n, as an  InterestArea .  line_n limits the iteration to a specific line number. If  alphabetical_only is set to  True , an ngram is defined as a string of consecutive alphabetical characters (as defined by the TextBlock's  alphabet property) of length  ngram_width .",
"func":1
},
{
"ref":"eyekit.text.TextBlock.zones",
"url":6,
"doc":" Deprecated in 0.4.1. Use  TextBlock.interest_areas() instead.",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_line",
"url":6,
"doc":" Deprecated in 0.6. ",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_word",
"url":6,
"doc":" Deprecated in 0.6. ",
"func":1
},
{
"ref":"eyekit.text.TextBlock.which_character",
"url":6,
"doc":" Deprecated in 0.6. ",
"func":1
},
{
"ref":"eyekit.text.TextBlock.serialize",
"url":6,
"doc":"Returns the  TextBlock 's initialization arguments as a dictionary for serialization.",
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