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

function keepSpecificSectionsFromConfig(config, prefix = '') {
  const fixedConfig = config;
  Object.entries(config).forEach(([section, _]) => {
    if (!section.startsWith(prefix)) {
      delete fixedConfig[section];
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

function fieldEmpty(data) {
  return data.trim() === '';
}

function highestItemIndexInConfig(config, prefix = '') {
  let highestItemIndex = -1;
  Object.keys(config).forEach((key) => {
    const itemNumber = parseInt(key.substr(key.length - 1), 10);
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

export {
  clearSectionData, checkConfigAndFix, fieldEmpty, highestItemIndexInConfig,
  fieldValueUniqueAmongAllfieldsInJSON, fixSpecificSectionsOfConfig,
  keepSpecificSectionsFromConfig,
};
