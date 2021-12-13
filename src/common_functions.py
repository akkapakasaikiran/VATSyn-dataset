import numpy as np
from numpy.random import choice, uniform
import json
from enum import Enum
import os
import math
from gtts import gTTS

DIR = Enum('DIR', 'right left up down clock anticlock bigger smaller')
ACTION = Enum('ACTION', 'shift rotate roll jump grow circle')
SPEED = Enum('SPEED', 'slow fast')
SHAPE = Enum('SHAPE', 'triangle square pentagon hexagon circle ellipse')
FGCOLOR = Enum('FGCOLOR', 'red magenta orange brown green cyan blue black')
# FGCOLOR = Enum('FGCOLORS', 'red blue')
BGCOLOR = Enum('BGCOLOR', 'white pink beige aquamarine yellow')
# BGCOLOR = Enum('BGCOLORS', 'white pink')
TYPE = Enum('TYPE', 'disjoint overlap subset same')
ACCENT = Enum('ACCENT', 'au ca ind uk')

regular_polygons = [SHAPE.triangle, SHAPE.square, SHAPE.pentagon, SHAPE.hexagon]
circular_shapes = [SHAPE.circle, SHAPE.ellipse]

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


def setup_dirs(data_path, remove_old):
	""" Create dirs and files, deleting old ones if specified. """
	print(f'SETUP_DIRS: remove_old is set to {remove_old}')
	for x in ['audio', 'video']:
		path = os.path.join(data_path, x)
		if not os.path.isdir(path):  
			os.makedirs(path)
		elif remove_old:
			for f in os.listdir(path):
				os.remove(os.path.join(path, f))
	
	text_file = os.path.join(data_path, 'texts.csv')
	if not os.path.isfile(text_file):
		open(text_file, 'a').close()
	elif remove_old:
		os.remove(text_file)


def circle_sampler():
	""" Return the centre and radius of a circle. 

	Return a circle (x, y, r) in the unit grid which doesn't touch the 
	edge of the grid (least count = .05).
	Number of unique circles possible ~ 2*10*10 = 98.
	~ because possible radii values depend on location of centres
	"""

	xs = np.arange(0.3, 0.75, 0.05)  
	ys = np.arange(0.3, 0.75, 0.05) 
	x, y = choice(xs), choice(ys)

	# max_r is between 0.2 and 0.5 
	min_r, max_r = 0.1, min(min(x, 1.0 - x), min(y, 1.0 - y)) 
	rs = np.arange(min_r, max_r, 0.05)
	r = choice(rs) 	
	return [x, y, r]


def regular_polygon_sampler():
	""" Return a regular polygon (its centre, "radius", and orientation). """
	x, y, r = circle_sampler()
	theta = uniform(0, 2 * math.pi) # in radians

	return [x, y, r, theta]


def ellipse_sampler(circle=False):
	x, y, a = circle_sampler()
	b = uniform(a/3, 2*a/3)
	theta = uniform(0, 360) # somehow this is in degrees in plt

	if circle: return [x, y, a, a, 0]
	else: return [x, y, a, b, theta]


def get_numpts(shape):
	if shape == SHAPE.triangle: return 3
	elif shape == SHAPE.square: return 4
	elif shape == SHAPE.pentagon: return 5
	elif shape == SHAPE.hexagon: return 6
	else: perror(f'get numpts undefined shape: {shape}')


def jump_update(xy, t, speed):
	""" Model the motion of point xy thrown upwards. """

	g = 0.005 if speed == SPEED.slow else 0.01
	u = 0.05 if speed == SPEED.slow else 0.05

	# rebound from the ground
	t = (t-1) % int(2*u/g) + 1

	# s = ut + (1/2)at^2
	# ds = s(t) - s(t-1) = u - (1/2)g(2t-1)
	y = xy[1] + u - (1/2) * g * (2*t - 1)
	return (xy[0], y)


def accent_to_args(accent):
	if accent == ACCENT.au: return {'lang': 'en', 'tld': 'com.au'}
	if accent == ACCENT.ca: return {'lang': 'en', 'tld': 'ca'}
	if accent == ACCENT.ind: return {'lang': 'en', 'tld': 'co.in'}
	if accent == ACCENT.uk: return {'lang': 'en', 'tld': 'co.uk'}
	