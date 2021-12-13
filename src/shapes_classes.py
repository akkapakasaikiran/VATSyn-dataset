import numpy as np
import os.path as op
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from gtts import gTTS
from numpy.random import randint, choice

from common_functions import *


class Shape:
	def __init__(self, type, fgcolor, bgcolor, id, 
				action, speed, dir, accent, data_path):
		self.fgcolor = fgcolor
		self.bgcolor = bgcolor
		self.id = id
		self.action = action
		self.og_speed = speed
		self.speed = speed_to_num(speed)
		self.dir = dir
		self.data_path = data_path
		self.type = type
		self.accent = accent

	def gen_sentences(self, shape):
		# eg: a blue triangle is moving right slowly on a yellow background 
		first_article = 'An' if self.fgcolor.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'A'
		second_article = 'an' if self.bgcolor.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
		verb = gen_verb(self.action, self.dir)
		adverb = speed_to_adverb(self.og_speed)

		if self.type == TYPE.disjoint:
			self.text_sentence = (f'{first_article} {self.fgcolor.name} '
				f'{shape.name} on '
				f'{second_article} {self.bgcolor.name} background.')
			self.audio_sentence = f'The shape is {verb} {adverb}.'
		
		elif self.type == TYPE.overlap:
			self.text_sentence = (f'{first_article} {self.fgcolor.name} ' 
				f'{shape.name} on '
				f'{second_article} {self.bgcolor.name} background.')
			self.audio_sentence = (f'{first_article} {shape.name} '
				f'is {verb} {adverb}.')
			
		elif self.type == TYPE.subset:
			self.text_sentence = (f'{first_article} {self.fgcolor.name} ' 
				f'{shape.name} on '
				f'{second_article} {self.bgcolor.name} background.')
			self.audio_sentence = (f'{first_article} {self.fgcolor.name} ' 
				f'{shape.name} is {verb} {adverb} on '
				f'{second_article} {self.bgcolor.name} background.')

		elif self.type == TYPE.same:
			self.text_sentence = (f'{first_article} {self.fgcolor.name} ' 
				f'{shape.name} is {verb} {adverb} on '
				f'{second_article} {self.bgcolor.name} background.')
			self.audio_sentence = self.text_sentence

		else: perror(f'gen sentences invalid type {self.type}')

		return self.text_sentence

	def gen_audio(self, filename):
		if self.audio_sentence is None: self.gen_sentences()
		try:
			obj = gTTS(self.audio_sentence, **accent_to_args(self.accent))
			obj.save(filename)
			return True
		except Exception as e:
			print(e)
			if os.path.isfile(filename):
				os.remove(filename)
			return False

	def gen_video(self, filename, func, duration):
		fig = plt.figure(figsize=(4,4), dpi=64)
		self.ax = fig.gca()
		plt.axis('off')
		fig.patch.set_facecolor(self.bgcolor.name)

		fps = 10; 
		anim = animation.FuncAnimation(fig, func, frames=int(duration*fps), blit=True)
		writer = animation.FFMpegWriter(fps=fps, bitrate=1800)
		anim.save(filename, writer=writer)
		plt.close(fig)
		return True


