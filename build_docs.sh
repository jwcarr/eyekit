#!/bin/bash

pdoc -f --html --output-dir docs eyekit
mv docs/eyekit/* docs/
rm -fr docs/eyekit/
