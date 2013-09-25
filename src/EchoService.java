public class EchoService extends Service 
{
    public void handleMessage(Message m) 
    {
        System.out.println((String)m.deserialize());
    }
}
