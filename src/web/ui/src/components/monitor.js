class Monitor {
  constructor(name, chain, lastUpdate, type) {
    this.name_ = name || '';
    this.chain_ = chain || '';
    this.lastUpdate_ = lastUpdate || Date.now(); // timestamp
    this.type_ = type || '';
  }

  get name() {
    return this.name_;
  }

  set name(name) {
    this.name_ = name;
  }

  get chain() {
    return this.chain_;
  }

  set chain(chain) {
    this.chain_ = chain;
  }

  get lastUpdate() {
    return this.lastUpdate_;
  }

  set lastUpdate(lastUpdate) {
    this.lastUpdate_ = lastUpdate;
  }

  get type() {
    return this.type_;
  }

  set monitorType(type) {
    this.type_ = type;
  }
}

export default Monitor;
