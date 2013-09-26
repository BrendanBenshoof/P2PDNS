package P2PDNS;

import java.util.ArrayList;
import java.lang.Thread;

import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;

public class Router implements java.lang.Runnable
{
    boolean alive = true;
    ArrayList<Service> table;
    static Router instance;
    private Thread mythread;
    
    public Router()
    {
        table = new ArrayList<Service>();
        mythread = new Thread(this);

    }
    
    public void start()
    {
        mythread.start();
    }
    
    public static synchronized Router getInstance()
    {
        if(instance==null)
        {
            instance = new Router();
        }
        return instance;
    }
    
    public void run()
    {
        while(alive)
        {
            try
            {
                Thread.sleep(0);
            }
            catch(InterruptedException e){;}
            route();
        }
    }

    public void route()
    {
        for( Service s: table)
        {
            Message m = s.outbox.poll();
            while(m!=null)
            {
                Integer dest = m.dest;
                table.get(dest).inbox.offer(m);
                m = s.outbox.poll();
            }
        }
    }
    
    public int addService(Service s)
    {
        int res = table.size();
        table.add(s);
        s.myid = res;
        return res;
    }
    
}
