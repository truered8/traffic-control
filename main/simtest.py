import pygame
import ctypes
import os
import random
from sim.simobjects import *

def reverse(flow):
  return 'horizontal' if flow == 'vertical' else 'vertical'

def _text_objects(text, font):
  textSurface = font.render(text, True, RED)
  return textSurface, textSurface.get_rect()

def message_display(text, center):
  largeText = pygame.font.Font('freesansbold.ttf',70)
  TextSurf, TextRect = _text_objects(text, largeText)
  TextRect.center = (center)
  screen.blit(TextSurf, TextRect)

user32 = ctypes.windll.user32
SCREEN_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
COMBINED_SCREEN_SIZE = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
SECOND_SCREEN_SIZE = (COMBINED_SCREEN_SIZE[0] - SCREEN_SIZE[0], COMBINED_SCREEN_SIZE[1])

DISPLAY_MODE = "single" if COMBINED_SCREEN_SIZE == SCREEN_SIZE else "dual"

ratio = 1.2
if DISPLAY_MODE == "dual":
  DISPLAY_WIDTH, DISPLAY_HEIGHT = tuple([int(i // ratio) for i in list(SECOND_SCREEN_SIZE)])
  x, y = ((COMBINED_SCREEN_SIZE[0] + SCREEN_SIZE[0] - DISPLAY_WIDTH) // 2, (COMBINED_SCREEN_SIZE[1] - DISPLAY_HEIGHT) // 2)
else:
  DISPLAY_WIDTH, DISPLAY_HEIGHT = tuple([int(i // ratio) for i in list(SCREEN_SIZE)])
  x, y = (SCREEN_SIZE[0] - DISPLAY_WIDTH) // 2, (SCREEN_SIZE[1] - DISPLAY_HEIGHT) // 2
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

LANE_WIDTH = int(DISPLAY_WIDTH * 0.1)
VERT_LANE_LENGTH = DISPLAY_HEIGHT // 2 - LANE_WIDTH
HORZ_LANE_LENGTH = (DISPLAY_WIDTH // 2 - LANE_WIDTH)

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

road = pygame.sprite.Group()
cars = pygame.sprite.Group()
intersection = Intersection(LANE_WIDTH * 2, LANE_WIDTH * 2, CENTER, screen)
road.add(intersection)

lanes = []
lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'down', ((DISPLAY_WIDTH - LANE_WIDTH) // 2, (DISPLAY_HEIGHT - VERT_LANE_LENGTH) // 2 - LANE_WIDTH), screen))
lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'up', ((DISPLAY_WIDTH + LANE_WIDTH) // 2, (DISPLAY_HEIGHT - VERT_LANE_LENGTH) // 2 - LANE_WIDTH), screen))
lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'left', ((DISPLAY_WIDTH + HORZ_LANE_LENGTH) // 2 + LANE_WIDTH, (DISPLAY_HEIGHT - LANE_WIDTH) // 2), screen))
lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'right', ((DISPLAY_WIDTH + HORZ_LANE_LENGTH) // 2 + LANE_WIDTH, (DISPLAY_HEIGHT + LANE_WIDTH) // 2), screen))

lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'up', ((DISPLAY_WIDTH + LANE_WIDTH) // 2, (DISPLAY_HEIGHT + VERT_LANE_LENGTH) // 2 + LANE_WIDTH), screen))
lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'down', ((DISPLAY_WIDTH - LANE_WIDTH) // 2, (DISPLAY_HEIGHT + VERT_LANE_LENGTH) // 2 + LANE_WIDTH), screen))
lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'right', ((DISPLAY_WIDTH // 2 - LANE_WIDTH) // 2, (DISPLAY_HEIGHT + LANE_WIDTH) // 2), screen))
lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'left', ((DISPLAY_WIDTH // 2 - LANE_WIDTH) // 2, (DISPLAY_HEIGHT - LANE_WIDTH) // 2), screen))
road.add(*lanes)

count = 0

SPEED = 20

l = random.choice([lanes[i] for i in [0, 2, 4, 6]])
car = Car((DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2), l.direction, SPEED, screen)
#cars.add(car)



while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      quit()

    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        pygame.quit()
        quit()
  
  if count % int(100 / SPEED) == 0:
    l = random.choice([lanes[i] for i in [0, 2, 4, 6]])
    cars.add(Car(l.start, l.direction, SPEED, screen))
  
  for c in cars.sprites():
    
    c.speed = SPEED
    
    for d in cars.sprites():
      if c.close(d) and Lane in [type(p) for p in c.position]:
        c.speed = 0
        d.speed = 0
    
    for d in road.sprites():
      if d.rect.contains(c):
        c.position.append(d)
    
    if c.rect.colliderect(intersection.rect):
      if not intersection.rect.contains(c.rect):
        if intersection.flow != c.orientation:
          c.speed = 0
        icars = []
        for d in cars.sprites():
          if intersection.rect.contains(d.rect):
            icars.append(d)
        if reverse(c.orientation) in [d.orientation for d in icars]:
          c.speed = 0
    
  if count % int(200 / SPEED) == 0:
    if not intersection.flow in [c.orientation for c in intersection.cars]:
      intersection.flow = reverse(intersection.flow)
  

  road.update(cars.sprites())
  cars.update()
  
  screen.fill(BLACK)

  road.draw(screen)
  cars.draw(screen)
  
  pygame.display.update()

  clock.tick(60)

  count += 1
  
