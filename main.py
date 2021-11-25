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

type = TYPE[metadata['type']] 

for id, data in tqdm(metadata['content'].items()):
	ids.append(id)
	shape = SHAPE[data['shape']]
	fgcolor = FGCOLOR[data['fgcolor']]
	bgcolor = BGCOLOR[data['bgcolor']]
	action = ACTION[data['action']]
	speed = SPEED[data['speed']]
	dir = DIR[data['dir']]
	accent = ACCENT[data['accent']]

	params = {'points': data['points'], 'type': type, 'shape': shape, 
			'fgcolor': fgcolor, 'bgcolor': bgcolor, 'action': action, 'dir': dir, 
			'speed': speed, 'id': id, 'accent': accent, 'data_path': args.data_path}

	if shape in regular_polygons: s = RegularPolygon(**params)
	elif shape in circular_shapes: s = Ellipse(**params)
	else: perror(f'main.py invalid shape: {shape}')

	s.gen_video(duration=data['duration'])
	text = s.gen_sentences()
	texts.append(text)
	s.gen_audio()
	print(id, ':', text)

save_text(op.join(args.data_path, 'texts.json'), ids, texts)
