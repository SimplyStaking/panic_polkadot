# Setting up the Alerter

The alerter requires its own setup process, involving three main parts, each of which generates its own respective config file:

- Linking up any of the optional features that you set up (`config/user_config_main.ini`)
- Providing a list of nodes that you wish to monitor (`config/user_config_nodes.ini`)
- Providing a list of GitHub repositories that you wish to monitor (`config/user_config_repos.ini`)

## Generating the config files

To generate the config files, the operator has three options.

### Using the Web UI

This method is the one that we highly recommend. The user can use the Web UI to set-up the alerter as follows:

- Go to the Settings &rarr; Main page to generate the `user_config_main.ini` file in the `panic_polkadot/config` folder.
- Go to the Settings &rarr; Nodes page to generate the `user_config_nodes.ini` file in the `panic_polkadot/config` folder.
- Go to the Settings &rarr; Repos page to generate the `user_config_repos.ini` file in the `panic_polkadot/config` folder.

It is of utmost importance that you follow the sequence provided above for expected execution/behaviour. The setup pages will let you know if they are able to tell that your information is not as expected!

**IMPORTANT NOTE:** The alerter is not able to detect changes in the config files mentioned above. Therefore, do not forget to restart the alerter after updating the config files. If you are using docker and the alerter container has already been created, you must restart the alerter container using the following command, otherwise, the changes would not be detected:

```bash
docker-compose restart alerter
```

In addition to this, if nodes are added/removed from the `config/user_config_nodes.ini` file, do not forget to update the [Polkadot API Server](https://github.com/SimplyVC/polkadot_api_server).

### Programmatic Setup Process

If you do not wish to use the Web UI, you can use the programmatic setup process which is started up by running the following in the project directory:

```bash
pipenv sync                             # use sudo in linux if necessary
pipenv run python run_alerter_setup.py  # use sudo in linux if necessary
# If multiple versions of Python are installed, the python executable may be `python3.6`, `python3.7`, etc.
```

The programmatic setup process is guided by instructions which we highly recommend that you read. The setup of any optional feature that was not installed in the previous section can be skipped. For convenience, any yes/no question can be answered with a *yes* just by pressing *ENTER*.

Lastly, note that if you wish to change some configurations and run the setup process again, it will detect the config files and will not simply overwrite the current configurations.

**IMPORTANT NOTE:** The alerter is not able to detect changes in the config files. Therefore, do not forget to restart the alerter after updating the config files. If you are using docker and the alerter container has already been created, you must restart the alerter container using the following command, otherwise, the changes would not be detected:

```bash
docker-compose restart alerter
```

In addition to this, if nodes are added/removed from the `config/user_config_nodes.ini` file, do not forget to update the [Polkadot API Server](https://github.com/SimplyVC/polkadot_api_server).

### Manually

Alternatively, you can take a look at the three `config/example_***.ini` files and perform the config file generation manually by copying the three example config files to the ones listed above and replacing the example pieces of information with actual ones.

**IMPORTANT NOTE:** The alerter is not able to detect changes in the config files. Therefore, do not forget to restart the alerter after updating the config files. If you are using docker and the alerter container has already been created, you must restart the alerter container using the following command, otherwise, the changes would not be detected:

```bash
docker-compose restart alerter
```

In addition to this, if nodes are added/removed from the `config/user_config_nodes.ini` file, do not forget to update the [Polkadot API Server](https://github.com/SimplyVC/polkadot_api_server). 

## Advanced Configuration

If you had a look in the `config/` folder, you may have seen the `config/internal_config_*.ini` files.

The **main internal configuration file** (`config/internal_config_main.ini`) defines values that are less likely to require changing. In fact, there is neither a setup page in the Web UI, nor a programmatic setup process.

However, we encourage more advanced users to experiment with different configurations if the consequences of any changes are realised and acknowledged beforehand.

This file consists of values such as:
- Which files to use for logging, and the logging level
- Which Redis databases to use (10 and 11 by default)
- Which Redis keys to use to store values in Redis
- Timeout setting for certain temporary Redis keys
- Data collection periods for each of the monitor types
- Alert frequency and severity modifiers (by time intervals and boundaries)
- Links to use for the `/validators`, `/block`, and `/tx` Telegram commands.

The **alerts internal configuration file** (`config/internal_config_alerts.ini`) lists all possible alerts and alert severities, allowing the user to disable specific alerts or even a whole alert severity.
 
The user can disable/enable specific alerts/severities either by manually setting the respective key in the `config/internal_config_alerts.ini` file from `True` to `False`, or by using the Alerts &rarr; Preferences page of the Web UI.

---
[Back to alerter installation page](INSTALL_AND_RUN.md)