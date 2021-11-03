import numpy as np
import os.path as op
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from gtts import gTTS
from numpy.random import randint, choice

from common_functions import *


class Shape:
	def __init__(self, fgcolor, bgcolor, id, action, speed, dir, data_path):
		self.fgcolor = fgcolor
		self.bgcolor = bgcolor
		self.id = id
		self.action = action
		self.og_speed = speed
		self.speed = speed_to_num(speed)
		self.dir = dir
		self.data_path = data_path

	def gen_sentence(self, shape):
		# eg: a blue triangle is moving right on a yellow background 
		first_article = 'An' if self.fgcolor.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'A'
		second_article = 'an' if self.bgcolor.name[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
		verb = gen_verb(self.action, self.dir)
		adverb = speed_to_adverb(self.og_speed)

		self.text = f'{first_article} {self.fgcolor.name} {shape.name} is ' + \
			f'{verb} {adverb} on {second_article} {self.bgcolor.name} background'
		return self.text

	def gen_audio(self):
		if self.text is None: self.gen_sentence()
		obj = gTTS(self.text)
		obj.save(op.join(self.data_path, 'audio', f'{self.id}.mp3'))
	
	def gen_video(self, func, duration):
		fig = plt.figure(figsize=(4,4), dpi=64)
		self.ax = fig.gca()
		plt.axis('off')
		fig.patch.set_facecolor(self.bgcolor.name)

		fps = 10; 
		anim = animation.FuncAnimation(fig, func, frames=int(duration*fps), blit=True)
		writer = animation.FFMpegWriter(fps=fps, bitrate=1800)
		anim.save(op.join(self.data_path, 'video', f'{self.id}.mp4'), writer=writer)
		plt.close(fig)


class Triangle(Shape):
	def __init__(self, points, fgcolor, bgcolor, id, action, speed, dir, data_path):
		super().__init__(fgcolor, bgcolor, id, action, speed, dir, data_path)
		self.patch = patches.Polygon(points, facecolor=fgcolor.name)

	def gen_sentence(self):
		return super().gen_sentence(SHAPE.triangle)

	def gen_audio(self):
		return super().gen_audio()

	def gen_video(self, duration):
		def shift(i):
			if i == 0: self.ax.add_patch(self.patch)
			points = self.patch.get_xy()
			if self.dir == DIR.right: points = [(pt[0] + self.speed, pt[1]) for pt in points] 
			elif self.dir == DIR.left: points = [(pt[0] - self.speed, pt[1]) for pt in points]
			elif self.dir == DIR.up: points = [(pt[0], pt[1] + self.speed) for pt in points]
			elif self.dir == DIR.down: points = [(pt[0], pt[1] - self.speed) for pt in points]
			else: perror('triangle shift func invalid dir')
			self.patch.set_xy(points)
			return [self.patch]

		def rotate(i):
			if i == 0: self.ax.add_patch(self.patch)
			points = self.patch.get_xy()
			centroid = tuple(np.mean(np.array(points), axis=0).tolist())
			new_points = []
			for (px, py) in points:
				nx, ny = rotateee((px, py), centroid, self.speed, self.dir)
				new_points.append([nx, ny])
			self.patch.set_xy(new_points)
			return [self.patch]

		if self.action == ACTION.shift: super().gen_video(shift, duration)
		elif self.action == ACTION.rotate: super().gen_video(rotate, duration)
		else: perror('gen video Triangle invalid action')	


class Circle(Shape):
	def __init__(self, points, fgcolor, bgcolor, id, action, speed, dir, data_path):
		super().__init__(fgcolor, bgcolor, id, action, speed, dir, data_path)
		x, y, r = points
		self.patch = patches.Circle((x, y), r, facecolor=fgcolor.name)

	def gen_sentence(self):
		return super().gen_sentence(SHAPE.circle)

	def gen_audio(self):
		return super().gen_audio()

	def gen_video(self, duration):
		def shift(i):
			if i == 0: self.ax.add_patch(self.patch)
			cx, cy = self.patch.get_center()
			if self.dir == DIR.right: cx += self.speed
			elif self.dir == DIR.left: cx -= self.speed
			elif self.dir == DIR.up: cy += self.speed
			elif self.dir == DIR.down: cy -= self.speed 
			else: perror(f'triangle shift func invalid dir: {self.dir}')
			self.patch.set_center((cx, cy))
			return [self.patch]

		def rotate(i):
			perror('rotate doesnt make sense for a circle')
			
		def grow(i):
			if i == 0: self.ax.add_patch(self.patch)
			self.patch.set_radius(self.patch.get_radius() + self.speed)
			return [self.patch]
		
		if self.action == ACTION.shift: super().gen_video(shift, duration)
		elif self.action == ACTION.grow: super().gen_video(grow, duration)
		else: perror(f'gen video circle invalid action: {action}')	

class Rectangle(Shape):
	def __init__(self, points, fgcolor, bgcolor, id, action, speed, dir, data_path):
		super().__init__(fgcolor, bgcolor, id, action, speed, dir, data_path)
		x0, y0, w, h, theta = points
		self.patch = patches.Rectangle((x0, y0), w, h, theta, facecolor=fgcolor.name) 

	def gen_sentence(self):
		return super().gen_sentence(SHAPE.rectangle)

	def gen_audio(self):
		return super().gen_audio()

	def gen_video(self, duration):
		def shift(i):
			if i == 0: self.ax.add_patch(self.patch)
			(x, y) = self.patch.get_xy()

			if self.dir == DIR.right: x += self.speed
			elif self.dir == DIR.left: x -= self.speed
			elif self.dir == DIR.up: y += self.speed
			elif self.dir == DIR.down: y -= self.speed 
			else: perror(f'triangle shift func invalid dir: {self.dir}')
			self.patch.set_xy((x, y))
			return [self.patch]

		def rotate(i):
			perror('rotate doesnt make sense for a circle')
			
		def grow(i):
			if i == 0: self.ax.add_patch(self.patch)
			self.patch.set_radius(self.patch.get_radius() + self.speed)
			return [self.patch]
		
		if self.action == ACTION.shift: super().gen_video(shift, duration)
		elif self.action == ACTION.grow: super().gen_video(shift, duration)
		else: perror(f'gen video circle invalid action: {action}')	