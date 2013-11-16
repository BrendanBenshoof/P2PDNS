###signs a given file
from userinfo import *

handle = raw_input("Enter Handle:")
filename = raw_input("File to sign:")

fp = open(handle+".userinfo","r")
secret = fp.read()
user = UserInfo.from_secret(secret)
fp.close()

fp = open(filename,"r")
data = fp.read()
sig = user.sign(data)
fp.close()

fp = open(filename,"a")
fp.write("\n")
fp.write(sig)
fp.close()

print "file is signed"