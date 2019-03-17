#!/bin/sh
DOCKER_COMPOSE="1.23.2"
DRY="0.9-beta.9"

# Exit immediately on error or undefined variable
set -e
set -u

echo "Downloading & installing Docker Compose ${DOCKER_COMPOSE} (to /usr/local/bin/docker-compose)"
curl -fsSL https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE}/docker-compose-`uname -s`-x86_64 -o /usr/local/bin/docker-compose
chmod 755 /usr/local/bin/docker-compose

echo "Downloading & installing Dry ${DRY} (to /usr/local/bin/dry)"
curl -fsSL https://github.com/moncho/dry/releases/download/v${DRY}/dry-`uname -s | sed -e 's/\(.*\)/\L\1/'`-amd64 -o /usr/local/bin/dry
chmod 755 /usr/local/bin/dry

exit 0
