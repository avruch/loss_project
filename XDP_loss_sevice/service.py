import subprocess
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import Intf
from mininet.node import Controller
import exp_topos

topo = exp_topos.eBPF_Topo()
net = Mininet(topo=topo,controller=RemoteController)
net.start()

p = subprocess.Popen(['python3', '/home/user/bcc/our_project/xdp_drop_control.py', 's1-eth3', 'pyramid_func','0','50000','100'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
p = subprocess.Popen(['python3', '/home/user/bcc/our_project/xdp_drop_control.py', 's1-eth2', 'random_func', '10000'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

CLI(net)


net.stop()
