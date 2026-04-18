arg PYTHON_VERSION=3.14.3
arg UV_VERSION=0.10.9

from ghcr.io/astral-sh/uv:${UV_VERSION} as uv

from python:${PYTHON_VERSION}-slim as base

# install uv
copy --from=uv /uv /bin/

env UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app \
    UV_PYTHON=${PYTHON_VERSION} \
    UV_PYTHON_DOWNLOADS=never

# install dependencies
copy ./uv.lock ./pyproject.toml /_lock/

arg UV_SYNC_DEV_OPTION=--no-dev

run --mount=type=cache,target=/root/.cache <<EOT
    cd /_lock
    uv sync \
    --locked \
    --no-install-project \
    ${UV_SYNC_DEV_OPTION}
EOT

# copy initialization scripts
copy --chmod=755 ./entrypoint* /app/bin/

#--------------------------------------------
from python:${PYTHON_VERSION}-slim as production

env PATH=/app/bin:$PATH

copy --from=base /app /app

workdir /app/chile

copy ./chile /app/chile

EXPOSE 8000

entrypoint ["entrypoint.sh"]
