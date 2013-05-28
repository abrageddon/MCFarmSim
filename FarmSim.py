#!/usr/bin/env python
import SlaveMachine

Machine = SlaveMachine.SlaveMachine(3)

Machine.step()
print Machine.isDone()

print "Reset machine; shoule be false"
print Machine.startRun(30)#already running; cant reset till done
Machine.step()
print Machine.isDone()
Machine.step()

print "Done with one"
print Machine.isDone()

print "Start two"
print Machine.startRun(3)
Machine.step()
print Machine.isDone()
Machine.step()
print Machine.isDone()
Machine.step()

print "Done with two"
print Machine.isDone()

