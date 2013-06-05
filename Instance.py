#!/usr/bin/env python
import SlaveMachine

class Instance:
    description = """Node representing a build of a particular application on a certain EC2 instance"""

    label = ''
    stepsToComplete = 0 # minutes
    stepsToCompleteCached = 0 # minutes
    computeCost = 0.01 # $/min
    isSpot = False

    def __init__(self, label, steps, cached, cost, isSpot):
        self.label = label
        self.stepsToComplete = steps # minutes
        self.stepsToCompleteCached = cached # minutes
        self.computeCost = cost # $/min
        self.isSpot = isSpot

    def setInstance(self, Slave):
        return Slave.setParameters(self.label, self.stepsToComplete, self.stepsToCompleteCached, self.computeCost, self.isSpot)

    #TODO ADD SELECTORS {fast, cheap} {spot, on-demand}

    #TODO ADD STATS