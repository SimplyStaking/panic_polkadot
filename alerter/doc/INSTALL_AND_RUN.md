# Installing and Running PANIC

This page will guide you through the steps required to get PANIC up and running, including the installation of dependencies and preliminaries. Some steps are optional.

We recommend that PANIC is installed on a Linux system, given the simpler installation and running process. Nevertheless, instructions on how to install the alerter on a Windows system are also provided. 

## Requirements

The major requirements to run the alerter are Python 3 and the JS API.
However, to unlock the full potential of the alerter, we recommend that you install or set up as many of the below requirements as possible:
- Python v3.7.4+ with pip package manager and pipenv packaging tool.
- The JS API
- **Optional**: Telegram account and bots, for Telegram alerts and commands.
- **Optional**: Twilio account, for highly effective phone call alerts.
- **Optional**: Redis server, to keep a backup of the alerter state and to have some control over the alerter, such as to snooze phone call alerts using Telegram commands.

### Python (with pip and pipenv)

To install Python, pip and pipenv follow [this guide](./INSTALL_PYTHON.md)

### JS API

If you haven't already installed the JS API follow [this guide](../../api/doc/INSTALL_AND_RUN.md)

### Optional Features

- **Telegram**: [Click here](./INSTALL_TELEGRAM.md) if you want to set up a Telegram account with bots.
- **Twilio**: [Click here](./INSTALL_TWILIO.md) if you want to set up a Twilio account.
- **Redis server**: [Click here](./INSTALL_REDIS.md) if you want to set up a Redis server.

## Running PANIC

Start by cloning the panic_polkadot repository and navigating into it:
```bash
git clone https://github.com/SimplyVC/panic_polkadot
cd panic_polkadot
```

You can either [run PANIC from source](#running-from-source) or [run PANIC using Docker](#run-using-docker).

### Running from Source

First start by setting up PANIC using [this guide](./SETUP.md).

After setting-up you will be glad to find out that running the alerter is a breeze. To start up the alerter simply run the following commands:
```bash
pipenv sync
pipenv run python run_alerter.py
# If multiple versions of Python are installed, the python executable may be `python3.6`, `python3.7`, etc.
```

Assuming that the setup process was followed till the end, the above commands will start up all of the necessary node, blockchain, and GitHub monitors. These will all start monitoring (and alerting) immediately.

It is recommended to check the console output or general log to make sure that all monitors started-up. Alternatively, you can run the `/status` command on Telegram if you set up both Telegram and Redis.

#### Running the Alerter as a Linux Service

Running the alerter as a service means that it starts up automatically on boot and restarts automatically if it runs into some issue and stops running. To do so, we recommend the following steps:
```bash
# Add a new user to run the alerter
sudo adduser <USER>

# Grant permissions
sudo chown -R <USER>:<USER> <PANIC_DIR>/          # ownership of alerter
sudo chmod -R 700 <PANIC_DIR>/alerter/logs        # write permissions for logs
sudo chmod +x <PANIC_DIR>/run_setup.py            # execute permission for runner (1)
sudo chmod +x <PANIC_DIR>/run_alerter.py          # execute permission for runner (2)

# Create virtual environment using pipenv
cd <PANIC_DIR>
su <USER> -c "pipenv sync"
```

The service file will now be created:

```bash
# Create the service file
sudo nano /etc/systemd/system/panic_alerter.service
```

It should contain the following, replacing `<USER>` with the created user's name and the two `<PANIC_DIR>` with PANIC's installation directory. 
This assumes that `pipenv` is found under `/usr/local/bin/pipenv` and that the Python executable is `python` (if multiple versions of Python are installed, the `python` executable may be `python3.6`, `python3.7`, etc.). We recommend that you run the command set for ExecStart manually to check that it works before starting the service.

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
ExecStart=/usr/local/bin/pipenv run python <PANIC_DIR>/run_alerter.py

[Install]
WantedBy=multi-user.target
```

Lastly, we will *enable* and *start* the alerter service:

```bash
sudo systemctl enable panic_alerter.service
sudo systemctl start panic_alerter.service
```

Check out `systemctl status panic_alerter` or the logs in `<PANIC_DIR>/alerter/logs/` to confirm that the alerter is running. Alternatively, if you set up Telegram, try interacting with the Telegram bot (using `/help`).

### Run using Docker
To run the alerter using Docker, you will first install Docker. 
You will then obtain the Docker images, make sure that the config files are where they should be, and run everything.

#### Installing Docker on your Machine
To install Docker on your machine, follow [this guide](./INSTALL_DOCKER.md)

#### Obtaining the Docker Image
This part can be done in either of two ways, either by [building the Docker image](#building-the-docker-image) yourself, or by [downloading it from Docker Hub](#downloading-the-pre-built-docker-image-from-dockerhub).

##### Building the Docker Image
First start off by cloning this repository:
```bash
git clone https://github.com/SimplyVC/panic_polkadot
```

Then run the following command to build the image:
```bash
cd panic_polkadot
docker build -t simplyvc/panic_polkadot:1.0.0 .
```

##### Downloading the Pre-Built Docker Image from DockerHub
The pre-built Docker container can simply be downloaded by running the following command:
```bash
docker pull simplyvc/panic_polkadot:1.0.0
```

### Config Files Directory and Permissions
First start by setting up PANIC using [this guide](./SETUP.md).

**Important note**: the `redis:host` parameter inside `alerter/config/user_config_main.ini` must be the IP (local or external) of the machine running the Redis container, and not `localhost`. This also applies to `api:polkadot_api_endpoint`.

The config files created by the setup process can be moved to any directory of your choosing `<CONFIG_DIR>`.

### Log Files Directory
Create a folder in any directory of your choosing `<LOGS_DIR>`.
Create a further two sub-directories inside `<LOGS_DIR>`, `alerts` and `general`.
```bash
mkdir <LOGS_DIR>/alerts
mkdir <LOGS_DIR>/general
```

#### On Ubuntu
If you created a new user earlier on, set the permissions as follows:
```bash
sudo chown -R panic_polkadot:panic_polkadot <CONFIG_DIR>
sudo chown -R panic_polkadot:panic_polkadot <LOGS_DIR>
```

#### On Windows
No further steps are required.

### Running the Docker Image

Now that the Docker image is on your machine, and you have written configurations for it, you can run it as follows, where `<CONFIG_DIR>` and `<LOGS_DIR>` are the **full paths** to the previously created folders:
```bash
docker run -v <CONFIG_DIR>:/opt/panic_polkadot/alerter/config:ro \
    -v <LOGS_DIR>:/opt/panic_polkadot/alerter/logs:rw \
    -d simplyvc/panic_polkadot:1.0.0
```

Note: The port after `-p` and before the `:` can be used to route a port from the machine to the internal port of the Docker. If changing this, the PANIC modules which refer to that module must refer to this port.\
Example: with `1234`:3000, the port of the `polkadot_api_endpoint` specified in `alerter/config/user_config_main.ini` must match `1234`, and not 3000.

---
[Back to front page](../../README.md)