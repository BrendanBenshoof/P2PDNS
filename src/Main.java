import java.lang.Thread;
import java.util.ArrayList;


class Main
{
 static Router router = Router.getInstance();
 static ArrayList<Service> services = new ArrayList<Service>();
  public static void main(String[] args)
  {

    Service echo = new Service();
    int echo_id = addService(echo);
    int c_id = addService(new Clock(echo_id));
    
    //addService(new NetworkTest());
    
    Message spoofed = new Message(echo_id, c_id, "kickstart");
    echo.outbox.offer(spoofed);


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
