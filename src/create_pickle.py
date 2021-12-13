import pickle
import os
import numpy as np
import json
import argparse
import os.path as op
import csv

def main():
	random_seed = 0
	np.random.seed(random_seed)

	args = get_args()

	text = dict()
	with open(args.text_file, newline='') as rf:
		reader = csv.reader(rf)
		for row in reader:
			text[row[0]] = row[1]

	ids = list(text.keys())
	ids_dict = train_test_split(ids)
	data_dict = {'train': [], 'test': []}

	for split, ids in ids_dict.items():
		cnt = 0
		for id in ids:
			r = {'id': id, 'caption': text[id]}
			a_fpath = op.join(args.a_path, id + '.npy')
			v_fpath = op.join(args.v_path, id + '.npy')
			if op.exists(a_fpath) and op.exists(v_fpath):
				r['audio'] = np.load(a_fpath)
				r['2d'] = np.load(v_fpath)
				cnt += 1
				data_dict[split].append(r)
		print(f'{split}: total: {len(ids)} success: {cnt}')

	for split, data in data_dict.items():
		pickle_file = op.join(args.o_path, f'{split}_data.pickle') 
		with open(pickle_file, 'wb') as wf:
			pickle.dump(data, wf)


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--text_file', type=str, default='data/text/texts.csv', 
		help='text file path')
	parser.add_argument('-v', '--v_path', type=str, default='features/video/', 
		help='video features dir path')
	parser.add_argument('-a', '--a_path', type=str, default='features/audio/', 
		help='audio features dir path')
	parser.add_argument('-o', '--o_path', type=str, default='pickle_files/', 
		help='output pickle files dir path')
	return parser.parse_args()


def train_test_split(ids):
	np.random.shuffle(ids)
	num_train = int(0.8 * len(ids))
	num_test = len(ids) - num_train 
	train_ids = ids[:num_train]
	test_ids = ids[num_train:]

	return {'train': train_ids, 'test': test_ids}


if __name__ == '__main__':
	main()