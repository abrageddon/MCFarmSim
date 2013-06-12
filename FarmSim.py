#!/usr/bin/env python
import SlaveMachine, Storage, Instance
import math, random, sys

##### INIT VARS
numberOfSlaves = 20
Slaves = []
Instances = []
S3 = None
currentStep = 0


# FRESH COPY BASED SETTINGS
freshCopyMin = 1000


#STALE CLEANUP SETTINGS
keepStalePct = 0.25




# stepsInSim = 10080 ; print "Period: 1 Week"
# stepsInSim = 43800 ; print "Period: 1 Month"
stepsInSim = 43800 * 6 ; print "Period: 6 Month"
# stepsInSim = 87600 ; print "Period: 2 Months"
# stepsInSim = 131400 ; print "Period: 3 Months"
# stepsInSim = 131400 *4 ; print "Period: 1 Year" # takes a few MINUTES

# stepsInSim = 30000 ; print "{0} Minutes".format(stepsInSim)


# 10,080 minutes in a week
# stepToStartTraffic = 1440 ; print "Time to Release: 1 Day (Emergency Release)"
# stepToStartTraffic = 10080 ; print "Time to Release: 1 Week (Quick Release)"
stepToStartTraffic = 10080 * 2 ; print "Time to Release: 2 Week (Quick Release)"
# stepToStartTraffic = 43800 ; print "Time to Release: 1 Month (Slow Release)"
# stepToStartTraffic = stepsInSim ; print "Time to Release: Never (No Traffic)"

# stepsInSim = stepToStartTraffic

FastestOnDemandRate = 0
CheapestOnDemandRate = 0
FastestSpotRate = 0
CheapestSpotRate = 0


#TODO Spot instance simulation
#SPOT OVERBID PROBABILITY
overbidProb = 0.001

trafficHistory = [None] * (stepsInSim - stepToStartTraffic) #INITALIZE HISTORY
calcFreshCopyMin = freshCopyMin


#TODO Determine these values based on Instances; replace 30 estimate
#ADAPTIVE BUILD ADJUSTMENT PARAMETERS
shortageMultiplier = 1.0
rise = (float(freshCopyMin)/float(numberOfSlaves))/float(freshCopyMin)/30
fall = ((float(freshCopyMin)/float(numberOfSlaves))/(float(freshCopyMin))/30) / ((float(freshCopyMin)/float(numberOfSlaves)) * 30)

def main():
    global traffic
    global currentStep
    currentStep = 0
    initSlaves()


    ##### Select Build Target
    # setup = initFirefox ; print "Building: Firefox"
    setup = initSmallApp ; print "Building: SmallApp"
    # setup = initLargeApp ; print "Building: LargeApp"




    ##### Select Algorithm
    # algorithm = algConstBuild ; print "Algorithm: Constant Build On-Demand"
    # algorithm = algConstBuildSpot ; print "Algorithm: Constant Build Spot"
    # algorithm = algSimpleLimitBuild ; print "Algorithm: Build When Below {0} Fresh Copies".format(freshCopyMin)

    # algorithm = algTierLinearBuild ; print "Algorithm: 3-Tier Linear\n\tPre: Constant Build With Cheapest Spot Instance\n\tPost: {0}x{{1.00, 0.75, 0.25}} Defines Fresh Copy Levels Based On Instance Cost".format(freshCopyMin)
    # algorithm = algTierExpBuild ; print "Algorithm: 3-Tier Exponential\n\tPre: Constant Build With Cheapest Spot Instance\n\tPost: {0}^{{1.00, 0.1, 0.01}} Defines Fresh Copy Levels Based On Instance Cost".format(freshCopyMin)
    
    # algorithm = algFreshAdaptiveBuild ; print "Algorithm: Fresh Percent Adaptive Linear 3-Tier; Initial Estimate {0} Fresh Copies".format(freshCopyMin)
    algorithm = algFlowAdaptiveBuild ; print "Algorithm: Flow Rate Adaptive (TODO)"
    # algorithm = algDailyBuild ; print "Algorithm: Daily"



    ##### Select Traffic Pattern
    # traffic = traConstantDemand ; print "Traffic: Constant"
    # traffic = traRandomDemand ; print "Traffic: Random"
    # traffic = traRandomSpikyDemand ; print "Traffic: Spiky"
    # traffic = traFirefox ; print "Traffic: Firefox 4 Release Simulation"
    # traffic = traVariedDemand; print "Traffic: Exponential"
    traffic = traDailyDemand; print "Traffic: Daily"






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
    print ''
    print '=' * 80
    S3.printStats()
    print 'Total Cost of Slaves:  ${0:10,.2f}'.format(totalSlaveCost())
    print 'Total Cost:            ${0:10,.2f}'.format(totalSlaveCost() + S3.totalCost)
    print '=' * 80

    if calcFreshCopyMin != freshCopyMin :
        print "Final Adaptive Fresh Copy Minimum: " + str(calcFreshCopyMin)








