# Install and Run the Custom JS API

Please Note: For this Polkadot JS API to run correctly, the version of the `@polkadot/api` JavaScript package, defined in `package.json`, must match the API version being run by the nodes.\
You can check the latest version of the `@polkadot/api` JavaScript package from [here](https://www.npmjs.com/package/@polkadot/api).

## Configuring the Nodes
In order for the API to be able to retrieve data from the Substrate/Polkadot Nodes, the nodes must be run with the following flags (in addition to any other flags you would like to use):
```bash
--pruning=archive --rpc-port=9933 --rpc-external --ws-port=9944 --ws-external
```
As of v0.7.10, the Validator must be run with these flags instead:
```bash
--pruning=archive --rpc-port=9933 --unsafe-rpc-external --ws-port=9944 --unsafe-ws-external
```

## Configuring the API
Configuring the API involves setting up two config files. This is a strict requirement for the API to be able to run.

Start off by cloning this repository and navigating into it:
```bash
git clone https://github.com/SimplyVC/panic_polkadot
cd panic_polkadot
```

The API can be configured in either of two ways, by [using the setup script](#using-the-setup-script), or [manually](#manually).

### Using the Setup Script
Please note that you will need to have installed Python before using this script.
To install Python, pip and pipenv follow [this guide](./INSTALL_PYTHON.md).

You can run the Python script `run_api_setup.py` which will guide you through the configuration process, and ask you to enter the values one by one. This can be done by running the following, starting from the root project directory, `panic_polkadot`:
```bash
pipenv sync
cd api
pipenv run python run_api_setup.py
```

### Manually
Alternatively, for advanced users, you can make a copy of the `example_*.ini` files inside the `config` folder, without the `example_` prefix, and manually change the values as required.

## Installing the API and Dependencies
This section will guide you through the installation of the API and any of its dependencies.

We recommend that the API is installed on a Linux system, given the simpler installation and running process. 
Nevertheless, instructions on how to install the API on a Windows system are also provided.

You can either [run the API from source](#running-from-source) or [run the API using Docker](#run-using-docker).
This affects what dependencies you will need to install.

### Running from Source
Running the API from source only requires you to install Node.js.

#### Install Node.js
##### On Ubuntu
```bash
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
sudo apt-get install -y nodejs
```
[Source](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions-enterprise-linux-fedora-and-snap-packages)

###### On Windows
Download the latest LTS Release of Node.js from [here](https://nodejs.org/en/download/) - Choose the ```Windows Installer (.msi)``` for your Operating System type (32-bit vs 64-bit).
Once the file is downloaded, double click on it to start the installation. The process is very simple, you can leave all the default options and simply press Next throughout the process.

#### Install Packages needed by the API
Install the packages defined in ```api/package.json``` by running:
```bash
cd api
npm install
```

#### Running the API
After having installed Node.js and the packages required by the API, you can now run the API as follows from the project directory:
```bash
bash run_api.sh
```

#### Running the API as a Linux Service
Running the API as a service means that it starts up automatically on boot and restarts automatically if it runs into some issue and stops running. To do so, we recommend the following steps:
```bash
# Add a new user to run the API
sudo adduser <USER>

# Grant permissions
sudo chown -R <USER>:<USER> <PANIC_DIR>/api/   # ownership of api
sudo chmod +x <PANIC_DIR>/run_api.sh           # execute permission for runner
```

The service file will now be created:

```bash
# Create the service file
sudo nano /etc/systemd/system/polkadot_api_server.service
```

It should contain the following, replacing `<USER>` with the created user's name and the two `<PANIC_DIR>` with PANIC's installation directory: 

```bash
[Unit]
Description=PANIC
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
User=<USER>
TimeoutStopSec=90s
WorkingDirectory=<PANIC_DIR>/
ExecStart=/bin/bash <PANIC_DIR>/run_api.sh

[Install]
WantedBy=multi-user.target
```

Lastly, we will *enable* and *start* the alerter service:

```bash
sudo systemctl enable polkadot_api_server.service
sudo systemctl start polkadot_api_server.service
```

Check out `systemctl status polkadot_api_server` to confirm that the API is running.

### Run using Docker
To run the API using Docker, you shouldn't be surprised to find out that you need to install Docker.

You will then obtain the Docker image, make sure that the config files are where they should be, and run everything.

#### Installing Docker on your Machine
To install Docker on your machine, follow [this guide](./INSTALL_DOCKER.md)

#### Obtaining the Docker Image
This part can be done in either of two ways, either by building the Docker image yourself, or by downloading it from Docker Hub.

##### Building the Docker Image
First start off by cloning this repository:
```bash
git clone https://github.com/SimplyVC/panic_polkadot
```

Then run the following commands to build each of the required images:
```bash
cd panic_polkadot/api
docker build -t simplyvc/polkadot_api_server:1.0.0 .
```

##### Downloading the Pre-Built Docker Image from DockerHub
The pre-built Docker container can simply be downloaded by running the following commands:
```bash
docker pull simplyvc/polkadot_api_server:1.0.0
```

#### Config Files Directory and Permissions
The config files needed by the Docker image are the same as those generated in the `Configuring the API` section above.\
These config files can be moved to any directory of your choosing `<CONFIG_DIR>`.

##### On Ubuntu
If you created a new user `<USER>` earlier on, set the permissions as follows:
```bash
sudo chown -R <USER>:<USER> <CONFIG_DIR>
```

##### On Windows
No further steps are required.

#### Running the Docker Image
Now that the Docker image is on your machine, and you have written configurations for it, you can run it as follows, where `<CONFIG_DIR>` is the **full path** to the folder containing the previously created config files:
```bash
docker run -p 3000:3000 \
    -v <CONFIG_DIR>:/opt/polkadot_api_server/config:ro \
    -d simplyvc/polkadot_api_server:1.0.0
```

Note: The port after `-p` and before the `:` can be used to route a port from the machine to the internal port of the Docker. If changing this, any program which refers to the API Docker container must refer to this port.\
Example: with `5678`:3000, the the API URL must look like `http://1.2.3.4:5678`, i.e. the port must match `5678`, and not 3000.

## Confirming the API Works
If you wish to make sure that the API is running, the following should return `{"result":"pong"}`:
```bash
curl -X GET http://localhost:3000/api/pingApi
```

If you wish to check the API's connection to a node, you can run the following for some node `<NODE>`:
```bash
curl -X GET http://localhost:3000/api/pingNode?websocket=ws://<NODE>
```

---
[Back to API front page](../README.md)