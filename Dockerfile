ARG PYTHON_IMAGE

FROM ${PYTHON_IMAGE}

ARG NEXUS_PROXY  

ENV PIP_INDEX_URL=${NEXUS_PROXY}
ENV PIP_TRUSTED_HOST='pypi.org ${NEXUS_PROXY}' 

WORKDIR /app

# USER root
COPY requirements.txt ./

# Pip aktualisieren
# RUN python -m pip config set global.trusted-host=${NEXUS_PROXY}
# RUN pip install --no-cache-dir --upgrade pip
# RUN pip --disable-pip-version-check list --outdated --format=json | python3 -c "import json, sys; print('\n'.join([x['name'] for x in json.load(sys.stdin)]))" | xargs -n1 pip install -U
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN chmod -R a+w /app/superset_report/
RUN mkdir -p /app/superset_report/jobs/
RUN mkdir -p /app/superset_report/logs/
RUN ["chmod", "-R", "ugo+rwx", "/app"]

# CMD ["flask", "run", "host", "0.0.0.0"]
CMD ["/bin/sh","-c","python3 flask_app.py"]