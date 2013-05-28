#!/usr/bin/env python

class SlaveMachine:
    description = """Slave machine that runs build jobs"""
    timeRemaining = 0
    def __init__(self, job):
        # +/- 3% or so?
        self.startRun(job)
    def startRun(self, job):
        if self.isDone():
            self.timeRemaining = job
            return True
        return False
    def step(self):
        if not self.isDone():
            self.timeRemaining -= 1
    def isDone(self):
        return self.timeRemaining <= 0
