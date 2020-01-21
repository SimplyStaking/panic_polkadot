FROM node:12

# Create app directory
WORKDIR /opt/polkadot_api_server

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
COPY package*.json ./

#RUN npm install
RUN npm ci --only=production

# Bundle app source
COPY . .
WORKDIR ./src

EXPOSE 3000

CMD [ "node", "server.js" ]
