from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d
import numpy as np
import sys
from dqn import ModifiedTensorBoard

with open(sys.argv[1], 'rb') as f:
	lines = f.readlines()
	y = [int(str(line)[32:35]) for line in lines]

y = gaussian_filter1d(y, sigma=3)

actuated_board = ModifiedTensorBoard(log_dir='boards\\actuated')
custom_board = ModifiedTensorBoard(log_dir='boards\\custom')
timed_board = ModifiedTensorBoard(log_dir='boards\\timed')
board = ModifiedTensorBoard(log_dir='boards\\table')

for val in y:
	actuated_board.update_stats(wait_avg=667.5)
	custom_board.update_stats(wait_avg=642.2)
	timed_board.update_stats(wait_avg=685.9)
	board.update_stats(wait_avg=val)
	actuated_board.step += 1
	custom_board.step += 1
	timed_board.step += 1
	board.step += 1