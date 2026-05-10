# Custom Radicale image with PostgreSQL storage plugin.
FROM kozea/radicale:3.7.2

USER root

# Runtime dependency — psycopg2-binary ships its own libpq but still
# needs the base PostgreSQL client library on Alpine for SSL/DNS.
RUN apk add --no-cache libpq

# Install the storage plugin (psycopg2-binary = pre-compiled, no gcc needed)
COPY radicale/pyproject.toml /tmp/plugin/pyproject.toml
COPY radicale/radicale_storage_postgresql/ /tmp/plugin/radicale_storage_postgresql/
RUN /app/bin/python -m pip install --no-cache-dir /tmp/plugin/ && \
    rm -rf /tmp/plugin/

# Drop back to the radicale user
USER 1000
