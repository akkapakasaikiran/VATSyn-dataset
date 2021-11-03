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
args = parser.parse_args()

random_seed = 3
np.random.seed(random_seed)
START_ID = int(1e5)
DURATION_SMALL, DURATION_BIG = 2.0, 5.0

metadata = dict()
metadata['seed'] = random_seed
metadata['content'] = dict()

cnt = 0
for shape, fgcolor, bgcolor, speed in product(SHAPE, FGCOLOR, BGCOLOR, SPEED):
	""" 2*8*5*2 = 160 """
	if shape == SHAPE.triangle: points = triangle_sampler()
	elif shape == SHAPE.circle: points = circle_sampler()
	else: perror(f'gen metadata invalid shape: {shape}')
	
	""" 160*(2+4) = 960 """
	actions = []
	if shape == SHAPE.triangle: actions = [ACTION.rotate, ACTION.shift]
	elif shape == SHAPE.circle: actions = [ACTION.shift, ACTION.grow]
	
	for action in actions:
		if action == ACTION.shift: dirs = [DIR.right, DIR.left, DIR.up, DIR.down]		
		elif action == ACTION.rotate: dirs = [DIR.clock, DIR.anticlock]
		elif action == ACTION.grow: dirs = [DIR.bigger, DIR.smaller]
		else: perror('gen metadata triangle invalid action')

		for dir in dirs: 
			duration = uniform(DURATION_SMALL, DURATION_BIG)
			d = {'shape': shape.name, 'points': points, 'fgcolor': fgcolor.name,
				'bgcolor': bgcolor.name, 'action': action.name,
				'speed': speed.name, 'dir': dir.name, 'duration': duration}

			# if 

			metadata['content'][START_ID + cnt] = d
			cnt += 1

with open(op.join(args.data_path, 'metadata.json'), 'w') as wf:
	json.dump(metadata, wf, indent=2)
