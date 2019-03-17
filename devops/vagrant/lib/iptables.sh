#!/bin/bash

# Provision iptables

# Exit immediately on error or undefined variable
set -e
set -u

echo "Setting up iptables"
logger "Setting up iptables"

# Prepare firewall rule directories
mkdir -p /etc/iptables.d/ipv4/{00_security,10_raw,20_nat,30_mangle,40_filter}
chmod 755 /etc/iptables.d/ipv4/{00_security,10_raw,20_nat,30_mangle,40_filter}

mkdir -p /etc/iptables.d/ipv6/{00_security,10_raw,20_nat,30_mangle,40_filter}
chmod 755 /etc/iptables.d/ipv6/{00_security,10_raw,20_nat,30_mangle,40_filter}

chmod 755 /etc/iptables.d

# IPv4: Write default "security" table policies
cat << "EOF" > /etc/iptables.d/ipv4/00_security/00_header.rules
*security
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv4/00_security/99_footer.rules

# IPv4: Write default "raw" table policies
cat << "EOF" > /etc/iptables.d/ipv4/10_raw/00_header.rules
*raw
:PREROUTING ACCEPT
:OUTPUT ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv4/10_raw/99_footer.rules

# IPv4: Write default "nat" table policies
cat << "EOF" > /etc/iptables.d/ipv4/20_nat/00_header.rules
*nat
:PREROUTING ACCEPT
:INPUT ACCEPT
:OUTPUT ACCEPT
:POSTROUTING ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv4/20_nat/99_footer.rules

# IPv4: Write default "mangle" table policies
cat << "EOF" > /etc/iptables.d/ipv4/30_mangle/00_header.rules
*mangle
:PREROUTING ACCEPT
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
:POSTROUTING ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv4/30_mangle/99_footer.rules

# IPv4: Write default "filter" table policies
cat << "EOF" > /etc/iptables.d/ipv4/40_filter/00_header.rules
*filter
:INPUT DROP
:FORWARD DROP
:OUTPUT DROP
:FILTERS -
:DOCKER-USER -
-F INPUT
-F DOCKER-USER
-F FILTERS
EOF
echo "COMMIT" > /etc/iptables.d/ipv4/40_filter/99_footer.rules

# IPv6: Write default "security" table policies
cat << "EOF" > /etc/iptables.d/ipv6/00_security/00_header.rules
*security
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv6/00_security/99_footer.rules

# IPv6: Write default "raw" table policies
cat << "EOF" > /etc/iptables.d/ipv6/10_raw/00_header.rules
*raw
:PREROUTING ACCEPT
:OUTPUT ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv6/10_raw/99_footer.rules

# IPv6: Write default "nat" table policies
cat << "EOF" > /etc/iptables.d/ipv6/20_nat/00_header.rules
*nat
:PREROUTING ACCEPT
:INPUT ACCEPT
:OUTPUT ACCEPT
:POSTROUTING ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv6/20_nat/99_footer.rules

# IPv6: Write default "mangle" table policies
cat << "EOF" > /etc/iptables.d/ipv6/30_mangle/00_header.rules
*mangle
:PREROUTING ACCEPT
:INPUT ACCEPT
:FORWARD ACCEPT
:OUTPUT ACCEPT
:POSTROUTING ACCEPT
EOF
echo "COMMIT" > /etc/iptables.d/ipv6/30_mangle/99_footer.rules

# IPv6: Write default "filter" table policies
cat << "EOF" > /etc/iptables.d/ipv6/40_filter/00_header.rules
*filter
:INPUT DROP
:FORWARD DROP
:OUTPUT DROP
:FILTERS -
:DOCKER-USER -
-F INPUT
-F DOCKER-USER
-F FILTERS
EOF
echo "COMMIT" > /etc/iptables.d/ipv6/40_filter/99_footer.rules

# IPv4: Write default "filter" table rules
cat << "EOF" > /etc/iptables.d/ipv4/40_filter/10_default.rules
# Drop any invalid state connections
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A FORWARD -m conntrack --ctstate INVALID -j DROP
-A OUTPUT -m conntrack --ctstate INVALID -j DROP
# Drop any new tcp connections that do not have a SYN flag set
-A INPUT -p tcp -m tcp ! --tcp-flags FIN,SYN,RST,ACK SYN -m conntrack --ctstate NEW -j DROP
# Drop fragmented packets
-A INPUT -f -j DROP
# Default traffic flow rules
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p icmp -m icmp --icmp-type 8 -j ACCEPT
-A INPUT -j FILTERS
-A DOCKER-USER -i eth1 -j FILTERS
-A OUTPUT -j ACCEPT
EOF

