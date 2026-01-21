# ---- Build Stage ----
# Use a full-featured Python image to build dependencies
FROM python:3.9-slim-bookworm AS builder

# Install system dependencies required for the build and for the CLI to function
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy project files
WORKDIR /app
COPY pyproject.toml ./

# Install dependencies into the virtual environment
# We install them here so they are cached by Docker
RUN pip install --no-cache-dir -e ".[dev]"

# Copy the rest of the application code
COPY . .


# ---- Final Stage ----
# Use a minimal, production-ready base image
FROM python:3.9-slim-bookworm

# Install only the necessary runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the PATH to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Set up the working directory and config volume
WORKDIR /work
VOLUME /config

# Copy the application code from the builder stage
COPY --from=builder /app /app

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["entrypoint.sh"]

# Default command if none is provided
CMD ["--help"]
