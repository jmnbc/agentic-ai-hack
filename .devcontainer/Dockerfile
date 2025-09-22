# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

USER root

# Install uv using pip first, then upgrade to latest version
RUN pip install uv \
    && uv --version

# Install Azure Functions Core Tools - try official APT method first, fallback to npm for arm64
RUN set -e; \
    # Try Microsoft's official APT repository (works for amd64) \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg && \
    sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/debian/$(lsb_release -rs 2>/dev/null | cut -d'"'"'.'"'"' -f 1)/prod $(lsb_release -cs 2>/dev/null) main" > /etc/apt/sources.list.d/dotnetdev.list' && \
    apt-get update && \
    (apt-get install -y azure-functions-core-tools-4 || \
     # Fallback to npm installation for arm64 or if APT fails \
     (curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
      apt-get install -y nodejs && \
      npm install -g azure-functions-core-tools@4 --unsafe-perm true))

# Preinstall project dependencies into a reusable virtual environment
WORKDIR /tmp/uv-bootstrap
COPY requirements.txt ./requirements.txt
RUN uv venv /opt/agentic-venv --seed --python /usr/local/bin/python3.11 \
    && uv pip install --python /opt/agentic-venv/bin/python --upgrade -r requirements.txt \
    && rm -rf /tmp/uv-bootstrap

# Make the pre-built environment available to the vscode user
RUN chown -R vscode:vscode /opt/agentic-venv

# Create and set proper permissions for UV cache directory
RUN mkdir -p /home/vscode/.cache/uv \
    && chown -R vscode:vscode /home/vscode/.cache

ENV PATH="/opt/agentic-venv/bin:${PATH}"
ENV VIRTUAL_ENV="/opt/agentic-venv"

USER vscode
WORKDIR /workspaces
