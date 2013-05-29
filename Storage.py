#!/usr/bin/env python
class Storage:
    description = """Node representing Amazon's S3"""
    total = 0
    fresh = 0

    freshDist = 0
    staleDist = 0

    costPerStep = 0.1
    totalCost = 0

    def __init__(self):
        pass
    def __init__(self, num, cost=0.1):
        self.addCopies(num)
        self.costPerStep = cost

    def addCopies(self, num):
        if num <= 0:
            return False
        self.total += num
        self.fresh += num
        return True
    def takeCopies(self, num):
        if self.total <= 0 or num <= 0:
            return false
        over = 0
        if num > self.fresh:
            over = num - self.fresh
            if self.fresh > 0:
                self.freshDist += self.fresh
                self.staleDist += over
                self.fresh = 0
        else:
            if self.fresh > 0:
                self.fresh -= num
                self.freshDist += num
            else:
                self.staleDist += num
        return True
    def delCopies(self, num):
        if self.total <= 0 or num <= 0:
            return false

        self.total -= num
    def step():
        self.totalCost += self.costPerStep * self.total

    def printStats(self):
        print '=' * 80
        print 'Total Copies: ' + str(self.total)
        print 'Fresh Copies: ' + str(self.fresh)
        print 'Total Cost: ' + str(self.totalCost)
        print '-' * 80
        print 'Fresh Copies Distributed: ' + str(self.freshDist)
        print 'Stale Copies Distributed: ' + str(self.staleDist)
        print '=' * 80