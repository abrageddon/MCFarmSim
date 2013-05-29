#!/usr/bin/env python

class SlaveMachine:
    description = """Slave machine that runs build jobs"""
    timeRemaining = 0
    costPerStep = 1
    totalCost = 0
    def __init__(self, job, cost=1):
        # +/- 3% or so?
        self.startRun(job)
        self.costPerStep = cost
    def startRun(self, job):
        if self.isDone():
            self.timeRemaining = job
            return True
        return False
    def step(self):
        if not self.isDone():
            self.timeRemaining -= 1
            self.totalCost += self.costPerStep
            return True
        return False
    def isDone(self):
        return self.timeRemaining <= 0
