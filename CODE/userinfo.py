import hash_util
import rsa

class UserInfo(object):
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
        return rsa.sign(msg, self.privatekey)

    @classmethod
    def load(cls, filename):
        data = open(filename+".userinfo","r").read()
        return cls.from_secret(data)

    def validate(self, msg, signature):
        return rsa.verify(msg, signature, self.publickey)

    @classmethod
    def generate_new(cls, handle):
        (pubkey, privkey) = rsa.newkeys(1024)
        pubkey_str = hex(pubkey.n)[:-1]+"?"+hex(pubkey.e)[:-1]
        myhash = hash_util.hash_str(pubkey_str)
        return UserInfo(handle,myhash,pubkey,privkey)

    def pub_key_str(self):
        return hex(self.publickey.n).replace("L", "")+"?"+hex(self.publickey.e).replace("L", "")

    def private_key_str(self):
        return '%(n)x?%(e)x?%(d)x?%(p)x?%(q)x' % self.privatekey

    @classmethod
    def from_secret(cls, string):
        if string == "NONE":
            return None
        parts = string.split(":")
        ##print parts
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
        return UserInfo(handle, hashid, pubkey, prikey)

    def gen_secret(self,prikey=False):
        if prikey and self.privatekey:
            return self.handle+":"+str(self.hashid.key)+":"+self.pub_key_str()+":"+self.private_key_str()
        else:
            return self.handle+":"+str(self.hashid.key)+":"+self.pub_key_str()
