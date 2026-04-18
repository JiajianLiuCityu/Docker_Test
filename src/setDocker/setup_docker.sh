#!/bin/bash
echo "--- [1/4] Updating System Packages ---"
sudo apt-get update -y && sudo apt-get upgrade -y

echo "--- [2/4] Installing Dependencies (sysbench, iperf3, python) ---"
sudo apt-get install -y ca-certificates curl gnupg lsb-release sysbench iperf3 python3-pip
sudo pip3 install pandas matplotlib
echo "--- [3/4] Installing Docker Engine ---"
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "--- [4/4] Configuring Permissions ---"
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

echo "Setup Complete! Please log out and log back in to apply Docker group changes."