package P2PDNS.Services;

import P2PDNS.MessageStructs.*;

public class EchoService extends Service 
{
    public void handleMessage(Message m) 
    {
        System.out.println(m.text);
    }
}
