package P2PDNS.MessageStructs;

public class RegisterStruct
{
    public int port;
    public int returnService;
    public RegisterStruct(int p, int s)
    {
        port = p;
        returnService = s;
    }
    
}
