function capitalizeSentence(sentence) {
  return sentence.charAt(0).toUpperCase() + sentence.slice(1);
}

function toBool(boolStr) {
  return ['true', 'yes', 'y'].some(element => boolStr.toLowerCase()
    .includes(element));
}

function seperatorValuesNonEmpty(data, separator) {
  const result = data.split(separator).map(value => value.trim() === '');
  return result.every(response => response === false);
}

export { capitalizeSentence, toBool, seperatorValuesNonEmpty };
