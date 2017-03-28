# mytest1
test using for liang chun long yan

guard deploy:<br/>

    sudo fdisk -l
    sudo mount /dev/mmcblk0p1 /mnt
    sudo leafpad /mnt/config.txt 
    sudo reboot 
    
    sudo apt-get update 
    sudo apt-get install vim htop iftop vlc mplayer iperf 
    sudo apt-get install unclutter firefox-esr-l10n-zh-cn python-dev build-essential
    sudo pip install tornado coapthon transitions onvif netifaces
    mkdir guard
    cd guard/
    git clone https://github.com/ncaew/mytest1 

    sudo tcpdump -i eth0 -nn greater 81 and less 83 and src port 51880 and dst port 51880 and src net 192.168 and '(udp[46:2] = 0x0c00)' -l | grep UDP
    

