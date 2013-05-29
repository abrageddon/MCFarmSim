#!/usr/bin/env python
import SlaveMachine, Storage

##### Setup
numberOfSlaves = 20
Slaves = []
S3 = None
currentStep = 0

# 10,080 minutes in a week
stepToStartTraffic = 10080

# 100,000 is ok; 1,000,000 takes some time
# 43,800 minutes in a month
stepsInSim = 43800


def main():


    ##### Select traffic pattern
    traffic = traConstantDemand

    ##### Select algorthm
    algorithm = algConstBuild

    ##### Select setup
    setup = setupFirefox_Naive_C_XL



    ##### START
    setup()

    global currentStep
    currentStep = 0

    #RUN ALGORITHM
    algorithm()

    #WHILE TRAFFIC IS RUNNING
    for i in range(stepsInSim):
        step()
        #RUN TRAFFIC
        S3.takeCopies(traffic())
        #RUN ALGORITHM
        algorithm()

    #REPORT STATS
    print '=' * 80
    print 'Total Cost of Slaves: ${0:.2f}'.format(totalSlaveCost())
    print '=' * 80
    S3.printStats()
    print '=' * 80
    print 'Total Cost: ${0:.2f}'.format(totalSlaveCost() + S3.totalCost)
    print '=' * 80


##### Algorithms

def algConstBuild():
    global Slaves
    for i in range(numberOfSlaves):
        if Slaves[i].isDone():
            Slaves[i].startRun(stepsToComplete)


##### Traffics

def traConstantDemand():
    demand = 1
    if currentStep > stepToStartTraffic:
        return demand
    return 0


##### Setups

def setupFirefox_Naive_C_XL():
    global stepsToComplete
    stepsToComplete = 22 # minutes
    computeCost = 0.01 # $/min C1.XL
    copiesPerGB = 33
    generalSetup(stepsToComplete, computeCost, copiesPerGB)





##### Simulation Functions
def generalSetup(stepsToComplete, computeCost, copiesPerGB):
    global S3
    global Slaves
    S3 = Storage.Storage(0,copiesPerGB) # copies per GB
    for i in range(numberOfSlaves):
        temp = SlaveMachine.SlaveMachine(0, computeCost)
        Slaves.append(temp)

def step():
    global S3
    global Slaves
    global currentStep
    currentStep += 1
    for slave in Slaves:
        slave.step()
        if slave.isDone():
            if slave.takeCopy():
                S3.addCopies(1)
    S3.step()
def totalSlaveCost():
    totalCost = 0
    for slave in Slaves:
        totalCost += slave.totalCost
    return totalCost


if __name__ == '__main__':
    main()