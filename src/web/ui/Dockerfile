FROM node:12

# Create app directory
WORKDIR /opt/panic_polkadot

# Copy the shell script used to run the UI
COPY ./run_ui_server.sh ./

# Change directory, and copy all UI contents from the host to the container.
WORKDIR ./src/web/ui
COPY ./src/web/ui ./

# RUN npm install
RUN npm install

# Build UI
RUN npm run-script build

# Change directory to run the UI
WORKDIR ../../../

# Expose port
EXPOSE 9000

CMD [ "bash", "run_ui_server.sh" ]
