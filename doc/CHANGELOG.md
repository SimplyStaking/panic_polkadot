# Change Log

## Unreleased

<!--New features/improvements/fixes go here-->

## 1.1.0

Released on 21st February 2020

This release of PANIC for Polkadot gives the operator more **flexibility** in how they want to use the tool. Although PANIC is happy to keep an eye on multiple nodes, the operator can now run PANIC with as little as one node.

The **Polkadot API server** that PANIC uses to extract data from nodes has been moved into its own [repository](https://github.com/SimplyVC/polkadot_api_server) and will thus have to be installed from there from now on. As a result of this, the config files and log files will now be expected to be in the project directories of the two separate tools. This is elaborated-on below.

As for new features, this version introduces **MongoDB** as a possible alerting channel. In future versions, the alerts stored in MongoDB will be used to present logs in a **dashboard UI**!

### Update Instructions

Before updating PANIC to the new version, we strongly recommend that you clone and set up the [Polkadot API server](https://github.com/SimplyVC/polkadot_api_server) if you have not already done this.

Additionally, you should make backups of the `logs/` and `config/` folders under both `api/` and `alerter/`. The API config folder can be moved to the now separate Polkadot API Server directory.

To update an instance of PANIC to this version:
```bash
git fetch            # Fetch these changes
git checkout v1.1.0  # Switch to this version

# At this stage, you should stop PANIC

mv alerter/config/*.ini config/             # copy alerter configs to new location
mv alerter/logs/alerts/*.log logs/alerts/   # copy alerts logs to new location
mv alerter/logs/general/*.log logs/general/ # copy general logs to new location

# You might have to update permissions so that PANIC 
# is able to create log files in the new logs folders

pipenv sync                                     # Update dependencies
pipenv run python run_util_update_to_v1.1.0.py  # Migrate config files
```

The `run_util_update_to_v1.1.0.py` script updates the config files (now expected to be under `config/`) so that they become compatible with the v1.1.0 config files.

PANIC can now be started up!

* If the alerter was running as a Linux service, the service should now be restarted:
```bash
sudo systemctl restart panic_alerter
```
* If the alerter was running on Docker, the docker image should now be started:
```bash
docker run -v <CONFIG_DIR>:/opt/panic_polkadot/config:ro \
    -v <LOGS_DIR>:/opt/panic_polkadot/logs:rw \
    -d simplyvc/panic_polkadot:1.1.0
```

### Features

* (channels) Added new MongoDB channel to be used by the dashboard UI (coming soon!)

### Improvements

* (design) Code structure now closer to the design
* (config) Periodic alive reminder config variables now use `par_` prefix to not get mixed up with other variables
* (telegram) Node monitor block height is now not shown in Telegram if archive monitoring is disabled for the respective chain
* (monitoring) Validators can now be used as a data source for node indirect monitoring and blockchain monitoring by setting the variable `use_as_data_source` to `true` for the validator in the `config/user_config_nodes.ini` config file. As a result, validator node monitors can use the validator they are monitoring as an indirect data source, however this is a last resort.
* (monitoring) Validators can now be used as a data source for archive monitoring by setting the variables `use_as_data_source` and `is_archive_node` to `true` for the validator in the `config/user_config_nodes.ini` config file. As a result, the validator node monitors can use the validator they are monitoring as an archive data source, however this is a last resort.

### Bug Fix

* (testing) `run_tests_with_coverage.sh` script now includes `--dev` command
* (monitoring) If no data sources for a chain are given by the operator, the user is informed that no blockchain monitor will start for that chain, rather than the blockchain monitor not starting at all.
* (monitoring) If no archive data sources for a chain are given by the operator, the user is informed that archive monitoring is disabled for that chain, rather than not being informed at all.
* (monitoring) The node monitor can now perform direct monitoring without indirect monitoring for validators by giving no data sources.

### Breaking Changes

* Separated Polkadot API Server into its own [repository](https://github.com/SimplyVC/polkadot_api_server)
    * Alerter config files need to be moved manually from `alerter/config/<files>` to `config/<files>` of this project.
    * API server config files need to be moved manually from `api/config/<files>` to `config/<files>` of the [API server](https://github.com/SimplyVC/polkadot_api_server).
    * Any service files or custom runners for the API server need to be pointed to the new instance of the [API server](https://github.com/SimplyVC/polkadot_api_server).
    * The provided PANIC runner (`run_alerter.py`) has not changed location and is still in the project directory.
* Changed the name of some variables in the `user_config_nodes` config file for clarity. These are:
    * `include_in_node_monitor` &rightarrow; `monitor_node`
    * `include_in_blockchain_monitor` &rightarrow; `use_as_data_source`
    * `include_in_github_monitor` &rightarrow; `monitor_repo`

**Additional note on the above:**
* The new keys have a slightly different meaning.
  * `monitor_node` stores whether a node should be monitored by a node monitor
  * `use_as_data_source` stores whether a node should be used as a data source for indirect monitoring, and archive monitoring if it is an archive node
  * `monitor_repo` stores whether the GitHub repo should be monitored using a GitHub monitor.
* If the `run_util_update_configs_to_v1.1.0.py` is run to update the configs, the key values for `monitor_node` and `use_as_data_source` are set as `true`, whilst for the `monitor_repo` the value is set to the old value of the `include_in_github_monitor` key.

## 1.0.0

Released on 21st January 2020

This release of PANIC for Polkadot satisfies Milestone 1 of the [Web3 Foundation grant](https://github.com/w3f/Web3-collaboration/blob/master/grants/speculative/panic_by_simply_vc.md) for this project.

Apart from the tool itself, it includes an API server for Polkadot nodes (now found [here](https://github.com/simplyvc/polkadot_api_server)) and testing reports are also included.

### Added

* First version of PANIC for Polkadot by Simply VC
