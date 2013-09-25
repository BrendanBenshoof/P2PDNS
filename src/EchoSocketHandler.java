import java.net.*;

public class EchoSocketHandler extends SocketHandler
{
    public EchoSocketHandler(Service a, Socket b)
    {
        super(a,b);
    }
    
    public void run()
    {
        String input = read();
        myService.sendMessage(0,input);
        close();
    }
}
