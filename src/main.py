from tqdm import tqdm
import argparse
import os.path as op 
import csv

from shapes_classes import *
from common_functions import *

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data_path', type=str, default='./data/')
parser.add_argument('-r', '--remove_old', action='store_true',
	help='remove all old audio, video, and text files')
args = parser.parse_args()

setup_dirs(args.data_path, args.remove_old)

metadata_file = op.join(args.data_path, 'metadata.json')
texts_file = op.join(args.data_path, 'texts.csv')

with open(metadata_file, 'r') as rf:
	metadata = json.load(rf)

type = TYPE[metadata['type']] 
failed_ids = []
for id, data in tqdm(metadata['content'].items()):
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

	video_file = os.path.join(args.data_path, 'video', f'{id}.mp4')
	audio_file = os.path.join(args.data_path, 'audio', f'{id}.mp3')
	
	text = s.gen_sentences()
	save_text = True
	try:
		if not os.path.isfile(video_file):
			v = s.gen_video(video_file, duration=data['duration'])
			save_text = save_text and v
		if not os.path.isfile(audio_file):
			a = s.gen_audio(audio_file)
			save_text = save_text and a

	except Exception as e:
		print(e)
		continue
		
	if save_text:
		with open(texts_file, 'a', newline='') as wf:
			csv.writer(wf).writerow([id, text])

