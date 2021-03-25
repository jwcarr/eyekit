<img src='https://jwcarr.github.io/eyekit/images/logo.png' width='300'>

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


**[Full documentation and a usage guide is available here](https://jwcarr.github.io/eyekit/)**
