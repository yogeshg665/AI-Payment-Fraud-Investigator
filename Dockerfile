# =============================================================================
# AI Payment Fraud Investigator - Container Image
# Multi-stage build producing a minimal, non-root runtime image.
# =============================================================================

FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY src ./src
COPY config ./config

RUN python -m pip install --upgrade pip build \
    && python -m pip wheel --wheel-dir /wheels .

# -----------------------------------------------------------------------------

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

# Create an unprivileged user to run the application.
RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels

COPY config ./config
COPY data ./data

USER app

ENTRYPOINT ["fraud-investigator"]
CMD ["--help"]
