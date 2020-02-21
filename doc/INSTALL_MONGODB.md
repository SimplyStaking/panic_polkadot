# DRAFT: Installing MongoDB

**TODO**: add more info to this page if necessary

## Installation

### Installing Directly to System

On Linux:
- https://docs.mongodb.com/manual/administration/install-on-linux/

On Windows:
- https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/

#### Enabling Authentication

- https://docs.mongodb.com/manual/tutorial/enable-authentication/

### Installing using Docker

To install and run MongoDB on your system:

```bash
docker run -p 27017:27017 -d mongo
```

To make sure that Mongo is running:

```bash
docker ps
```

---
[Back to alerter installation page](INSTALL_AND_RUN.md)