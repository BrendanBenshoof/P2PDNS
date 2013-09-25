import java.lang.Thread;
import java.lang.Runnable;


class Clock extends Service
{
    private class Ticker implements Runnable
    {
        Clock owner;
        int target;
        int count = 0;
        public void run()
        {
            while(true)
            {
                try{
            Thread.sleep(1);
            owner.sendMessage(target,"tick"+count++);
                if(count > 10000)
                {
                    System.exit(0);
                }
                }
                catch(java.lang.InterruptedException e)
                {;}
            }
        }
    }
    
    public void handleMessage(Message m){;}
    
    int target = 0;
    public Clock(int t)
    {
        super();
        Ticker tick = new Ticker();
        tick.owner = this;
        tick.target = t;
        Thread ticker = new Thread(tick);
        ticker.start();        
    }
    
}
