# Update Instructions

To update an instance of PANIC to this version, run these commands inside the project directory:
```bash
git fetch                # Fetch these changes
git checkout v2.0.1      # Switch to this version

# At this stage, you should stop the alerter and the UI

pipenv sync              # Update dependencies
```

Follow one of the guides below depending whether you were running PANIC from source, or using docker-compose.

## Running from Source

First navigate into the the UI directory and install the packages defined in package.json:
```bash
cd src/web/ui
npm install              # use sudo in linux if necessary
```

Re-build the UI, re-direct to the PANIC Polkadot directory, and start the UI
```bash
npm run-script build     # use sudo in linux if necessary
cd ../../../
bash run_ui_server.sh
```

The next step is to make sure that the inputs in the `To` and `Phone numbers to dial` fields in the `E-mail Alerts` and `Twilio Alerts` forms respectively are formatted as required by the `Main` page.

To make sure that the above step is correct, click on `Save Config`. The `Main` page should perform the validation itself.

For PANIC to detect changes in the configs (if any), the next step is to restart the alerter. If the alerter was **running as a Linux service**, the service should now be restarted:
```bash
sudo systemctl restart panic_alerter
```

Otherwise, perform this command in the project directory:
```bash
pipenv sync
pipenv run python run_alerter.py          # use sudo in linux if necessary
# If multiple versions of Python are installed, the python executable may be `python3.6`, `python3.7`, etc.
```

## Run using Docker-Compose

First, either re-build the docker image for the UI, or download it from Docker Hub.
 
**Option 1: Building The Docker Image**

Run the following command in the project directory to build the image:
```bash
docker-compose build ui
```

**Option 2: Downloading the Pre-Built Docker Image from Docker Hub**

The pre-built Docker image can simply be downloaded by running the following command:
```bash
docker pull simplyvc/panic_polkadot_ui:1.0.1
```

Run the UI docker image using this command:
```bash
docker-compose up -d ui
```

The next step is to make sure that the inputs in the `To` and `Phone numbers to dial` fields in the `E-mail Alerts` and `Twilio Alerts` forms respectively are formatted as required by the `Main` page.

To make sure that the above step is correct, click on `Save Config`. The `Main` page should perform the validation itself.

For PANIC to detect changes in the configs (if any), the next step is to restart the alerter container using this command:
```bash
docker-compose restart alerter
```