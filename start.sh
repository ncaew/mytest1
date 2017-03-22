#!/bin/bash

pushd mytest1
sudo route add -net 224.0.1.187 netmask 255.255.255.255 eth0
kill -9 `pgrep -f  monitor.py`
python monitor.py &
sleep 1
popd

pushd NJWL@Pi2
./start.sh 
sleep 1
popd

pushd install 
./start_p_d.sh
popd

sleep 20
firefox http://127.0.0.1:8888/static/Default.html &


