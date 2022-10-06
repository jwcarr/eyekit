<img src='https://jwcarr.github.io/eyekit/images/logo.png' width='300'>

Eyekit is a Python package for analyzing reading behavior using eyetracking data. Eyekit aims to be entirely independent of any particular eyetracker hardware, experiment software, or data formats. It has an object-oriented style that defines three core objects – the TextBlock, InterestArea, and FixationSequence – that you bring into contact with a bit of coding.


Is Eyekit the Right Tool for Me?
--------------------------------

- You want to analyze which parts of a text someone is looking at and for how long.

- You need convenient tools for extracting areas of interest from texts, such as specific words, phrases, or letter combinations.

- You want to calculate common reading measures, such as gaze duration or initial landing position.

- You need support for arbitrary fonts, multiline passages, right-to-left text, or non-alphabetical scripts.

- You want the flexibility to define custom reading measures and to build your own reproducible processing pipeline.

- You would like tools for dealing with noise and calibration issues, and for discarding fixations according to your own criteria.

- You want to share your data in an open format and produce publication-ready vector graphics.


Installation
------------

Eyekit may be installed using `pip`:

```shell
$ pip install eyekit
```

Eyekit is compatible with Python 3.8+. Its main dependency is the graphics library [Cairo](https://cairographics.org), which you might also need to install if it's not already on your system. Many Linux distributions have Cairo built in. On a Mac, it can be installed using [Homebrew](https://brew.sh): `brew install cairo`. On Windows, it can be installed using [Anaconda](https://anaconda.org/anaconda/cairo): `conda install -c anaconda cairo`.


**[Full documentation and a usage guide is available here](https://jwcarr.github.io/eyekit/)**
