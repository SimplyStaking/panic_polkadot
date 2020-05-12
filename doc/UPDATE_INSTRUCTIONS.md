# Update Instructions

To update an instance of PANIC to this version, run these commands inside the project directory:
```bash
git fetch                # Fetch these changes
git checkout v2.0.0      # Switch to this version

# At this stage, you should stop PANIC

pipenv sync              # Update dependencies
```

Given the recent overhaul of how PANIC uses Redis, we highly recommend clearing up Redis by running the `run_util_reset_redis.py` script using this command:
```bash
pipenv run python run_util_reset_redis.py         # Reset redis. Replace 'python' with 'python3' if the latter was installed
```

## Alerter
PANIC can now be started up!

If the alerter was **running as a Linux service**, the service should now be restarted:
```bash
sudo systemctl restart panic_alerter
```

For all users **running PANIC using Docker**, we now have a new installation and running procedure using Docker-Compose.

Therefore, start by stopping the Mongo, Redis and alerter containers using this command:
```bash
docker kill <MONGO_CONTAINER_ID> <REDIS_CONTAINER_ID> <ALERTER_CONTAINER_ID>
```

Now, proceed as follows:
* First [install Docker-Compose](INSTALL_DOCKER_AND_COMPOSE.md) if it is currently not installed on your system.
* Follow the instructions in [this guide](INSTALL_AND_RUN.md#run-using-docker) to re-build and re-run the images.

## User Interface

To make use of the brand new PANIC Web UI:
* **Running from source**: Follow the instructions [here](INSTALL_AND_RUN.md#running-from-source)
* **Running using Docker and Docker-Compose**: Follow the instructions [here](INSTALL_AND_RUN.md#run-using-docker)