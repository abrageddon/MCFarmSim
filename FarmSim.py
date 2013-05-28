#!/usr/bin/env python
import SlaveMachine

Machine = SlaveMachine.SlaveMachine(3)

Machine.step()
print Machine.isDone()
Machine.step()
print Machine.isDone()
Machine.step()
print Machine.isDone()

