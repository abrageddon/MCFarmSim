#!/usr/bin/env python

class SlaveMachine:
	description = """Slave machine that runs build jobs"""
	timeOfJob = 0
	timeRemaining = 0
	def __init__(self, job):
		self.timeOfJob = job
		# +/- 3% or so?
		self.timeRemaining = job
	def step(self):
		self.timeRemaining -= 1
	def isDone(self):
		return self.timeRemaining <= 0
