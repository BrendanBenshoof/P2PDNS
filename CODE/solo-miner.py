import hash_util
import sec_service

###first the struct for a block

#hash of Last Block|blockid|Exchanges|declaration|timestamp|nonce 
#64 bit int
#hash of last block = 160 bit hash of the previous block
#Exchanges = <Domain,Newowner>sig(oldowner)
#Declaration = <Domain, newowner>
#timestamp = unix epoc time
#none = 

# '|' is the divider between sections
# '+' is the divider between Exchanges
#EXAMPLE
"""
test = hash_util.hash_str("TEST")
print test
test_user = sec_service.SecNodeInfo.generate_new("Brendan")
print test_user.gen_secret(False)
"""
difficulty = 2**140


test="""0x0000000000000000000000000000000000000000|0||<test,Brendan:0x540be95c12e72a28c32388994ff0efb12ac63ca7:0x800b400ed966fcc0d4807adf5e884f1ed6af227aaeb00c463ebdf473d4da1b9bde466a9d155df80dbc565575a5130344691425d0f705c88514d77912f3fd339d?0x10001>|1384540375.4590001|"""


nonce = hash_util.generate_random_key()
newhash = hash_util.hash_str(test+str(nonce))
while newhash.toint() > difficulty:
	print 
	nonce = hash_util.generate_random_key()
	newhash = hash_util.hash_str(test+str(nonce))
print ""
print nonce
print newhash

