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

    def __init__(self):
        pass
    def __init__(self, num, perGB=0):
        self.addCopies(num)
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
        if num > self.fresh:
            over = num - self.fresh
            self.freshDist += self.fresh
            self.staleDist += over
            self.fresh = 0
        else:
            if self.fresh > 0:
                self.fresh -= num
                self.freshDist += num
        return True
    def delCopies(self, num):
        if self.total <= 0 or num <= 0:
            return false

        self.total -= num
    def step(self):
        self.totalCost += self.costPerStep * float(self.total/self.copiesPerGB)

    def printStats(self):
        print 'Total Copies: ' + str(self.total)
        print 'Fresh Copies: ' + str(self.fresh)
        print 'Total Cost of Storage: ${0:.2f}'.format(self.totalCost)
        print '-' * 80
        print 'Fresh Copies Distributed: ' + str(self.freshDist)
        print 'Stale Copies Distributed: ' + str(self.staleDist)
        print 'Percent With Fresh Copy: {0:.2f}'.format( (float(self.freshDist) / float(self.freshDist + self.staleDist))*100 )