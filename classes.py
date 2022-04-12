from vars import *

import math
import random



class Ball():
	def __init__(self, 
		paddles,
		nets,
		ge,
		x: float = 0.0, 
		y: float = 0.0, 
		vx: float = 0.0, 
		vy: float = 0.0
		):

		self.paddles = paddles
		self.nets = nets
		self.ge = ge

		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy

		self.initial_x = x
		self.initial_y = y

#—————————————————————————————————————————————————————————————————————————————————————————————————

		
	def update_position(self, 
		current_timescale: float = timescale, 
		current_framerate: float = framerate,
		paddles: list = []
		):


		if current_framerate == 0:
			current_framerate = framerate
		time = current_timescale / current_framerate
		accelerationX = 0
		accelerationY = 0

		next_x = self.x + self.vx * time + (accelerationX * (time ** 2)) / 2
		next_y = self.y + self.vy * time + (accelerationY * (time ** 2)) / 2

		# BOUNDARY COLLISION
		if next_y - ball_radius < boundary_upper:
			self.vy = -self.vy
			next_y = boundary_upper + ball_radius
		elif self.y + ball_radius > screen_height - boundary_lower:
			self.vy = -self.vy
			next_y = screen_height - boundary_lower - ball_radius
		self.y = next_y

		# PADDLE COLLISION, should rebound like Pong and Breakout instead of perfectly bouncing
		# Single AI player (no humans)
		if next_x - ball_radius < goal_width:
			next_x = goal_width + ball_radius
			self.vx *= -velocity_increment
			self.vy *= velocity_increment

		to_remove = []
		position_removed = []
		bams = 0
		if next_x + ball_radius > screen_width - goal_width:
			
			for i, paddle in enumerate(paddles): # they should maybe get more carrots the closer to the center of the paddle the hit is
				# if next_y + ball_radius > paddle.y - ((paddle_height / 2) * 0.9) and next_y - ball_radius < paddle.y + ((paddle_height / 2) * 1.1):
				# 	self.paddles[i].score += 1 # useless 'innit?
				# 	self.ge[i].fitness += 15
				# 	bams += 1
				if next_y + ball_radius > paddle.y and next_y - ball_radius < paddle.y + paddle_height:
					self.paddles[i].score += 1 # useless 'innit?
					self.ge[i].fitness += 7
					bams += 1

				else: # destroy paddle if it lets the ball through
					if next_y + ball_radius > paddle.y / 1.1 and next_y - ball_radius < (paddle.y + paddle_height) * 1.1:
						self.ge[i].fitness += 5
					elif next_y + ball_radius > paddle.y / 1.2 and next_y - ball_radius < (paddle.y + paddle_height) * 1.2:
						self.ge[i].fitness += 3
					elif next_y + ball_radius > paddle.y / 1.3 and next_y - ball_radius < (paddle.y + paddle_height) * 1.3:
						self.ge[i].fitness += 1
					elif next_y + ball_radius > paddle.y / 1.4 and next_y - ball_radius < (paddle.y + paddle_height) * 1.4:
						self.ge[i].fitness -= 1
					elif next_y + ball_radius > paddle.y / 1.5 and next_y - ball_radius < (paddle.y + paddle_height) * 1.5:
						self.ge[i].fitness -= 3
					else:
						self.ge[i].fitness -= 7
					to_remove.append(i)
					position_removed.append((self.paddles[i].x, self.paddles[i].y))
			else:
				pass

		if bams > 0:
			next_x = screen_width - goal_width - ball_radius
			self.vx *= -velocity_increment
			self.vy *= velocity_increment
			# print(f'{bams} BAMS')	
			
		self.x = next_x

		return to_remove, position_removed

	

#—————————————————————————————————————————————————————————————————————————————————————————————————


	def reset(self):
		self.x = self.initial_x
		self.y = self.initial_y
		self.vx = random.choice([random.randrange(-800, -500), random.randrange(500, 800)])	
		self.vy = random.choice([random.randrange(-800, -500), random.randrange(500, 800)])		

#—————————————————————————————————————————————————————————————————————————————————————————————————
#—————————————————————————————————————————————————————————————————————————————————————————————————


class Paddle():
	def __init__(self, 
		controller: str = 'Player',
		x: float = 0.0, 
		y: float = 0.0,
		score: int = 0
		):

		self.controller = controller
		self.x = x
		self.y = y
		self.score = score

		self.initial_x = x
		self.initial_y = y

		self.color = (random.randrange(0, 215), random.randrange(0, 215), random.randrange(0, 215))

#—————————————————————————————————————————————————————————————————————————————————————————————————


	def update_position(self, 
		increment: float = 0.0
		):
		paddle_bottom = self.y + paddle_height

		if self.y + increment < boundary_upper:
			self.y = boundary_upper
		elif paddle_bottom + increment > screen_height - boundary_lower:
			self.y = screen_height - boundary_lower - paddle_height
		else:
			self.y += increment

#—————————————————————————————————————————————————————————————————————————————————————————————————


	def reset(self):
		self.x = self.initial_x
		self.y = self.initial_y
		self.score = 0