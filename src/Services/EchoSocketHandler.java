package P2PDNS.Services;
import java.net.*;
import P2PDNS.MessageStructs.*;

public class EchoSocketHandler extends SocketHandler
{
    int forward;
    public EchoSocketHandler(Service a, Socket b)
    {
        super(a,b);
        forward = 0;
    }
    
    public EchoSocketHandler(Service a, Socket b, int f)
    {
        super(a,b);
        forward = f;
    }
    
    public void run()
    {
        String input = read();
        NetMessage m = 
            new NetMessage( input,
                            mySocket.getInetAddress().getHostAddress(),
                            mySocket.getPort(),
                            mySocket.getLocalPort());

        myService.sendMessage(forward,m);
        close();
    }
}
