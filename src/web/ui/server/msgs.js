module.exports = {
  // General
  MSG_MISSING_ARGUMENTS: 'Missing arguments',
  MSG_INVALID_ENDPOINT: 'Invalid endpoint',
  MSG_PONG: 'pong',
  MSG_NO_CONNECTION: 'No connection',
  MSG_RETRY_TIME_EXCEEDED: 'Retry time exceeded',
  MSG_CHAIN_NOT_FOUND: 'Chain not found',

  // Authentication
  MSG_INVALID_AUTH: 'Incorrect credentials',

  // Configs
  MSG_CONFIG_UNRECOGNIZED: 'Config unrecognised',
  MSG_CONFIG_SUBMITTED: 'Config submitted',
  MSG_CONFIG_EMPTY: 'Config empty',
  MSG_CONFIG_NOT_FOUND: 'Config not found',

  // General channel errors
  MSG_REDIS_ERROR: 'Redis error',
  MSG_MONGO_ERROR: 'Mongo error',
  MSG_TWILIO_ERROR: 'Twilio error',
  MSG_SMTP_ERROR: 'SMTP error',

  // Redis
  MSG_REDIS_NOT_SET_UP: 'Redis not set up',
  MSG_REDIS_NOT_SET_UP_LONG: 'Tried to use Redis but Redis not set up or '
    + 'main user config missing.',
  MSG_REDIS_RECONNECTING: 'Redis is reconnecting...',
  MSG_REDIS_CONNECTED: 'Redis connection established ',
  MSG_REDIS_AUTH_INCORRECT: 'Redis password missing or incorrect',

  // Mongo
  MSG_MONGO_NOT_SET_UP: 'Mongo not set up',
  MSG_MONGO_NOT_SET_UP_LONG: 'Tried to use Mongo but Mongo not set up or '
    + 'main user config missing.',

  // Polkadot API server
  MSG_POLKADOT_API_SERVER_ERROR: 'Polkadot API server error',
  MSG_POLKADOT_API_SERVER_NOT_CONFIGURED: 'Polkadot API server not configured',
};

// TODO: error messages should be able to take arguments sometimes
// Example: the MSG_MISSING_ARGUMENTS can take the actual arguments
