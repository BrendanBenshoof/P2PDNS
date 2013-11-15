### ripped add credits
"""
'stolen' with much thanks to:

Licence: GNU Lesser General Public License (LGPL) version 2.1 (http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)

Author: Benjamin Evans

Email: benny.j.evans92_at_gmail.com (replace at with @)


https://github.com/BennyEvans/PyChordDHT
"""
import hashlib
import random
class Key():
    def __init__(self, key):
        self.key = key

    def __eq__(self, other):
        return hash_equal(self, other)

    def __str__(self):
        return str(self.key)

    def __hash__(self):
        return int(self.key,16)

    def toint(self):
        return int(self.key,16)

    def toXY(self):
        a = self.toint()
        y = a%(2**(KEY_SIZE/2))
        x = a >> (KEY_SIZE/2)
        return (x,y)
#key size
KEY_SIZE = 160

#max chord index
MAX_INDEX = (0x01 << 160) - 1

#returns true if h1>h2
def hash_greater_than(h1, h2):
    if int(h1.key, 16) > int(h2.key, 16):
        return True
    return False

#returns true if h1<h2
def hash_less_than(h1, h2):
    if int(h1.key, 16) < int(h2.key, 16):
        return True
    return False

#returns true if h1==h2
def hash_equal(h1, h2):
    if int(h1.key, 16) == int(h2.key, 16):
        return True
    return False

#returns True if h1 is between s1 and s2
def hash_between(h1, s1, s2):
    
    #if s1 == s2 then h1 must be between them assuming a full loop
    if(hash_equal(s1, s2)):
        return True

    #if h1 == s1 || h1 == s2 then return False
    if(hash_equal(h1, s1) or hash_equal(h1, s2)):
        return False

    #Check if s2 < s1 - if so assume a loop
    if hash_less_than(s2, s1):
        #assume a loop around the circle in which case h1 must be h1 > s1 || h1 < s2
        if hash_greater_than(h1, s1) or hash_less_than(h1, s2):
            return True
    else:
        #normal s1 < h1 < s2
        if hash_greater_than(h1, s1) and hash_less_than(h1, s2):
            return True
        
    return False

def hash_between_right_inclusive(h1, s1, s2):
    
    #if s1 == s2 then h1 must be between them assuming a full loop
    if(hash_equal(s1, s2)):
        return True

    #if h1 == s1 || h1 == s2 then return False
    if(hash_equal(h1, s1)):
        return False

    if(hash_equal(h1, s2)):
        return True

    #Check if s2 < s1 - if so assume a loop
    if hash_less_than(s2, s1):
        #assume a loop around the circle in which case h1 must be h1 > s1 || h1 < s2
        if hash_greater_than(h1, s1) or hash_less_than(h1, s2):
            return True
    else:
        #normal s1 < h1 < s2
        if hash_greater_than(h1, s1) and hash_less_than(h1, s2):
            return True
        
    return False

def add_keys(k1, k2):
    x = (int(k1.key, 16) + int(k2.key, 16)) % MAX_INDEX
    return Key(hex(x).replace("L", ""))


def subtract_keys(k1, k2):
    x = (int(k1.key, 16) - int(k2.key, 16))
    if x < 0:
        x = MAX_INDEX + x
    return Key(hex(x).replace("L", ""))

    
def hash_str(strToHash):
    m = hashlib.sha1()
    m.update(strToHash)
    return Key("0x" + m.hexdigest())


def generate_key_with_index(index):
    return Key(hex(0x01 << index).replace("L", ""))

def generate_random_key():
    return Key(hex(random.getrandbits(160)).replace("L", ""))


def generate_lookup_key_with_index(thisIndex, indexOfKey):
    return add_keys(thisIndex, generate_key_with_index(indexOfKey))


def generate_reverse_lookup_key_with_index(thisIndex, indexOfKey):
    return subtract_keys(thisIndex, generate_key_with_index(indexOfKey))




