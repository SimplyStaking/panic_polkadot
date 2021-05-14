# Change Log

## Unreleased

## 2.3.0

Released on 7th May 2021

* (alerter) Updated dependencies.
* (alerter) Fixed issue with persistent connections when retrieving data from the API Server.
* (UI) Fixed some security vulnerabilities for fixable dependencies.

## 2.2.0

Released on 13th April 2021

* Fixed failing unit tests.
* Fixed UI dependencies.
* Now using react-toastify notifications.

## 2.1.3

Released on 29th January 2021

**Alerter**:
* Fixed number of blocks authored, session index, era index, proposal counts and referendum count parsing. Now the parsing takes in consideration values in hex.

**UI**:
* Updated third party libraries

PANIC is now compatible with version 1.26.1 of the Polkadot API Server.

## 2.1.2

Released on 3rd September 2020

### Bug Fixes

* (CLI Setup) The cli setup now writes the `chain_name` key for each node configuration inside the `user_config_nodes.ini` file as expected.

## 2.1.1

Released on 31th August 2020

### Improvements

*(UI Setup) When the user inputs the password during the UI setup process, the password is not displayed on the terminal. Note that for this setup script to execute as expected, the UI setup process must be executed inside a proper terminal.
*(UI Server) The UI server now requires authentication to get data from any endpoint.

### Bug Fixes

*(UI Nodes and Repos pages) The remove button in the Added Nodes/Repos table no longer fails to remove a node from the list if there are more than 9 nodes.

## 2.1.0

Released on 10th July 2020

### Improvements
* (UI)
    * (Authentication) Session based authentication is now used to secure access to the UI. The user must define a username and password by running the `run_ui_setup.py` script.
    * (Dashboard) The data cards now have a fixed height and are placed on the dashboard using `react-bootstrap`'s grid system. This avoids having messy data cards, and adds more structure to the layout of the dashboard.
    * (HTTPS) The UI back-end server is now an HTTPS server. The user must put his own SSL certificate signed by a certificate authority in the `panic_polkadot/src/web/ui/certificates` folder for maximum security. For convenience, a dummy certificate and key are provided. Note, the UI server does not start without these files.
* (alerter)
    * Whenever a validator node monitor loses connection with the API server for 15 seconds, a critical alert is sent to the operator, informing them that the monitor cannot retrieve validator data for monitoring.
    * The alerter now calculates `blocks authored` alerts over an era, not session. By default, the alerter will now raise a `no blocks authored so far` or `last block authored block was 3 hrs ago` if 3 hours passed and no blocks have been authored in the current era or since the last block authored in the current era respectively. Note, the user can set the `max_time_alert_between_blocks_authored` in the `internal_config_main.ini` config to any value less than the era duration.
* (setup) The CLI setup no longer forces nodes and repos to be accessible for them to be added to the configs.

### Bug Fixes

* (UI Dashboard) The columns of the `Monitors Status` table were fixed to a minimum of `200px` in width. This allows for better visualisation on mobile devices.
* (UI Settings Pages) The `Save Config` button in the `Nodes` and `Settings` pages no longer disappears when the respective configs are empty.
* (alerter)
    * A monitor no longer fails if a function from the Polkadot API Server fails.
    * A node that is removed from the API server is no longer declared as down. Now, the user is specifically informed about this scenario via a critical/warning alert if the node is a validator/full-node respectively. The user is then informed via an info alert whenever the operator adds the node back to the API server.
    * PANIC no longer crashes if one of the nodes/repos is inaccessible during start-up. In this version, the monitor belonging to the inaccessible node/repo only does not start.
* (UI twilio) Fixed Twilio error not being reported when making a test call with an incorrectly formatted AccountSID or Auth Token.

### Other

* (Security Vulnerability) Updated `package-lock.json` to resolve the `Denial of Service` vulnerability issue in `react-scripts`.
* Better file/folder layout and decomposition of components.
* The `run_setup.py` file was renamed to `run_alerter_setup.py`, as a new setup script named `run_ui_setup.py` was added for the UI.
* A new config file was added for the UI named `user_config_ui.ini`, and can be located in the `panic_polkadot/config` folder.
* The `run_util_validate_configs.py` now also validates the `user_config_ui.ini` config.
* Added util `run_util_change_ui_auth_pass.py` to change the UI authentication password.

## 2.0.1

Released on 15th May 2020

This new version of PANIC fixes some UI related minor bugs.

### Bug Fixes

