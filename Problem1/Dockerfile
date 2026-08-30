FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    fortune-mod \
    fortunes-min \
    cowsay \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="${PATH}:/usr/games"
WORKDIR /app
COPY wisecow.sh .
RUN chmod +x wisecow.sh && chown -R 10001:10001 /app

EXPOSE 4499
USER 10001
CMD ["./wisecow.sh"]