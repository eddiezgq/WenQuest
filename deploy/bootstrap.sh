#!/usr/bin/env bash
# One-time setup of a fresh Ubuntu 24.04 server. Run as root:
#   bash bootstrap.sh "<CI public key>"
# The CI public key is the .pub half of the key pair whose private half you store in GitHub
# as the DEPLOY_SSH_KEY secret. It lets the deploy job log in as the 'deploy' user.
set -euo pipefail

CI_PUBKEY="${1:?Usage: bash bootstrap.sh \"ssh-ed25519 AAAA... github-deploy\"}"
WQ_DIR=/opt/wenquest

[ "$(id -u)" -eq 0 ] || { echo "Run as root." >&2; exit 1; }

echo "== System updates and basic tools"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get upgrade -yq
apt-get install -yq ca-certificates curl ufw fail2ban unattended-upgrades
dpkg-reconfigure -f noninteractive unattended-upgrades

echo "== Docker"
if ! command -v docker >/dev/null; then
    curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

echo "== Swap (2 GB) so upgrades and builds do not run out of memory"
if ! swapon --show | grep -q .; then
    fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "== Deploy user"
id deploy >/dev/null 2>&1 || useradd -m -s /bin/bash deploy
usermod -aG docker deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
touch /home/deploy/.ssh/authorized_keys
# Your own key (the one you used to log in as root) plus the CI key.
cat /root/.ssh/authorized_keys >> /home/deploy/.ssh/authorized_keys 2>/dev/null || true
grep -qxF "$CI_PUBKEY" /home/deploy/.ssh/authorized_keys || echo "$CI_PUBKEY" >> /home/deploy/.ssh/authorized_keys
sort -u -o /home/deploy/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys && chmod 600 /home/deploy/.ssh/authorized_keys

echo "== SSH: keys only"
cat > /etc/ssh/sshd_config.d/10-wenquest.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
EOF
sshd -t
# Ubuntu 24.04 starts sshd on demand (ssh.socket) and each new connection reads the config,
# so a reload is only needed when the service is already running.
if systemctl is-active --quiet ssh; then systemctl reload ssh; fi

echo "== Firewall: SSH, HTTP, HTTPS only"
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

echo "== Install directory and daily backup"
install -d -o deploy -g deploy "$WQ_DIR" "$WQ_DIR/backups"
cat > /etc/cron.d/wenquest-backup <<EOF
# Daily backup at 03:30 server time.
30 3 * * * deploy $WQ_DIR/deploy/backup.sh >> $WQ_DIR/backups/backup.log 2>&1
EOF

echo
echo "Server ready. Next: log in as deploy, create $WQ_DIR/.env (see the runbook), then run the"
echo "GitHub Actions 'Build and deploy' workflow."
