import subprocess
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import Intf
from mininet.node import Controller
import exp_topos


#p = subprocess.Popen(['python3', '/home/user/bcc/our_project/xdp_drop_control.py', 's1-eth3', 'pyramid_func','0','10','1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#p = subprocess.Popen(['python3', '/home/user/bcc/our_project/xdp_drop_control.py', 's1-eth3', 'random_func', '90'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#print(p.stdout.read().decode('UTF-8'), flush=True)
#print("done service", flush=True)
#"poisson_func" 100

topo = exp_topos.eBPF_Topo()
#link = sys.argv[2]
net = Mininet(topo=topo,controller=RemoteController)
net.start()

# Make Switch act like a normal switch
# net['s1'].cmd('ovs-ofctl add-flow s1 action=normal')
# Make Switch act like a hub
# net['s1'].cmd('ovs-ofctl add-flow s1 action=flood')

#p = subprocess.Popen(['python3', '/home/user/bcc/our_project/xdp_drop_control.py', 's1-eth3', 'pyramid_func','0','10','1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
p = subprocess.Popen(['python3', '/home/user/bcc/our_project/xdp_drop_control.py', 's1-eth3', 'random_func', '60'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
CLI(net)
#p = subprocess.Popen(['python3', '/home/user/bcc/our_project/xdp_drop_control.py', link, args[1],'0','10','1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#print(p.stdout.read().decode('UTF-8'), flush=True)

net.stop()
