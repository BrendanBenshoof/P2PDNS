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
            server = new ServerSocket(9000);
        }
        
        public void run()
        {
            for(;;)
            {
                Socket client = server.accept();
                OutputStream out = client.getOutputStream();
                out.write("HELLO WORLD".getBytes());
                client.close();
            }
        }
    }

    NetServer server;
    
    public NetworkTest()
    {
        super();
        server = new NetServer(this);
    }
    
}
