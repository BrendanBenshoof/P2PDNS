package P2PDNS.Services;

import java.net.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.io.*;
import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;


public class NetworkTest extends Service
{
    
    class NetServer implements Runnable
    {
        NetworkTest myservice;
        private ServerSocket server;
        public NetServer(NetworkTest N)
        {
            myservice = N;
            try{
                server = new ServerSocket(8000);
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
                new EchoSocketHandler(myservice, client);
                }
                catch(IOException e){;}
            }
        }
    }

    NetServer server;
    public void handleMessage(Message m){;}
    public NetworkTest()
    {
        super();
        server = new NetServer(this);
        Thread serverThread = new Thread(server);
        serverThread.start();
    }
    
}
