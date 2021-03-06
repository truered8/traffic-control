import ctypes
import os
import sys
import random
import pygame
import subprocess
import platform
import pickle
import numpy as np
<<<<<<< HEAD
from argparse import ArgumentParser
#from dqn import DQNAgent
from sim.simobjects import *

def main(control, sim_length, frequency, dmin, dmax, render):
	global screen, clock, reverse, lanes, intersection, cars, intersection, total_wait, count, trial_reward, \
=======
from sim.simobjects import *

def main(control, sim_length, frequency, dmin, dmax, render):
	global screen, clock, reverse, lanes, intersection, cars, intersection, total_wait, count, \
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
	LANE_WIDTH, SPEED, SCREEN_SIZE

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

	def get_reward():
			result = 0
			for l in lanes:
				for c in l.cars:
					if c.speed == 0:
						result += 1
			return (1 / (result + 1e-4))

	i = 6
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

		if count % int(200 / SPEED) == 0:
			i = random.choice(range(0, 7, 2))
			l = lanes[i]
			g = random.choice(['straight', 'right'])
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

		control(frequency, dmin, dmax, total_wait)
<<<<<<< HEAD
		trial_reward += get_reward()
=======

>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

		intersection.update(cars.sprites())
		cars.update(intersection.sprites())
		
		screen.fill(YELLOW)

		intersection.draw(screen)
		cars.draw(screen)
		
		if render: pygame.display.update()

		clock.tick(180)

		count += 1

''' Get information on the screen the program is running on '''
def get_screen_metrics():
	if platform.system() == 'Windows':
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
	elif platform.system() == 'Linux':
		output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
		resolution = [int(i) for i in output.split()[0].split(b'x')]
		return resolution[0] // 2, 0, resolution[0], resolution[1]
	return 683, 0, 1366, 768

if __name__ == '__main__':

	def timed(frequency, *args):
		''' Simple interval-based traffic control '''
		if count % frequency == 0:
			middle.flow = reverse(middle.flow)

	def custom(frequency, *args):
		''' Traffic control in which road with more cars gets the green light '''
		hlanes = [lanes[2], lanes[6]]
		vlanes = [lanes[0], lanes[4]]
		if count % frequency == 0:
			middle.flow = 'horizontal' if sum([len(l.cars) for l in hlanes]) > sum([len(l.cars) for l in vlanes]) else 'vertical'
		
	def actuated(frequency, dmin, dmax, *args):
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
			if (switch and duration > dmin and duration < dmax) or (duration > dmax):
				middle.flow = reverse(middle.flow)
				duration = 0
		else:
			duration += 1

	def q_control(frequency, *args):
		''' Traffic control using pretrained q table '''
		if count % frequency != 0: return
		def get_cars():
			hcars = 0
			vcars = 0
			for l in hlanes:
				hcars += len(l.cars)
			for l in vlanes:
				vcars += len(l.cars)
<<<<<<< HEAD
			return (min(hcars, 7), min(vcars, 7))
			return (hcars, vcars)
=======
<<<<<<< HEAD
			return (min(hcars, 7), min(vcars, 7))
=======
			return (hcars, vcars)
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

		hlanes = [lanes[2], lanes[6]]
		vlanes = [lanes[0], lanes[4]]
			
		state = get_cars()
		action = np.argmax(table[state])
		middle.flow = ACTIONS[action]

<<<<<<< HEAD
	def deep_q_control(frequency, *args):
		''' Traffic control using deep q learning '''
		global action, old_state, episode_reward
		if count % frequency != 0: return
		def get_stat():
			hcars = 0
			vcars = 0
			for l in hlanes:
				hcars += len(l.cars)
			for l in vlanes:
				vcars += len(l.cars)
			return np.array([min(hcars, 15), min(vcars, 15)])

		def get_state():
			cars = [len(l.cars) for l in [*hlanes, *vlanes]]
			return np.array([min(c, 8) for c in cars])
		
		hlanes = [lanes[2], lanes[6]]
		vlanes = [lanes[0], lanes[4]]

		action = np.argmax(agent.get_qs(get_state()))
		middle.flow = ACTIONS[action]


	ap = ArgumentParser()
	ap.add_argument('-t', '--table', type=str, help='Path to the pretrained q table')
	ap.add_argument('-m', '--model', type=str, help='Path to the pretrained neural network')
	args = vars(ap.parse_args())

	if args.get('table', None):
		with open(args['table'], 'rb') as table_file:
			table = pickle.load(table_file)

	if args.get('model', None):
		agent = DQNAgent('test')
		agent.load(args['model'])
=======
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

	reverse = lambda flow: {'horizontal': 'vertical'}.get(flow, 'horizontal')

	x, y, DISPLAY_WIDTH, DISPLAY_HEIGHT = 640, 640, 1280, 1280#get_screen_metrics()
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

<<<<<<< HEAD
	SPEED = 8
	TRIALS = 2
	SIM_LENGTH = 300

	ACTIONS = ['horizontal', 'vertical']
	MAX_SIZE = 15

	RENDER = True

	controls = [timed, custom]
	frequencies = [88]
=======
	SPEED = 16
<<<<<<< HEAD
	TRIALS = 20
=======
	TRIALS = 5
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
	SIM_LENGTH = 500

	ACTIONS = ['horizontal', 'vertical']

	RENDER = True

	with open(sys.argv[1], 'rb') as table_file:
		table = pickle.load(table_file)


	controls = [actuated, custom, q_control]
	frequencies = [30]
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

	pygame.init()
	screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
	pygame.display.set_caption('Simulation')
<<<<<<< HEAD

	
=======
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

	# Iterate through each combination of the chosen control methods and frequencies
	for control in controls:
		rewards = []
		waits = []
		for frequency in frequencies:

			count = 0
<<<<<<< HEAD
=======
			total_wait = 0
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
			duration = 0

			for i in range(TRIALS):

				trial_reward = 0
				total_wait = 0

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
			
				main(control, SIM_LENGTH, frequency, 40, 150, RENDER)
<<<<<<< HEAD
				rewards.append(trial_reward)
				waits.append(total_wait)

			print(f'Stats for {control.__name__}:')
			print(f'Min: {min(rewards)}')
			print(f'Avg: {sum(rewards)/TRIALS}')
			print(f'Max: {max(rewards)}')
			print(f'Wait: {sum(waits)/TRIALS}')

=======

			print(f'\nAverage frames waited for {control.__name__}: {total_wait // TRIALS}')
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
			

	pygame.quit()
	quit()