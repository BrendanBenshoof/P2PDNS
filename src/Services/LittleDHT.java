package P2PDNS.Services;

import java.net.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.io.*;
import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;
import P2PDNS.*;

public class LittleDHT extends Service
{
    
    public enum MessageType { FIND, NOTIFY, EXIT }
    
    public enum RouteMode { DIRECT, LOOKUP }
    
    static Peer me;
    
    class Peer
    {
        String IP;
        int port;
        double id;
        
        public Peer(String IP, int port, double id)
        {
            this.IP = IP;
            this.port = port;
            this.id = id;
        }
        
    }
    
    class DHTmessage
    {
        MessageType type;//type of message 
        Peer origin;
        RouteMode routemode;
        Peer dest;
        String data;
        public DHTmessage (MessageType type, Peer dest, RouteMode routemode, String data)
        {
            this.type = type;
            this.dest = dest;
            this.origin = me;
            this.routemode = routemode;
            this.data = data;
        }
        
    }
    
    
    Peer[] forwards;
    Peer sucessor;
    Peer predecessor;
    
    public void run()
    {
        super.run();
    }
    public void handleMessage(Message m){;}
    
    public void sendNetMessage(DHTmessage m)
    {
        Message wrapped = new Message(0,0,m);
        SendMessageStruct s = new SendMessageStruct(m.dest.IP, m.dest.port, wrapped.text);
        this.sendMessage(GLOBALS.NETSERV,s);
    }
    
    public void setup()
    {
        Peer entrypoint = new Peer("127.0.0.1", 9000, 0.0);
        RegisterStruct r = new RegisterStruct(9000,myid);
        this.sendMessage(GLOBALS.NETSERV,r);
        DHTmessage init = new DHTmessage(MessageType.FIND, entrypoint, RouteMode.LOOKUP, Double.toString(me.id));
        this.sendNetMessage(init);
    }
    
}
