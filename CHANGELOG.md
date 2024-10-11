Eyekit 0.6.1 - 2024-10-11
=========================

General
-------

- Support for Python 3.13.


Eyekit 0.6 - 2024-10-02
=======================

Added
-----

- `InterestArea`s can now be serialized and written to JSON.

Changed
-------

- `TextBlock.zones()` is now `TextBlock.interest_areas()`.

Deprecated
----------

- `measure.landing_distances()` has been deprecated, since it does not return a single value and therefore does not play well with `measure.interest_area_report()`.
- `TextBlock.which_line()`, `TextBlock.which_word()`, and `TextBlock.which_character()` have been deprecated, since there is no obvious use case for finding an interest area given a fixation.

Removed
-------

- `io.read()`
- `io.write()`
- `tools.discard_short_fixations()`
- `tools.discard_out_of_bounds_fixations()`
- `tools.snap_to_lines()`
- `TextBlock.word_centers()`
- `TextBlock.which_zone()`


Eyekit 0.5.3 - 2024-07-15
=========================

Added
-----

- Added `interest_area_report()` convenience function, which allows you to create interest area reports for multiple measures across many trials.


Eyekit 0.5.2 - 2024-06-06
=========================

General
-------

- Modernized installation process with pyproject.toml.


Eyekit 0.5.1 - 2023-11-04
=========================

Added
-----

- Added `create_stimuli()` function for creating experimental PNG stimulus images.
- `segment()` method added to `FixationSequence` for segmenting fixation sequence at given time intervals (e.g. page turns or subtitle timings).


Eyekit 0.5 - 2022-10-08
=======================

General
-------

- Eyekit is now licensed under the terms of the GPLv3.
- Dropped support for Python 3.7

Added
-----

- Ability to extract individual samples from an ASC file in addition to the fixations by setting `import_samples=True`.
- Ability to place a background image in an `Image` object, which is useful if you want to render participant fixations over a screenshot of the experimental screen.
- Added `render_frame()` method to `Image` for building videos and animations.
- `discard_long_fixations()` method added to `FixationSequence`.
- `shift_x()`, `shift_y()`, and `shift_time()` methods added to `Fixation` and `FixationSequence`.

Changed
-------

- The fixation tagging system now allows arbitrary key-value pairs.
- The `snap_to_lines()` method now returns two measures of data quality, delta and kappa.


Eyekit 0.4.3 - 2022-06-29
=========================

Added
-----

- Option to specify the character encoding when importing ASC or CSV files.


Eyekit 0.4.2 - 2022-05-02
=========================

Added
-----

