import java.util.concurrent.ConcurrentLinkedQueue;
import java.lang.Runnable;
import java.lang.Thread;

class Service implements Runnable
{
  ConcurrentLinkedQueue<Message> inbox;
  ConcurrentLinkedQueue<Message> outbox;
  boolean alive = true;
  int myid = -1;
  private Thread mythread;
  
  public void run()
  {
    while(alive)
    {
        try
        {
        Thread.sleep(0);
        }
        catch(InterruptedException e)
        {;}
      Message m = inbox.poll();
      if(m != null)
      {
        handleMessage(m);
      }
    }
  }
  
  public void sendMessage(int dest, String message)
  {
    Message m = new Message(myid, dest, message);
    outbox.offer(m);
  }
  
  public void handleMessage(Message m)
  {
    String msg = m.text;
    System.out.println(msg);
  }
  
  public void start()
  {
      mythread.start();
  }
  
  public Service()
  {
    inbox = new ConcurrentLinkedQueue<Message>();
    outbox = new ConcurrentLinkedQueue<Message>();
    mythread = new Thread(this);
  }
  
}
