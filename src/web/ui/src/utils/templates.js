const nodeConfig = {
  node_name: '',
  chain_name: '',
  node_ws_url: '',
  node_is_validator: 'false',
  is_archive_node: 'false',
  monitor_node: 'true',
  use_as_data_source: 'true',
  stash_account_address: '',
};

const repoConfig = {
  repo_name: '',
  repo_page: '',
  monitor_repo: 'true',
};

const mainUserConfig = {
  general: { unique_alerter_identifier: '' },
  telegram_alerts: { enabled: 'false', bot_token: '', bot_chat_id: '' },
  email_alerts: {
    enabled: 'false',
    smtp: '',
    from: '',
    to: '',
    user: '',
    pass: '',
  },
  twilio_alerts: {
    enabled: 'false',
    account_sid: '',
    auth_token: '',
    twilio_phone_number: '',
    phone_numbers_to_dial: '',
  },
  telegram_commands: { enabled: 'false', bot_token: '', bot_chat_id: '' },
  redis: {
    enabled: 'false',
    host: '',
    port: '',
    password: '',
  },
  mongo: {
    enabled: 'false',
    host: '',
    port: '',
    db_name: '',
    user: '',
    pass: '',
  },
  api: { polkadot_api_endpoint: '' },
  periodic_alive_reminder: {
    enabled: 'false',
    interval_seconds: '',
    email_enabled: 'false',
    telegram_enabled: 'false',
    mongo_enabled: 'false',
  },
};

export { nodeConfig, repoConfig, mainUserConfig };
