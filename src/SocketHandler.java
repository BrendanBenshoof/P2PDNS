import java.net.Socket;
import java.io.*;
import java.lang.Thread;
import java.lang.Runnable;
public abstract class SocketHandler implements Runnable
{   protected Service myService;
    protected Socket mySocket;
    public SocketHandler(Service parent, Socket s)
    {
        myService = parent;
        mySocket =s;
        Thread myThread = new Thread(this);
        myThread.start();
    }
    protected boolean send(String s)
    {
        try
        {
        PrintWriter out = new PrintWriter(mySocket.getOutputStream(), true);
        out.print(s);
        }
        catch(IOException e){return false;}
        return true;
    }
    
    public abstract void run();
    
    protected boolean close()
    {
        
        try
        {
        mySocket.close();
        }
        catch(IOException e){return false;}
        return true;

    }
    
    protected String read()
    {
        try
        {
        BufferedReader in = new BufferedReader(new InputStreamReader(mySocket.getInputStream()));
        boolean done = false;
        String stuff = "";
        while(!done)
        {
            try
            {
                String newstuff = in.readLine();
                
                //System.out.print(stuff);
                if(newstuff == null)
                {
                    done = true;
                    break;
                }
                stuff += newstuff;
            }
            catch(IOException e)
            {
                done = true;
            }
            
        }
        return stuff;
                }
        catch(IOException e){return "";}
    }
    
}
