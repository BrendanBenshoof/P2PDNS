import shelver
import service
import hash_util
import Queue
import threading
import time

class Partial_file(object):
    def __init__(self,filename):
        self.filename = filename
        self.filehash_name = hash_util.hash_str(filename)
        self.done = False
        self.has_key = False
        self.input_stream = Queue.Queue()
        self.chunklist = []
        self.chunks = {}
    
    def add_key(self,keyfile):
        lines = keyfile.split("\n")
        if lines[0]!="KEYFILE":
            return False
        if lines[1]!=self.filename:
            return False
        for l in lines[2:]:
            self.chunklist.append(l)
        self.hash_key = True

    def process_queue(self):
        while not self.input_stream.empty():
            next_msg = self.input_stream.get(True,0.1)
            chunkid = str(next_msg.get_content("destkey"))
            addr, cont = next_msg.get_content("file_contents").split("\n",1)
            self.chunks[chunkid] = cont
            self.input_stream.task_done()
        done = True
        for c in self.chunklist:
            if not c in self.chunks.keys():
                done = False
        self.done = done
        return done

    def get_file(self,blocking=False):
        if self.done:
            output = ""
            for c in self.chunklist:
                output+=self.chunks[c]
            return output
        elif blocking:
            while not self.done:
                time.sleep(0.1)
            output = ""
            for c in self.chunklist:
                output+=self.chunks[c]
            return output
        else:
            return None
                

class FileSystem(service.Service):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self):
        super(FileSystem,self).__init__()
        self.service_id = "FileSystem"
        self.partial_files = {}

    def attach(self, owner, callback):
        """Called when the service is attached to the node"""
        """Should return the ID that the node will see on messages to pass it"""
        self.callback = callback
        self.owner = owner
        return self.service_id

    def read(self,filename):
        filehash = hash_util.hash_str(filename)
        new_partial = Partial_file(filename)
        self.partial_files[str(filehash)]=new_partial
        get_keyfile_message = shelver.Database_Message(self.owner,filehash, "FileSystem", "GET")
        self.send_message(get_keyfile_message,None)

    def store(self, filename,segment_size=128):
        segment_ids = []
        segments = []
        with open(filename, "rb") as f:
            byte = f.read(segment_size)
            while byte:
                newid = hash_util.generate_random_key().key
                segment_ids.append(newid)
                segments.append(byte)
                byte = f.read(segment_size)
        keyfile = "KEYFILE\n"+filename+"\n"+reduce(lambda x,y: x+"\n"+y,segment_ids)
        keyfile_hash = hash_util.hash_str(filename)
        keyfile_message = shelver.Database_Message(self.owner,keyfile_hash, "FileSystem", "PUT")
        keyfile_message.add_content("file_contents",keyfile)
        self.send_message(keyfile_message,None)
        number_of_chunks = len(segments)
        for i in range(0,number_of_chunks):
            chunkfile_message = shelver.Database_Message(self.owner,hash_util.Key(segment_ids[i]), "FileSystem", "PUT")
            actual_contents = str(keyfile_hash)+"\n"+segments[i]
            chunkfile_message.add_content("file_contents",actual_contents)
            self.send_message(chunkfile_message,None)


    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")
        if msg.type == "RESP":
            contents = msg.get_content("file_contents")
            fileid = msg.get_content("destkey")
            if contents[:7] == "KEYFILE":
                partial = self.partial_files[str(fileid)]
                partial.add_key(contents)
                for k in partial.chunklist:
                    get_datafile_message = shelver.Database_Message(self.owner,hash_util.Key(k), "FileSystem", "GET")
                    self.send_message(get_datafile_message,None)
            else:
                print contents
                addr, cont = contents.split("\n",1)
                if addr in self.partial_files.keys():
                    self.partial_files[addr].input_stream.put(msg)
                    if self.partial_files[addr].process_queue():
                        print "FINISHED FILE"
                        print self.partial_files[addr].get_file(True)
                


        return msg.service == self.service_id

    def attach_to_console(self):
        ### return a list of command-strings
        return ["store","read"]

    def handle_command(self, command_st, arg_str):
        if command_st == "store":
            self.store(arg_str)
        elif command_st == "read":
            self.read(arg_str)
        ### one of your commands got typed in
        return None

