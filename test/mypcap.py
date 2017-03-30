import dpkt

import pcap

import threading
import os
import signal


def capture():
    myfilter = 'icmp'

    p = pcap.pcap('wlp2s0')
    p.setfilter(myfilter)

    try:
        for ptime, pdata in p:
            print ptime
            ether = dpkt.ethernet.Ethernet(pdata)

            #p=dpkt.ip.IP(pdata)

            ip = ether.data
            ip_str = '%d.%d.%d.%d' % tuple(map(ord, list(ip.src)))
            print ip_str
            '''
            udp = ip.data
            port = udp.sport
            node = '%s:%d' % (ip_str, port)
            content_len = len(udp) - 8
            print node

            if udp.data[0] == 'd' and udp.data[content_len - 1] == 'e':
            print node
            '''
    except KeyboardInterrupt:
        print("capture finish")


def timeout(id):
    os.kill(id, signal.SIGINT)


if __name__ == '__main__':
    t = threading.Thread(target=capture)
    t.start()
    print (t.ident)
    timer = threading.Timer(10, t.ident)
