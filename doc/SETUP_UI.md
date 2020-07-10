# Setting up the UI

To set up the UI you need to do two things. First, since the UI server is an HTTPS server, you need to supply an SSL certificate signed by a certificate authority. The SSL certificate (cert.pem) and the key (key.pem) should be inputted in the `panic_polkadot/src/web/ui/certificates` folder, and they should replace the existing dummy files. Note that these dummy files were given just for convenience as the UI server won't start without them, however, for maximum security these must be replaced.

We suggest reading [this](https://nodejs.org/en/knowledge/HTTP/servers/how-to-create-a-HTTPS-server/) for more details on SSL certificates, and how to generate a self signed certificate in case you do not want to obtain a certificate signed by a certificate authority. However, for maximum security, the self signed certificate option is not recommended.

To prevent malicious access to infrastructure details stored in the web UI, the UI can only be accessed via authentication credentials. These credentials can be defined by running the `run_ui_setup.py` setup script in the project directory:
```bash
pipenv sync                         # use sudo in linux if necessary
pipenv run python run_ui_setup.py   # use sudo in linux if necessary
# If multiple versions of Python are installed, the python executable may be `python3.6`, `python3.7`, etc.
```

Since the UI uses session-based authentication, the user will be asked to enter a cookie secret during the setup process. This is a string used by the UI server to sign the cookie stored in the browser to avoid tampering. For more details about session-based authentication you can read [this](https://medium.com/@sherryhsu/session-vs-token-based-authentication-11a6c5ac45e4)

The setup process above will create a config file `panic_polkadot/config/user_config_ui.ini` containing the UI authentication details. Note that the password is hashed inside the config for maximum security, hence if you would like to change your password, please use the `panic_polkadot/run_util_change_ui_auth_pass.py` util. If you want to change the username and cookie secret, we suggest re-running the `run_ui_setup.py` script. The UI server is able to detect such changes and log out each incorrectly authenticated user automatically, so you do not have to restart the UI server.

**Note that**: Users can only gain access to the UI via 1 set of credentials only.

---
[Back to installation page](INSTALL_AND_RUN.md)