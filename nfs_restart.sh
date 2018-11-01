#!/bin/bash

echo "restart dnsmasq"
/etc/init.d/dnsmasq restart
echo "restart rpcbind"
#/etc/init.d/portmap restart
service portmap restart
echo "restart nfs server"
/etc/init.d/nfs-kernel-server restart
echo "rpcinfo"
rpcinfo -p
echo "exportfs"
exportfs -a
echo "showmount"
showmount -e localhost
echo "done."