* (UI buttons) After they are clicked, the buttons will now have the same colour as the navigation bar rather than their colour getting stuck.
* (UI Main page) The `To` and `Phone numbers to dial` fields in the `Email alerts` and `Twilio alerts` forms respectively were incorrectly set up to use comma separators instead of colon separators, which clashes with PANIC. Now, these fields can take multiple inputs separated with a colon.

## 2.0.0

Released on 12th May 2020

First things first, this new version of PANIC is now **compatible with the latest changes in the [Polkadot API](https://polkadot.js.org/api/)**, and is packed with new features.

Users can now install our brand new **Web UI** to view the status of the nodes, alerter and view alerts in real-time. The Web UI can also be used for much simpler setting up and reconfiguration of PANIC, including switching on/off specific alerts.

But this is not all. Redis keys are now much more efficient and organized using **hash-based functions**, and we also included **Mongo's status in Telegram**.

As a way to facilitate the life of users running PANIC using docker, we also improved PANIC's docker installation using **docker-compose**.

### Breaking Changes

* (redis) Nodes, blockchains, GitHub repositories, and monitor keys have been changed as a result of improvements in the use of Redis keys

### Polkadot API Compatibility Changes

* (data wrapper) PANIC is now using different endpoints from the [Polkadot API server](https://github.com/SimplyVC/polkadot_api_server) due to changes in the [polkadot-js/api](https://github.com/polkadot-js/api)
    * To get the set of elected validators for the next session, PANIC is now using the `/api/derive/staking/validators` endpoint instead of the `/api/query/staking/currentElected` endpoint.
    * To get the bonded balance of a validator, PANIC is now using the `/api/query/staking/erasStakers` endpoint instead of the `/api/query/staking/stakers` endpoint.
* (parsing) Some monitors are now expecting different JSON structures from the [Polkadot API server](https://github.com/SimplyVC/polkadot_api_server) due to updates in the [polkadot-js/api](https://github.com/polkadot-js/api).
    * For ongoing referendums, the blockchain monitor expects the `/api/query/democracy/referendumInfoOf` endpoint to return a JSON with the following structure:
      ```
      {
            'Ongoing': {
                'proposalHash': '0x345jtg8ergfg8df89h9we9t9sd9g9gsd9g9sdfg',
                'end': 124143848,
                'threshold': 'Supermajorityapproval',
                'delay': 11549,
                'tally': {
                    'ayes': '4544545 KSM',
                    'nayes': '3454 KSM',
                    'turnout': '4545454454 KSM'
                }
            }
        }
      ```

### Features

* (alerts) Added ability to switch on/off specific alerts via the alerts internal config (`internal_config_alerts.ini`)
* (web) Added the full implementation of the Web UI for PANIC. The operator can use this UI in the following ways:
    * Use the `Dashboard` page to view the status of the nodes, chains and monitors.
    * Use the `Alerts` &rightarrow; `Logs` page to view incoming alerts. The operator can also view historical alerts by navigating through this page.
    * Use the `Settings` &rightarrow; (`Main`, `Nodes`, `Repos`) pages to create the `user_config_main.ini`, `user_config_nodes.ini`, `user_config_repos.ini` files respectively. This facilitates the setting up process of PANIC.
    * Use the `Alerts` &rightarrow; `Preferences` page to switch on/off specific alerts. The operator can also switch off alerts of a particular severity.
* (redis) Added hash-based `hset`/`hget` functions (and variations) to the Redis API
* (telegram) Added Mongo's status in the Telegram `/status` output.
* (docker) Dockerised the Web UI
* (docker) Added the functionality of using docker-compose to run the Web UI, Alerter, Mongo and Redis.
    * Each component is able to restart automatically if it runs into an erroneous state and crashes.

### Improvements

* (twilio) Added official support for [TwiML](https://www.twilio.com/docs/voice/twiml). Configurable from the internal config to either a URL or raw TwiML instructions
* (redis) Centralised and streamlined Redis key usage in a new `store_keys.Keys` class
* (redis) Keys for nodes from a blockchain and the blockchain itself are now grouped using hashes (`hset`/`hget`)
* (redis) Reduced code duplication in Redis API by defining a `_safe` function with common error-handling and default return value functionality
* (timing) PANIC now saves date & time values in the store as UTC timestamps instead of datetime

### Bug Fixes

* (setup) Repository names are now forced to be unique during setup. This is necessary to prevent key clashes in Redis

### Other

* Renamed `internal_config.ini` to `internal_config_main.ini`
* Moved RedisApi and MongoApi to `store/` folder to match PANIC's design
* Updated the documentation to be compatible with the latest changes.

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
