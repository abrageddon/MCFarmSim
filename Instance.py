#!/usr/bin/env python
import SlaveMachine

class Instance:
    description = """Node representing a build of a particular application on a certain EC2 instance"""

    label = ''
    stepsToComplete = 0 # minutes
    stepsToCompleteCached = 0 # minutes
    computeCost = 0.01 # $/min

    def __init__(self, label, steps, cached, cost):
        self.label = label
        self.stepsToComplete = steps # minutes
        self.stepsToCompleteCached = cached # minutes
        self.computeCost = cost # $/min

    def setInstance(self, Slave):
        return Slave.setMachine(Label, stepsToComplete, stepsToCompleteCached, computeCost)