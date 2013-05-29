#!/usr/bin/env python
import SlaveMachine, Storage

numberOfSlaves = 19
Slaves = []
S3 = None

def main():
    setup()

    #RUN ALGORITHM

    for i in enumerate(10):
        step()
        #RUN ALGORITHM

    #REPORT STATS
    S3.printStats

def setup():
    S3 = Storage.Storage(1)
    for i in enumerate(numberOfSlaves):
        Slaves.append(SlaveMachine.SlaveMachine(0))

def step():
    for slave in Slaves:
        slave.step()
        if slave.isDone():
            S3.addCopies(1)
    S3.step()

def test():
    Machine = SlaveMachine.SlaveMachine(3)
    S3 = Storage.Storage(1)

    Machine.step()
    Machine.isDone()

    print "Trying to interrupt build; should be false: " + str(Machine.startRun(30))#already running; cant reset till done
    Machine.step()
    Machine.isDone()

    Machine.step()
    print "Done with one: " + str(Machine.isDone())
    S3.addCopies(1)

    S3.takeCopies(2)

    print "Start two"
    Machine.startRun(3)
    Machine.step()
    Machine.isDone()

    S3.takeCopies(2)

    Machine.step()
    Machine.isDone()
    Machine.step()

    print "Done with two: " + str(Machine.isDone())
    S3.addCopies(1)

    S3.takeCopies(2)
    S3.printStats()
    print Machine.totalCost


if __name__ == '__main__':
    # main()
    test()
