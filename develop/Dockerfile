ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}
ARG NETBOX_VERSION
ENV PYTHONUNBUFFERED 1
RUN set -x \
    && cd /opt \
    && adduser --system --group netbox \
    && curl -sSLO https://github.com/netbox-community/netbox/archive/refs/tags/v${NETBOX_VERSION}.tar.gz \
    && tar xzf v${NETBOX_VERSION}.tar.gz \
    && mv -fv /opt/netbox-${NETBOX_VERSION} /opt/netbox \
    && chown -cR netbox:root /opt/netbox/netbox/media \
    && pip install --no-cache-dir --upgrade pip wheel \
    && pip install --no-cache-dir poetry -r netbox/base_requirements.txt

WORKDIR /opt/netbox_ninja_plugin

COPY .. /opt/netbox_ninja_plugin

RUN set -x \
    && poetry config virtualenvs.create false \
    && poetry install --no-ansi --no-interaction --without dev

WORKDIR /opt/netbox/netbox

COPY develop/configuration.py /opt/netbox/netbox/netbox/

RUN set -x && python manage.py collectstatic --no-input
