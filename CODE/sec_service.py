from service import Service
from message import Message
import hash_util
import rsa

#store a list of vouchers by peers. Attempt to construct a voucher chain to a arbitary node
#wrap messages in encryption/decryption upon request

class SecNodeInfo(object):
    def __init__(self, handle, hashid, publickey, privatekey = None):
        self.handle = handle
        self.hashid = hashid
        self.publickey = publickey
        self.privatekey = privatekey

    def encrypt(self,msg):
        return rsa.encrypt(msg, self.publickey)
        #d = triple_des(self.key)
        #return d.encrypt(msg, padmode=PAD_PKCS5)

    def decrypt(self,msg):
        return rsa.decrypt(msg, self.privatekey)
        #d = triple_des(self.key, padmode=PAD_PKCS5)
        #return d.decrypt(msg)

    def sign(self, msg):
        hash_to_sign = hash_util.hash_str(msg).key
        return rsa.encrypt(hash_to_sign, self.publickey)

    def validate(self, msg, signature):
        return signature == self.sign(msg)

    @classmethod
    def generate_new(cls, handle):
        (pubkey, privkey) = rsa.newkeys(512)
        pubkey_str = hex(pubkey.n)[:-1]+"?"+hex(pubkey.e)[:-1]
        myhash = hash_util.hash_str(pubkey_str)
        return SecNodeInfo(handle,myhash,pubkey,privkey)

    def pub_key_str(self):
        return hex(self.publickey.n).replace("L", "")+"?"+hex(self.publickey.e).replace("L", "")

    def private_key_str(self):
        return '%(n)x?%(e)x?%(d)x?%(p)x?%(q)x' % self.privatekey

    @classmethod
    def from_secret(cls, string):
        if string == "NONE":
            return None
        parts = string.split(":")
        #print parts
        if len(parts) < 3:
            return None
        handle = parts[0]
        hashid = hash_util.Key(parts[1])
        keyparts = parts[2].split("?")
        pubkey = rsa.PublicKey(int(keyparts[0],16),int(keyparts[1],16))
        prikey = None
        if len(parts) == 4:
            keyparts = parts[3].split("?")
            keyints = map( lambda x: int(x,16), keyparts)
            prikey = rsa.PrivateKey(keyints[0],keyints[1],keyints[2],keyints[3],keyints[4])
        return SecNodeInfo(handle, hashid, pubkey, prikey)

    def gen_secret(self,prikey=False):
        if prikey and self.privatekey:
            return self.handle+":"+str(self.hashid.key)+":"+self.pub_key_str()+":"+self.private_key_str()
        else:
            return self.handle+":"+str(self.hashid.key)+":"+self.pub_key_str()


class SecMessage(Message):
    def __init__(self, origin_node, destination_key):
        Message.__init__(self, "SEC", "MSG")
        self.origin_node = origin_node  # node that just sent this message
        self.destination_key = destination_key  # the key we're trying to find the node responsible for
    def embed(self, othermsg):
        raw_data = othermsg.serialize()
        self.add_content("DATA",raw_data)

    def encrypt(self, destSecInfo):
        raw_data = self.get_content("DATA")
        destSecInfo.encrypt(raw_data)
        self.add_content("DATA",raw_data)

    def sign(self, mySecInfo):
        pass




class SECservice(Service):
    """Handler of Chord behavoir and internal messages"""
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = "SEC"
        self.priority = 1 #normal priority

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")
        return True

    def attach_to_console(self):
        ### return a list of command-strings
        return []

    def handle_command(self, comand_st, arg_str):
        pass
        ### one of your commands got typed in


