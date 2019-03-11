#!/bin/bash

# Provisioning boostrap script

# Vars
PYTHON_BIN_PATH="/usr/bin/python3"
VENV_URL="https://files.pythonhosted.org/packages/37/db/89d6b043b22052109da35416abc3c397655e4bd3cff031446ba02b9654fa/virtualenv-16.4.3.tar.gz"
VENV_SAVE_PATH="/usr/local/src/virtualenv-16.4.3.tar.gz"
VENV_SHA256="984d7e607b0a5d1329425dd8845bd971b957424b5ba664729fab51ab8c11bc39"
VENV_SHA256_FILE="/usr/src/virtualenv_sha256"
VENV_INSTALL_DIR="/opt/virtualenv"
ANSIBLE_VENV_DIR="/opt/ansible/venv" # Note: if you alter this path you must make the same change to {{ ansible_venv_path }} in group_vars of the ansible inventory
ANSIBLE_GALAXY_ROLES_DIR="/opt/ansible/roles" # Note: for ansible to find these roles, this past must be added to "roles_path" in ansible.cfg

# Exit immediately on error or undefined variable
set -e
set -u

# Add pubkey to root
function provision_root_pubkey ()
{
    echo "Adding pubkey to root"

    mkdir -p /root/.ssh
    touch /root/.ssh/authorized_keys

    # Append rather than overwrite in case vagrant image has some pubkeys already bundled
    cat /vagrant/id_rsa.pub >> /root/.ssh/authorized_keys

    # Safety precaution in case id_rsa.pub contents isn't terminated with \n
    echo -en '\n' >> /root/.ssh/authorized_keys

    # Remove duplicate lines (e.g. when provisioner is run multiple times)
    sort -u -o /root/.ssh/authorized_keys /root/.ssh/authorized_keys && sed -i '/^$/d' /root/.ssh/authorized_keys

    # Remove any settings before keys
    sed -i 's/^.*ssh-rsa/ssh-rsa/' /root/.ssh/authorized_keys

    # Set perms
    chmod 600 /root/.ssh/authorized_keys
    chmod 700 /root/.ssh/  
    chown -R root:root /root/.ssh

    # Restart sshd
    service sshd restart

	return 0
}

# Replace APT sources
function provision_apt ()
{
echo "Updating APT sources.list"
mv /etc/apt/sources.list /etc/apt/sources.list.bak
cat << EOF > /etc/apt/sources.list
###### Ubuntu Main Repos
deb http://eu.archive.ubuntu.com/ubuntu/ bionic main restricted universe
deb-src http://eu.archive.ubuntu.com/ubuntu/ bionic main restricted universe

###### Ubuntu Update Repos
deb http://eu.archive.ubuntu.com/ubuntu/ bionic-security main restricted universe
deb http://eu.archive.ubuntu.com/ubuntu/ bionic-updates main restricted universe
deb-src http://eu.archive.ubuntu.com/ubuntu/ bionic-security main restricted universe
deb-src http://eu.archive.ubuntu.com/ubuntu/ bionic-updates main restricted universe
EOF

echo "Performing APT cache update and package upgrade"
export DEBIAN_FRONTEND=noninteractive
apt-get -y update && apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
}

# Install virtualenv
function provision_virtualenv ()
{
    if [ ! -d "${VENV_INSTALL_DIR}" ]; then
        echo "Downloading ${VENV_URL}"
        cd "$( dirname "${VENV_SAVE_PATH}" )"
        curl -sL "${VENV_URL}" -o "${VENV_SAVE_PATH}"

        echo "Verifying download"
        echo "${VENV_SHA256}  $( basename "${VENV_SAVE_PATH}" )" > "${VENV_SHA256_FILE}"
        if ! sha256sum -c "${VENV_SHA256_FILE}" --quiet --strict --status; then
            echo "Could not verify integrity of virtualenv download. Exiting."
            rm -f "${VENV_SAVE_PATH}"
            rm -f "${VENV_SHA256_FILE}"
            exit 1
        fi

        echo "Installing virtualenv dependencies"
        apt-get -y -qq install python

        echo "Installing virtualenv to $( dirname "${VENV_INSTALL_DIR}" )"
        mkdir -p "${VENV_INSTALL_DIR}"
        tar zxvf "$( basename "${VENV_SAVE_PATH}" )" -C "${VENV_INSTALL_DIR}" --strip 1
        rm -f "${VENV_SAVE_PATH}"
        rm -f "${VENV_SHA256_FILE}"

    else
        echo "Virtualenv already installed, skipping."
    fi
}

# Install ansible
function provision_ansible ()
{
    if [ ! -d "${ANSIBLE_VENV_DIR}" ]; then
        echo "Installing ansible dependencies"
        apt-get -y -qq install python3 python3-dev libssl-dev zlib1g-dev libffi-dev git

        echo "Installing ansible"
        mkdir -p "$( dirname "${ANSIBLE_VENV_DIR}" )"
        "${VENV_INSTALL_DIR}/virtualenv.py" --python="${PYTHON_BIN_PATH}" "${ANSIBLE_VENV_DIR}"
        "${ANSIBLE_VENV_DIR}/bin/pip" install ansible cryptography netaddr
        echo "export PATH=\"\$PATH:${ANSIBLE_VENV_DIR}/bin\"" >> /root/.profile
        echo "export PATH=\"\$PATH:${ANSIBLE_VENV_DIR}/bin\"" >> /home/vagrant/.profile
    else
        echo "Ansible already installed, skipping."
    fi
}

# Install ansible galaxy roles
function provision_ansible_galaxy_roles ()
{
    if [ ! -f "${ANSIBLE_VENV_DIR}/bin/ansible-galaxy" ]; then
        echo "Ansible galaxy not found, skipping."

    elif [ -f "${1}" ]; then
        rm -rf "${ANSIBLE_GALAXY_ROLES_DIR}"
        mkdir -p "${ANSIBLE_GALAXY_ROLES_DIR}"
        "${ANSIBLE_VENV_DIR}/bin/ansible-galaxy" install --roles-path "${ANSIBLE_GALAXY_ROLES_DIR}" -r "${1}"

    else
        echo "No requirements file found for galaxy roles, skipping."
    fi
}

# !!! Main script execution starts HERE

provision_root_pubkey
provision_apt
provision_virtualenv
provision_ansible
provision_ansible_galaxy_roles "${1}"

exit 0
