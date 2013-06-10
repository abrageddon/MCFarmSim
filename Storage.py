#!/usr/bin/env python
class Storage:
    description = """Node representing Amazon's S3"""
    total = 0
    fresh = 0

    freshDist = 0
    staleDist = 0

    costPerStep = 0.076/43800 #$/GB/min
    copiesPerGB = 100
    totalCost = 0

    def __init__(self, num, perGB=0):
        self.total = num
        self.fresh = num
        if perGB != 0:
            self.copiesPerGB = perGB
    def addCopies(self, num):
        if num <= 0:
            return False
        self.total += num
        self.fresh += num
        return True
    def takeCopies(self, num):
        if num <= 0:
            return True
        if self.total <= 0:
            print 'NO COPIES TO FUFILL REQUEST!!!'
            return False

        if num > self.total:
            print "DEMAND WAS HIGER THAN TOTAL COPIES: " + str(self.total) +'-'+ str(num)
            over = num - self.fresh
            self.freshDist += self.fresh
            self.staleDist += over
            self.fresh = 0
        elif num > self.fresh:
            over = num - self.fresh
            self.freshDist += self.fresh
            self.staleDist += over
            self.fresh = 0
        elif self.fresh > 0:
            self.fresh -= num
            self.freshDist += num

        return True

    def delCopies(self, num):
        if self.total <= 0 or self.total < num or self.total - self.fresh < num or num <= 0 or self.total <= self.fresh:
            return False
        self.total -= num
        return True

    def step(self):
        self.totalCost += self.costPerStep * float(self.total/self.copiesPerGB)

    def freshPct(self):
        if self.total == 0:
            return 0
        return (float(self.fresh) / float(self.total))
    def stalePct(self):
        if self.total == 0:
            return 0
        return (float(self.total - self.fresh) / float(self.total))
    def printStats(self):
        print 'Fresh Copies:   {0:10,}'.format(self.fresh)
        print 'Total Copies:   {0:10,}'.format(self.total)
        if self.total != 0:
            print 'Percent Fresh: {0:10,.1f}%'.format( self.freshPct()*100 )
        print '-' * 80
        print 'Stale Copies Distributed:   {0:10,}'.format(self.staleDist)
        print 'Fresh Copies Distributed:   {0:10,}'.format(self.freshDist)
        totalCopiesDist = self.freshDist + self.staleDist
        print 'Total Copies Distributed:   {0:10,}'.format( totalCopiesDist)
        if totalCopiesDist != 0:
            print 'Percent With A Fresh Copy: {0:10,.2f}%'.format( (float(self.freshDist) / float(totalCopiesDist))*100 )
        print '-' * 80
        print 'Total Cost of Storage: ${0:10,.2f}'.format(self.totalCost)




