package P2PDNS;
import java.lang.Thread;
import java.util.ArrayList;
import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;

public class Main
{
    static Router router = Router.getInstance();
    static ArrayList<Service> services = new ArrayList<Service>();
    public static void main(String[] args)
    {

        Service echo = new EchoService();
        GLOBALS.ECHO = addService(echo);
        GLOBALS.NETSERV = addService(new NetServer());
        GLOBALS.NETSEND = addService(new NetSender());
       Message m = new Message(GLOBALS.ECHO,GLOBALS.NETSERV,new RegisterStruct(8000,GLOBALS.ECHO ));
        //System.out.println(m.text);
        echo.outbox.offer(m);

        start();
    }
    
    public static int addService(Service s)
    {
            services.add(s);
            return router.addService(s);
    }
    
    public static void start()
    {
            router.start();
            for(Service s: services)
            {
                    s.start();
            }
    }
    
}
