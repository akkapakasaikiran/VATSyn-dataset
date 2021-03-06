import numpy as np
from numpy.random import uniform
from itertools import product
import json
import argparse
import os.path as op

from common_functions import *
from shapes_classes import *

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data_path', type=str, default='./data/')
parser.add_argument('-t', '--metadata_type', type=str, default='disjoint',
					choices=['disjoint', 'overlap', 'subset', 'same'])
args = parser.parse_args()

random_seed = 42
np.random.seed(random_seed)
START_ID = int(1e5)
DURATION_SMALL, DURATION_BIG = 2.0, 5.0

metadata = dict()
metadata['seed'] = random_seed
metadata['type'] = args.metadata_type
metadata['content'] = dict()

cnt = 0
for shape, fgcolor, bgcolor, speed in product(SHAPE, FGCOLOR, BGCOLOR, SPEED):		
	if shape == SHAPE.circle:
		actions = [ACTION.shift, ACTION.grow, ACTION.jump]
	else:
		actions = [ACTION.rotate, ACTION.shift, ACTION.grow, ACTION.jump]

	for action in actions:
		if action == ACTION.shift: dirs = [DIR.right, DIR.left, DIR.up, DIR.down]		
		elif action == ACTION.rotate: dirs = [DIR.clock, DIR.anticlock]
		elif action == ACTION.grow: dirs = [DIR.bigger, DIR.smaller]
		elif action == ACTION.jump: dirs = [DIR.up]
		else: perror('gen metadata triangle invalid action')

		for dir in dirs: 
			if shape in regular_polygons:
				points = regular_polygon_sampler()
			elif shape in circular_shapes:
				points = ellipse_sampler(shape == SHAPE.circle)
			else: perror(f'gen metadata invalid shape: {shape}')

			duration = uniform(DURATION_SMALL, DURATION_BIG)
			accent = choice(ACCENT) # for TTS
			d = {'shape': shape.name, 'points': points, 'fgcolor': fgcolor.name,
				'bgcolor': bgcolor.name, 'action': action.name, 'speed': speed.name,
				'dir': dir.name, 'duration': duration, 'accent': accent.name}

			metadata['content'][START_ID + cnt] = d
			cnt += 1

with open(op.join(args.data_path, f'metadata.json'), 'w') as wf:
	json.dump(metadata, wf, indent=2)
