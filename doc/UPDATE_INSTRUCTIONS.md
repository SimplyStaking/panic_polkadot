# Update Instructions

To update an instance of PANIC to this version, run these commands inside the project directory:
```bash
git fetch                # Fetch these changes
git checkout v2.3.0      # Switch to this version

# At this stage, you should stop the alerter and the UI

pipenv sync              # Update dependencies
```

The next step is to make sure that you are running version 1.28.1 of the Polkadot API Server, this is important as otherwise PANIC won't be able to retrieve data.

When you have done all of the above follow one of the guides below depending on whether you were running PANIC from source, or using docker-compose.

## Running from Source

### Restart the UI

Start by navigating into the the UI directory and install the packages defined in package.json:
```bash
cd src/web/ui
npm ci --only=production    # use sudo in linux if necessary
```

Re-build the UI, re-direct to the PANIC Polkadot directory, and start the UI
```bash
npm run-script build     # use sudo in linux if necessary
cd ../../../
bash run_ui_server.sh
```

### Restart the Alerter

The final step is to restart the alerter. If the alerter was **running as a Linux service**, the service should now be restarted:
```bash
sudo systemctl restart panic_alerter
```

Otherwise, if you are not using Linux services perform this command in the project directory:
```bash
pipenv sync
pipenv run python run_alerter.py          # use sudo in linux if necessary
# If multiple versions of Python are installed, the python executable may be `python3.6`, `python3.7`, etc.
```

## Run using Docker-Compose

### Update and Run the UI Container

The first step is to obtain the updated UI docker image. This can either be done by re-building it manually or downloading it from Docker Hub.
 
**Option 1: Building the Docker Image**

Run the following command in the project directory to build the image:
```bash
docker-compose build ui
```

**Option 2: Downloading the Pre-Built Docker Image from Docker Hub**

The pre-built Docker image can simply be downloaded by running the following command:
```bash
docker pull simplyvc/panic_polkadot_ui:2.3.0
```

Run the UI docker image using this command:
```bash
docker-compose up -d ui
```

### Update and Run the Alerter Container

Start by obtaining the updated alerter docker image. This can either be done by re-building it manually or by downloading it from Docker Hub

**Option 1: Building The Docker Image**

Run the following command to build the image:
```bash
docker-compose build alerter
```

**Option 2: Downloading the Pre-Built Docker Image from Docker Hub**

The pre-built Docker image can simply be downloaded by running the following command:
```bash
docker pull simplyvc/panic_polkadot:2.3.0
```

Now that the Docker image is on your machine, you can run it as follow:
```bash
docker-compose up -d alerter
```