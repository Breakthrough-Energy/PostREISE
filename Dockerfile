FROM powersimdata:latest

WORKDIR /PostREISE
COPY Pipfile .
COPY Pipfile.lock .

RUN pip install -U pip pipenv ipython; \
    pipenv sync --dev --system; \
    pip install jedi==0.17.2

COPY . .
RUN pip install .

CMD ["ipython"]
