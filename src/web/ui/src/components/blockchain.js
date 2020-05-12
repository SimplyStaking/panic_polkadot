class Blockchain {
  constructor(name, referendumCount, publicPropCount, councilPropCount,
    validatorSetSize) {
    this.name_ = name || null;
    this.referendumCount_ = referendumCount || 0;
    this.publicPropCount_ = publicPropCount || 0;
    this.councilPropCount_ = councilPropCount || 0;
    this.validatorSetSize_ = validatorSetSize || 0;
  }

  get name() {
    return this.name_;
  }

  get referendumCount() {
    return this.referendumCount_;
  }

  get publicPropCount() {
    return this.publicPropCount_;
  }

  get councilPropCount() {
    return this.councilPropCount_;
  }

  get validatorSetSize() {
    return this.validatorSetSize_;
  }
}


export default Blockchain;
