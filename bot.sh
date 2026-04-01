#!/bin/bash
sudo systemctl mask cups
sudo systemctl stop cups
sudo systemctl mask sshd
sudo systemctl stop sshd
sudo systemctl mask ssh
sudo systemctl stop ssh
sudo apt purge ufw -y 
sudo apt install iptables -y 
sudo iptables -F
sudo ip6tables -F
sudo iptables -I OUTPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I OUTPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -I OUTPUT -p udp --dport 123 -j ACCEPT
sudo iptables -I OUTPUT -p udp --dport 53 -j ACCEPT
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT
sudo ip6tables -A INPUT -i lo -j ACCEPT
sudo ip6tables -A OUTPUT -o lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT DROP
sudo ip6tables -P INPUT DROP
sudo ip6tables -P FORWARD DROP
sudo ip6tables -P OUTPUT DROP
sudo iptables -A INPUT -p icmp -j DROP
sudo iptables -A OUTPUT -p icmp -j DROP
sudo ip6tables -A INPUT -p icmp -j DROP
sudo ip6tables -A OUTPUT -p icmp -j DROP
sudo ip6tables -I OUTPUT -p tcp --dport 80 -j ACCEPT
sudo ip6tables -I OUTPUT -p tcp --dport 443 -j ACCEPT
sudo ip6tables -I OUTPUT -p udp --dport 123 -j ACCEPT
sudo ip6tables -I OUTPUT -p udp --dport 53 -j ACCEPT
sudo ip6tables -I FORWARD -p tcp --dport 80 -j ACCEPT
sudo ip6tables -I FORWARD -p tcp --dport 443 -j ACCEPT
sudo ip6tables -I FORWARD -p udp --dport 123 -j ACCEPT
sudo ip6tables -I FORWARD -p udp --dport 53 -j ACCEPT
sudo iptables -I FORWARD -p tcp --dport 80 -j ACCEPT
sudo iptables -I FORWARD -p tcp --dport 443 -j ACCEPT
sudo iptables -I FORWARD -p udp --dport 123 -j ACCEPT
sudo iptables -I FORWARD -p udp --dport 53 -j ACCEPT
sudo apt install iptables-persistent -y
sudo iptables-save
sudo ip6tables-save
sudo apt purge *libreo* -y
sudo rm -rf /usr/lib/libreoffice
sudo apt purge *telnet* -y
sudo apt purge cups-ipp-utils -y
sudo apt purge *samba* -y
sudo apt purge avahi-* -y
sudo apt purge *dnsmasq* -y
sudo apt purge nftables -y

