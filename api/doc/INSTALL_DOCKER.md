# Installing Docker

## On Ubuntu
First, install Docker on your machine:
```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
```
[Source](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04#step-1-%E2%80%94-installing-docker)

In order to confirm that Docker has been installed correctly, run:
```bash
docker --version
```

### Creating a new user
You should create a new user from which you will run the Docker containers. This is not required, but suggested for security reasons.
```bash
sudo adduser polkadot_api_server
```

You must then grant this user access to use Docker.
```bash
sudo usermod -aG docker polkadot_api_server
```
[Source](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04#step-2-%E2%80%94-executing-the-docker-command-without-sudo-\(optional\))

In order to log in to this user, you can simply run:
```bash
su polkadot_api_server
```

## On Windows
Download and Install the `Stable` version of `Docker Desktop for Windows` from [here](https://hub.docker.com/editions/community/docker-ce-desktop-windows).\
Once it has installed, you must Log out and back in in order for the installation to complete

In order to confirm that Docker has been installed correctly, inside `Command Prompt` or `Powershell` run:
```bash
docker --version
```
[Source](https://docs.docker.com/docker-for-windows/)

---
[Back to API installation page](./INSTALL_AND_RUN.md)