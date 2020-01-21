# The Custom JavaScript API

The custom JavaScript (JS) API is a wrap-around of the [polkadot-js/api](https://polkadot.js.org/api/). This makes it easier to use the polkadot-js/api with any programming language in order to query data from Polkadot nodes. In addition to this, a number of custom defined calls were also implemented in the JS API. For example, one can query directly the amount of tokens a validator has been slashed at any block height.

The JS API was specifically built as a way for PANIC to be able to retrieve data from the Polkadot nodes that it will monitor. As a result, not all functions from the polkadot-js/api were included in the JS API. Note that in the future the JS API will be moved to a separate repository, as it can be used without PANIC. 

## Design and Features

If you want to dive into the design and feature set of the JS API [click here](doc/DESIGN_AND_FEATURES.md).

## Ready, Set, Query!

If you are ready to try out the JS API on your Polkadot nodes, setup and run the JS API using [this](doc/INSTALL_AND_RUN.md) guide.

---
[Back to front page](../README.md)