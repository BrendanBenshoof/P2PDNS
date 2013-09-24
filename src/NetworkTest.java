import java.net.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.io.*;


class NetworkTest extends Service
{
    class NetServer implements Runnable
    {
        NetworkTest myservice;
        private ServerSocket server;
        public NetServer(NetworkTest N)
        {
            myservice = N;
            try{
                server = new ServerSocket(9000);
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
                BufferedReader in = new BufferedReader(new InputStreamReader(
                                        client.getInputStream()));
                boolean done = false;
                while(!done)
                {
                    try{
                    String stuff = in.readLine();
                    if(stuff == null)
                    {
                        done = true;
                        break;
                    }
                    sendMessage(0,stuff);
                    }
                    catch(IOException e)
                    {
                        done = true;
                    }
                    
                }
                }
                catch(IOException e)
                {
                    System.out.println("it broke");
                }
            }
        }
    }

    NetServer server;
    
    public NetworkTest()
    {
        super();
        server = new NetServer(this);
        Thread serverThread = new Thread(server);
        serverThread.start();
    }
    
}
