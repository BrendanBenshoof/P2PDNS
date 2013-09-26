package P2PDNS.MessageStructs;

public class SendMessageStruct
{
    public String ip;
    public int port;
    public String msg;
    public SendMessageStruct(String ip, int port, String msg)
    {
        this.ip = ip;
        this.port = port;
        this.msg = msg;
    }
    
}
