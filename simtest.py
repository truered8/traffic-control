import ctypes
import os
import random
import pygame
from sim.simobjects import *
from p_attr import print_attributes as pa

def main(control, sim_length, frequency, dmin, dmax):
	global screen, clock, reverse, intersections, cars, intersection, total_wait, count, \
	SPEED, DISPLAY_WIDTH, DISPLAY_HEIGHT

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
  
	CAR_WIDTH  = int(DISPLAY_WIDTH * 0.04)
	CAR_LENGTH = int(DISPLAY_WIDTH * 0.02)

	i = random.choice(range(1))
	l = intersections[1].lanes[i]
	car = Car(CAR_WIDTH, CAR_LENGTH, l.start, l.direction, SPEED, random.choice(['straight','right']), screen)
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
			s = random.choice(range(0, 7, 2))
			i = random.choice(intersections)
			l = i.lanes[s]
			g = random.choice(['straight', 'right'])
			c = Car(CAR_WIDTH, CAR_LENGTH, l.start, l.direction, SPEED, g, screen)
			c.start = s
			cars.add(c)
		
		for c in cars.sprites():
			
			c.speed = SPEED
			for intersection in intersections:
				if c.rect.colliderect(intersection.middle.rect):
					if not intersection.middle.rect.contains(c.rect):
						if intersection.middle.flow != c.orientation and c.rect.colliderect(intersection.lanes[c.start]):
							c.speed = 0
						if reverse(c.orientation) in [d.orientation for d in intersection.middle.incars] and c.rect.colliderect(intersection.lanes[c.start]):
							c.speed = 0
					else:
						if c.goal != 'straight':
							t = intersection.middle.turns[get_turn(c.start, c.goal)]
							if approx(c.rect.center, t) and not c.turned:
								c.direction = rotate(c.direction, c.goal)
								c.turned = True

			if c.speed == 0:
				total_wait += 1

		for intersection in intersections: control(intersection, frequency, dmin, dmax)


		for intersection in intersections: intersection.sprites.update(cars.sprites())
		cars.update(intersection.sprites.sprites())
		
		screen.fill(YELLOW)

		for intersection in intersections: intersection.sprites.draw(screen)
		cars.draw(screen)

		pygame.display.update()

		clock.tick(180)

		count += 1

def get_screen_metrics():
	''' Get information on the screen the program is running on '''
	user32 = ctypes.windll.user32
	SCREEN_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
	COMBINED_SCREEN_SIZE = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
	SECOND_SCREEN_SIZE = (COMBINED_SCREEN_SIZE[0] - SCREEN_SIZE[0], COMBINED_SCREEN_SIZE[1])
	DISPLAY_MODE = "single" if COMBINED_SCREEN_SIZE == SCREEN_SIZE else "dual"
	print(SCREEN_SIZE)
	print(COMBINED_SCREEN_SIZE)
	RATIO = 1.0
	if DISPLAY_MODE == "dual":
		DISPLAY_WIDTH, DISPLAY_HEIGHT = tuple([int(i // RATIO) for i in list(SECOND_SCREEN_SIZE)])
		x, y = ((COMBINED_SCREEN_SIZE[0] + SCREEN_SIZE[0] - DISPLAY_WIDTH) // 2, (COMBINED_SCREEN_SIZE[1] - DISPLAY_HEIGHT) // 2)
	else:
		DISPLAY_WIDTH, DISPLAY_HEIGHT = tuple([int(i // RATIO) for i in list(SCREEN_SIZE)])
		x, y = (SCREEN_SIZE[0] - DISPLAY_WIDTH) // 2, (SCREEN_SIZE[1] - DISPLAY_HEIGHT) // 2
	return x, y, DISPLAY_WIDTH, DISPLAY_HEIGHT

if __name__ == '__main__':

	def timed(intersectionfrequency, *args):
		''' Simple interval-based traffic control '''
		if count % frequency == 0:
			intersection.middle.flow = reverse(intersection.middle.flow)

	def custom(intersection, frequency, *args):
		''' Control in which the side with more cars gets the green light '''
		hlanes = [intersection.lanes[2], intersection.lanes[6]]
		vlanes = [intersection.lanes[0], intersection.lanes[4]]
		if count % frequency == 0:
			intersection.middle.flow = 'horizontal' if sum([len(l.cars) for l in hlanes]) > sum([len(l.cars) for l in vlanes]) else 'vertical'
		
	def actuated(intersection, frequency, dmin, dmax):
		''' Semi-actuated traffic control '''
		global duration
		def is_empty(lanes):
			for l in lanes:
				for c in l.cars:
					position = [type(p) for p in c.position]
					if Lane in position and Middle in position:
						return False
			return True
		hlanes = [intersection.lanes[2], intersection.lanes[6]]
		vlanes = [intersection.lanes[0], intersection.lanes[4]]
		if count % frequency == 0:
			switch = is_empty(hlanes) if intersection.middle.flow == 'horizontal' else is_empty(vlanes)
			if switch and duration > dmin and duration < dmax:
				intersection.middle.flow = reverse(intersection.middle.flow)
				duration = 0
		else:
			duration += 1

	reverse = lambda flow: {'horizontal': 'vertical'}.get(flow, 'horizontal')

	x, y, DISPLAY_WIDTH, DISPLAY_HEIGHT = get_screen_metrics()
	print(DISPLAY_WIDTH, DISPLAY_HEIGHT)
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

	SPEED = 2
	TRIALS = 1
	SIM_LENGTH = 1500

	controls = [custom]
	frequencies = [100]


	for control in controls:
		for frequency in frequencies:

			count = 0
			total_wait = 0
			last_wait = 0
			duration = 0
			pygame.init()
			screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
			pygame.display.set_caption('Simulation')

			for i in range(TRIALS):

				clock = pygame.time.Clock()
				cars = pygame.sprite.Group()
				intersections = []
				intersections.append(Intersection(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2, 0, 0, screen))
				intersections.append(Intersection(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2, DISPLAY_WIDTH // 2, 0, screen))
				intersections.append(Intersection(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2, 0, DISPLAY_HEIGHT // 2, screen))
				intersections.append(Intersection(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2, DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2, screen))
				main(control, SIM_LENGTH, frequency, 40, 150)

				print(f'\nWait Time: {total_wait - last_wait}')
				last_wait = total_wait

			print(f'\nAverage frames waited: {total_wait // TRIALS}')
			
			pygame.quit()

	quit()