# Use an official node runtime as a parent image
# TODO: make library compatible with node >= 18
FROM node:16

WORKDIR /app/

# Install dependencies
COPY package.json yarn.lock /app/

RUN yarn

EXPOSE 3000

CMD yarn start
