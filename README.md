# README

Demo repo illustrating a full stack approach to building and running a high
performance micro-service in Python with the Flask framework.

This demo wraps some of the Netatmo APIs (including AuthT) and presents it to
a wider system through JWT authorized endpoints.

## Featured tech & concepts:

- Key based JWT auth (with support for mock tokens during dev/testing)
- Gevented non-blocking Flask server (with modern python3.7 code, inline
  token refresh and pluggable storage backend)
- Optional Docker workflow (dev and prod containers, multi-stage builds)
- Vagrant + Ansible (for clean, cross-platform dev machine provisioning)
- Simple JAMStack inspired API Sandbox (to make playing with the Flask
  server's auth flow and API endpoints quick & easy)

## Install / How to run

1. Go to https://dev.netatmo.com and create a dev account (make a note of
  your client id and client secret credentials)

2. Check out this repo to your host, cd to `devops/vagrant`, read the
intructions in the README and then issue `vagrant up`.

3. Once the vagrant box is provisioned, SSH in to it and run:

```
cd /opt/gitrepos/netatmo/app

sudo /opt/gitrepos/netatmo/devops/hack/docker-tools.sh

sudo /opt/gitrepos/netatmo/devops/hack/jwt-tools.sh install

cat << "EOF" > /opt/gitrepos/netatmo/app/server/.env
NETATMO_CLIENT_ID="<your client id>"
NETATMO_CLIENT_SECRET="<your client secret>"
SECRET_KEY="<random secret string for use by Flask when signing cookies>"
EOF

chmod 600 /opt/gitrepos/netatmo/app/server/.env

sudo docker-compose up --build
```

The Flask server is available on port 5000 of your vagrant box.
The API Sandbox is available on port 3000 of your vagrant box.

## Using the API

All endpoints need a JWT token to access them, you can generate a mock
one via a helper script:

`/opt/gitrepos/netatmo/devops/hack/jwt-tools.sh token user .jwt/dummy/privkey.der`

Once you have a token, use either curl or the Sandbox to start playing with the
exposed endpoints.
