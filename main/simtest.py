import pygame
import ctypes
import os
import random
from sim.simobjects import *

def _text_objects(text, font):
  textSurface = font.render(text, True, BLACK)
  return textSurface, textSurface.get_rect()


def message_display(text):
  largeText = pygame.font.Font('freesansbold.ttf',115)
  TextSurf, TextRect = _text_objects(text, largeText)
  TextRect.center = ((DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
  screen.blit(TextSurf, TextRect)

  #time.sleep(1)

def rect(x, y, w, h, c):
  pygame.draw.rect(screen, c, [x, y, w, h])

user32 = ctypes.windll.user32
SCREEN_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
COMBINED_SCREEN_SIZE = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
SECOND_SCREEN_SIZE = (COMBINED_SCREEN_SIZE[0] - SCREEN_SIZE[0], COMBINED_SCREEN_SIZE[1])

ratio = 1.2
DISPLAY_WIDTH, DISPLAY_HEIGHT = tuple([int(i // ratio) for i in list(SECOND_SCREEN_SIZE)])

x, y = ((COMBINED_SCREEN_SIZE[0] + SCREEN_SIZE[0] - DISPLAY_WIDTH) // 2, (COMBINED_SCREEN_SIZE[1] - DISPLAY_HEIGHT) // 2)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

ROAD_WIDTH = 250

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

CENTER = (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)

pygame.init()

screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Simulation')
clock = pygame.time.Clock()
objects = pygame.sprite.Group()
carlist = []
for i in range(4):
  direction = random.choice(['up', 'down', 'right', 'left'])
  carlist.append(Car((random.randint(0,DISPLAY_WIDTH),random.randint(0,DISPLAY_HEIGHT)), direction, screen))
objects.add(*carlist)
objects.add(Intersection(CENTER, screen))

while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      quit()

    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        pygame.quit()
        quit()

  objects.update()
  
  screen.fill(BLUE)
  coords = ((DISPLAY_WIDTH - ROAD_WIDTH) // 2, (DISPLAY_HEIGHT - ROAD_WIDTH) // 2)
  #rect(coords[0], 0, ROAD_WIDTH, SCREEN_SIZE[1], BLACK)
  #rect(0, coords[1], SCREEN_SIZE[0], ROAD_WIDTH, BLACK)

  objects.draw(screen)

  pygame.display.update()


  clock.tick(60)

