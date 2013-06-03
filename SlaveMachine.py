#!/usr/bin/env python
import random

class SlaveMachine:
    description = """Slave machine that runs build jobs"""
    
    label = ''
    jobLength = 0
    cachedLength = 0
    isCached = False

    timeRemaining = -1
    costPerStep = 0.1

    totalCost = 0

    def __init__(self):
        pass
    def setMachine(self, label, job, cached, cost=0):
        self.label = label
        self.jobLength = job
        self.cachedLength = cached
        self.isCached = False
        if cost != 0:
            self.costPerStep = cost
    def startRun(self):
        if self.timeRemaining <= 0 and self.jobLength > 0 and self.cachedLength > 0:
            if self.isCached:
                #TODO +/- 5% or so?
                self.timeRemaining = self.jobLength + variance(self.jobLength)
            else:
                #TODO +/- 5% or so?
                self.timeRemaining = self.cachedLength + variance(self.cachedLength)
            return True
        return False
    def step(self):
        if self.timeRemaining > 0:
            self.timeRemaining -= 1
            self.totalCost += self.costPerStep
            return True
        return False
    def isDone(self):
        if self.timeRemaining <= 0:
            self.isCached = True
            return True
        return False
    def takeCopy(self):
        if self.timeRemaining == 0:
            self.timeRemaining = -1
            return True
        return False
def variance(time):
    var = random.uniform(-0.05,0.05)
    return int(var * time)
