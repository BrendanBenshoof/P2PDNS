#Mining Service
import voronoinode as node
from message import Message
from service import Service
from userinfo import *
import hash_util
import rsa
import time
import os
from random import choice

d_rate = 0.110924374808
difficulty = (2.0**160-1)*d_rate
GENSIS_BLOCK = """0
0
0+.+AWARD+Brendan:0x540be95c12e72a28c32388994ff0efb12ac63ca7:0x800b400ed966fcc0d4807adf5e884f1ed6af227aaeb00c463ebdf473d4da1b9bde466a9d155df80dbc565575a5130344691425d0f705c88514d77912f3fd339d?0x10001>++
1384617855.6170001
0"""


class minerMessage(Message):
    def __init__(self,type):
        Message.__init__(self,"MINER",type)

class Miner_Service(Service):
    """Handler of Chord behavoir and internal messages"""
    def __init__(self):
        super(Miner_Service, self).__init__()
        self.service_id = "MINER"
        self.priority = 1 #highest priority
        self.chainhandler = blockchain_manager(".\\DB\\")
        self.chainhandler.bootstrap()
    def handle_message(self, msg):
        ##new block messages
        ##catchup messages
        if msg.type =="newblock":
            raw_block = msg.get_content("block")
            parsed_block = Block.gen(raw_block)
            state = self.chainhandler.offer(parsed_block) #true if this is valid new block
            if state:
                new_msg = minerMessage("newblock")
                new_msg.add_content("block",raw_block)
                for p in node.peers:
                    new_msg.destination_key = p.key
                    self.send_message(new_msg, p)
        if msg.type == "catchup":
            print "got a catchup"
            last_id = msg.get_content("last key")
            response = {}
            for k in self.chainhandler.blocks.keys():
                if int(k) > last_id:
                    response[k] = str(self.chainhandler.blocks[k])
            resp = minerMessage("catchup-reply")
            resp.destination_key = msg.reply_to.key
            resp.add_content("blocks", response)
            self.send_message(resp, msg.reply_to)
        if msg.type == "catchup-reply":
            print "got a catchup-reply"
            print sorted(msg.get_content("blocks").keys(), key=int)
            for k in sorted(msg.get_content("blocks").keys(), key=int):
                raw_b = msg.get_content("blocks")[k]
                b= Block.gen(raw_b)
                self.chainhandler.offer(b)


    def attach_to_console(self):
        ### return a list of command-strings

        #Make sure there is a record of my own userinfo
        #Check and see if there is a mining todo list
        #start mining subprocesses
        return ["claim", "update-chain","save"]

    def handle_command(self, comand_st, arg_str):
        if comand_st == "claim":
            args = arg_str.split(" ")
            domain_owner = UserInfo.load(args[0])
            t = transaction()
            t.fromUser = "AWARD"
            t.toUser = domain_owner.gen_secret(False)
            t.domain = args[1]
            raw = self.chainhandler.mine([],t)
            new_msg = minerMessage("newblock")
            new_msg.add_content("block",raw)
            for p in node.peers:
                new_msg.destination_key = p.key
                self.send_message(new_msg, p)
        if comand_st == "save":
            self.chainhandler.write()
        if comand_st == "update-chain":
            self.chainhandler.currentBlock = Block.gen(GENSIS_BLOCK)
            self.chainhandler.blockid = 0
            p = choice(node.peers)
            m = minerMessage("catchup")
            m.reply_to = self.owner
            m.add_content("last key",0)
            self.send_message(m,p)



class transaction(object):
    #FORMAT
    #Transaction id is blockid.transactionum
    #transaction_num+domain+from_usrid+to_usrid+proofid+sig_from_usr
    #from_usrid = "AWARD" if this is a mining award

    def __init__(self):
        self.tansactionID = ""
        self.fromUser = ""
        self.proofid = ""
        self.toUser = ""
        self.domain = ""
        self.sig = ""

    def checksig(self):
        if(self.fromUser == "AWARD"):
            return True 
        fromusr = UserInfo.from_secret(self.fromUser)
        tosign = self.domain+"+"+self.fromUser+"+"+self.toUser
        return fromusr.validate(tosign, self.sig)

    def __str__(self):
        output = ""
        output += self.domain+"+"+self.fromUser+"+"+self.toUser+"+"+self.proofid+"+"+self.sig
        return output

    @classmethod
    def gen(cls, string, Tid):
        self = cls()
        stuff = string.split("+")
        self.transactionID = str(Tid)+"."+stuff[0]
        #print stuff
        self.domain = stuff[1]
        self.fromUser = stuff[2]
        self.toUser = stuff[3]
        self.proofid = stuff[4]
        self.sig = stuff[5]
        return self