##### Algorithms





def algConstBuild():
    startAvailableOnCheapestOnDemand()

def algConstBuildSpot():
    startAvailableOnCheapestSpot()

def algSimpleLimitBuild():
    if currentStep <= stepToStartTraffic:
        startAvailableOnCheapestSpot()
    else:
        if S3.fresh < calcFreshCopyMin:
            startAvailableOnCheapestOnDemand()
        doRemoveStale()

def algTierLinearBuild():
    if currentStep <= stepToStartTraffic:
        startAvailableOnCheapestSpot()
    else:
        if S3.fresh < calcFreshCopyMin * 0.25:
            startAvailableOnFastestOnDemand()
        elif S3.fresh < calcFreshCopyMin * 0.75:
            startAvailableOnFastestSpot()
        elif S3.fresh < calcFreshCopyMin:
            startAvailableOnCheapestSpot()
        doRemoveStale()

def algTierExpBuild():
    if currentStep <= stepToStartTraffic:
        startAvailableOnCheapestSpot()
    else:
        if S3.fresh < calcFreshCopyMin * 0.01:
            startAvailableOnFastestOnDemand()
        elif S3.fresh < calcFreshCopyMin * 0.1:
            startAvailableOnFastestSpot()
        elif S3.fresh < calcFreshCopyMin:
            startAvailableOnCheapestSpot()
        doRemoveStale()

def algFreshAdaptiveBuild():
    global shortageMultiplier
    global Slaves
    global S3
    global calcFreshCopyMin

    
    if currentStep <= stepToStartTraffic:
        startAvailableOnCheapestSpot()
    else:
        if S3.freshPct() < 0.95:
            shortageMultiplier = shortageMultiplier + rise
            calcFreshCopyMin = int(shortageMultiplier * freshCopyMin)
        elif S3.freshPct() < 0.75:
            shortageMultiplier = shortageMultiplier + (2*rise)
            calcFreshCopyMin = int(shortageMultiplier * freshCopyMin)
        elif S3.freshPct() > 0.99:
            shortageMultiplier = max(1, shortageMultiplier - fall)  # slow fall
            calcFreshCopyMin = int(shortageMultiplier * freshCopyMin)

        # assign machines
        algTierLinearBuild()

        # this is redundant with the one in algTierLinearBuild
        # doRemoveStale()
        
