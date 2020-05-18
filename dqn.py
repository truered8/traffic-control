from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.callbacks import TensorBoard
from keras.optimizers import Adam
from keras.models import load_model
import tensorflow as tf
from collections import deque
import numpy as np
import time
import random

input_shape = (4,)
REPLAY_MEMORY_SIZE = 50_000
MIN_REPLAY_MEMORY_SIZE = 2_000
MINIBATCH_SIZE = 1_024
DISCOUNT = 0.99
UPDATE_TARGET_EVERY = 5
MAX_SIZE = 15

class ModifiedTensorBoard(TensorBoard):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.step = 1
		self.writer = tf.summary.FileWriter(self.log_dir)

	def set_model(self, model):
		pass

	def on_epoch_end(self, epoch, logs=None):
		self.update_stats(**logs)

	def on_batch_end(self, batch, logs=None):
		pass

	def on_train_end(self, _):
		pass

	def update_stats(self, **stats):
		self._write_logs(stats, self.step)


class DQNAgent:
	def __init__(self, name):
		self.name = name
		self.model = self.create_model()

		self.target_model = self.create_model()
		self.target_model.set_weights(self.model.get_weights())

		self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)
		self.tensorboard = ModifiedTensorBoard(log_dir=f'boards/{self.name}')
		self.target_update_counter = 0

	def create_model(self):
		model = Sequential()
		model.add(Dense(3, input_shape=input_shape, activation="relu"))
		model.add(Dense(2, activation="linear"))
		model.compile(loss="mse", optimizer=Adam(lr=0.001), metrics=['accuracy'])
		return model

	def load(self, path):
		self.model = load_model(path)

	def update_replay_memory(self, transition):
		self.replay_memory.append(transition)

	def get_qs(self, state):
		return self.model.predict(np.array(state).reshape(-1, *state.shape) / MAX_SIZE)[0]

	def train(self, terminal_state, step):
		if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE: return
		
		minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

		current_states = np.array([transition[0] for transition in minibatch]) / MAX_SIZE
		current_qs_list = self.model.predict(current_states)

		new_current_states = np.array([transition[3] for transition in minibatch]) / MAX_SIZE
		future_qs_list = self.target_model.predict(new_current_states)

		X = []
		y = []

		for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):
			if not done:
				max_future_q = np.max(future_qs_list[index])
				new_q = reward + DISCOUNT * max_future_q
			else:
				new_q = reward

			current_qs = current_qs_list[index]
			current_qs[action] = new_q

			X.append(current_state)
			y.append(current_qs)

		self.model.fit(np.array(X) / MAX_SIZE, np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False, callbacks=[self.tensorboard] if terminal_state else None)

		# Update target_model
		if terminal_state:
			self.target_update_counter += 1

		if self.target_update_counter > UPDATE_TARGET_EVERY:
			self.target_model.set_weights(self.model.get_weights())
			self.target_update_counter = 0