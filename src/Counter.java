class Counter extends Service
{
  int count = 0;
  
  public void handleMessage(Message m)
  {
    count++;
    String c_text = Integer.toString(count);
    //sendMessage(m.origin, c_text);
  }
  
}
