#!/usr/bin/env python
import SlaveMachine, Storage
import math, random

##### INIT VARS
numberOfSlaves = 100
Slaves = []
S3 = None
currentStep = 0


#ADAPTIVE BUILD SETTINGS
freshCopyMin = 10000


#STALE CLEANUP SETTINGS
keepStalePct = 0.30


stepsInSim = 10080 ; print "Period: 1 Week"
# stepsInSim = 43800 ; print "Period: 1 Month"
# stepsInSim = 87600  ; print "Period: 2 Months"
# stepsInSim = 131400  ; print "Period: 3 Months"

# stepsInSim = 30000 ; print "{0} Minutes".format(stepsInSim)


# 10,080 minutes in a week
stepToStartTraffic = 1440 ; print "Time to Release: 1 Day (Emergency Release)"
# stepToStartTraffic = 10080 ; print "Time to Release: 1 Week (Quick Release)"
# stepToStartTraffic = 43800 ; print "Time to Release: 1 Month (Slow Release)"

trafficHistory = [None] * (stepsInSim - stepToStartTraffic) #INITALIZE HISTORY

def main():
    global traffic
    global currentStep
    currentStep = 0
    initSlaves()


    ##### Select Build Target
    setup = initFirefox ; print "Building: Firefox"



    ##### Select Algorithm
    # algorithm = algConstBuild ; print "Algorithm: Constant"
    algorithm = algFreshCopyMinBuild ; print "Algorithm: Keep {0} Fresh Copies".format(freshCopyMin)
    # algorithm = algAdaptiveBuild ; print "Algorithm: Adaptive (TODO)"



    ##### Select Traffic Pattern
    # traffic = traConstantDemand ; print "Traffic: Constant"
    # traffic = traRandomDemand ; print "Traffic: Random"
    traffic = traRandomSpikyDemand ; print "Traffic: Spiky"






    ##### START
    setup()

    #WHILE TRAFFIC IS RUNNING
    for i in range(stepsInSim):
        #RUN ALGORITHM
        algorithm()
        #RUN TRAFFIC
        S3.takeCopies(getTraffic(currentStep))
        #NEXT MINUTE
        step()

    #REPORT STATS
    print '=' * 80
    S3.printStats()
    print 'Total Cost of Slaves:  ${0:10,.2f}'.format(totalSlaveCost())
    print 'Total Cost:            ${0:10,.2f}'.format(totalSlaveCost() + S3.totalCost)
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
    waitForTraffic = 0  # Get at least this many samples

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
        
        divisor = min(currentStep - stepToStartTraffic, avgRange)
        average = int(math.ceil(float(sumTotal)/float(divisor)))
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

#TODO keep all traffic points; gen first?
def traRandomDemand(step):
    global trafficHistory
    if trafficHistory[step] == None:
        trafficHistory[step] = random.randint(0,10)
    return trafficHistory[step]
    

#TODO keep all traffic points; gen first?
def traRandomSpikyDemand(step):
    spikePct = 0.08

    global trafficHistory
    if trafficHistory[step] == None:
        demand = random.randint(0,10)
        if random.random() < spikePct:
            demand *= demand
        trafficHistory[step] = demand
    return trafficHistory[step]

#TODO Poisson process or Queuing theory arrival rate or 

#TODO arrivals peak during the day and ebb at night; e.g. sin(step % minuted_in_a_day)

#TODO rational (y=1/x) probability curve; high chance of low traffic, low chance of high traffic

#TODO Major release; start with really high demand and level out to constant; model actual Firefox release

#TODO Adaptive traffic; try to keep freshPct as low as possible




##### Setups

#TODO load available instances to a list for easy management
def initFirefox():
    global S3
    S3 = Storage.Storage(0,33) # copies per GB
    global Slaves
    for i in range(numberOfSlaves):
        setFirefox_C_Med_OD(Slaves[i])



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
    if (step >= stepToStartTraffic):
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