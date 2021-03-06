import pygame
import ctypes
import os
import random
from sim.simobjects import *
import datetime

def main(control, sim_length, frequency, dmin, dmax):
	global screen, clock, reverse, lanes, intersection, cars, middle, total_wait, count, \
	LANE_WIDTH, SPEED, SCREEN_SIZE

	def _text_objects(text, font):
		textSurface = font.render(text, True, BLUE)
		return textSurface, textSurface.get_rect()

	def message_display(text, center):
		largeText = pygame.font.Font('freesansbold.ttf',70)
		TextSurf, TextRect = _text_objects(text, largeText)
		TextRect.center = (center)
		screen.blit(TextSurf, TextRect)

	def approx(p1, p2):
		if abs(p1[0] - p2[0]) < SPEED // 2:
			if abs(p1[1] - p2[1]) < SPEED // 2:
				return True
		return False

	def rotate(direction, turn):
		return {
			'right': {
				'up': 'right',
				'right': 'down',
				'down': 'left',
				'left': 'up'
			},
			'left': {
				'up': 'left',
				'left': 'down',
				'down': 'right',
				'right': 'up'
			}
		} [turn] [direction]
		

	def get_turn(lane, turn):
		return {
			0: {
				'right': 0,
				'left': 2
			},
			2: {
				'right': 1,
				'left': 0
			},
			4: {
				'right': 3,
				'left': 1
			},
			6: {
				'right': 2,
				'left': 3
			}
		} [lane] [turn]

	i = random.choice(range(1))
	l = lanes[i]
	car = Car(l.start, l.direction, SPEED, random.choice(['straight','right','left']), screen)
	car.start = i
	cars.add(car)
	#total_wait = 0


	for count in range(sim_length):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

			elif event.type == pygame.KEYDOWN:
								if event.key == pygame.K_q:
										pygame.quit()
										quit()
								elif event.key == 27:
										pygame.quit()
										quit()

		'''
		i = 6
		l = lanes[i]
		g = random.choice(['straight', 'left', 'right'])
		c = Car(l.start, l.direction, SPEED, g, screen)
		c.start = i
		cars.add(c)
		'''
		
		if count % int(200 / SPEED) == 0:
			i = random.choice(range(0, 7, 2))
			l = lanes[i]
			g = random.choice(['straight', 'left', 'right'])
			c = Car(l.start, l.direction, SPEED, g, screen)
			c.start = i
			cars.add(c)
		
		for c in cars.sprites():
			
			c.speed = SPEED
			
			if c.rect.colliderect(middle.rect):
				if not middle.rect.contains(c.rect):
					if middle.flow != c.orientation and c.rect.colliderect(lanes[c.start]):
						c.speed = 0
					if reverse(c.orientation) in [d.orientation for d in middle.incars] and c.rect.colliderect(lanes[c.start]):
						c.speed = 0
				else:
					if c.goal != 'straight':
						t = middle.turns[get_turn(c.start, c.goal)]
						if approx(c.rect.center, t) and not c.turned:
							c.direction = rotate(c.direction, c.goal)
							c.turned = True

			if c.speed == 0:
				total_wait += 1

		control(frequency, dmin, dmax)


		intersection.update(cars.sprites())
		cars.update(intersection.sprites())
		
		screen.fill(YELLOW)

		intersection.draw(screen)
		cars.draw(screen)

		
		pygame.display.update()

		clock.tick(180)

		count += 1

