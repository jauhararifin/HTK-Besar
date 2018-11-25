#!/bin/python3

import queue
import subprocess
from threading import Thread
from graphics import *
from pynput import keyboard

window_size = 600

win = GraphWin('Gomoku', window_size, window_size)

state = {
	'inGame': False,
	'winner': 'X',
	'moves': [(1,2),(4,5),(6,2)],	
}

def text_to_int(str):
	return {
		'SATU': 1,
		'DUA': 2,
		'TIGA': 3,
		'EMPAT': 4,
		'LIMA': 5,
		'ENAM': 6,
		'TUJUH': 7,
		'DELAPAN': 8,
		'SEMBILAN': 9,
		'SEPULUH': 10,
		'SEBELAS': 11,
		'DUABELAS': 12,
		'TIGABELAS': 13,
		'EMPATBELAS': 14,
		'LIMABELAS': 15,
	}[str]

def draw_state(win, state):
	for item in win.items[:]:
		item.undraw()
	win.update()

	for i in range(1,15):
		vertical = Line(
			Point(i * window_size // 15, 0),
			Point(i * window_size // 15, window_size)
		)
		vertical.draw(win)
		horizontal = Line(
			Point(0, i * window_size // 15), 
			Point(window_size, i * window_size // 15)
		)
		horizontal.draw(win)
	
	for i, (x, y) in enumerate(state['moves']):
		if i % 2 == 0:
			line = Line(
				Point(x * window_size // 15 + 5, y * window_size // 15 + 5),
				Point((x + 1) * window_size // 15 - 5, (y + 1) * window_size // 15 - 5)
			)
			line.draw(win)
			line = Line(
				Point((x + 1) * window_size // 15 - 5, y * window_size // 15 + 5),
				Point(x * window_size // 15 + 5, (y + 1) * window_size // 15 - 5)
			)
			line.draw(win)
		else:
			circle = Circle(
				Point(
					x * window_size // 15 + window_size // 30,
					y * window_size // 15 + window_size // 30
				),
				window_size // 30 - 5
			)
			circle.draw(win)
	
	if not state['inGame'] and state['winner'] is not None:
		message = Text(
			Point(win.getWidth()/2, win.getHeight()/2),
			state['winner'] + ' Win'
		)
		message.setSize(32)
		message.draw(win)

def start_game(state):
	return {
		'inGame': True,
		'winner': None,
		'moves': []
	}

def put_item(state, x, y):
	if state['inGame']:
		x = x - 1
		y = y - 1
		if (x, y) not in state['moves']:
			positions = state['moves'][len(state['moves']) % 2::2]
			direction = [(1,1),(1,-1),(1,0),(0,1)]
			for dx, dy in direction:
				n = 1
				for i in range(1, 7):
					if (x + i * dx, y + i * dy) in positions:
						n += 1
					else:
						break
				for i in range(1, 7):
					if (x - i * dx, y - i * dy) in positions:
						n += 1
					else:
						break
				if n == 5:
					return {
						'inGame': False,
						'winner': 'X' if len(state['moves']) % 2 == 0 else 'O',
						'moves': state['moves'][:] + [(x,y)]
					}
			return {
				'inGame': True,
				'winner': None,
				'moves': state['moves'][:] + [(x,y)]
			}
	return state

def surender(state):
	if state['inGame']:
		round = len(state['moves'])
		if round % 2 == 0:
			return {
				'inGame': False,
				'moves': state['moves'][:],
				'winner': 'O'
			}
		else:
			return {
				'inGame': False,
				'moves': state['moves'][:],
				'winner': 'X'
			}
	return state

def undo(state, num):
	if state['inGame'] and len(state['moves']) >= num:
		return {
			'inGame': True,
			'winner': None,
			'moves': state['moves'][:-num]
		}
	return state

def act(state, command_str):
	cmd_arr = command_str.split(' ')
	if len(cmd_arr) == 0:
		return state
	cmd_name = cmd_arr[0]
	if cmd_name in ['MULAI', 'MAIN']:
		return start_game(state)
	elif cmd_name in ['PASANG', 'TARUH']:
		x, y = text_to_int(cmd_arr[1]), text_to_int(cmd_arr[2])
		return put_item(state, x, y)
	elif cmd_name in ['MENYERAH', 'NYERAH']:
		return surender(state)
	elif cmd_name in ['ULANG', 'BATAL']:
		num = text_to_int(cmd_arr[1])
		return undo(state, num)
	return state

class Recorder():

	def __init__(self, queue):
		self.recording = False
		self.proc = None
		self.queue = queue

	def on_press(self, key):
		if key == keyboard.Key.enter and not self.recording:
			self.recording = True
			self.proc = subprocess.Popen(
				'arecord -r 16000 -V mono -c 1 -f S16_LE -d 10 rectest.wav'.split(' '),
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
			)

		if key == keyboard.Key.esc:
			self.queue.put('QUIT')
			return False

	def on_release(self, key):
		if key == keyboard.Key.enter and self.recording:
			self.recording = False
			self.proc.terminate()
			self.proc.wait()
			predict_prog = subprocess.Popen('./predict.sh rectest.wav'.split(' '),
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			)
			communication = predict_prog.communicate()
			cmd = str(communication[0].decode()[:-1])
			self.queue.put(cmd)

	def start(self):
		with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
			listener.join()

queue = queue.Queue()
Thread(target=Recorder(queue).start).start()

draw_state(win, state)
while True:
	command = queue.get()
	print(command)
	if command == 'QUIT':
		break
	state = act(state, command)
	draw_state(win, state)
	queue.task_done()
