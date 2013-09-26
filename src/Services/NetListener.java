package P2PDNS.Services;

import java.net.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.io.*;
import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;

public class NetListener implements Runnable
{
    Service myservice;
    private ServerSocket server;
    int replyport;
    public NetListener(Service N, int netport, int replyport)
    {
        this.replyport = replyport;
        myservice = N;
        try{
            server = new ServerSocket(netport);
        }
        catch(IOException e)
        {
            System.out.println("looks like it broke");
            System.exit(0);
        }
    }
    

    
    public void run()
    {
        for(;;)
        {
            try{
            Socket client = server.accept();
            new EchoSocketHandler(myservice, client,replyport);
            }
            catch(IOException e){;}
        }
    }
}
