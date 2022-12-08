#!/usr/bin/python3
#
# xdp_drop_count.py Drop incoming packets on XDP layer and count for which
#                   protocol type
#
# Copyright (c) 2016 PLUMgrid
# Copyright (c) 2016 Jan Ruth
# Licensed under the Apache License, Version 2.0 (the "License")
import sys
import numpy as np
sys.path.append('/usr/local/lib/python3.8/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')
from bcc import BPF
import ctypes as ct
import time
import RepeatedTimer


i=0 #itr counter.
param = 10  #default parameter for ebpf protection
function = sys.argv[2]
args = sys.argv[3:]
# BPF loading prog
b = BPF(src_file="my_drop_count.c",cflags=["-w","-DPARAM=\"%d\"" % param], debug=0) #maybe remove cflag
fn = b.load_func("drop_func",BPF.XDP,None)
device = sys.argv[1] #"s1-eth3"
b.attach_xdp(device, fn, 0)

# BPF Maps monitoring.
user_param = b["user_param"]
user_param[ct.c_int(0)] = ct.c_int(param)

def random_func(args):
    #FIXME check legal args
   param = int(args[0])
   user_param[ct.c_int(0)] = ct.c_int(param)

def pyramid_func(args):
    #FIXME check legal args
    #if args[0] is None or args[1] is None or args[2] is None :
        #error
    #    return
    # Create NumPy arrays
    global i
    #range_start=int(args[0])
    #range_end=int(args[1])
    #delta=int(args[2])
   #if not range_start in range (0,range_end ) :
   #    #error range should be
   #    pass
   #if not range_start in range (range_start,100) :
   #    #error range should be
   #    pass
    arr = np.arange(0, 100, 10)
    arr1 = np.arange(100, 0, -10)
    # Use concatenate() to join two arrays
    con = np.concatenate((arr, arr1))
    param = int(con[i % len(con)])
    user_param[ct.c_int(0)] = ct.c_int(param)
    i+=1

if args:
    if function == "random_func":
        print("running",random_func)
        print("drop percentage",args[0])
        rt = RepeatedTimer.RepeatedTimer(1,random_func,args)
    if function == "pyramid_func":
        print("running", pyramid_func)
        rt = RepeatedTimer.RepeatedTimer(1,pyramid_func,args)

print("Printing drops per IP protocol-number, hit CTRL+C to stop")
#b.trace_print()
while 1:
    time.sleep(1)
print("Removing filter from device")
b.remove_xdp(device)
print("finish")