# IPv4: Write SSH rules
cat << "EOF" > /etc/iptables.d/ipv4/30_mangle/20_ssh.rules
-A PREROUTING -p tcp -m tcp --dport 22 -j TOS --set-tos 0x10/0x3f
-A POSTROUTING -p tcp -m tcp --dport 22 -j TOS --set-tos 0x10/0x3f
EOF
cat << "EOF" > /etc/iptables.d/ipv4/40_filter/20_ssh.rules
-A FILTERS -p tcp -m tcp --dport 22 --tcp-flags FIN,SYN,RST,ACK SYN -m conntrack --ctstate NEW -j ACCEPT
EOF

# IPv6: Write default "filter" table rules
cat << "EOF" > /etc/iptables.d/ipv6/40_filter/10_default.rules
# Drop any invalid state connections
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A FORWARD -m conntrack --ctstate INVALID -j DROP
-A OUTPUT -m conntrack --ctstate INVALID -j DROP
# Drop any new tcp connections that do not have a SYN flag set
-A INPUT -p tcp -m tcp ! --tcp-flags FIN,SYN,RST,ACK SYN -m conntrack --ctstate NEW -j DROP
# Default traffic flow rules
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A OUTPUT -j ACCEPT
EOF

# Set ownership to root
chown root:root -R /etc/iptables.d

# Write firewall rules loader script
cat << "EOF" > /etc/iptables.d/loader
#!/bin/bash

# This script merges a collection of discreet iptables rule files (under /etc/iptables.d/ipv4
# and /etc/iptables.d/ipv6) into a single rule file (one for ipv4 and one for ipv6) and then
# applies them with iptables-restore.
#
# Rules loaded via this script will automatically persist through reboots providing you
# have the iptables-persistent and netfilter-persistent packages installed.
#
# IMPORTANT:
#
# 1. No changes (or additions/deletions) you make to rule files under /etc/iptables.d will take
# effect until you run this script. Running this script once after making your changes is sufficient
# to immediately apply your rules and make them persist across reboots.
#
# 2. When running this script any existing rules in /etc/iptables/rules.v4 and /etc/iptables/rules.v6
# will be replaced (and any active iptables rules will be flushed).
#
# For help with debugging rules, try running: iptables -L -vnx --table filter
#

RETVAL=0

TMP_IPTABLES_RULES_V4="$(mktemp -q -p /etc/iptables.d/ipv4 rules.XXXXXXXXXXXXXXXXXXXX)"
TMP_IPTABLES_RULES_V6="$(mktemp -q -p /etc/iptables.d/ipv6 rules.XXXXXXXXXXXXXXXXXXXX)"

find /etc/iptables.d/ipv4 -maxdepth 2 -mindepth 1 -type f -name "*.rules" 2>&1 | grep -v "Permission denied" | sort -V | xargs cat > ${TMP_IPTABLES_RULES_V4}
find /etc/iptables.d/ipv6 -maxdepth 2 -mindepth 1 -type f -name "*.rules" 2>&1 | grep -v "Permission denied" | sort -V | xargs cat > ${TMP_IPTABLES_RULES_V6}

if $(iptables-restore -t $TMP_IPTABLES_RULES_V4); then
  echo "Applying IPv4 iptables rules..."
  mv ${TMP_IPTABLES_RULES_V4} /etc/iptables/rules.v4
  iptables-restore -n < /etc/iptables/rules.v4 2> /dev/null
else
  echo "iptables restore failed (malformed IPv4 rule file):" >&2
  echo "---" >&2
  cat ${TMP_IPTABLES_RULES_V4} >&2
  rm ${TMP_IPTABLES_RULES_V4}
  RETVAL=2
fi

if $(ip6tables-restore -t $TMP_IPTABLES_RULES_V6); then
  echo "Applying IPv6 iptables rules..."
  mv ${TMP_IPTABLES_RULES_V6} /etc/iptables/rules.v6
  ip6tables-restore -n < /etc/iptables/rules.v6 2> /dev/null
else
  echo "iptables restore failed (malformed IPv6 rule file):" >&2
  echo "---" >&2
  cat ${TMP_IPTABLES_RULES_V6} >&2
  rm ${TMPIPTABLES_RULES_V6}
  RETVAL=3
fi

exit ${RETVAL}
EOF

# Ensure system packages are installed to persist rules across reboots
export DEBIAN_FRONTEND=noninteractive
apt-get -y -qq -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install iptables-persistent netfilter-persistent 

# Load rules
chmod 700 /etc/iptables.d/loader
chown root:root /etc/iptables.d/loader
/etc/iptables.d/loader

exit 0
