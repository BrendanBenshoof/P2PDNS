import java.util.ArrayList;

class Router implements java.lang.Runnable
{
  boolean alive = true;
  ArrayList<Service> table;
  static Router instance;
  
  public Router()
  {
    table = new ArrayList<Service>();
  }
  
  public static synchronized Router getInstance()
  {
    if(instance==null)
    {
      instance = new Router();
    }
    return instance;
  }
  
  public void run()
  {
    while(alive)
    {
      route();
    }
  }

  public void route()
  {
    for( Service s: table)
    {
      Message m = s.outbox.poll();
      if(m!=null)
      {
        Integer dest = m.dest;
        table.get(dest).inbox.offer(m);
      }
    }
  }
  
  public int addService(Service s)
  {
    int res = table.size();
    table.add(s);
    s.myid = res;
    return res;
  }
  
}