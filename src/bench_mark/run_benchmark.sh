#!/bin/bash

TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_TYPE=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/instance-type)
OUT="results_${INSTANCE_TYPE}.csv"

echo "Metric,Value,Unit" > $OUT

echo "--- Running CPU/Mem tests ---"
CPU_RES=$(sysbench cpu --cpu-max-prime=20000 run | grep "events per second" | awk '{print $4}')
echo "CPU_Throughput,$CPU_RES,eps" >> $OUT
MEM_RES=$(sysbench memory --memory-block-size=1M --memory-total-size=10G run | grep "transferred" | awk -F'[(|)]' '{print $2}' | awk '{print $1}')
echo "Mem_Bandwidth,$MEM_RES,MiB/s" >> $OUT

echo "--- Running Disk I/O tests ---"

D_LAYER=$(sudo docker run --rm ubuntu:24.04 sh -c "dd if=/dev/zero of=test_file bs=1M count=1024 oflag=direct 2>&1" | awk '/copied/ {print $(NF-1)}')
echo "Disk_Container_Layer,$D_LAYER,MB/s" >> $OUT

D_VOLUME=$(sudo docker run --rm -v $(pwd):/data ubuntu:24.04 sh -c "dd if=/dev/zero of=/data/test_file bs=1M count=1024 oflag=direct 2>&1" | awk '/copied/ {print $(NF-1)}')
echo "Disk_Docker_Volume,$D_VOLUME,MB/s" >> $OUT

echo "--- Running Network tests ---"
sudo pkill iperf3
iperf3 -s -D
sleep 3

GATEWAY_IP="172.17.0.1"
NET_BRIDGE=$(sudo docker run --rm networkstatic/iperf3 -c $GATEWAY_IP -t 5 | grep "receiver" | awk '{print $7}')
echo "Network_Bridge_Mode,$NET_BRIDGE,Gbits/sec" >> $OUT

NET_HOST=$(sudo docker run --rm --network host networkstatic/iperf3 -c 127.0.0.1 -t 5 | grep "receiver" | awk '{print $7}')
echo "Network_Host_Mode,$NET_HOST,Gbits/sec" >> $OUT

sudo pkill iperf3
echo "----------------------------------------------------------"
echo "Done! Data saved to: $OUT"
cat $OUT