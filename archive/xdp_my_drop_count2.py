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
import ctypes as ct


maptype="percpu_array"
param = 3

b = BPF(src_file="my_drop_count.c",cflags=["-w","-DMAPTYPE=\"%s\"" % maptype,"-DPARAM=\"%d\"" % param], debug=0)
fn = b.load_func("xdp_prog2",BPF.XDP,None) #prog1-drop every 5


device = "s1-eth3"
b.attach_xdp(device, fn, 0)

dropcnt = b.get_table("drop_cnt2")   #read_only option.
prev = [0]
print("Printing drops per IP protocol-number, hit CTRL+C to stop")

# preparing keys and new values array
random_param = b.get_table("random_param") #try_param = b["random_param"]

# preparing parameter to pass to xdp prog.
user_param = b["user_param"] #try_param = b["random_param"]
user_param[ct.c_int(0)] = ct.c_int(param)



#b.trace_print()
while 1:
    print(user_param[0].value)
    #print(random_param[0].value)
    #print(random_param[1].value)
    #print(random_param[2].value)
    #print(random_param[3].value)
    try:
        for k in dropcnt.keys():
            val = dropcnt[k].value #if maptype == "array" else dropcnt.sum(k).value
            i = k.value
            if val:
                delta = val - prev[i]
                prev[i] = val
                print("{}: {} pkt/s".format(i,delta))
        time.sleep(1)
    except KeyboardInterrupt:
        print("Removing filter from device")
        break



b.remove_xdp(device)
