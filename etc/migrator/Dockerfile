ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL}/base/liquibase:4.8.0

USER root

WORKDIR /app

RUN sed -i 's/http:\/\/deb.debian.org\/debian/http:\/\/archive.debian.org\/debian/g' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends netcat postgresql-client && \
    apt-get remove -y unzip && \
    rm -rf /var/lib/apt/lists/*

COPY ./etc/migrator/wait-for.sh ./
COPY ./etc/migrator/entrypoint.sh ./entrypoint.sh
COPY ./etc/migrator/migrations ./migrations

RUN chmod +x ./wait-for.sh
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

RUN useradd -Ms /bin/bash deps
USER deps

CMD ["update"]
