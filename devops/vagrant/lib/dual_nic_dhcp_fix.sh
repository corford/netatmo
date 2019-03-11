#!/bin/bash

# dhclient (used by Ubuntu to manage DHCP leases) doesn't pickup changes made by Vagrant to
# /etc/network/interfaces during first boot. This results in dhclient clobbering the static IP
# on the second interface with an errant lease.
#
# To prevent this we add a reject line (for the Virtualbox DHCP server on the second interface's
# network) to dhclient's config file. Unfortunately, dhclient is an arcane piece of shit and there
# is no way to reload the config. We have to kill dhclient, write the changes to the config file
# and then start it again. We also have to bounce the second interface to make sure it's been assigned
# the correct static IP.
#

/sbin/dhclient -r && pkill -f dhclient
grep -q -F "reject $1;" /etc/dhcp/dhclient.conf || echo "reject $1;" >> /etc/dhcp/dhclient.conf
/sbin/dhclient
ip addr flush $2 && netplan apply

exit 0
