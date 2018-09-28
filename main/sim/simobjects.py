'''
Created on Sep 27, 2018

@author: Babtu
'''
import pygame
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

img_folder = r'C:\Users\Babtu\eclipse-workspace\TrafficControl\main\sim'

class Car(pygame.sprite.Sprite):

    def __init__(self, center, direction, screen):
      pygame.sprite.Sprite.__init__(self)
      self.direction = direction
      self.screen = screen
      self.image = pygame.image.load(os.path.join(img_folder, r'redcar.png')).convert()
      self.image.set_colorkey(WHITE)
      self.rect = self.image.get_rect()
      self.rect.center = center

      if self.direction == 'left':
        self.image = pygame.transform.rotate(self.image, 180)
      elif self.direction == 'down':
        self.image = pygame.transform.rotate(self.image, 270)
      elif self.direction == 'up':
        self.image = pygame.transform.rotate(self.image, 90)

    def update(self):
      if self.direction == 'right':
        self.rect.x += 5
      elif self.direction == 'left':
        self.rect.x -= 5
      elif self.direction == 'down':
        self.rect.y += 5
      elif self.direction == 'up':
        self.rect.y -= 5
      '''
      if self.direction == 'right':
        self.rect.x += 5
        if self.rect.left > self.screen.get_size()[0] - self.rect.w:
          self.direction = 'left'
      elif self.direction == 'left':
        self.rect.x -= 5
        if self.rect.right < self.rect.w:
          self.direction = 'right'
      elif self.direction == 'down':
        self.rect.y += 5
        if self.rect.top > self.screen.get_size()[1] - self.rect.h:
          self.direction = 'up'
      elif self.direction == 'up':
        self.rect.y -= 5
        if self.rect.bottom < self.rect.h:
          self.direction = 'down'
      '''
  
class Intersection(pygame.sprite.Sprite):
  def __init__(self, center, screen):
    pygame.sprite.Sprite.__init__(self)
    self.screen = screen
    w, h = screen.get_size()
    self.image = pygame.Surface((int(h * 0.2), int(h * 0.2)))#pygame.image.load(os.path.join(img_folder, r'redcar.png')).convert()
    self.image.fill(BLACK)
    self.image.set_colorkey(WHITE)
    self.rect = self.image.get_rect()
    self.rect.center = center

class Road(pygame.sprite.Sprite):
  def __init__(self, center, screen):
    pygame.sprite.Sprite.__init__(self)
    self.screen = screen
    w, h = screen.get_size()
    self.image = pygame.Surface((int(h * 0.2), int(h * 0.2)))#pygame.image.load(os.path.join(img_folder, r'redcar.png')).convert()
    self.image.fill(BLACK)
    self.image.set_colorkey(WHITE)
    self.rect = self.image.get_rect()
    self.rect.center = center
