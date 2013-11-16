#difficulty calculator
from math import log as lg

rate = 100 #hash/sec
idealreward = 1.0/60.0 #block/sec
"""
idealreward = 1-(1-difficulty)**rate
lg(id - 1)/lg(rate) = 1 - difficulty
1- lg(id - 1)/lg(rate) = difficulty
"""
difficulty = lg(1-idealreward**rate,.5)

print difficulty
print (2**(160-difficulty))/(2**160)