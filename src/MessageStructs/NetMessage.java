package P2PDNS.MessageStructs;
public class NetMessage
{
    public String contents;
    public String originip;
    public int originport;
    public int destport;
    
    public NetMessage(String contents, String origin, int oport, int dport)
    {
        this.contents = contents;
        this.originip = origin;
        this.originport = originport;
        this.destport = dport;
    }
}
