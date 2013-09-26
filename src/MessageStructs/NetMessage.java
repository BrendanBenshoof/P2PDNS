package P2PDNS.MessageStructs;
public class NetMessage
{
    String contents;
    String originip;
    int originport;
    int destport;
    
    public NetMessage(String contents, String origin, int oport, int dport)
    {
        this.contents = contents;
        this.originip = origin;
        this.originport = originport;
        this.destport = dport;
    }
}