"""
#blocks are shaped like:
hash_of_last
blockid
trans1
trans2
...
award
time
nonce
"""

class Block(object):
    def __init__(self):
        self.raw = ""
        self.blockid = 0
        self.lasthash = ""
        self.time = ""
        self.nonce = ""
        self.transactions = []
        self.award = None
    @classmethod
    def gen(cls, string):
        self = cls()
        self.raw = string
        stuff = string.split("\n")
        self.lasthash = stuff[0]
        self.blockid = stuff[1]
        keeptrack = 1
        for i in range(2,len(stuff)-4):
            #print "TRANS"
            self.transactions.append(transaction.gen(stuff[i],self.blockid))
            keeptrack = i
        keeptrack+=1
        self.award = transaction.gen(stuff[keeptrack], self.blockid)
        #print self.award
        keeptrack+=1
        self.time = stuff[keeptrack]
        keeptrack+=1
        self.nonce = stuff[keeptrack]
        return self
    def gethashval(self):
        if self.raw == "":
            self.raw = str(self)
        return hash_util.hash_str(self.raw).key
    def __str__(self):
        output = ""
        output+=self.lasthash+"\n"
        output+=str(self.blockid)+"\n"
        c = 0
        for i in self.transactions:
            output+= str(c)+"+"+str(i)+"\n"
            c+=1
        output+=str(c)+"+"+str(self.award)+"\n"
        output+=self.time+"\n"
        output+=self.nonce
        return output


class blockchain_manager(object):
    def __init__(self, directory):
        self.dir = directory
        self.blocks = {}
        self.currentBlock = None
        self.currentid = 0
        self.domains = {}

    def bootstrap(self):
        newblock = Block.gen(GENSIS_BLOCK)
        self.currentBlock = newblock

    def get_owner(self,domain):
        if domain in self.domains.keys():
            return self.domains[domain]
        else:
            return None

    def write(self):
        for k in self.blocks:
            fp  = open(os.path.join(self.dir,k+".block"),"w+")
            fp.write(str(self.blocks[k]))
            fp.close()

    def load(self):
        loaded = {}
        onlyfiles = [ f for f in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir,f)) ]
        for fname in onlyfiles:
            if fname[-6:] == ".block":
                fp = open(os.path.join(self.dir,fname),"r")
                raw = fp.read()
                b = Block.gen(raw)
                k = fname[:-6]
                loaded[k] = b
        keys = sorted(loaded.keys(), key=int)
        for k in keys:
            if not self.offer(loaded[k]):
                break

    def validate(self, RAW_DNS, sig, domain):
        owner = self.get_owner(domain)
        print domain
        if not owner is None:
            owner = UserInfo.from_secret(owner)
            try:
                return owner.validate(RAW_DNS,sig)
            except VerificationError:
                return False
        return False

    def offer(self, newblock):
        #does it match the last block?
        if self.currentBlock.gethashval() == newblock.lasthash:
            if int(self.currentBlock.blockid)+1 == int(newblock.blockid):
                #are the transactions valid?
                valid = True
                for t in newblock.transactions:
                    if not t.checksig():
                        valid = False
                        break
                    self.domains[t.domain] = t.toUser
                self.domains[newblock.award.domain] = newblock.award.toUser
                if valid:
                    #we should really validate everything better, but meh
                    self.blocks[newblock.blockid] = newblock
                    self.currentBlock = newblock
                    self.currentid = int(newblock.blockid)
                    print "Block Accepted:"+str(self.currentid)
                    return True
        return False

    def mine(self, transfers, award):
        done = False
        newblock = Block()
        while not done:
            curr = self.currentBlock
            #print curr
            newblock = Block()
            newblock.lasthash = curr.gethashval()
            newblock.blockid = str(int(curr.blockid)+1)
            newblock.award = award
            newblock.transactions = transfers
            newblock.time = str(time.time())
            newblock.nonce = hash_util.generate_random_key().key
            hashval = int(newblock.gethashval(),16)
            print float(hashval), difficulty
            if hashval < difficulty:
                break
            else:
                time.sleep(0.01)
                print "fail"
        print "new block"
        self.offer(newblock)
        return str(newblock)


