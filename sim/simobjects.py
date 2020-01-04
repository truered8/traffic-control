'''
Created on Sep 27, 2018

@author: Babtu
'''
import pygame
import random
import time
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

img_folder = os.path.join(os.getcwd(), 'sim')

def rot_center(image, rect, angle):
	"""rotate an image while keeping its center"""
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = rot_image.get_rect(center=rect.center)
	return rot_image, rot_rect

class Car(pygame.sprite.Sprite):
		def close(self, c):
			if self.direction == c.direction:
				if self.direction == 'right':
					if abs(self.rect.midright[0] - c.rect.midleft[0]) < self.rect.h:
						return True
				elif self.direction == 'left':
					if abs(self.rect.midleft[0] - c.rect.midright[0]) < self.rect.h:
						return True
				elif self.direction == 'up':
					if abs(self.rect.midtop[1] - c.rect.midbottom[1]) < self.rect.h:
						return True
				else:
					if abs(self.rect.midbottom[1] - c.rect.midtop[1]) < self.rect.h:
						return True
			return False

		def __init__(self, center, direction, speed, goal, screen):
			pygame.sprite.Sprite.__init__(self)
			self.direction = direction
			self.screen = screen
			self.image = pygame.image.load(os.path.join(img_folder, r'redcar.png')).convert()
			self.image.set_colorkey(WHITE)
			self.rect = self.image.get_rect()
			self.rect.center = center
			self.speed = speed
			self.position = []
			self.orientation = 'horizontal' if direction in ['left', 'right'] else 'vertical'
			self.goal = goal
			self.turned = False
			self.angle = 0

			if self.direction == 'left':
				self.image = pygame.transform.rotate(self.image, 180)
				self.front = self.rect.midleft
				self.back = self.rect.midright
				self.angle += 180
			elif self.direction == 'down':
				self.image = pygame.transform.rotate(self.image, 270)
				self.front = self.rect.midbottom
				self.back = self.rect.midtop
				self.angle += 270
			elif self.direction == 'up':
				self.image = pygame.transform.rotate(self.image, 90)
				self.front = self.rect.midtop
				self.back = self.rect.midbottom
				self.angle += 90
			else:
				self.front = self.rect.midright
				self.back = self.rect.midleft


		def update(self, road):
			self.position = []
			for r in road:
				if r.rect.colliderect(self.rect):
					self.position.append(r)
			
			for c in self.groups()[0]:
				if self.close(c) and self != c and Lane in [type(p) for p in self.position]:
					self.speed = 0

			if self.direction == 'left':
				self.image = pygame.transform.rotate(self.image, 180 - self.angle)
				self.front = self.rect.midleft
				self.back = self.rect.midright
				self.angle = 180
				self.rect.x -= self.speed
			elif self.direction == 'down':
				self.image = pygame.transform.rotate(self.image, 270 - self.angle)
				self.front = self.rect.midbottom
				self.back = self.rect.midtop
				self.angle = 270
				self.rect.y += self.speed
			elif self.direction == 'up':
				self.image = pygame.transform.rotate(self.image, 90 - self.angle)
				self.front = self.rect.midtop
				self.back = self.rect.midbottom
				self.angle = 90
				self.rect.y -= self.speed
			else:
				self.image = pygame.transform.rotate(self.image, -self.angle)
				self.front = self.rect.midright
				self.back = self.rect.midleft
				self.angle = 0
				self.rect.x += self.speed

			# Check if the car has left the screen
			if not self.screen.get_rect().colliderect(self.rect):
				self.kill()
				del self	

	
class Middle(pygame.sprite.Sprite):
	''' Between the roads '''
	def __init__(self, width, height, center, screen):
		pygame.sprite.Sprite.__init__(self)
		self.screen = screen
		w, h = screen.get_size()
		self.image = pygame.image.load(os.path.join(img_folder,'Middle.png'))
		self.image = pygame.transform.scale(self.image, (width, height))
		self.image.set_colorkey(WHITE)
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.flow = 'horizontal'
		self.cars = []
		self.incars = []
		self.turns = [
			[int(self.rect.x + width * 0.25), int(self.rect.y + height * 0.25)],
			[int(self.rect.x + width * 0.75), int(self.rect.y + height * 0.25)],
			[int(self.rect.x + width * 0.25), int(self.rect.y + height * 0.75)],
			[int(self.rect.x + width * 0.75), int(self.rect.y + height * 0.75)]
		]
	
	def update(self, cars):
		self.cars = []
		self.incars = []
		for c in cars:
			if self in c.position:
				self.cars.append(c)
			if self.rect.contains(c):
				self.incars.append(c)
		

class Lane(pygame.sprite.Sprite):
	''' A single lane '''
	def __init__(self, width, height, direction, center, screen):
		pygame.sprite.Sprite.__init__(self)
		self.screen = screen
		w, h = screen.get_size()
		self.image = pygame.image.load(os.path.join(img_folder,'Lane.png'))
		self.image = pygame.transform.scale(self.image, (width, height))
		self.image.set_colorkey(WHITE)
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.direction = direction
		self.cars = []

		self.angle = 0
		if direction == 'right':
			self.image, self.rect = rot_center(self.image, self.rect, 90)
			self.start = self.rect.midleft
			self.end = self.rect.midright
		elif direction == 'left':
			self.image, self.rect = rot_center(self.image, self.rect, 90)
			self.start = self.rect.midright
			self.end = self.rect.midleft
		elif direction == 'down':
			self.start = self.rect.midtop
			self.end = self.rect.midbottom
		elif direction == 'up':
			self.start = self.rect.midbottom
			self.end = self.rect.midtop
	
	def update(self, cars):
		self.cars = []
		for c in cars:
			if self in c.position:
				self.cars.append(c)


	