''' Get information on the screen the program is running on '''
def get_screen_metrics():
	user32 = ctypes.windll.user32
	SCREEN_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
	COMBINED_SCREEN_SIZE = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
	SECOND_SCREEN_SIZE = (COMBINED_SCREEN_SIZE[0] - SCREEN_SIZE[0], COMBINED_SCREEN_SIZE[1])
	DISPLAY_MODE = "single" if COMBINED_SCREEN_SIZE == SCREEN_SIZE else "dual"
	RATIO = 1.0
	if DISPLAY_MODE == "dual":
		DISPLAY_WIDTH, DISPLAY_HEIGHT = tuple([int(i // RATIO) for i in list(SECOND_SCREEN_SIZE)])
		x, y = ((COMBINED_SCREEN_SIZE[0] + SCREEN_SIZE[0] - DISPLAY_WIDTH) // 2, (COMBINED_SCREEN_SIZE[1] - DISPLAY_HEIGHT) // 2)
	else:
		DISPLAY_WIDTH, DISPLAY_HEIGHT = tuple([int(i // RATIO) for i in list(SCREEN_SIZE)])
		x, y = (SCREEN_SIZE[0] - DISPLAY_WIDTH) // 2, (SCREEN_SIZE[1] - DISPLAY_HEIGHT) // 2
	return x, y, DISPLAY_WIDTH, DISPLAY_HEIGHT

if __name__ == '__main__':

	def timed(frequency, *args):
		''' Simple interval-based traffic control '''
		if count % frequency == 0:
			middle.flow = reverse(middle.flow)

	def custom(frequency, *args):
		''' Traffic control in which intersection with more cars gets the green light '''
		hlanes = [lanes[2], lanes[6]]
		vlanes = [lanes[0], lanes[4]]
		if count % frequency == 0:
			middle.flow = 'horizontal' if sum([len(l.cars) for l in hlanes]) > sum([len(l.cars) for l in vlanes]) else 'vertical'
		
	def actuated(frequency, dmin, dmax):
		''' Actuated traffic control '''
		global duration
		def is_empty(lanes):
			for l in lanes:
				for c in l.cars:
					position = [type(p) for p in c.position]
					if Lane in position and Middle in position:
						return False
			return True
		hlanes = [lanes[2], lanes[6]]
		vlanes = [lanes[0], lanes[4]]
		if count % frequency == 0:
			switch = is_empty(hlanes) if middle.flow == 'horizontal' else is_empty(vlanes)
			if switch and duration > dmin and duration < dmax:
				middle.flow = reverse(middle.flow)
				duration = 0
		else:
			duration += 1

	reverse = lambda flow: {'horizontal': 'vertical'}.get(flow, 'horizontal')

	x, y, DISPLAY_WIDTH, DISPLAY_HEIGHT = get_screen_metrics()
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
	
	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	YELLOW = (255, 255, 0)

	LANE_WIDTH = int(DISPLAY_WIDTH * 0.1)
	VERT_LANE_LENGTH = DISPLAY_HEIGHT // 2 - LANE_WIDTH
	HORZ_LANE_LENGTH = (DISPLAY_WIDTH // 2 - LANE_WIDTH)

	CENTER = (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)


	SPEED = 8
	TRIALS = 15
	SIM_LENGTH = 500

	controls = [actuated, custom]
	frequencies = [50, 100, 200, 300, 400, 500]

	if not os.path.exists('logs'):
		os.makedirs('logs')

	# Iterate through each combination of the chosen control methods and frequencies
	for control in controls:
		for frequency in frequencies:

			count = 0
			total_wait = 0
			last_wait = 0
			duration = 0
			pygame.init()
			screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
			pygame.display.set_caption('Simulation')

			with open(f'logs/{control.__name__}-{frequency}.txt', 'w') as file:
				file.write(f'\nTime: {datetime.datetime.now()}')

			for i in range(TRIALS):

				clock = pygame.time.Clock()
				intersection = pygame.sprite.Group()
				cars = pygame.sprite.Group()
				middle = Middle(LANE_WIDTH * 2, LANE_WIDTH * 2, CENTER, screen)
				intersection.add(middle)
				lanes = []
				lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'down', ((DISPLAY_WIDTH - LANE_WIDTH) // 2, (DISPLAY_HEIGHT - VERT_LANE_LENGTH) // 2 - LANE_WIDTH), screen))
				lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'up', ((DISPLAY_WIDTH + LANE_WIDTH) // 2, (DISPLAY_HEIGHT - VERT_LANE_LENGTH) // 2 - LANE_WIDTH), screen))
				lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'left', ((DISPLAY_WIDTH + HORZ_LANE_LENGTH) // 2 + LANE_WIDTH, (DISPLAY_HEIGHT - LANE_WIDTH) // 2), screen))
				lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'right', ((DISPLAY_WIDTH + HORZ_LANE_LENGTH) // 2 + LANE_WIDTH, (DISPLAY_HEIGHT + LANE_WIDTH) // 2), screen))
				lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'up', ((DISPLAY_WIDTH + LANE_WIDTH) // 2, (DISPLAY_HEIGHT + VERT_LANE_LENGTH) // 2 + LANE_WIDTH), screen))
				lanes.append(Lane(LANE_WIDTH, VERT_LANE_LENGTH, 'down', ((DISPLAY_WIDTH - LANE_WIDTH) // 2, (DISPLAY_HEIGHT + VERT_LANE_LENGTH) // 2 + LANE_WIDTH), screen))
				lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'right', ((DISPLAY_WIDTH // 2 - LANE_WIDTH) // 2, (DISPLAY_HEIGHT + LANE_WIDTH) // 2), screen))
				lanes.append(Lane(LANE_WIDTH, HORZ_LANE_LENGTH, 'left', ((DISPLAY_WIDTH // 2 - LANE_WIDTH) // 2, (DISPLAY_HEIGHT - LANE_WIDTH) // 2), screen))
				intersection.add(*lanes)
				
				main(control, SIM_LENGTH, frequency, 40, 100)

				with open(f'logs/control-{control.__name__}-frequency-{frequency}.txt', 'a') as file:
					file.write(f'\nWait Time: {total_wait - last_wait}')
				last_wait = total_wait

			with open(f'logs/control-{control.__name__}-frequency-{frequency}.txt', 'a') as file:
				file.write(f'\nAverage frames waited: {total_wait // TRIALS}')
			pygame.quit()

	quit()