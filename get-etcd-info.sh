#!/bin/bash
# Colors for output
green="\033[0;32m"
blue="\033[1;34m"
grey="\033[1;37m"
reset="\033[0m"
# Get IP addresses
public_ip=$(curl -s ifconfig.me)
private_ip=$(hostname -I | awk '{print $1}')
# Check if etcd is running in Docker
docker_container=$(docker ps | grep etcd | awk '{print $NF}')
if [ -n "$docker_container" ]; then
  echo -e "${green}<---------- ETCD INFORMATION ---------->${reset}"
  echo -e "${blue}ETCD is running in Docker container:${grey} $docker_container${reset}"
  
  # Get port mappings
  port_info=$(docker port $docker_container)
  echo -e "${blue}Port mappings:${grey}\n$port_info${reset}"
  
  # Get volume mounts
  volume_info=$(docker inspect $docker_container | grep -A 10 Mounts)
  echo -e "${blue}Volume mounts:${grey}\n$volume_info${reset}"
  
  # Check for TLS/SSL configuration
  uses_tls=$(docker inspect $docker_container | grep -i "cert\|tls\|ssl" | wc -l)
  if [ "$uses_tls" -gt 0 ]; then
    echo -e "${blue}TLS/SSL appears to be configured${reset}"
  else
    echo -e "${blue}TLS/SSL does not appear to be configured${reset}"
  fi
  
  # Get command used to start etcd
  cmd=$(docker inspect $docker_container --format='{{.Config.Cmd}}')
  echo -e "${blue}Command:${grey} $cmd${reset}"
  
  # Check for certificate files
  if [ -d "/var/lib/etcd/cfssl" ]; then
    echo -e "${blue}Certificate files found at:${grey} /var/lib/etcd/cfssl${reset}"
    ls -la /var/lib/etcd/cfssl
  fi
  
  # Docker commands
  echo -e "\n${green}<---------- DOCKER COMMANDS ---------->${reset}"
  echo -e "${blue}TO START ETCD:${grey} docker start $docker_container${reset}"
  echo -e "${blue}TO STOP ETCD:${grey} docker stop $docker_container${reset}"
  echo -e "${blue}TO CHECK STATUS/LOGS OF ETCD:${grey} docker logs $docker_container${reset}"
fi
# Check if etcd is running directly on host
host_pid=$(pgrep -f "/usr/local/bin/etcd")
if [ -n "$host_pid" ]; then
  echo -e "\n${green}<---------- HOST ETCD INFORMATION ---------->${reset}"
  echo -e "${blue}ETCD is running directly on host with PID:${grey} $host_pid${reset}"
  
  # Get command line
  cmd_line=$(ps -p $host_pid -o args=)
  echo -e "${blue}Command line:${grey} $cmd_line${reset}"
  
  # Extract data directory
  data_dir=$(echo "$cmd_line" | grep -o -- "--data-dir [^ ]*" | cut -d' ' -f2)
  echo -e "${blue}Data directory:${grey} $data_dir${reset}"
  
  # Extract client URLs
  client_urls=$(echo "$cmd_line" | grep -o -- "--listen-client-urls [^ ]*" | cut -d' ' -f2)
  echo -e "${blue}Client URLs:${grey} $client_urls${reset}"
  
  # Extract advertise URLs
  adv_urls=$(echo "$cmd_line" | grep -o -- "--advertise-client-urls [^ ]*" | cut -d' ' -f2)
  echo -e "${blue}Advertise URLs:${grey} $adv_urls${reset}"
  
  # Host commands
  echo -e "\n${green}<---------- HOST COMMANDS ---------->${reset}"
  echo -e "${blue}TO STOP ETCD:${grey} kill $host_pid${reset}"
  echo -e "${blue}TO CHECK STATUS:${grey} curl $adv_urls/health${reset}"
fi
# Check health
echo -e "\n${green}<---------- HEALTH CHECK ---------->${reset}"
http_health=$(curl -s http://localhost:2379/health)
echo -e "${blue}HTTP Health check:${grey} $http_health${reset}"
# Try HTTPS health check if certificates exist
if [ -f "/var/lib/etcd/cfssl/ca.pem" ] && [ -f "/var/lib/etcd/cfssl/client.pem" ] && [ -f "/var/lib/etcd/cfssl/client-key.pem" ]; then
  https_health=$(curl -s --cacert /var/lib/etcd/cfssl/ca.pem --cert /var/lib/etcd/cfssl/client.pem --key /var/lib/etcd/cfssl/client-key.pem https://${private_ip}:2379/health)
  echo -e "${blue}HTTPS Health check:${grey} $https_health${reset}"
  
  echo -e "\n${green}<---------- TLS COMMAND ---------->${reset}"
  echo -e "${blue}COMMAND TO TEST WITH TLS:${grey} curl --cacert /var/lib/etcd/cfssl/ca.pem --cert /var/lib/etcd/cfssl/client.pem --key /var/lib/etcd/cfssl/client-key.pem https://${private_ip}:2379/health${reset}"
fi
echo -e "\n${green}<---------- SUMMARY ---------->${reset}"
echo -e "${blue}Private IP:${grey} $private_ip${reset}"
echo -e "${blue}Public IP:${grey} $public_ip${reset}"
