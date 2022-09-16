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
import ctypes as ct
from numpy import random
import threading
import time

def main(*args):
    function = args[1]
    fn_param = args[2]
    ####                             Repeated timer by sec                      #######
    class RepeatedTimer(object):
      def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

      def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

      def start(self):
        if not self.is_running:
          self.next_call += self.interval
          self._timer = threading.Timer(self.next_call - time.time(), self._run)
          self._timer.start()
          self.is_running = True

      def stop(self):
        self._timer.cancel()
        self.is_running = False
    returns = {}
    param = 50  #defult param = P(drop)
    prev = 0
    ###BPF loading prog
    b = BPF(src_file="my_drop_count.c",cflags=["-w","-DPARAM=\"%d\"" % param], debug=0)
    fn = b.load_func(args[1],BPF.XDP,None) #prog1-drop every 5
    device = args[0] #"s1-eth3"
    b.attach_xdp(device, fn, 0)
    ###BPF Maps monitoring.
    dropcnt = b.get_table("drop_cnt2")
    user_param = b["user_param"]

    def noraml(mu,sigma):
        returns[0]= random.normal(mu,sigma)
    def poisson(lam):
        returns[0] = random.poisson(lam, 1)
        param = int(returns[0])
        user_param[ct.c_int(1)] = ct.c_int(param)   #updating number of pckts.
        dropcnt[ct.c_int(0)] = ct.c_int(0)          #updating inner counter.
        #print(" lamda=", user_param[1].value)

    if function == "random_func":
        print("running",args[1])
        param = fn_param
        user_param[ct.c_int(0)] = ct.c_int(param)
    if function == "poisson_func":
        print("running",args[1])
        # RepeatedTimer(secs,function,lamda)
        rt = RepeatedTimer(1, poisson,fn_param)
    print("Printing drops per IP protocol-number, hit CTRL+C to stop")
    b.trace_print()
    while 1:
        try:
            for k in dropcnt.keys():
                val = dropcnt[0].value #if maptype == "array" else dropcnt.sum(k).value
                #print(dropcnt.sum(k))
                print(" counet=",val)
            time.sleep(1)
        except KeyboardInterrupt:
            print("Removing filter from device")
            break
    b.remove_xdp(device)

if __name__ == "__main__":
    main()

