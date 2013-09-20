import java.lang.Thread;

class Main
{
 
  public static void main(String[] args)
  {
    Router r = Router.getInstance();
    Service echo = new Service();
    int echo_id = r.addService(echo);
    Clock c = new Clock(echo_id);
    int c_id = r.addService(c);
    Message spoofed = new Message(echo_id, c_id, "kickstart");
    echo.outbox.offer(spoofed);
    
    Thread r_thread = new Thread(r);
    Thread c_thread = new Thread(c);
    Thread e_thread = new Thread(echo);
    r_thread.start();
    c_thread.start();
    e_thread.start();    
  }
  
  
}