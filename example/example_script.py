"""

Eyekit example script. Load in some fixation data and the associated texts.
For each trial, produce a pdf showing the relevant text overlaid with the
fixation sequence.

"""

import eyekit

# Read in fixation data
data = eyekit.io.load("example_data.json")

# Read in texts
texts = eyekit.io.load("example_texts.json")

# For each trial in the dataset
for trial_id, trial in data.items():

    # Get the fixation sequence for that trial
    seq = trial["fixations"]

    # Get the passage ID of that trial
    passage_id = trial["passage_id"]

    # Get the relevant text with that passage ID
    txt = texts[passage_id]["text"]

    # Create an image with a screen size of 1920x1080
    img = eyekit.vis.Image(1920, 1080)

    # Draw the text
    img.draw_text_block(txt)

    # Draw the fixation sequence
    img.draw_fixation_sequence(seq)

    # Save the image as a PDF
    img.save(f"{trial_id}.pdf")