def algFlowAdaptiveBuild():
    waitForTraffic = 120  # Get at least this many samples

    global Slaves
    global S3

    if currentStep <= stepToStartTraffic + waitForTraffic:
        startAvailableOnCheapestSpot()
    else:
        # calculate average demand
        #TODO range based on build time; reaction time
        avgRange = 120 # over past X steps
        sumTotal = 0
        
        
        for i in range(avgRange):
            print currentStep - i - stepToStartTraffic
            sumTotal += trafficHistory[currentStep - i - stepToStartTraffic - 1]
        
        avgDemand = sumTotal/avgRange
        
        #divisor = min(currentStep - stepToStartTraffic, avgRange)
        #average = int(math.ceil(float(sumTotal)/float(divisor)))
        # print str(average) + ' : ' + str(S3.freshPct()) + ' : ' + str(S3.fresh) + '/' + str(S3.total)
        
        # plan to build 10%? over the expected demand
        #build rate for each instance
        #dynamic algorithm to start the optimal number of 


        if avgDemand > FastestOnDemandRate:
            startAvailableOnFastestOnDemand()
        elif avgDemand > CheapestOnDemandRate:
            startAvailableOnCheapestOnDemand()
        elif avgDemand > FastestSpotRate:
            startAvailableOnFastestSpot()
        else:
            startAvailableOnCheapestSpot()
        # assign machines
        #if S3.fresh < freshCopyMin * 0.001:
        #    startAvailableOnFastestOnDemand()
        #elif S3.fresh < freshCopyMin * 0.01:
        #    startAvailableOnCheapestOnDemand()
        #elif S3.fresh < freshCopyMin * 0.1:
        #    startAvailableOnFastestSpot()
        #elif S3.fresh < freshCopyMin:
        #    startAvailableOnCheapestSpot()

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


#TODO keep all traffic points; gen first?
count = 0

def traVariedDemand(step):
    global count
    global trafficHistory
    if trafficHistory[step] == None:
        if count >= 10 and count <= 13:
             trafficHistory[step] = trafficHistory[step-1] * random.randint(0,10)
             count += 1
        elif count > 13 and count <= 16:
             trafficHistory[step] = int(trafficHistory[step-1] / random.randint(1,10))
             count += 1
        else:
             trafficHistory[step] = random.randint(0,10)
             count = random.randint(0,10)
    return trafficHistory[step]

#TODO keep all traffic points; gen first?
# The step starts from mid-night
def traDailyDemand(step):
    global count
    global trafficHistory
    clockTime = step % 1440
    if trafficHistory[step] == None:
        if clockTime >= 0 and clockTime <= 360:   # everyone is sleeping
            trafficHistory[step] = random.randint(0,1) * random.randint(0,1) * random.randint(0,1) * random.randint(0,1)
        elif clockTime > 360 and clockTime <= 540:  # a few people start to work
            trafficHistory[step] = random.randint(0,2)
        elif clockTime > 540 and clockTime <= 720: # lot of people start to work and exponentially increase
            if count >= 10 and count <= 12:
                trafficHistory[step] = trafficHistory[step-1] * random.randint(2,10)
                count += 1
            elif count > 12 and count <= 14:
                trafficHistory[step] = int(trafficHistory[step-1] / random.randint(2,10))
                count += 1
            else:
                trafficHistory[step] = random.randint(2,10)
                count = random.randint(0,10)
        elif clockTime > 720 and clockTime <= 780: # lunch time
            trafficHistory[step] = random.randint(0,1)
        elif clockTime > 780 and clockTime <= 960: # back to work
            if count >= 10 and count <= 12:
                trafficHistory[step] = trafficHistory[step-1] * random.randint(2,10)
                count += 1
            elif count > 12 and count <= 14:
                trafficHistory[step] = int(trafficHistory[step-1] / random.randint(2,10))
                count += 1
            else:
                trafficHistory[step] = random.randint(2,10)
                count = random.randint(0,10)
        elif clockTime > 960 and clockTime <= 1080: # start to slack off
            trafficHistory[step] = random.randint(0,3)
        elif clockTime > 1080 and clockTime <= 1200: # dinner time
            trafficHistory[step] = random.randint(0,1)
        elif clockTime > 1200 and clockTime <= 1320: # entertainment time
            trafficHistory[step] = random.randint(0,3)
        else:                                    # before sleep 
            trafficHistory[step] = random.randint(0,1)
    return trafficHistory[step]


