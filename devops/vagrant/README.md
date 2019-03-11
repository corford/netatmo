Use this Vagrant image if you would like a clean, ready-to-go Ubuntu Bionic machine to
work on this project from.

Notes:

1. This Vagrant guest comes with a private network adapter so you can access it via its own
IP address from the host (see "private_ip" in vagrant.conf.yml)

2. /opt/gitrepos from within the guest will be exported via samba so you can access it on the
host. This gives you the benefit of a clean dev environment to work in while allowing you to
use your normal IDE on your laptop/desktop when writing code (particularly handy for devs
on Windows hosts). To access it from the host, just browse to the guest's IP address in your
file explorer and you should see the export.

## How to use:

Copy this "vagrant" dir to your host and then, before issuing "vagrant up" for the first time,
do the following (all in the same directory as this README file):

1. Create a file called "id_rsa.pub" containing your public SSH key

2. (optional) Create an "ansible.conf.yml" configuration file to override any desired role
   variable (e.g. "user_account_name" and "user_account_home_dir" if you want your own user
   account rather than the prexisting "vagrant" user)

3. (optional) Create a gitconfig.txt file with your git prefs

4. (optional) Make any changes you need to vagrant.conf.yml (e.g. altering IP addresses)
