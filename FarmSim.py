#!/usr/bin/env python
import SlaveMachine, Storage
import math, random

##### Setup
numberOfSlaves = 100
Slaves = []
S3 = None
currentStep = 0

#ADAPTIVE BUILD SETTINGS
freshCopyMin = 10000
keepStalePct = 0.30

# 10,080 minutes in a week
stepToStartTraffic = 10080 # 1 week (Emergency Release)

# 100,000 is ok; 1,000,000 takes some time
# 43,800 minutes in a month
stepsInSim = 43800 # 1 Month
# stepsInSim = 87600 # 2 Month
# stepsInSim = 131400 # 3 Month

# stepsInSim = 30000

def main():
    global traffic
    global currentStep
    currentStep = 0
    initSlaves()




    ##### Select traffic pattern
    # traffic = traConstantDemand
    # traffic = traRandomDemand
    traffic = traRandomSpikyDemand

    ##### Select algorthm
    # algorithm = algConstBuild
    algorithm = algFreshCopyMinBuild
    # algorithm = algAdaptiveBuild

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


def doRemoveStale():
    global S3
    removeStale = 0
    if S3.stalePct() > keepStalePct: #TODO change to real cleanup algorithm; if demand is up then keep more stale
        if S3.fresh < freshCopyMin:
            removeStale = int(S3.total - freshCopyMin)
        elif S3.total > freshCopyMin:
            removeStale = int(math.floor(S3.total - S3.fresh/((1.0-(keepStalePct/2))) ))

    if removeStale == 0 : return True

    # print "Too Stale: " + str(S3.stalePct()) + ' : ' + str(removeStale) + ' - ' + str(S3.fresh) + '/' + str(S3.total)
    S3.delCopies(removeStale)
    # print str(S3.stalePct()) + " : " + str(S3.total)
    return True

def algFreshCopyMinBuild():
    #Keep a set amount of fresh; current implementation of actual system

    global Slaves
    global S3

    if currentStep <= stepToStartTraffic:
        for i in range(numberOfSlaves):
            if Slaves[i].isDone():
                Slaves[i].startRun()
    else:
        for i in range(numberOfSlaves):
            if Slaves[i].isDone() and S3.fresh < freshCopyMin:
                Slaves[i].startRun()

        doRemoveStale()

def algAdaptiveBuild():
    waitForTraffic = 1  # Get at least this many samples

    global Slaves
    global S3

    if currentStep <= stepToStartTraffic + waitForTraffic:
        for i in range(numberOfSlaves):
            if Slaves[i].isDone():
                Slaves[i].startRun()
    else:
        # calculate average demand
        #TODO range based on build time; reaction time
        avgRange = 120 # over past X steps
        sumTotal = 0
        for j in range(currentStep - avgRange, currentStep):
            sumTotal += getTraffic(j)
        divisor = min(currentStep - stepToStartTraffic, avgRange)
        average = int(math.ceil(float(sumTotal)/float(divisor))) #TODO number of non-zero
        # print str(average) + ' : ' + str(S3.freshPct()) + ' : ' + str(S3.fresh) + '/' + str(S3.total)
        
        # plan to build 10%? over the expected demand
        #build rate for each instance
        #dynamic algorithm to start the optimal number of 


        # assign machines
        for i in range(numberOfSlaves):
            if Slaves[i].isDone() and S3.fresh < freshCopyMin: #TODO change to real limiter
                Slaves[i].startRun()

        doRemoveStale()


##### Traffics

def traConstantDemand(step):
    demand = 1
    return demand #dl/min

def traRandomDemand(step):
    demand = random.randint(0,10)
    return demand #dl/min

def traRandomSpikyDemand(step):
    demand = random.randint(0,10)
    spikePct = 0.07
    if random.random() < spikePct:
        demand *= demand
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