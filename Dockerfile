FROM python:3.10-slim-bookworm AS libs
ENV XDG_BIN_HOME=/usr/local/bin
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin/:$PATH"

FROM libs AS app
WORKDIR /usr/src/app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY . ./
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uv", "run", "--no-dev", "main.py"]
