import java.lang.Thread;
import java.util.ArrayList;


class Main
{
    static Router router = Router.getInstance();
    static ArrayList<Service> services = new ArrayList<Service>();
    public static void main(String[] args)
    {

        Service echo = new EchoService();
        int echo_id = addService(echo);
     //   for(int i =0; i<1; i++) {
      //      addService(new Clock(echo_id));
       // }
     addService(new NetworkTest());
       // Message m = new Message(0,0,router);
        //System.out.println(m.text);
        

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
