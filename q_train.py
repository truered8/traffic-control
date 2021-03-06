import ctypes
import os
import random
import pygame
import subprocess
import platform
import pickle
import numpy as np
from tqdm import tqdm
from sim.simobjects import *

def main(control, sim_length, frequency, dmin, dmax, render):
	global screen, clock, reverse, lanes, intersection, cars, intersection, total_wait, count, \
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

		control(frequency, dmin, dmax, total_wait)


		intersection.update(cars.sprites())
		cars.update(intersection.sprites())
		
		if render: screen.fill(YELLOW)

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

<<<<<<< HEAD
=======
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

>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
	def q_control(frequency, *args):
		''' Traffic control using q learning '''
		global action, old_state
		if count % frequency != 0: return
		def get_state_1():
			hcars = 0
			vcars = 0
			for l in hlanes:
				hcars += len(l.cars)
			for l in vlanes:
				vcars += len(l.cars)
			return (min(hcars, 15), min(vcars, 15))
		def get_state_2():
			state = [0, 0, 0, 0]
			for i, l in enumerate([lanes[0], lanes[2], lanes[4], lanes[6]]):
				state[i] += len(l.cars) if len(l.cars) < 7 else 7
			return tuple(state)
		def get_reward():
			result = 0
			for l in lanes:
				for c in l.cars:
					if c.speed == 0:
						result += 1
			return (1 / (result + 1e-4))
		
		hlanes = [lanes[2], lanes[6]]
		vlanes = [lanes[0], lanes[4]]
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
		get_state = get_state_1
		
		if count > 1:
			current_q = table_1[old_state + (action,)]
			new_state = get_state()
			max_future_q = np.max(table_1[new_state])
			reward = get_reward()
			new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
			table_1[old_state + (action,)] = new_q
		old_state = get_state()
		if np.random.random() > epsilon:
			action = np.argmax(table_1[old_state])
<<<<<<< HEAD
=======
=======
		get_state = get_state_2
		
		if count > 1:
			current_q = table_2[old_state + (action,)]
			new_state = get_state()
			max_future_q = np.max(table_2[new_state])
			reward = get_reward()
			new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
			table_2[old_state + (action,)] = new_q
		old_state = get_state()
		if np.random.random() > epsilon:
			action = np.argmax(table_2[old_state])
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
		else:
			action = np.random.randint(0, 2)
		middle.flow = ACTIONS[action]


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

	SPEED = 16
	TRIALS = 1
	SIM_LENGTH = 500

<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
	LEARNING_RATE = 0.15
	DISCOUNT = 0.95
	EPISODES = 1000
	GOAL = 575
<<<<<<< HEAD
	SAVE = 50
	LEARNING_RATE = 0.1
	DISCOUNT = 0.95
	EPISODES = 1000
=======
	SAVE = 1
=======
	LEARNING_RATE = 0.1
	DISCOUNT = 0.95
	EPISODES = 1000
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
	epsilon = 1
	START_EPSILON_DECAYING = 1
	END_EPSILON_DECAYING = EPISODES//2
	epsilon_decay_value = epsilon/(END_EPSILON_DECAYING - START_EPSILON_DECAYING)

	ACTIONS = ['horizontal', 'vertical']

<<<<<<< HEAD
	RENDER = True

	table_1 = np.zeros((16, 16, 2))

	NAME = 'table-10'
=======
	RENDER = False

	table_1 = np.zeros((16, 16, 2))
<<<<<<< HEAD

	NAME = 'table-9'
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

	frequency = 30
	episode = 0
	total_wait = 0
<<<<<<< HEAD
=======
=======
	table_2 = np.zeros((8, 8, 8, 8, 2))

	NAME = 'table-2'

	frequency = 30
	start_wait = 0
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

	pygame.init()
	screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
	pygame.display.set_caption('Simulation')

<<<<<<< HEAD
	while True:
=======
<<<<<<< HEAD
	while True: #for episode in tqdm(range(EPISODES)):
=======
	for episode in tqdm(range(EPISODES)):
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

		count = 0
		total_wait = 0
		duration = 0

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
		
		main(q_control, SIM_LENGTH, frequency, 40, 150, RENDER)

<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
		if episode % SAVE == 0:
			with open(f'tables/{NAME}.npy', 'wb') as table_file:
				pickle.dump(table_1, table_file)

		with open(f'logs/{NAME}.txt', 'a') as file:
			file.write(f'\n[{str(episode + 1).zfill(4)}] Average frames waited: {total_wait}')

		if total_wait <= GOAL and episode >= EPISODES:
			break
<<<<<<< HEAD
		if episode == 0: start_wait = total_wait
=======
=======
		if episode == 0: start_wait = total_wait
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e

		if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
			epsilon -= epsilon_decay_value

<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
		episode += 1

	with open(f'tables/{NAME}.npy', 'wb') as table_file:
				pickle.dump(table_1, table_file)

<<<<<<< HEAD

=======
=======

	with open(f'logs/{NAME}.txt', 'a') as file:
		file.write(f'\n[START] Average frames waited: {start_wait}')
		file.write(f'\n[END] Average frames waited: {total_wait}')
	with open(f'tables/{NAME}.npy', 'wb') as table_file:
		pickle.dump(table_2, table_file)
>>>>>>> d7063b3b83a5f01b86467f8c0c906e4a4acd70b5
>>>>>>> a5c2fc7961c043221138ed8771d55c24576bc46e
	pygame.quit()
	quit()