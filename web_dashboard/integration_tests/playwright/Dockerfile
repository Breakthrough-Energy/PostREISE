FROM mcr.microsoft.com/playwright:bionic

WORKDIR /integration/

# Install dependencies
COPY package.json yarn.lock /integration/

RUN yarn

CMD /bin/bash