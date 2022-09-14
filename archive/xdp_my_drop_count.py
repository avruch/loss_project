#!/usr/bin/python3
#
# xdp_drop_count.py Drop incoming packets on XDP layer and count for which
#                   protocol type
#
# Copyright (c) 2016 PLUMgrid
# Copyright (c) 2016 Jan Ruth
# Licensed under the Apache License, Version 2.0 (the "License")
import sys
sys.path.append('/usr/local/lib/python3.8/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')

from bcc import BPF
import pyroute2
import time


maptype="percpu_array"

b = BPF(src_file="my_drop_count.c",cflags=[ "-DMAPTYPE=\"%s\"" % maptype], debug=0)

fn = b.load_func("xdp_prog3", BPF.XDP,None) #prog1-drop every 5


device = "s1-eth3"
b.attach_xdp(device, fn, 0)

dropcnt = b.get_table("dropcnt")
prev = [0] * 256
print("Printing drops per IP protocol-number, hit CTRL+C to stop")
while 1:
    try:
        for k in dropcnt.keys():
            val = dropcnt[k].value if maptype == "array" else dropcnt.sum(k).value
            i = k.value
            if val:
                delta = val - prev[i]
                prev[i] = val
                print("{}: {} pkt/s".format(i, delta))
        time.sleep(1)
    except KeyboardInterrupt:
        print("Removing filter from device")
        break


b.remove_xdp(device)
