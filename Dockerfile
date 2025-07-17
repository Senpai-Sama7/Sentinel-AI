# Dockerfile

# --- Stage 1: Builder ---
# This stage installs dependencies into a virtual environment. It includes development
# dependencies for testing within CI/CD pipelines. The goal is to create a cacheable
# layer of installed packages.
FROM python:3.11-slim as builder

WORKDIR /app

# Set environment variables for Poetry to manage dependencies globally within the container.
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Install Poetry, the dependency manager for Python.
RUN pip install poetry

# Copy only the dependency definition files to leverage Docker's layer caching.
# This step will only be re-run if pyproject.toml or poetry.lock changes.
COPY pyproject.toml poetry.lock ./

# Install all project dependencies, including dev dependencies for potential CI steps.
RUN poetry install --no-root

# --- Stage 2: Final Production Image ---
# This stage builds the final, lean image for production. It starts from a clean
# base and copies only the necessary artifacts from the builder stage.
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user and group for security best practices.
# Running as a non-root user minimizes potential security risks if the container is compromised.
RUN addgroup --system --gid 1001 app && adduser --system --uid 1001 --gid 1001 app

# Copy the installed Python packages from the builder stage's virtual environment.
# This is the key to a small and secure final image, as it excludes build tools.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/poetry /usr/local/bin/poetry

# Copy the application source code into the final image.
COPY ./api ./api
COPY ./core ./core
COPY ./tools ./tools
COPY main.py .

# Change ownership of the application files to the non-root user.
RUN chown -R app:app /app

# Switch to the non-root user.
USER app

# Expose the port the application runs on.
EXPOSE 8000

# The command to run the application in production.
# Gunicorn is a battle-tested WSGI server that manages Uvicorn workers.
# This provides better process management, scalability, and robustness than running Uvicorn directly.
# The number of workers (-w 4) should be tuned based on the server's CPU cores (a common rule of thumb is 2 * num_cores + 1).
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]