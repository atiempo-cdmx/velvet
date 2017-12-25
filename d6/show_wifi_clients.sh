#!/bin/sh
str=""
tm="/tmp/MAC"
maclist=`iwinfo wlan0 assoclist | grep dBm | cut -f 1 -s -d" "`
for mac in $maclist
  do
    cip=""
    cid="${mac//:/}"
    ip=`cat /tmp/dhcp.leases | cut -f 2,3,4 -s -d" " | grep -i $mac | cut -f 2 -s -d" "`
    cip="${ip//./-}"
	ar="${tm}${cip}_${cid}"
	if ! [ -f $ar ]
        then            
		pi=`cat < /sys/class/net/eth0/address`
		pid="${pi//:/}"
            	snd=`/usr/bin/curl -v --silent -H "Content-Type: application/x-www-form-urlencoded" -X POST --data "id=${cid}&pid=${pid}" "http://lxvoip.ddns.net/captive/sh.php" 2>&1 |grep SVR_DATA`
		rst="${snd//SVR_DATA/}"
		echo $str >> $ar
		echo "(${rst})"
    fi
done