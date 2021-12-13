import soundfile as sf
import torch
from transformers import Wav2Vec2Model, Wav2Vec2Processor, Wav2Vec2ForCTC
import numpy as np
import os
import subprocess
from os import path
from tqdm import tqdm
import argparse

# `conda activate test`

def main():
	args = parse_args()

	# load model and tokenizer
	tokenizer, model = load_model()

	for f in tqdm(os.listdir(args.audio_path)):
		f_path = os.path.join(args.audio_path, f)
		f_wav_path = os.path.join(args.audio_path, f.replace('.mp3', '.wav'))
		out_feat_path = os.path.join(args.feat_path, f.replace('.mp3', '.npy'))

		if out_feat_path in os.listdir(args.feat_path):
			continue

		mp3_to_wav(f_path, f_wav_path)
		try:
			extract_wav2vec(tokenizer, model, f_wav_path, out_feat_path)
		except Exception as e:
			print(e)
			os.remove(f_wav_path)
			exit()
		os.remove(f_wav_path)


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--audio_path',  type=str, default='../data/audio',
		help='dir path of input audio files') 
	parser.add_argument('-f', '--feat_path',  type=str, default='../features/audio',
		help='dir path of output features') 
	return parser.parse_args()

def load_model():
	tokenizer = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
	model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
	print('Loaded model --------------------------------------------')
	return tokenizer, model

""" Step 1: Extracts audio at the native sampling rate into a separate wav file """
def mp3_to_wav(input_file, output_file):
	subprocess.call(['ffmpeg', '-y', '-i', input_file, output_file,
					 '-hide_banner', '-loglevel', 'error'])

def extract_wav2vec(tokenizer, model, input_file, output_file):
	data, samplerate = sf.read(input_file)
	if len(data.shape) > 1: 
		data = data[:,0] + data[:,1]
	data += np.zeros(1)

	input_values = tokenizer(data, return_tensors="pt").input_values

	input_values = input_values \
		.flatten()[:(input_values.shape[1] // 10) * 10].reshape(-1, 10)
	input_values = torch.mean(input_values, axis=1) \
		.reshape(1, input_values.shape[0])

	padder = torch.zeros(1, 320)
	input_values = torch.cat([input_values, padder], dim = 1)
	feats = model(input_values)
	feats = feats.last_hidden_state[0]
	size = feats.shape[0] // 5
	feats = feats.flatten()[:(5*size*768)]
	feats = feats.reshape(5, size, 768)
	feats = torch.mean(feats, axis=0).reshape(size, 768)
	feats = feats.detach().cpu().numpy()
	with open( output_file, 'wb') as f:
		np.save(f, feats)


if __name__ == '__main__':
	main()
