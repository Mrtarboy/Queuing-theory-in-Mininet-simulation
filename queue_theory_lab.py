#此工程用于在mininet中验证排队论
from mininet.net import Mininet
from mininet.node import CPULimitedHost,RemoteController
from mininet.link import TCLink
from mininet.cli import CLI

#建立排队论参数：
Lambda = 10 #来流速率
mu = 11 #包处理速率
N_bfr = 100 #内存容量上限
rho0 = Lambda/mu #稳态输运流量

#建立结点
net = Mininet(controller=RemoteController,host=CPULimitedHost,link=TCLink)
c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
s1 = net.addSwitch('s1')
h1 = net.addHost('h1')
h2 = net.addHost('h2', cpu=0.5)
h3 = net.addHost('h3')

#建立topo结构
net.addLink(s1,h1, bw = 10, delay = '0ms', max_queue_size =N_bfr, use_htb=True)
#这个参数设置链路的带宽为10 Mbps
net.addLink(s1,h2)
net.addLink(s1,h3)

#启动实验
net.start()
s1.dpctl('add-flow','actions=normal')
net.pingAll()

print("在h1上启动iperf")
h1.cmd('iperf -s -u &')#服务器模式并且后台挂起

print("在h3上启动iperf")
iperf_result = h2.cmd(f'iperf -c 10.0.0.100 -u -b {Lambda}M -t 15')#尝试以每秒 10 Megabits 的速率发送数据。
print("----以下是测试结果----")
print(iperf_result)

#以下是排队论理论计算部分
print("对比理论计算")
P_Loss = ((1-rho0)/(1-rho0**(N_bfr)))*(rho0**N_bfr)#丢包率
Length_sys = (rho0/(1-rho0))-(((N_bfr+1)*(rho0**(N_bfr+1)))/(1-(rho0**(N_bfr+1)))) #系统平均长度
t_Delay = Length_sys / (Lambda*(1-P_Loss))#延迟
print(f"丢包率：{P_Loss} 平均队长：{Length_sys} 延迟：{t_Delay}")

CLI(net)