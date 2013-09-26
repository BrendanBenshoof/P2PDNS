package P2PDNS.MessageStructs;
import P2PDNS.Services.*;
import com.thoughtworks.xstream.XStream;

public class Message
{
    static XStream mystream = new XStream();
    static public int origin;
    public int dest;
    public String text;
    public Message(int origin, int dest, Object o)
    {
        this.origin = origin;
        this.dest = dest;
        this.text = Message.mystream.toXML(o);
    }

    public void setText(String t)
    {
        this.text = t;
    }

    public Object deserialize()
    {
        return mystream.fromXML(this.text);
    }


}
