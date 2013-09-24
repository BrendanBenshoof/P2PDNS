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
                OutputStream out = client.getOutputStream();
                out.write("HELLO WORLD\n".getBytes());
                client.close();
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
