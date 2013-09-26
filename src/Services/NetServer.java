package P2PDNS.Services;

import java.net.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.io.*;
import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;


public class NetServer extends Service
{
    NetListener server;
    public void handleMessage(Message m){
        try{
            RegisterStruct R = (RegisterStruct)(m.deserialize());

        server = new NetListener(this, R.port, R.returnService);
        Thread serverThread = new Thread(server);
        serverThread.start();
        }
        catch(ClassCastException e)
        {
            return;
        }
        }
    public NetServer()
    {
        super();
    }
    
}
