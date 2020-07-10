# Hashes
_hash_blockchain = "hash_bc1"

# Unique keys
_key_twilio_snooze = "tw1"
_key_alive_reminder_mute = "ar1"

# nX_<node_name>
_key_node_went_down_at = "n1"
_key_node_bonded_balance = "n2"
_key_node_is_syncing = "n3"
_key_node_no_of_peers = "n4"
_key_node_active = "n5"
_key_node_council_member = "n6"
_key_node_elected = "n7"
_key_node_disabled = "n8"
_key_node_no_of_blocks_authored = "n9"
_key_node_time_of_last_block = "n10"
_key_node_is_authoring = "n11"
_key_node_time_of_last_block_check_activity = "n12"
_key_node_time_of_last_height_check_activity = "n13"
_key_node_time_of_last_height_change = "n14"
_key_node_finalized_block_height = "n15"
_key_node_no_change_in_height_warning_sent = "n16"
_key_node_auth_index = "n17"

# nmX_<monitor_name>
_key_node_monitor_alive = "nm1"
_key_node_monitor_session_index = "nm2"
_key_node_monitor_last_height_checked = "nm3"
_key_node_monitor_era_index = "nm4"

# bcX_<chain_name>
_key_blockchain_get_referendum_count = "bc1"
_key_blockchain_get_public_prop_count = "bc2"
_key_blockchain_get_council_prop_count = "bc3"
_key_blockchain_get_validator_set_size = "bc4"

# bcmX_<monitor_name>
_key_blockchain_monitor_alive = "bcm1"

# ghX_<repo_name>
_key_github_releases = "gh1"


def _as_prefix(key) -> str:
    return key + "_"


class Keys:

    @staticmethod
    def get_hash_blockchain(chain_name: str) -> str:
        return _as_prefix(_hash_blockchain) + chain_name

    @staticmethod
    def get_twilio_snooze() -> str:
        return _key_twilio_snooze

    @staticmethod
    def get_alive_reminder_mute() -> str:
        return _key_alive_reminder_mute

    @staticmethod
    def get_node_went_down_at(node_name: str) -> str:
        return _as_prefix(_key_node_went_down_at) + node_name

    @staticmethod
    def get_node_bonded_balance(node_name: str) -> str:
        return _as_prefix(_key_node_bonded_balance) + node_name

    @staticmethod
    def get_node_is_syncing(node_name: str) -> str:
        return _as_prefix(_key_node_is_syncing) + node_name

    @staticmethod
    def get_node_no_of_peers(node_name: str) -> str:
        return _as_prefix(_key_node_no_of_peers) + node_name

    @staticmethod
    def get_node_active(node_name: str) -> str:
        return _as_prefix(_key_node_active) + node_name

    @staticmethod
    def get_node_council_member(node_name: str) -> str:
        return _as_prefix(_key_node_council_member) + node_name

    @staticmethod
    def get_node_elected(node_name: str) -> str:
        return _as_prefix(_key_node_elected) + node_name

    @staticmethod
    def get_node_disabled(node_name: str) -> str:
        return _as_prefix(_key_node_disabled) + node_name

    @staticmethod
    def get_node_blocks_authored(node_name: str) -> str:
        return _as_prefix(_key_node_no_of_blocks_authored) + node_name

    @staticmethod
    def get_node_time_of_last_block(node_name: str) -> str:
        return _as_prefix(_key_node_time_of_last_block) + node_name

    @staticmethod
    def get_node_is_authoring(node_name: str) -> str:
        return _as_prefix(_key_node_is_authoring) + node_name

    @staticmethod
    def get_node_time_of_last_block_check_activity(node_name: str) -> str:
        return _as_prefix(
            _key_node_time_of_last_block_check_activity) + node_name

    @staticmethod
    def get_node_time_of_last_height_check_activity(node_name: str) -> str:
        return _as_prefix(
            _key_node_time_of_last_height_check_activity) + node_name

    @staticmethod
    def get_node_time_of_last_height_change(node_name: str) -> str:
        return _as_prefix(_key_node_time_of_last_height_change) + node_name

    @staticmethod
    def get_node_finalized_block_height(node_name: str) -> str:
        return _as_prefix(_key_node_finalized_block_height) + node_name

    @staticmethod
    def get_node_no_change_in_height_warning_sent(node_name: str) -> str:
        return _as_prefix(
            _key_node_no_change_in_height_warning_sent) + node_name

    @staticmethod
    def get_node_auth_index(node_name: str) -> str:
        return _as_prefix(_key_node_auth_index) + node_name

    @staticmethod
    def get_node_monitor_alive(monitor_name: str) -> str:
        return _as_prefix(_key_node_monitor_alive) + monitor_name

    @staticmethod
    def get_node_monitor_session_index(monitor_name: str) -> str:
        return _as_prefix(_key_node_monitor_session_index) + monitor_name

    @staticmethod
    def get_node_monitor_era_index(monitor_name: str) -> str:
        return _as_prefix(_key_node_monitor_era_index) + monitor_name

    @staticmethod
    def get_node_monitor_last_height_checked(monitor_name: str) -> str:
        return _as_prefix(_key_node_monitor_last_height_checked) + monitor_name

    @staticmethod
    def get_blockchain_referendum_count(chain_name: str) -> str:
        return _as_prefix(_key_blockchain_get_referendum_count) + chain_name

    @staticmethod
    def get_blockchain_public_prop_count(chain_name: str) -> str:
        return _as_prefix(_key_blockchain_get_public_prop_count) + chain_name

    @staticmethod
    def get_blockchain_council_prop_count(chain_name: str) -> str:
        return _as_prefix(_key_blockchain_get_council_prop_count) + chain_name

    @staticmethod
    def get_blockchain_validator_set_size(chain_name: str) -> str:
        return _as_prefix(_key_blockchain_get_validator_set_size) + chain_name

    @staticmethod
    def get_blockchain_monitor_alive(monitor_name: str) -> str:
        return _as_prefix(_key_blockchain_monitor_alive) + monitor_name

    @staticmethod
    def get_github_releases(repo_name: str) -> str:
        return _as_prefix(_key_github_releases) + repo_name
