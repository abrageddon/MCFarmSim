#!/usr/bin/env python

class SlaveMachine:
    description = """Slave machine that runs build jobs"""
    timeRemaining = 0
    costPerStep = 0.1
    totalCost = 0
    def __init__(self, job, cost=0):
        # +/- 3% or so?
        self.startRun(job)
        if cost != 0:
            self.costPerStep = cost
    def startRun(self, job):
        if self.timeRemaining <= 0:
            self.timeRemaining = job
            return True
        return False
    def step(self):
        if self.timeRemaining > 0:
            self.timeRemaining -= 1
            self.totalCost += self.costPerStep
            return True
        return False
    def isDone(self):
        return self.timeRemaining <= 0
    def takeCopy(self):
        if self.timeRemaining == 0:
            self.timeRemaining = -1
            return True
        return False
