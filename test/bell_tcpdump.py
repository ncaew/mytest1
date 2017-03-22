#! /usr/bin/python  
  
def tcpdump():  
    import subprocess, fcntl, os  
    # sudo tcpdump -nn -i eth0 icmp -l | grep ICMP 
    #cmd1 = ['tcpdump', '-i', 'eth0', '-n','-B', '4096','-s', '0', '-w', '-']  
    #cmd2 = ['grep', '--line-buffered', '-a', '-o', '-E', 'Host: .*|GET /.*']  
    cmd1 = ['tcpdump', '-i', 'eth0', '-n','-B', '4096','-s', '0', '-l'] 
    cmd2 = ['grep', '--line-buffered', '-E', 'ICMP']

    print cmd1
    print cmd2
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)  
    p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stdin=p1.stdout)  
      
    flags = fcntl.fcntl(p2.stdout.fileno(), fcntl.F_GETFL)  
    fcntl.fcntl(p2.stdout.fileno(), fcntl.F_SETFL, (flags | os.O_NDELAY | os.O_NONBLOCK))  
    return p2  


def poll_tcpdump(proc):
    #print 'poll_tcpdump....'  
    import select  
    txt = None  
    while True:  
        # wait 1/10 second   
        readReady, aaa, bbb = select.select([proc.stdout.fileno()], [], [], 0.1)  
        #print 'data ready:',readReady,aaa,bbb
        if not len(readReady):  
            break  
        try:  
            for line in iter(proc.stdout.readline, ""):  
                if txt is None:  
                    txt = ''  
                txt += line  
        except IOError:  
            #print 'data empty...'  
            pass  
        break  
    return txt  
  
  
proc = tcpdump()  
while True:  
    text = poll_tcpdump(proc)  
    if text:  
        print 'Get >>>> :' + text  
        print '========='
        print ''
        print ''


