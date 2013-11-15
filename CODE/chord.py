#!/usr/bin/env python
###Startup and commandline file
from subprocess import Popen
from time import sleep
from random import random
die_chance = 0.0000775

thingy = Popen(["./chordreduce.py", "?", "54.225.230.238","9000"])
sleep(20)
while(True):
    sleep(1)
    if random() < die_chance:
        thingy.kill()
        sleep(1)
        thingy = Popen(["./chordreduce.py", "?", "54.225.230.238","9000"])
        sleep(20)
        