#TODO Poisson process or Queuing theory arrival rate or 

#TODO arrivals peak during the day and ebb at night; e.g. sin(step % minuted_in_a_day)

#TODO rational (y=1/x) probability curve; high chance of low traffic, low chance of high traffic

#TODO Major release; start with really high demand and level out to constant; model actual Firefox release
def traFirefox(step):
    dpm = 5503 # average
    divisor = max(1, int(float(step)/float(2880)))
    return int(dpm/divisor)



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
    setSlaves(500)

    #Start with a high estimate; adaptive only
    # global calcFreshCopyMin
    # calcFreshCopyMin = freshCopyMin * 2

    global S3
    S3 = Storage.Storage(0,33) # copies per GB
    
    global FastestOnDemandRate
    FastestOnDemandRate = int(500/8)
    global CheapestOnDemandRate
    CheapestOnDemandRate = int(500/15)
    global FastestSpotRate
    FastestSpotRate = int(FastestOnDemandRate/2)
    
    

##### Setups

#TODO load available instances to a list for easy management
def initSmallApp():
    global instances
    instances = []
    instances.append(Instance.Instance('C1.Medium Spot',      21, 5, 0.00046, True))
    instances.append(Instance.Instance('C1.XLarge Spot',      8,  2, 0.00186, True))
    instances.append(Instance.Instance('C1.Medium On-Demand', 21, 5, 0.00241, False))
    instances.append(Instance.Instance('C1.XLarge On-Demand', 8,  2, 0.00967, False))
    #TODO adjust number of slaves
    setSlaves(500)

    #Start with a high estimate; adaptive only
    # global calcFreshCopyMin
    # calcFreshCopyMin = freshCopyMin * 2

    global S3
    S3 = Storage.Storage(0,100) # copies per GB
    
    global FastestOnDemandRate
    FastestOnDemandRate = int(500/3)
    global CheapestOnDemandRate
    CheapestOnDemandRate = int(500/6)
    global FastestSpotRate
    FastestSpotRate = int(FastestOnDemandRate/1.5)


##### Setups

#TODO load available instances to a list for easy management
def initLargeApp():
    global instances
    instances = []
    instances.append(Instance.Instance('C1.Medium Spot',      252, 60, 0.00046, True))
    instances.append(Instance.Instance('C1.XLarge Spot',      100,  28, 0.00186, True))
    instances.append(Instance.Instance('C1.Medium On-Demand', 252, 60, 0.00241, False))
    instances.append(Instance.Instance('C1.XLarge On-Demand', 100,  28, 0.00967, False))
    #TODO adjust number of slaves
    setSlaves(500)

    #Start with a high estimate; adaptive only
    # global calcFreshCopyMin
    # calcFreshCopyMin = freshCopyMin * 2

    global S3
    S3 = Storage.Storage(0,8) # copies per GB
    
    global FastestOnDemandRate
    FastestOnDemandRate = int(500/29)
    global CheapestOnDemandRate
    CheapestOnDemandRate = int(500/61)
    global FastestSpotRate
    FastestSpotRate = int(FastestOnDemandRate/2)


##### Helper Functions


def doRemoveStale():
    global S3
    removeStale = 0
    if S3.stalePct() > keepStalePct: #TODO change to real cleanup algorithm; if demand is up then keep more stale
        if S3.fresh < calcFreshCopyMin:
            removeStale = int(S3.total - calcFreshCopyMin)
        elif S3.total > calcFreshCopyMin:
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

def setSlaves(num):
    global numberOfSlaves
    numberOfSlaves = num
    initSlaves()
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

#TODO
    # percentComplete = currentStep/stepsInSim
    # if percentComplete:
    #     sys.stdout.write(".")
    if currentStep == stepToStartTraffic:
        sys.stdout.write('+')

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