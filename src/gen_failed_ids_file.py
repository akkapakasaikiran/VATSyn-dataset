import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data_path', type=str, default='./data/')
args = parser.parse_args()

metadata_file = os.path.join(args.data_path, 'metadata.json')
with open(metadata_file, 'r') as rf:
	metadata = json.load(rf)

failed_ids = []
for id in metadata['content']:
	f = os.path.join(args.data_path, 'audio', f'{id}.mp3')
	if not os.path.isfile(f):
		failed_ids.append(id)

failed_ids_file = os.path.join(args.data_path, 'failed_ids.json')
with open(failed_ids_file, 'w') as wf:
	json.dump(failed_ids, wf, indent=2)