class Node {
  constructor(name, chain, isValidator, wentDownAt, isDown, isSyncing,
    noOfPeers, lastHeightUpdate, height, bondedBalance, isActive,
    isDisabled, isElected, isCouncilMember, noOfBlocksAuthored) {
    this.name_ = name || '';
    this.chain_ = chain || '';
    this.isValidator_ = isValidator || false;
    this.wentDownAt_ = wentDownAt || null;
    this.isDown_ = isDown || false;
    this.isSyncing_ = isSyncing || false;
    this.noOfPeers_ = noOfPeers || 0;
    this.lastHeightUpdate_ = lastHeightUpdate || Date.now(); // timestamp
    this.height_ = height || 0;
    this.bondedBalance_ = bondedBalance || 0;
    this.isActive_ = isActive || false;
    this.isDisabled_ = isDisabled || false;
    this.isElected_ = isElected || false;
    this.isCouncilMember_ = isCouncilMember || false;
    this.noOfBlocksAuthored_ = noOfBlocksAuthored || 0;
  }

  get name() {
    return this.name_;
  }

  get chain() {
    return this.chain_;
  }

  get isValidator() {
    return this.isValidator_;
  }

  get wentDownAt() {
    return this.wentDownAt_;
  }

  get isDown() {
    return this.isDown_;
  }

  get isSyncing() {
    return this.isSyncing_;
  }

  get noOfPeers() {
    return this.noOfPeers_;
  }

  get lastHeightUpdate() {
    return this.lastHeightUpdate_;
  }

  get height() {
    return this.height_;
  }

  get bondedBalance() {
    return this.bondedBalance_;
  }

  get isActive() {
    return this.isActive_;
  }

  get isDisabled() {
    return this.isDisabled_;
  }

  get isElected() {
    return this.isElected_;
  }

  get isCouncilMember() {
    return this.isCouncilMember_;
  }

  get noOfBlocksAuthored() {
    return this.noOfBlocksAuthored_;
  }
}

export default Node;
