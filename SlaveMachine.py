#!/usr/bin/env python
import random

class SlaveMachine:
    description = """Slave machine that runs build jobs"""
    
    label = ''
    jobLength = 0
    cachedLength = 0
    isCached = False

    timeRemaining = -1
    costPerStep = 0

    totalCost = 0

    def __init__(self):
        pass
    def setMachine(self, label, job, cached, cost):
        # kill current run
        self.timeRemaining = -1
        self.isCached = False
        # load new settings
        self.label = label
        self.jobLength = job
        self.cachedLength = cached
        self.costPerStep = cost
    def startRun(self):
        if self.timeRemaining <= 0 and self.jobLength > 0 and self.cachedLength > 0:
            if self.isCached:
                self.timeRemaining = self.cachedLength + variance(self.cachedLength)
            else:
                self.timeRemaining = self.jobLength + variance(self.jobLength)
                self.isCached = True
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
            return True
        return False
    def takeCopy(self):
        if self.timeRemaining == 0:
            self.timeRemaining = -1
            return True
        return False
def variance(time):
    varRange = 0.05
    var = random.uniform(-varRange,varRange)
    return int(var * time)
