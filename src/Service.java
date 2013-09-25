import java.util.concurrent.ConcurrentLinkedQueue;
import java.lang.Runnable;
import java.lang.Thread;

abstract class Service implements Runnable
{
    ConcurrentLinkedQueue<Message> inbox;
    ConcurrentLinkedQueue<Message> outbox;
    protected boolean alive = true;
    protected int myid = -1;
    private Thread mythread;
    
    public void run()
    {
        while(alive)
        {
            try
            {
                Thread.sleep(1);
            }
            catch(InterruptedException e)
            {
                ;
            }
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
    
    public abstract void handleMessage(Message m);
    
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
