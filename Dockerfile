FROM python:3.7.5-slim-stretch

# Create app directory
WORKDIR /opt/panic_polkadot

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
COPY Pipfile* ./

RUN pip install pipenv
RUN pipenv sync

# Bundle app source
COPY . .

CMD [ "pipenv", "run", "python", "run_alerter.py" ]
