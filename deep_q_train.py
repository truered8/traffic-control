import ctypes
import os
import random
import pygame
import subprocess
import platform
import pickle
import numpy as np
from tqdm import tqdm
from time import time
from sim.simobjects import *
from dqn import DQNAgent, ModifiedTensorBoard

def main(control, sim_length, frequency, dmin, dmax, render):
	global screen, clock, reverse, lanes, intersection, cars, intersection, total_wait, count, \
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
		
		if render: screen.fill((255, 255, 0))

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
	return 960, 0, 1920, 1080

if __name__ == '__main__':

	def deep_q_control(frequency, *args):
		''' Traffic control using deep q learning '''
		global action, old_state, episode_reward
		if count % frequency != 0: return
		def get_state():
			cars = [len(l.cars) for l in [*hlanes, *vlanes]]
			return np.array([min(c, 8) for c in cars])
		def get_reward():
			result = 0
			for l in lanes:
				for c in l.cars:
					if c.speed == 0:
						result += 1
			return (1 / (result + 1e-4))
		
		hlanes = [lanes[2], lanes[6]]
		vlanes = [lanes[0], lanes[4]]
		
		# Updating model with current state
		if count > 1:
			current_q = agent.get_qs(old_state)[action]
			current_state = get_state()
			reward = get_reward()
			done = (count==(SIM_LENGTH - 1))
			agent.update_replay_memory((old_state, action, reward, current_state, done))
			agent.train(done, count)
			episode_reward += reward
		old_state = get_state()
		if np.random.random() > epsilon:
			action = np.argmax(agent.get_qs(old_state))
		else:
			action = np.random.randint(0, 2)
		middle.flow = ACTIONS[action]


	reverse = lambda flow: {'horizontal': 'vertical'}.get(flow, 'horizontal')

	x, y, DISPLAY_WIDTH, DISPLAY_HEIGHT = get_screen_metrics()
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
	
	LANE_WIDTH = int(DISPLAY_WIDTH * 0.1)
	VERT_LANE_LENGTH = DISPLAY_HEIGHT // 2 - LANE_WIDTH
	HORZ_LANE_LENGTH = (DISPLAY_WIDTH // 2 - LANE_WIDTH)

	CENTER = (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)

	SPEED = 16
	TRIALS = 1
	SIM_LENGTH = 500

	EPISODES = 1000
	epsilon = 1
	START_EPSILON_DECAYING = 1
	END_EPSILON_DECAYING = EPISODES//2
	STAT_FREQ = 10
	MIN_REWARD = 10_000
	epsilon_decay_value = epsilon/(END_EPSILON_DECAYING - START_EPSILON_DECAYING)

	ACTIONS = ['horizontal', 'vertical']
	RENDER = False

	agent = DQNAgent('model-9')
	actuated_board = ModifiedTensorBoard(log_dir='boards/actuated')
	custom_board = ModifiedTensorBoard(log_dir='boards/custom')
	timed_board = ModifiedTensorBoard(log_dir='boards/timed')

	frequency = 30
	episode = 1
	total_wait = 0
	rewards = []
	waits = []

	pygame.init()
	screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
	pygame.display.set_caption('Simulation')

	for episode in tqdm(range(EPISODES)):

		count = 0
		total_wait = 0
		episode_reward = 0
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
		
		main(deep_q_control, SIM_LENGTH, frequency, 40, 150, RENDER)
		rewards.append(episode_reward)
		waits.append(total_wait)
		agent.tensorboard.step += 1
		actuated_board.step += 1
		custom_board.step += 1
		timed_board.step += 1

		# Add stats to TensorBoard log
		if not episode % STAT_FREQ or episode == 1:
			avg_reward = sum(rewards[-STAT_FREQ:])/len(rewards[-STAT_FREQ:])
			min_reward = min(rewards[-STAT_FREQ:])
			max_reward = max(rewards[-STAT_FREQ:])
			avg_wait = sum(waits[-STAT_FREQ:])/len(waits[-STAT_FREQ:])
			agent.tensorboard.update_stats(reward_avg=avg_reward, reward_min=min_reward, reward_max=max_reward, wait_avg=avg_wait)
			actuated_board.update_stats(reward_avg=1122288.2424991261, reward_min=560305.4759104166, reward_max=1860248.9781853524)
			custom_board.update_stats(reward_avg=858327.6210402126, reward_min=450371.30007536866, reward_max=1940231.4805767455)
			timed_board.update_stats(reward_avg=1099260.2129769058, reward_min=600234.0681588055, reward_max=1720225.982301521)			

			# Save the model if it meets the requirements
			if min_reward >= MIN_REWARD:
				agent.model.save(f'models/{agent.name}__{max_reward:_>7.2f}max_{avg_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

		# Decay epsilon 
		if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
			epsilon -= epsilon_decay_value


	pygame.quit()
	quit()