class RegularPolygon(Shape):
	def __init__(self, points, type, shape, fgcolor, bgcolor, 
				id, action, speed, dir, accent, data_path):
		super().__init__(type, fgcolor, bgcolor, id, action, speed, dir, accent, data_path)
		cx, cy, r, theta = points
		self.shape = shape
		self.patch = patches.RegularPolygon((cx, cy), get_numpts(shape),
				radius=r, orientation=theta, facecolor=fgcolor.name) 

	def gen_sentences(self):
		return super().gen_sentences(self.shape)

	def gen_audio(self, filename):
		return super().gen_audio(filename)

	def gen_video(self, filename, duration):
		def shift(i):
			if i == 0: self.ax.add_patch(self.patch)
			(x, y) = self.patch.xy

			if self.dir == DIR.right: x += self.speed
			elif self.dir == DIR.left: x -= self.speed
			elif self.dir == DIR.up: y += self.speed
			elif self.dir == DIR.down: y -= self.speed
			else: perror(f'triangle shift func invalid dir: {self.dir}')
			self.patch.xy = (x, y)
			return [self.patch]

		def rotate(i):
			if i == 0:
				self.ax.add_patch(self.patch)
				if self.dir == DIR.clock: self.speed *= -1
				
			self.patch.orientation += self.speed * np.pi
			return [self.patch]
			
		def grow(i):
			if i == 0:
				self.ax.add_patch(self.patch)
				if self.dir == DIR.smaller: self.speed *= -1
			
			if self.patch.radius >= 0.05:
				self.patch.radius += self.speed
			return [self.patch]
		
		def jump(i):
			if i == 0: self.ax.add_patch(self.patch)
			else: self.patch.xy = jump_update(self.patch.xy, i, self.og_speed)
			return [self.patch]
		
		if self.action == ACTION.shift: super().gen_video(filename, shift, duration)
		elif self.action == ACTION.rotate: super().gen_video(filename, rotate, duration)
		elif self.action == ACTION.grow: super().gen_video(filename, grow, duration)
		elif self.action == ACTION.jump: super().gen_video(filename, jump, duration)
		else: perror(f'gen video RegularPolygon invalid action: {action}')	


class Ellipse(Shape):
	def __init__(self, points, type, shape, fgcolor, bgcolor, 
				id, action, speed, dir, accent, data_path):
		super().__init__(type, fgcolor, bgcolor, id, action, speed, dir, accent, data_path)
		x, y, w, h, theta = points
		self.shape = shape
		self.patch = patches.Ellipse((x, y), w, h, angle=theta, facecolor=fgcolor.name)

	def gen_sentences(self):
		return super().gen_sentences(self.shape)

	def gen_audio(self, filename):
		return super().gen_audio(filename)

	def gen_video(self, filename, duration):
		def shift(i):
			if i == 0: self.ax.add_patch(self.patch)
			(cx, cy) = self.patch.get_center()
			if self.dir == DIR.right: cx += self.speed
			elif self.dir == DIR.left: cx -= self.speed
			elif self.dir == DIR.up: cy += self.speed
			elif self.dir == DIR.down: cy -= self.speed 
			else: perror(f'triangle shift func invalid dir: {self.dir}')
			self.patch.set_center((cx, cy))
			return [self.patch]

		def rotate(i):
			if i == 0:
				self.ax.add_patch(self.patch)
				if self.dir == DIR.clock: self.speed *= -1
			angle = self.patch.get_angle() 
			self.patch.set_angle(angle + self.speed * 360)
			return [self.patch]

		def grow(i):
			if i == 0:
				self.ax.add_patch(self.patch)
				if self.dir == DIR.smaller: self.speed *= -1

			w, h = self.patch.get_width(), self.patch.get_height()
			if max(w, h) >= 0.05:
				h += (h/w) * self.speed
				w += self.speed
				self.patch.set_width(w)
				self.patch.set_height(h)
			return [self.patch]

		def jump(i):
			if i == 0: self.ax.add_patch(self.patch)
			else:
				(cx, cy) = self.patch.get_center()
				(cx, cy) = jump_update((cx, cy), i, self.og_speed)
				self.patch.set_center((cx, cy))
			return [self.patch]
		
		if self.action == ACTION.shift: super().gen_video(filename, shift, duration)
		elif self.action == ACTION.rotate: super().gen_video(filename, rotate, duration)
		elif self.action == ACTION.grow: super().gen_video(filename, grow, duration)
		elif self.action == ACTION.jump: super().gen_video(filename, jump, duration)
		else: perror(f'gen video Ellipse invalid action: {action}')