- Added new line assignment method "slice" based on the algorithm described by [Glandorf & Schroeder (2021)](https://doi.org/10.1016/j.procs.2021.09.069).


Eyekit 0.4.1 - 2022-03-24
=========================

General
-------

- The concept of "zones" will be removed in the future due to the confusing terminology. It will still be possible to mark up IAs in the raw text, but these will no longer be called zones.
- Updated code style to Black v22.

Added
-----

- Added `set_crop_area()` to `Image`, which allows you to specify a particular area of the image to crop (rather than using the limits of any TextBlocks placed on the image).
- The opacity can now be set on line segments drawn using the `draw_line()` method of `Image`.

Changed
-------

- When manually setting the start or end time of a `Fixation`, an error is raised if the start time is after the end time or the end time is before the start time.

Deprecated
----------

- The `TextBlock.word_centers()` method has been deprecated, since this is of limited use. Instead, use something like `[word.center for word in txt.words()]` to accomplish the same thing.
- The `TextBlock.zones()` and `TextBlock.which_zone()` methods have been deprecated.


Eyekit 0.4 - 2021-11-14
=======================

General
-------

- Changed development status to beta. Going forward, the aim will be to minimize non backwards compatible changes to the API.
- Bump required Python version to 3.7 and make Numpy an optional dependency.
- Many function and method arguments are now explicitly keyword-only.

Added
-----

- Support for storing pupil size data and importing this information from ASC files.
- Added basic fixation tagging scheme, allowing you to tag fixations with arbitrary identifiers.
- Added `shift_start_time_to_zero` method to `FixationSequence` – shift all timings so that the first fixation starts at time 0.
- The color and radius of a fixation can be set for each fixation independently based on user-defined functions.
- The color of saccade lines can be set separately from the color of fixations.
- Option to set the opacity of fixations.

Changed
-------

- When importing from ASC, 1ms is added to the end time for consistency with SR Research's calculation of duration.
- Fixations are now serialized as dictionaries, which will permit greater flexibility in the future.

Deprecated
----------

- The functions `io.read` and `io.write` have been deprecated in favor of `io.load` and `io.save`.
- The functions `tools.snap_to_lines`, `tools.discard_short_fixations`, and `tools.discard_out_of_bounds_fixations` have been deprecated; these are now methods of `FixationSequence`.

Removed
-------

- `Image.draw_sequence_comparison` has been removed since this can now be accomplished with `Image.draw_fixation_sequence`.


Eyekit 0.3.14 - 2021-10-10
==========================

- Fix bug when attempting to draw empty fixation sequence
- If a variable in an ASC file has no value, treat the time as its value

    
Eyekit 0.3.13 - 2021-06-23
==========================

- Added wisdom of the crowd feature to `snap_to_lines()`: apply many line assignment algorithms and, for each fixation, pick the majority line assignment
- Added `first_of_many_duration()` measurement function
- Customizable stroke width in `draw_fixation_sequence()`
- Option to customize fixation radii by passing in a callable in which you declare the relationship between duration and radius

    
Eyekit 0.3.12 - 2021-04-09
==========================

- `analysis` module renamed to `measure` to better reflect its purpose
- Measurement functions only return a dictionary of results if given a collection of `InterestArea`s
- `initial_landing_distance()` now more consistent with behavior of `initial_landing_position()`
- Renamed `go_past_time()` to `go_past_duration()`
- Renamed `set_lettering()` to `set_enumeration()`
- New options to change to the style of panel enumerations
- Added `mask_text` option to `draw_text_block()`
- Renamed `draw_text_block_heatmap()` to `draw_heatmap()`
- Option to iterate over words without ignoring non-alphabetical chars
- Updated user guide, tidied up code, and added clearer error messages

    
Eyekit 0.3.11 - 2021-03-28
==========================

- Arguments to `draw_` functions are more consistent
- Changed how opacity is applied to strokes vs. fills
- Added `go_past_time()`
- Added `second_pass_duration()`
- Renamed `number_of_regressions()` to `number_of_regressions_in()`
- Added relative position methods to `InterestArea`: `is_left_of()`,` is_right_of()`, `is_before()`, `is_after()`

    
Eyekit 0.3.10 - 2021-03-04
==========================

- Implemented `number_fixations` option in `draw_fixation_sequence()`
- Customizable opacity levels in rects, circles, and lines
- Customizable dash patterns in rects, circles, and lines
- Round joins and caps in rects and lines
- Text alignment in annotations

    
Eyekit 0.3.9 - 2021-03-03
=========================

- Customizable panel borders in `Figure`
- `Fixation` now has an `index` property
- Improvements to `iter_pairs()`
- `number_of_regressions()` analysis function
- Customizable vertical padding around `InterestArea`
- Fixed some visualization bugs

    
Eyekit 0.3.8 - 2021-02-27
=========================

- `Image.draw_rectangle()` can now directly take an `InterestArea` object
- `number_of_fixations()` analysis function
- New `discard()` method
- Methods for manually setting and adjusting `InterestArea` padding
- Discarded fixations are now more clearly marked as such in JSON output
- Updated guide with more examples

    
Eyekit 0.3.7 - 2021-02-24
=========================

- Fixed bug causing non-left-aligned texts to be displayed incorrectly

    
Eyekit 0.3.6 - 2021-02-23
=========================

- `initial_landing_x()` renamed to `initial_landing_distance()` and is now measured from interest area onset (rather the bbox edge)
- Padding is now applied to all interest areas (not just those created with the `words()` method). Padding can be turned off using the new `autopad` TextBlock parameter.
- Interest areas are now cached on creation, so that they can be easily found by ID
- Better regex pattern matching in `words()` method

    
Eyekit 0.3.5 - 2021-01-14
=========================

- Better bidirectional text support
- Fixed some minor visualization bugs

    
Eyekit 0.3.4 - 2021-01-10
=========================

- Support for right-to-left languages and Arabic reshaping

    
Eyekit 0.3.3 - 2021-01-09
=========================

- `TextBlock`s can now be right or center aligned
- Other minor tweaks 

    
Eyekit 0.3.2 - 2021-01-06
=========================

- New `iter_pairs()` method for iterating over pairs of consecutive fixations
- More general definition of alphabetical characters by default for better language support

    
Eyekit 0.3.1 - 2020-12-29
=========================

- Added `fixation_radius` option to `draw_fixation_sequence()`: allows for manual specification of fixation radii
- Efficiency improvements

    
Eyekit 0.3 - 2020-12-28
=======================

- Eyekit 0.3 makes a core change to the way fixation data is stored. Rather than store fixations as `(x, y, duration)`, fixations are now stored as `(x, y, start_time, end_time)`, from which duration can be computed on the fly. The advantage of this is that FixationSequences can now be synchronized with other experimental events or imaging data.

    
Eyekit 0.2.14 - 2020-12-28
==========================

- Added a new `import_csv()` function
- Simplified the `import_asc()` function

    
Eyekit 0.2.13 - 2020-12-26
==========================

- New `import_asc()` function which is more resilient to different kinds of input file
- By default, `write()` does not compress the JSON

    
Eyekit 0.2.12 - 2020-10-27
==========================

- File paths in `io` and `vis` are explicitly converted to string, allowing support for e.g. pathlib paths
- Removed test code from wheel

    
Eyekit 0.2.11 - 2020-10-24
==========================

- Minor changes to the `cluster`, `merge`, and `regress` correction algorithms

    
Eyekit 0.2.10 - 2020-10-22
==========================

- Added `discard_short_fixations` tool
- `snap_to_lines` now modifies `FixationSequence` in place, like other tools
- Added `purge` method to `FixationSequence`
- Removed `fixation_sequence_distance` function – no clear use case

    
Eyekit 0.2.9 - 2020-10-21
=========================

- Added new correction method "stretch"
- Clearer parameter names for the merge and regress correction methods
- Option to make image background transparent
- Properly pass figure scale down to images for correct stroke widths in figures

    
Eyekit 0.2.8 - 2020-10-11
=========================

- Added `set_default_font()` to `vis` module
- Entire codebase converted to black style

    
Eyekit 0.2.7 - 2020-10-10
=========================

- Added new `Booklet` class for making multipage visualizations
- Renamed `image` module to `vis` and removed the `Image` and `Figure` classes from the top-level
- Fixed the `discard_out_of_bounds_fixations()` tool
- Figure crop margins now set with method rather than at save time

    
Eyekit 0.2.6 - 2020-10-06
=========================

- Added gaze duration analysis function

    
Eyekit 0.2.5 - 2020-09-29
=========================

- Caption and lettering fonts can now be set independently

    
Eyekit 0.2.4 - 2020-09-29
=========================

- Added support for bold and italic font styles

    
Eyekit 0.2.3 - 2020-09-27
=========================

- Cropping now supports multiple TextBlocks in the same image

    
Eyekit 0.2.2 - 2020-09-27
=========================

- Default alphabet is now maximalist rather than minimalist. In most cases, it should not be necessary to specify an alphabet manually.

    
Eyekit 0.2.1 - 2020-09-26
=========================

- More built-in alphabets, which are specified directly rather than through the ALPHABETS global
- The crop margin is now set in the save() methods
- Default figure padding in millimeters rather than points
- Fixed small bugs and documentation typos

    
Eyekit 0.2 - 2020-09-25
=======================

- Overhauled the image module so that it works directly with Cairo without using SVG as an intermediary
- Added ability to set TextBlock defaults
- Added Figure class for creating figures, combinations of images
- Changed some method names for consistency
- Dropped pillow as a dependency
- Added support for HTML color names

    
Eyekit 0.1.17 - 2020-09-21
==========================

- Image `label` property is now called `caption`, and `combine_images()` is now `make_figure()`
- Output raster figures at 300dpi with correct font sizes
- Bug fixes

    
Eyekit 0.1.16 - 2020-09-20
==========================

- Support for JPEG and TIFF output
- Bug fixes

    
Eyekit 0.1.15 - 2020-09-19
==========================

- Better text rendering in images (especially kerning)
- Added `font_size_at_72dpi()`
- Miscellaneous tidying up

    
Eyekit 0.1.14 - 2020-09-19
==========================

- Improvements to proportional font support and more consistent text block positioning regardless of line height
- Added `align_to_screenshot()` tool
- Added some default alphabets for several European languages
- Various extra visualization options

    
Eyekit 0.1.13 - 2020-09-16
==========================

- Duration mass can now be computed on proportional fonts
- Additional options for filtering interest areas by line number
- Fixed the `discard_out_of_bounds_fixations()` function
- Marked up interest areas are now called "zones" to distinguish them from other types of interest area
- Faster font loading

    
Eyekit 0.1.12 - 2020-09-15
==========================

- Added support for setting a default alphabet and changing the alphabet on a per TextBlock basis.
- Added ability to filter words using a regex pattern.

    
Eyekit 0.1.11 - 2020-09-14
==========================

- Added support for proportional fonts!
- Reworked the serialization of Eyekit objects into and out of JSON.

    
Eyekit 0.1.10 - 2020-09-12
==========================

- Eyekit is now listed on PyPI.

    
Eyekit 0.1.9 - 2020-09-11
=========================

- Eyekit now has a logo!
- Renamed `correct_vertical_drift()` to `snap_to_lines()`, removed the `attach` correction method, and added some `initial_landing_` analysis functions.

    
Eyekit 0.1.8 - 2020-09-11
=========================

- Added a lot of documentation and some initial analysis functions. Also some general tidying of the package namespace and some renaming, e.g. Text -> TextBlock.

    
Eyekit 0.1.7 - 2020-09-10
=========================

- General tiding up and initial documentation


Eyekit 0.1.6 - 2020-09-09
=========================

- Initial release
