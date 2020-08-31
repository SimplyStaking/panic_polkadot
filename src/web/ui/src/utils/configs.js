import { toBool } from './string';

function clearSectionData(data) {
  const clearedData = data;
  Object.entries(data).forEach(([key, _]) => {
    if (key !== 'enabled') {
      clearedData[key] = '';
    }
  });
  return clearedData;
}

function checkSectionAndFix(section, template) {
  const fixedConfig = section;
  Object.entries(template).forEach(([key, value]) => {
    if (!Object.prototype.hasOwnProperty.call(fixedConfig, key)) {
      fixedConfig[key] = value;
    }
  });
  return fixedConfig;
}

function fixSpecificSectionsOfConfig(config, template, prefix = '') {
  const fixedConfig = config;
  Object.entries(config).forEach(([section, data]) => {
    if (section.startsWith(prefix)) {
      fixedConfig[section] = checkSectionAndFix(data, template);
    }
  });
  return fixedConfig;
}

function checkConfigAndFix(config, template) {
  const fixedConfig = config;
  Object.entries(template).forEach(([section, data]) => {
    if (!Object.prototype.hasOwnProperty.call(fixedConfig, section)) {
      fixedConfig[section] = data;
    } else {
      fixedConfig[section] = checkSectionAndFix(fixedConfig[section], data);
    }
  });
  return fixedConfig;
}

function keepSpecificSectionsFromConfig(config, prefix = '') {
  const fixedConfig = config;
  Object.entries(config).forEach(([section, _]) => {
    if (!section.startsWith(prefix)) {
      delete fixedConfig[section];
    }
  });
  return fixedConfig;
}

function fieldEmpty(data) {
  return data.trim() === '';
}

function highestItemIndexInConfig(config, prefix = '') {
  let highestItemIndex = -1;
  Object.keys(config).forEach((key) => {
    const itemNumber = parseInt(key.substr(key.indexOf('_') + 1, key.length),
      10);
    if (key.startsWith(prefix) && !Number.isNaN(itemNumber)
      && itemNumber > highestItemIndex) {
      highestItemIndex = itemNumber;
    }
  });
  return highestItemIndex;
}

function fieldValueUniqueAmongAllfieldsInJSON(jsonObject, field, value) {
  const result = Object.entries(jsonObject).map(
    ([_, data]) => (data[field] !== value),
  );
  return result.every(response => response === true);
}

// This function is used to fix data fields which are dependent on each other.
// For example there is no need to store the mongo password if authentication
// is disabled. This must be done before saving the config to prevent having
// un-meaningful data in the config.
function fixUserConfigMain(mainUserConfigJson) {
  const newMainUserConfig = mainUserConfigJson;
  // if username is blank, then authentication is disabled, therefore
  // password should be cleared
  if (fieldEmpty(newMainUserConfig.email_alerts.user)) {
    newMainUserConfig.email_alerts.pass = '';
  }
  if (fieldEmpty(newMainUserConfig.mongo.user)) {
    newMainUserConfig.mongo.pass = '';
  }

  // if a channel is disabled, there is no point in leaving it enabled for
  // the PAR
  if (!toBool(newMainUserConfig.email_alerts.enabled)) {
    newMainUserConfig.periodic_alive_reminder.email_enabled = 'false';
  }
  if (!toBool(newMainUserConfig.telegram_alerts.enabled)) {
    newMainUserConfig.periodic_alive_reminder.telegram_enabled = 'false';
  }
  if (!toBool(newMainUserConfig.mongo.enabled)) {
    newMainUserConfig.periodic_alive_reminder.mongo_enabled = 'false';
  }

  // Clear data of non-enabled sections
  Object.entries(newMainUserConfig).forEach(([section, data]) => {
    if (section !== 'general' && section !== 'api') {
      if (toBool(newMainUserConfig[section].enabled) === false) {
        newMainUserConfig[section] = clearSectionData(data);
      }
    }
  });

  return newMainUserConfig;
}

export {
  clearSectionData, checkConfigAndFix, fieldEmpty, highestItemIndexInConfig,
  fieldValueUniqueAmongAllfieldsInJSON, fixSpecificSectionsOfConfig,
  keepSpecificSectionsFromConfig, fixUserConfigMain,
};
