from service import Service
from threading import Lock
import threading
import time
import hash_util
import shelve
import voronoinode as node
from message import Message
from globals import *

GET = "GET"
PUT = "PUT"
DATABASE = "DATABASE"
RESPONSE = "RESP"

class Database_Message(Message):
    def __init__(self, origin_node, destination_key, Response_service=SERVICE_SHELVER, file_type="GET"):
        Message.__init__(self, SERVICE_SHELVER, file_type)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.add_content("service",Response_service)
        self.reply_to = origin_node

class Database_Backup_Message(Message):
    def __init__(self, origin_node, backup_pile):
        Message.__init__(self, SERVICE_SHELVER, "BACKUP")
        self.origin_node = origin_node
        self.add_content("backup",backup_pile)
        self.reply_to = origin_node

def backup_loop(self):
    while True:
        self.periodic_backup()

class Shelver(Service):
    """docstring for Database"""
    def __init__(self, db):
        super(Shelver, self).__init__()
        self.service_id = SERVICE_SHELVER

        self.write_lock = Lock()
        self.db = db
        self.own_start = None
        self.own_end = None
        self.back_thread = threading.Thread(target=lambda:  backup_loop(self) )
        self.back_thread.daemon = True
        self.back_thread.start()
        

    def __lookup_record(self, hash_name):
        records = shelve.open(self.db)
        content = None
        try:
            print "looking up:"+hash_name
            content = records[hash_name]    #this retrieved COPY OF CONTENT
        except KeyError: 
            content =  "404 Error"
        finally:
            records.close()
            return content

    def __write_record(self, hash_name,content):
        self.write_lock.acquire()
        records = shelve.open(self.db)
        records[hash_name] = content
        records.close()
        self.write_lock.release()
        return True

    def put_record(self,name,data):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Message(self.owner,hash_loc,DATABASE,PUT)
        newmsg.add_content("file_contents",data)
        self.send_message(newmsg, None)

    def get_record(self,name,return_service="DATABASE"):
        hash_loc = hash_util.hash_str(name)
        newmsg = Database_Message(self.owner,hash_loc,SERVICE_ECHO,GET)
        self.send_message(newmsg, None)

    def attach_to_console(self):
        ### return a dict of command-strings
        return ["put","get","test_store","test_get"]

    def handle_command(self, command_st, arg_str):
        ### one of your commands got typed in
        if command_st == "put":
            args = arg_str.split(" ",1)
            key = args[0]
            value = args[1]
            self.put_record(key,value)
        elif command_st == "get":
            self.get_record(arg_str)
        elif command_st == "test_store":
            newfile = file("shelver.py","r")
            counter=0
            for l in newfile:
                self.put_record("book:"+str(counter),l)
                counter+=1
                print counter
            newfile.close()
        elif command_st == "test_get":
            args = arg_str.split(" ",1)
            line = args[0]
            self.get_record("book:"+line)
            


    def handle_message(self, msg):
        if not msg.service == self.service_id:
            return False
        if msg.type == "GET":
            filename = str(msg.destination_key)
            content = self.__lookup_record(str(filename))
            #this add other instances of database messages are borked
            return_service = msg.get_content("service")
            newmsg = Database_Message(self.owner, msg.reply_to.key, return_service, "RESP")
            newmsg.add_content("file_contents",content)
            newmsg.add_content("destkey",msg.destination_key)
            newmsg.service=return_service
            self.send_message(newmsg, msg.reply_to)
        if msg.type == "PUT":
            filename = str(msg.destination_key)
            self.__write_record(filename,msg.get_content("file_contents"))
        if msg.type == "RESP":
            print msg.get_content("file_contents")
        if msg.type == "BACKUP":
            self.integrate(msg.get_content("backup"))
    
    def integrate(self, new_data): #take a backup dump and integrate with my own data
        #WARNING THIS CODE TRUSTS PEERS
        for k in new_data.keys():
            self.__write_record(k,new_data[k])
    
    def change_in_responsibility(self,new_pred_key, my_key):
        self.own_start = new_pred_key
        self.own_end = my_key
        backup = {}
        self.write_lock.acquire()
        records = shelve.open(self.db)
        for k in records.keys():
            k_key = hash_util.Key(k)
            if not node.I_own_hash(k_key):
                backup[k] = records[k]
        msgbuckets = {}
        for k in backup.keys():
            k_key = hash_util.Key(k)
            best_foward = node.find_ideal_forward(k_key)
            if best_foward in msgbuckets.keys():
                msgbuckets[best_foward][k] = backup[k]
            else:
                msgbuckets[best_foward] = {}
                msgbuckets[best_foward][k] = backup[k]
        for n in msgbuckets.keys():
            if n != self.owner:
                newmsg = Database_Backup_Message(self.owner, msgbuckets[n])
                self.send_message(newmsg,n)
        records.close()
        self.write_lock.release()
    
    def periodic_backup(self):
        time.sleep(10)
        backup = {}
        self.write_lock.acquire()
        records = shelve.open(self.db)
        for k in records.keys():
            k_key = hash_util.Key(k)
            if node.I_own_hash(k_key):
                backup[k] = records[k]
        size = len(backup.keys())
        if size > 0:
            for n in node.peers:
                newmsg = Database_Backup_Message(self.owner, backup)
                newmsg.destination_key = n.key
                self.send_message(newmsg,n)
        records.close()
        self.write_lock.release()
          
