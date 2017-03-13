#coding:utf8
import re
import os
import sys
import json
import time
from optparse import OptionParser
from HTMLParser import HTMLParser
#email
import smtplib  
from email.mime.text import MIMEText 

class Job:
  def __init__(self, conf):
    self.conf = conf

    self.name = conf['name']
    self.url = conf['url']
    self.status = conf['status']
    self.interval = conf['interval']
    self.failed_times = 0; #conf['failed_times']
    self.alert_interval = conf['alert_interval']
    self.relist = []
    for re_str in conf['re']:
      re_obj = re.compile(re_str);
      self.relist.append({"str":re_obj, "status":0})
    self.email = conf['email']
    #record
    self.times_check = 0
    self.time_start = time.time()
    self.time_last = self.time_start
    self.time_alert_last = self.time_start
  
  def check(self):
    status = 1
    time_now = time.time()
    fn = "/tmp/pagemonitor.%s.%d"%(self.name, time_now)
    try:
      if self.times_check==0 or time_now-self.time_last > self.interval:
        self.times_check = self.times_check + 1
        #crawl
        curlcmd = "curl -L -o %s %s"%(fn, self.url)
        print curlcmd
        os.system(curlcmd)
        file_object = open(fn, 'r')
        page_str = file_object.read( )
        file_object.close( )
    
        if not page_str:
          status = 0
        else:
          #check
          for re_str in self.relist:
            if re_str['str'].search( page_str ) :
              re_str['status'] = 0
            else:
              status = 0
              re_str['status'] = re_str['status'] + 1
              print "failed url=%s re=%s"%(self.url, re_str['str'].pattern)
        
        self.time_last = time.time()
    except Exception as e:
      status = 0
      self.time_last = time.time()
      print >>sys.stderr, e 
    #alert
    if status:
      self.failed_times = 0
      if os.path.exists(fn):
        os.system("rm %s"%(fn))
    else:
      if self.failed_times == 0:
        self.failed_times = 1
      else:
        self.failed_times = self.failed_times + 1
      if self.failed_times >= self.conf['failed_times']:
        #send email
        for email in self.email:
          try:
            title = "%s failed "%(self.name)
            fp = open(fn, 'r')
            content = "%s failed %d times<br>\nfn=%s<br>\nresponse:%s"%(self.name, self.failed_times, fn, fp.read() )
            fp.close();
            sendmail("hupaialert@163.com", email, title, content);
          except Exception as e:
            print >>sys.stderr, e 
          self.time_alert_last = time.time()
   

def sendmail(me, you, head, content):
    msg = MIMEText(content,'html','utf8') #这是正确显示Html中文的设置，会解析html标签，不再是原始文本。  
    msg.set_charset('utf8')#这是正确显示中文的设置  
    msg['Subject'] = head
    msg['From'] = me   
    msg['To'] = you  
   
    s = smtplib.SMTP('smtp.163.com');
    s.login(me, "123456") 
    s.sendmail(me, [you], msg.as_string())  
    s.quit() 
 
def run(options):
  try:
    file_object = open(options.cf, 'r')
    conf_str = file_object.read( )
    file_object.close( )
    
    conf = json.loads(conf_str)
    joblist = []
    for urlconf in conf['urlist']:
      job = Job(urlconf)
      joblist.append(job)
      
    while(1):
      for job in joblist:
        job.check()
      time.sleep(1)
      #break
  except Exception as e:
    print >>sys.stderr, options.cf, e

if __name__=="__main__":#
  parser = OptionParser()
  parser.add_option("-c", "--conf", action="store",
                    dest="cf",
                    default="conf.json",
                    help="json format configure file path")
  (options, args) = parser.parse_args()
  run(options)
