from tqdm import tqdm
import argparse
import os.path as op 

from shapes_classes import *
from common_functions import *

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data_path', type=str, default='./data/')
args = parser.parse_args()

setup_dirs(args.data_path)
texts, ids = [], []

with open(op.join(args.data_path, 'metadata.json'), 'r') as rf:
	metadata = json.load(rf)

for id, data in tqdm(metadata['content'].items()):
	ids.append(id)
	shape = SHAPE[data['shape']]
	fgcolor = FGCOLOR[data['fgcolor']]
	bgcolor = BGCOLOR[data['bgcolor']]
	action = ACTION[data['action']]
	speed = SPEED[data['speed']]
	dir = DIR[data['dir']]

	if shape == SHAPE.circle:
		s = Circle(points=data['points'], fgcolor=fgcolor, 
				bgcolor=bgcolor, action=action, dir=dir, 
				speed=speed, id=id, data_path=args.data_path)
	elif shape == SHAPE.triangle:
		s = Triangle(points=data['points'], fgcolor=fgcolor, 
				bgcolor=bgcolor, action=action, dir=dir, 
				speed=speed, id=id, data_path=args.data_path)
	else: perror(f'main.py invalid shape: {shape}')

	s.gen_video(duration=data['duration'])
	text = s.gen_sentence()
	texts.append(text)
	s.gen_audio()

save_text(op.join(args.data_path, 'texts.json'), ids, texts)
