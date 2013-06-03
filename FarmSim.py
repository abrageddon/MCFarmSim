#!/usr/bin/env python
import SlaveMachine, Storage
import math, random

##### Setup
numberOfSlaves = 50
Slaves = []
S3 = None
currentStep = 0

# 10,080 minutes in a week
stepToStartTraffic = 10080 # 1 week

# 100,000 is ok; 1,000,000 takes some time
# 43,800 minutes in a month
# stepsInSim = 43800 # 1 Month
# stepsInSim = 87600 # 2 Month
# stepsInSim = 131400 # 3 Month

stepsInSim = 15000

def main():
    global traffic
    global currentStep
    currentStep = 0
    initSlaves()




    ##### Select traffic pattern
    traffic = traConstantDemand
    # traffic = traRandomDemand

    ##### Select algorthm
    # algorithm = algConstBuild
    algorithm = algAdaptiveConstBuild

    ##### Select setup
    setup = initFirefox
    # setup = initFirefoxMixed




    ##### START
    setup()

    #RUN ALGORITHM FIRST
    algorithm()

    #WHILE TRAFFIC IS RUNNING
    for i in range(stepsInSim):
        #NEXT MINUTE
        step()
        #RUN TRAFFIC
        S3.takeCopies(getTraffic(currentStep))
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
            Slaves[i].startRun()


def algAdaptiveConstBuild():
    global Slaves
    waitForTraffic = 1
    if currentStep <= stepToStartTraffic + waitForTraffic:
        for i in range(numberOfSlaves):
            if Slaves[i].isDone():
                Slaves[i].startRun()
    else:
        # calculate average demand
        avgRange = 30
        sumTotal = 0
        for j in range(currentStep - avgRange, currentStep):
            sumTotal += getTraffic(j)
        average = int(math.ceil(float(sumTotal)/float(avgRange)))

        # plan to build 10%? over the expected demand

        # assign machines
        for i in range(numberOfSlaves):
            if Slaves[i].isDone():
                Slaves[i].startRun()

##### Traffics

def traConstantDemand(step):
    demand = 1
    return demand #dl/min

def traRandomDemand(step):
    demand = random.randint(0,10)
    return demand #dl/min


##### Setups

def initFirefox():
    global S3
    S3 = Storage.Storage(0,33) # copies per GB
    global Slaves
    for i in range(numberOfSlaves):
        setFirefox_C_Med_OD(Slaves[i])

def initFirefoxMixed():
    global S3
    S3 = Storage.Storage(0,33) # copies per GB
    global Slaves
    for i in range(numberOfSlaves/2):
        setFirefox_C_Med_OD(Slaves[i])
    for i in range(numberOfSlaves/2, numberOfSlaves):
        setFirefox_C_XL_OD(Slaves[i])


#TODO make these into objects to be able to reference their data
C_XL_OD = 'C1.XLarge On-Demand'
def setFirefox_C_XL_OD(Slave):
    stepsToComplete = 25 # minutes
    stepsToCompleteCached = 7 # minutes
    computeCost = 0.01 # $/min C1.XL
    return Slave.setMachine(C_XL_OD, stepsToComplete, stepsToCompleteCached, computeCost)

#TODO make these into objects to be able to reference their data
C_Med_OD = 'C1.Medium On-Demand'
def setFirefox_C_Med_OD(Slave):
    stepsToComplete = 63 # minutes
    stepsToCompleteCached = 15 # minutes
    computeCost = 0.0025 # $/min C1.Med
    return Slave.setMachine(C_Med_OD, stepsToComplete, stepsToCompleteCached, computeCost)

#TODO Spot instance simulation

##### Simulation Functions

def initSlaves():
    global Slaves
    for i in range(numberOfSlaves):
        slave = SlaveMachine.SlaveMachine()
        Slaves.append(slave)
def getTraffic(step):
    if (step > stepToStartTraffic):
        return traffic(step - stepToStartTraffic)
    return 0
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