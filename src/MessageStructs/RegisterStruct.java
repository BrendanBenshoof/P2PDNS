package P2PDNS.MessageStructs;

public class RegisterStruct
{
    int port;
    int returnService;
    public RegisterStruct(int p, int s)
    {
        port = p;
        returnService = s;
    }
    
}
