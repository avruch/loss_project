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
import ctypes as ct
from numpy import random
import threading
import time
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
################################ Clock Thread functions #########################################
returns = {}
def noraml(mu,sigma):
    returns[0]= random.normal(mu,sigma)
def poisson(lam):
    returns[0] = random.poisson(lam, 1)

rt = RepeatedTimer(1, poisson ,2) # it auto-starts, no need of rt.start()
param = 15  #param = P(drop)
############################## BPF loading prog ###########################################
b = BPF(src_file="my_drop_count.c",cflags=["-w","-DPARAM=\"%d\"" % param], debug=0)
fn = b.load_func("xdp_prog3",BPF.XDP,None) #prog1-drop every 5
device = "s2-eth2"
b.attach_xdp(device, fn, 0)
#########################################################################################
dropcnt = b.get_table("drop_cnt2")   #read_only option.
prev = [0]
print("Printing drops per IP protocol-number, hit CTRL+C to stop")
# preparing parameter to pass to xdp prog.
user_param = b["user_param"]
user_param[ct.c_int(0)] = ct.c_int(param)
#b.trace_print()
print(user_param[0].value)
while 1:
    #print("new-param")
    param= int(returns[0])
    user_param[ct.c_int(1)] = ct.c_int(param)
    #print(user_param[1].value)
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
