FROM ghcr.io/breakthrough-energy/powersimdata:latest

WORKDIR /PostRIESE
COPY Pipfile .
COPY Pipfile.lock .
RUN pip install -U pip pipenv jupyterlab; \
    pipenv sync --dev --system;

COPY . .
RUN pip install .

CMD ["jupyter", "lab", "--port=10000", "--no-browser", "--ip=0.0.0.0", "--allow-root"]