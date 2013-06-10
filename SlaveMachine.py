#!/usr/bin/env python
import random

class SlaveMachine:
    description = """Slave machine that runs build jobs"""
    
    label = ''
    jobLength = 0
    cachedLength = 0
    isCached = False
    isSpot = False

    timeRemaining = -1
    costPerStep = 0

    totalCost = 0

    def __init__(self):
        pass
    def reset(self):
        self.timeRemaining = -1
        self.isCached = False
    def setParameters(self, label, steps, cached, cost, isSpot):
        # kill current run
        self.reset()
        # load new settings
        self.label = label
        self.jobLength = steps
        self.cachedLength = cached
        self.costPerStep = cost
        self.isSpot = isSpot
    def setMachine(self, instance):
        instance.setInstance(self)
    def startRun(self):
        if self.timeRemaining <= 0 and self.jobLength > 0 and self.cachedLength > 0:
            if self.isCached:
                self.timeRemaining = self.cachedLength + variance(self.cachedLength)
            else:
                self.timeRemaining = self.jobLength + variance(self.jobLength)
            self.isCached = True
            return True
        return False
    def step(self, outbid):

        #TODO Charge by the hour

        if self.timeRemaining > 0:
            if outbid and self.isSpot:
                # print "DIED: "+str(self.timeRemaining)
                self.reset()
                return False
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
    varRange = 0.03
    var = random.uniform(-varRange,varRange)
    return int(var * time)
