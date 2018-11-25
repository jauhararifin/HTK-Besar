#!/bin/python3

from graphics import *

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
		vertical = Line(Point(i * window_size // 15, 0), Point(i * window_size // 15, window_size))
		vertical.draw(win)
		horizontal = Line(Point(0, i * window_size // 15), Point(window_size, i * window_size // 15))
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
			circle = Circle(Point(x * window_size // 15 + window_size // 30, x * window_size // 15 + window_size // 30), window_size // 30 - 5)
			circle.draw(win)
	if not state['inGame'] and state['winner'] is not None:
		message = Text(Point(win.getWidth()/2, win.getHeight()/2), state['winner'] + ' Win')
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

			# check horizontal
			n = 1
			for i in range(1, 7):
				if (x + i, y) in state['moves']: n += 1 else break
			for i in range(1, 7):
				if (x - i, y) in state['moves']: n += 1 else break
			if n == 5:
				return {
					'inGame': True,
					'winner': 'X' if len(state['moves']) % 2 == 0 else 'O',
					'moves': state['moves'][:] + [(x,y)]
				}

			# check vertical
			n = 1
			for i in range(1, 7):
				if (x, y + i) in state['moves']: n += 1 else break
			for i in range(1, 7):
				if (x, y - i) in state['moves']: n += 1 else break
			if n == 5:
				return {
					'inGame': True,
					'winner': 'X' if len(state['moves']) % 2 == 0 else 'O',
					'moves': state['moves'][:] + [(x,y)]
				}

			# check diagonal 1
			n = 1
			for i in range(1, 7):
				if (x + i, y + i) in state['moves']: n += 1 else break
			for i in range(1, 7):
				if (x - i, y - i) in state['moves']: n += 1 else break
			if n == 5:
				return {
					'inGame': True,
					'winner': 'X' if len(state['moves']) % 2 == 0 else 'O',
					'moves': state['moves'][:] + [(x,y)]
				}

			# check diagonal 2
			n = 1
			for i in range(1, 7):
				if (x + i, y - i) in state['moves']: n += 1 else break
			for i in range(1, 7):
				if (x - i, y + i) in state['moves']: n += 1 else break
			if n == 5:
				return {
					'inGame': True,
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

draw_state(win, state)

while True:
	command_str = input()
	if command_str == 'QUIT':
		break
	state = act(state, command_str)
	draw_state(win, state)
