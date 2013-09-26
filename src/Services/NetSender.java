package P2PDNS.Services;

import java.net.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.io.*;
import P2PDNS.Services.*;
import P2PDNS.MessageStructs.*;

public class NetSender extends Service
{

    public void handleMessage(Message m){
        Socket sock = null;
        PrintWriter out = null;
        try
        {
            SendMessageStruct R = (SendMessageStruct)(m.deserialize());
            try {
                sock = new Socket(R.ip, R.port);
                out = new PrintWriter(echoSocket.getOutputStream(), true);
                out.println(R.msg);
                sock.close();
            } catch (UnknownHostException e) {
                System.err.println("Don't know about host: "+R.ip);
                return;
            } catch (IOException e) {
                System.err.println("Couldn't get I/O for "
                                   + "the connection to: "+R.ip);
                System.exit(1);
            }
            System.out.println(R.msg);


        }
        catch(ClassCastException e)
        {
            return;
        }
        }


}
