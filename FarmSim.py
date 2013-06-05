#!/usr/bin/env python
import SlaveMachine, Storage, Instance
import math, random

##### INIT VARS
numberOfSlaves = 20
Slaves = []
Instances = []
S3 = None
currentStep = 0
shortageMultiplier = 1



# algFourTierLinearBuild SETTINGS
freshCopyMin = 10000


#STALE CLEANUP SETTINGS
keepStalePct = 0.30


#TODO Spot instance simulation
#SPOT OVERBID PROBABILITY
overbidProb = 0.001

#SPOT OVERBID LENGTH


# stepsInSim = 10080 ; print "Period: 1 Week"
stepsInSim = 43800 ; print "Period: 1 Month"
# stepsInSim = 87600 ; print "Period: 2 Months"
# stepsInSim = 131400 ; print "Period: 3 Months"
# stepsInSim = 131400 *4 ; print "Period: 1 Year" # takes a few MINUTES

# stepsInSim = 30000 ; print "{0} Minutes".format(stepsInSim)


# 10,080 minutes in a week
# stepToStartTraffic = 1440 ; print "Time to Release: 1 Day (Emergency Release)"
stepToStartTraffic = 10080 ; print "Time to Release: 1 Week (Quick Release)"
# stepToStartTraffic = 43800 ; print "Time to Release: 1 Month (Slow Release)"
# stepToStartTraffic = stepsInSim ; print "Time to Release: Never (No Traffic)"





trafficHistory = [None] * (stepsInSim - stepToStartTraffic) #INITALIZE HISTORY

def main():
    global traffic
    global currentStep
    currentStep = 0
    initSlaves()


    ##### Select Build Target
    setup = initFirefox ; print "Building: Firefox"



    ##### Select Algorithm
    # algorithm = algConstBuild ; print "Algorithm: Constant Build On-Demand"
    # algorithm = algConstBuildSpot ; print "Algorithm: Constant Build Spot"
    # algorithm = algSimpleLimitBuild ; print "Algorithm: Build When Below {0} Fresh Copies".format(freshCopyMin)
    # algorithm = algFourTierLinearBuild ; print "Algorithm: 4-Tier Linear\n\tPre: Constant Build With Cheapest Spot Instance\n\tPost: {0}x{{1.00, 0.75, 0.50, 0.25}} Defines Fresh Copy Levels Based On Instance Cost".format(freshCopyMin)
    # algorithm = algFourTierExpBuild ; print "Algorithm: 4-Tier Exponential\n\tPre: Constant Build With Cheapest Spot Instance\n\tPost: {0}^{{1.00, 0.1, 0.01, 0.001}} Defines Fresh Copy Levels Based On Instance Cost".format(freshCopyMin)
    algorithm = algFreshAdaptiveBuild ; print "Algorithm: Fresh Percent Adaptive 4-Tier; Linear Or Exponential 4-Tier (TODO)"
    # algorithm = algFlowAdaptiveBuild ; print "Algorithm: Flow Rate Adaptive (TODO)"



    ##### Select Traffic Pattern
    # traffic = traConstantDemand ; print "Traffic: Constant"
    # traffic = traRandomDemand ; print "Traffic: Random"
    traffic = traRandomSpikyDemand ; print "Traffic: Spiky"





#TODO TIME SIM
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


    print freshCopyMin







##### Algorithms





def algConstBuild():
    startAvailableOnCheapestOnDemand()

def algConstBuildSpot():
    startAvailableOnCheapestSpot()

def algSimpleLimitBuild():
    if currentStep <= stepToStartTraffic:
        startAvailableOnCheapestSpot()
    else:
        if S3.fresh < freshCopyMin:
            startAvailableOnCheapestOnDemand()

        doRemoveStale()

def algFourTierLinearBuild():
    if currentStep <= stepToStartTraffic:
        startAvailableOnCheapestSpot()
    else:
        if S3.fresh < freshCopyMin * 0.25:
            startAvailableOnFastestOnDemand()
        elif S3.fresh < freshCopyMin * 0.50:
            startAvailableOnCheapestOnDemand()
        elif S3.fresh < freshCopyMin * 0.75:
            startAvailableOnFastestSpot()
        elif S3.fresh < freshCopyMin:
            startAvailableOnCheapestSpot()

        doRemoveStale()

