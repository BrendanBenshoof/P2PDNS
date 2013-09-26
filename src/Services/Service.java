package P2PDNS.Services;

import java.util.concurrent.ConcurrentLinkedQueue;
import java.lang.Runnable;
import java.lang.Thread;

import P2PDNS.MessageStructs.*;

public abstract class Service implements Runnable
{
    public ConcurrentLinkedQueue<Message> inbox;
    public ConcurrentLinkedQueue<Message> outbox;
    protected boolean alive = true;
    public int myid = -1;
    private Thread mythread;
    
    public void run()
    {
        while(alive)
        {
            try
            {
                Thread.sleep(2);
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
    
    public void sendMessage(int dest, Object message)
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
