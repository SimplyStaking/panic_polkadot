const RESOURCE_NOT_FOUND = {
  code: 404,
  message: 'Oh no, it seems you have wandered to the unknown.',
};

const DEFAULT_ERROR = {
  message: 'Wow, that\'s embarrassing. We are working on fixing this.',
  code: 430,
};

const INTERNAL_ALERTS_CONFIG_NOT_FOUND = {
  code: 431,
  message: 'The internal alerts config is either missing or empty.',
};

const MONGO_NOT_SET_UP = {
  code: 432,
  message: 'Mongo not set up',
};

export {
  RESOURCE_NOT_FOUND,
  DEFAULT_ERROR,
  INTERNAL_ALERTS_CONFIG_NOT_FOUND,
  MONGO_NOT_SET_UP,
};
