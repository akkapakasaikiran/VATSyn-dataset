import numpy as np
from numpy.random import choice
import json
from enum import Enum
import os
import math
from gtts import gTTS

DIR = Enum('DIR', 'right left up down clock anticlock bigger smaller')
ACTION = Enum('ACTION', 'shift rotate roll jump grow circle')
SPEED = Enum('SPEED', 'slow fast')
SHAPE = Enum('SHAPE', 'triangle circle')
FGCOLOR = Enum('FGCOLOR', 'red magenta orange brown green cyan blue black')
# FGCOLOR = Enum('FGCOLORS', 'red blue')
BGCOLOR = Enum('BGCOLOR', 'white pink beige aquamarine yellow')
# BGCOLOR = Enum('BGCOLORS', 'white pink')

def perror(msg):
	""" Print error and exit. """
	print(f'Error: {msg}')
	exit(1)


def speed_to_num(speed):
	""" Convert speed enum to a number. """
	if speed == SPEED.slow: return 5e-3
	elif speed == SPEED.fast: return 1e-2
	else: perror(f'speed_to_num invalid speed: {speed}')


def speed_to_adverb(speed):
	""" Convert speed enum to an adverb """
	if speed == SPEED.slow: return 'slowly'
	elif speed == SPEED.fast: return 'quickly'
	else: perror(f'speed_to_adverb invalid speed: {speed}')


def gen_verb(action, dir=None):
	""" Generate verb from action. """
	if action == ACTION.shift:
		if dir == DIR.right: return 'moving right'
		elif dir == DIR.left: return 'moving left'
		elif dir == DIR.up: return 'moving up'
		elif dir == DIR.down: return 'moving down'
		else: perror(f'gen verb shift invalid dir: {dir}')
	elif action == ACTION.rotate: 
		if dir == DIR.clock: return 'rotating clockwise'
		elif dir == DIR.anticlock: return 'rotating anticlockwise'
		else: perror(f'gen verb rotate invalid dir: {dir}')
	elif action == ACTION.roll: return 'rolling'
	elif action == ACTION.grow: 
		if dir == DIR.bigger: return 'growing in size'
		elif dir == DIR.smaller: return 'shrinking in size'
	elif action == ACTION.jump: return 'jumping up and down'
	elif action == ACTION.circle: return 'going around in a circle'
	else: perror(f'gen verb invalid action: {action}')


def setup_dirs(data_path):
	""" Create audio and video dirs, if they exist, delete old files. """
	for x in ['audio', 'video']:
		path = os.path.join(data_path, x)
		if os.path.isdir(path):  
			for f in os.listdir(path): os.remove(os.path.join(path, f))
		else: os.makedirs(path)


def save_text(path, ids, texts):
	""" Save ids and sentences into path (json file). """
	data = dict(zip(ids, texts))
	with open(path, 'w') as wf:
		json.dump(data, wf, indent=2)


def rotateee(pt1, pt2, angle, dir=DIR.anticlock):
	""" Rotate pt1 about pt2 and return rotated point. """
	ox, oy = pt2 	# "origin"
	dx, dy = pt1[0] - ox, pt1[1] - oy
	if dir == DIR.clock: angle = - angle 
	c, s = math.cos(angle), math.sin(angle)

	nx = ox + dx * c - dy * s
	ny = oy + dx * s + dy * c 

	return nx, ny


# 2 | 1
# -------
# 3 | 4
def sample_point(quadrant_num):
	"""	Return a point (x,y) from a specified quadrant in the unit grid. """
	if quadrant_num not in [1, 2, 3, 4]:
		print("error: quadrant number should be between 1 and 4")
		exit()

	if quadrant_num in [1, 4]: 
		xs = np.arange(0.6, 1.0, 0.1)
	else:
		xs = np.arange(0.1, 0.5, 0.1)

	if quadrant_num in [1, 2]:
		ys = np.arange(0.6, 1.0, 0.1)
	else:
		ys = np.arange(0.1, 0.5, 0.1)

	return choice(xs), choice(ys)


def triangle_sampler():
	""" Return three points, all lying in different quadrants. 

	Return a triangle [(x1,y1), (x2,y2), (x3,y3)] in the unit grid 
	such that no two points lie in the same quadrant (least count = .1).
	Number of unique triangles possible = 4*16*16*16 = 16384
	"""

	quadrants = choice(range(1, 5), 3, replace=False) # three quadrants
	pts = [sample_point(quad) for quad in quadrants]
	return pts


def circle_sampler():
	""" Return the centre and radius of a circle. 

	Return a circle (x, y, r) in the unit grid which doesn't touch the 
	edge of the grid (least count = .05).
	Number of unique circles possible ~ 2*10*10 = 98.
	~ because possible radii values depend on location of centres
	"""

	xs = np.arange(0.3, 0.7, 0.05)  
	ys = np.arange(0.3, 0.7, 0.05) 
	x, y = choice(xs), choice(ys)

	# between 0.25 and 0.45 
	max_r = min(min(x, 1.0 - x), min(y, 1.0 - y)) - .05 
	min_r = 0.2
	rs = np.arange(min_r, max_r, 0.05)
	r = choice(rs) 	
	return [x, y, r]