def algFourTierExpBuild():
    if currentStep <= stepToStartTraffic:
        startAvailableOnCheapestSpot()
    else:
        if S3.fresh < freshCopyMin * 0.001:
            startAvailableOnFastestOnDemand()
        elif S3.fresh < freshCopyMin * 0.01:
            startAvailableOnCheapestOnDemand()
        elif S3.fresh < freshCopyMin * 0.1:
            startAvailableOnFastestSpot()
        elif S3.fresh < freshCopyMin:
            startAvailableOnCheapestSpot()

        doRemoveStale()

def algFreshAdaptiveBuild():
    waitForTraffic = 1440  # Wait 1 day for traffic to settle
    global shortageMultiplier
    global Slaves
    global S3
    global freshCopyMin

    if currentStep <= stepToStartTraffic + waitForTraffic:
        startAvailableOnCheapestSpot()
    else:
        change = 0.01
        if S3.freshPct() < 0.20:
            shortageMultiplier = max(int(shortageMultiplier * (1.0+change)), 1)
            print str(shortageMultiplier) +":++:"+str(S3.freshPct())
        elif S3.freshPct() > 0.80:
            shortageMultiplier = max(int(shortageMultiplier * (1.0-change)), 1)
            print str(shortageMultiplier) +":--:"+str(S3.freshPct())

        calcFreshCopyMin = freshCopyMin * shortageMultiplier

        # assign machines
        algFourTierLinearBuild()
        # algFourTierExpBuild()

        doRemoveStale()






def algFlowAdaptiveBuild():
    waitForTraffic = 0  # Get at least this many samples

    global Slaves
    global S3

    if currentStep <= stepToStartTraffic + waitForTraffic:
        startAvailableOnCheapestSpot()
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
        if S3.fresh < freshCopyMin * 0.001:
            startAvailableOnFastestOnDemand()
        elif S3.fresh < freshCopyMin * 0.01:
            startAvailableOnCheapestOnDemand()
        elif S3.fresh < freshCopyMin * 0.1:
            startAvailableOnFastestSpot()
        elif S3.fresh < freshCopyMin:
            startAvailableOnCheapestSpot()

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
    global instances
    instances = []
    instances.append(Instance.Instance('C1.Medium Spot',      63, 15, 0.00046, True))
    instances.append(Instance.Instance('C1.XLarge Spot',      25,  7, 0.00186, True))
    instances.append(Instance.Instance('C1.Medium On-Demand', 63, 15, 0.00241, False))
    instances.append(Instance.Instance('C1.XLarge On-Demand', 25,  7, 0.00967, False))
    #TODO adjust number of slaves
    global numberOfSlaves
    numberOfSlaves = 100
    initSlaves()

    global S3
    S3 = Storage.Storage(0,33) # copies per GB




##### Helper Functions


def doRemoveStale():
    global S3
    removeStale = 0
    if S3.stalePct() > keepStalePct: #TODO change to real cleanup algorithm; if demand is up then keep more stale
        if S3.fresh < freshCopyMin:
            removeStale = int(S3.total - freshCopyMin)
        elif S3.total > freshCopyMin:
            removeStale = int(math.floor(S3.total - S3.fresh/((1.0-(keepStalePct/2))) ))

    if removeStale <= 0 : return True
    return S3.delCopies(removeStale)

def startAvailableOnCheapestSpot():
    global Slaves
    for i in range(numberOfSlaves):
        if Slaves[i].isDone():
            if Slaves[i].label != instances[0].label:
                Slaves[i].setMachine(instances[0])#TODO Replace with cheapest spot selector
            Slaves[i].startRun()
def startAvailableOnFastestSpot():
    global Slaves   
    for i in range(numberOfSlaves):
        if Slaves[i].isDone():
            if Slaves[i].label != instances[1].label:
                Slaves[i].setMachine(instances[1])#TODO Replace with selector
            Slaves[i].startRun()
def startAvailableOnCheapestOnDemand():
    global Slaves  
    for i in range(numberOfSlaves):
        if Slaves[i].isDone():
            if Slaves[i].label != instances[2].label:
                Slaves[i].setMachine(instances[2])#TODO Replace with selector
            Slaves[i].startRun()
def startAvailableOnFastestOnDemand():
    global Slaves
    for i in range(numberOfSlaves):
        if Slaves[i].isDone():
            if Slaves[i].label != instances[3].label:
                Slaves[i].setMachine(instances[3])#TODO Replace with selector
            Slaves[i].startRun()








##### Simulation Functions

def initSlaves():
    global Slaves
    Slaves = []
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

    roll = random.random()
    outbid = False if overbidProb < roll else True
    # if outbid:print "OUTBID: "+str(currentStep)

    for slave in Slaves:
        slave.step(outbid)
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