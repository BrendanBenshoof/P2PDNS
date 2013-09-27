package P2PDNS.Services;

import java.net.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.io.*;
import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;


public class LittleDHT extends Service
{
    
    public enum MessageType { FIND, NOTIFY, EXIT }
    
    public enum RouteMode { DIRECT, LOOKUP }
    
    class Peer
    {
        String IP;
        int port;
        float id;
        
        public Peer(String IP, int port, float id)
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
    }
    
    
    Peer[] forwards;
    Peer sucessor;
    Peer predecessor;
    Peer me;
    
    public void run()
    {
        super.run();
    }
    public void handleMessage(Message m){;}
    
}
