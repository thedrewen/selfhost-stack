#!/bin/bash
# Created By TheDreWen
# Github : https://github.com/thedrewen/debian-server-installer

log() { echo -e "\n\033[1;34m[INFO]\033[0m $*"; }
warn() { echo -e "\n\033[1;33m[WARNING]\033[0m $*"; }
error() { echo -e "\n\033[1;31m[ERROR]\033[0m $*" >&2; }

# Variables are read from the .env file (copy .env.example to .env and fill it in).

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
env_file="$script_dir/.env"

if [ ! -f "$env_file" ]; then
    error "Missing $env_file : copy .env.example to .env and configure it."
    exit 1
fi

set -a
. "$env_file"
set +a

for required in USERNAME PASSWORD PUBLIC_KEY; do
    if [ -z "${!required}" ]; then
        error "Variable $required is empty in $env_file."
        exit 1
    fi
done

username="$USERNAME"
password="$PASSWORD"
publickey="$PUBLIC_KEY"

# Script :

log "[1/6] Updating the system and installing utilities (btop, neofetch, fastfetch, zsh)..."
sudo apt update && apt upgrade -y
sudo apt install btop -y
sudo apt install neofetch -y
sudo apt install fastfetch -y
sudo apt install zsh -y

log "[2/6] Installing Docker..."
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

log "[3/6] Creating user '$username' (sudo + docker groups)..."
# Create the user with the specified username
sudo useradd -m -s /bin/bash $username
sudo usermod -aG docker $username
sudo usermod -aG sudo $username

# Set the user's password
echo "$username:$password" | sudo chpasswd
sudo mkdir /home/$username/.ssh
sudo chown -R $username:$username /home/$username/.ssh
echo "$publickey" > /home/$username/.ssh/authorized_keys

log "[4/6] Configuring SSH (key authentication only, password authentication disabled)..."
# Hosting providers drop their own files here (e.g. 50-cloud-init.conf) and they take precedence over sshd_config
sudo rm -f /etc/ssh/sshd_config.d/*.conf
sudo sed -i -e 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config
sudo sed -i -e 's/#PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config
# Refuse to restart with a broken config to avoid locking ourselves out
sudo sshd -t || { error "Invalid sshd configuration, SSH was not restarted."; exit 1; }
sudo systemctl restart sshd
sudo chown -R $username:$username /home/$username/.ssh
log "[5/6] Installing Oh My Zsh for '$username'..."
sudo -i -u $username bash -c 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'

log "[6/6] Copying home/ content to /home/$username..."
# Done after Oh My Zsh so the files from home/ (including dotfiles) take precedence
sudo cp -a --no-preserve=ownership "$script_dir/home/." "/home/$username/"
sudo chown -R $username:$username /home/$username

log "Installation finished."
warn "Check your SSH configuration (/etc/ssh/sshd_config) BEFORE closing this session!"
warn "Open a new terminal and verify you can log in as '$username' with your SSH key, otherwise you may lock yourself out."
