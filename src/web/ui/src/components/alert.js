class Alert {
  constructor(severity, message, timestamp) {
    this.severity_ = severity || '';
    this.message_ = message || '';
    this.timestamp_ = timestamp || Date.now();
  }

  get severity() {
    return this.severity_;
  }

  get message() {
    return this.message_;
  }

  get timestamp() {
    return this.timestamp_;
  }
}

export default Alert;
