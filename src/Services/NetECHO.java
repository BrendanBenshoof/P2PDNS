package P2PDNS.Services;

import P2PDNS.MessageStructs.*;
import P2PDNS.*;

public class NetECHO extends Service
{
    public void run()
    {
        RegisterStruct R = new RegisterStruct(8000,myid);
        sendMessage(GLOBALS.NETSERV,R);
        super.run();
    }
    public void handleMessage(Message m)
    {
        NetMessage N = (NetMessage) m.deserialize();
        SendMessageStruct send = new SendMessageStruct(N.originip, N.originport, N.contents);
        sendMessage(GLOBALS.NETSEND, send);
    }


}
