# PANIC for Polkadot


> :warning: **This Repo has been archived. Substrate node monitoring and alerting has been integrated into [this product](https://github.com/SimplyVC/panic), which we now actively maintain.**

<img src="doc/images/IMG_PANIC.png" alt="PANIC Logo"/>

PANIC for [Polkadot](https://polkadot.network/) is a lightweight yet powerful open source monitoring and alerting solution for Polkadot nodes by [Simply VC](https://simply-vc.com.mt/). It is compatible with any [Substrate](https://www.parity.io/substrate/) based chain provided that it is injected with the default types (latest Polkadot and Substrate master types).

The tool was built with user friendliness in mind, without excluding cool and useful features like phone calls for critical alerts and Telegram commands for increased control over your alerter. In addition to this, a brand new **User Interface** is included so that the users can check the status of their nodes at a glance, view alerts in real-time, and easily set-up PANIC to their liking.

The alerter's focus on a modular design means that not only is it beginner friendly but also developer friendly. It allows the user to decide which components of the alerter to set up while making it easy for developers to add new features. PANIC also offers two levels of configurability, _user_ and _internal_, allowing more experienced users to fine-tune the alerter to their preference.

We are sure that PANIC will be beneficial for node operators in the Polkadot community and we look forward for [feedback](https://forms.gle/fLoM39h7TX7HmVMfA). Feel free to read on if you are interested in the design of the alerter, if you wish to try it out, or if you would like to support and contribute to this open source project.

## Design and Features

To be able to monitor and alert, PANIC was designed to retrieve data from Polkadot nodes using a custom-built [Polkadot API Server](https://github.com/SimplyVC/polkadot_api_server). The API Server is an intermediate component which interacts with the Polkadot nodes via the [polkadot-js/api](https://polkadot.js.org/api/). For more details on the API Server please refer to the [Polkadot API Server repository](https://github.com/SimplyVC/polkadot_api_server). If you want to dive into the design and feature set of PANIC [click here](doc/DESIGN_AND_FEATURES.md).

## Ready, Set, Alert!

PANIC is highly dependent on the [Polkadot API Server](https://github.com/SimplyVC/polkadot_api_server) for correct execution. Therefore, if you are ready to try out PANIC on your Polkadot nodes, you should first setup and run the API Server, and connect it to **ALL** nodes you want to monitor using the guides found inside the [Polkadot API Server repository](https://github.com/SimplyVC/polkadot_api_server). After the API Server is successfully running, you should set up and run the alerter using [this guide](doc/INSTALL_AND_RUN.md). We have also provided an installation demo via docker [here](https://www.youtube.com/watch?v=T2y8Gz9PVEo&feature=youtu.be).

## Support and Contribution

On top of the additional work that we will put in ourselves to improve and maintain the tool, any support from the community through development will be greatly appreciated. Before contributing please make sure to read the contribution [guidelines here](CONTRIBUTING.md).

## Who We Are
Simply VC runs highly reliable and secure infrastructure in our own datacentre in Malta, built with the aim of supporting the growth of the blockchain ecosystem. Read more about us on our website and Twitter:

- Simply VC website: <https://simply-vc.com.mt/>
- Simply VC Twitter: <https://twitter.com/Simply_VC>

---

Official PANIC for Polkadot image adapted from [slidescarnival.com](https://www.slidescarnival.com/)
