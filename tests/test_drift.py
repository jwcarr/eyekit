import numpy as np
from eyekit import _drift

fixation_XY = np.array([[395, 150], [479, 152], [619, 155], [670, 168], [726, 142], [912, 161], [1086, 176], [401, 212], [513, 230], [594, 228], [725, 229], [806, 231], [884, 216], [1000, 234], [1133, 225], [379, 270], [472, 273], [645, 310], [713, 289], [788, 288], [948, 286], [1072, 307], [378, 360], [496, 357], [634, 338]], dtype=int)
line_Y = np.array([155, 219, 283, 347], dtype=int)
word_XY = np.array([[400, 155], [496, 155], [592, 155], [672, 155], [744, 155], [896, 155], [1080, 155], [392, 219], [496, 219], [592, 219], [704, 219], [808, 219], [896, 219], [1000, 219], [1120, 219], [384, 283], [496, 283], [640, 283], [720, 283], [824, 283], [952, 283], [1072, 283], [400, 347], [504, 347], [616, 347]], dtype=int)

correct_Y = np.array([155, 155, 155, 155, 155, 155, 155, 219, 219, 219, 219, 219, 219, 219, 219, 283, 283, 283, 283, 283, 283, 283, 347, 347, 347], dtype=int)

output = _drift.chain(fixation_XY.copy(), line_Y)
for y, correct_y in zip(output[:, 1], correct_Y):
	assert y == correct_y

output = _drift.cluster(fixation_XY.copy(), line_Y)
for y, correct_y in zip(output[:, 1], correct_Y):
	assert y == correct_y

output = _drift.merge(fixation_XY.copy(), line_Y)
for y, correct_y in zip(output[:, 1], correct_Y):
	assert y == correct_y

output = _drift.regress(fixation_XY.copy(), line_Y)
for y, correct_y in zip(output[:, 1], correct_Y):
	assert y == correct_y

output = _drift.segment(fixation_XY.copy(), line_Y)
for y, correct_y in zip(output[:, 1], correct_Y):
	assert y == correct_y

output = _drift.split(fixation_XY.copy(), line_Y)
for y, correct_y in zip(output[:, 1], correct_Y):
	assert y == correct_y

output = _drift.warp(fixation_XY.copy(), word_XY)
for y, correct_y in zip(output[:, 1], correct_Y):
	assert y == correct_y
