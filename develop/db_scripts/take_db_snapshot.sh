#! /bin/bash

# Run this script from the project root with Make
#
# Usage:
# - make take_snapshot

set -e

PROJECT_ROOT=$(pwd)
POSTGRES_CONTAINER=netbox-ninja-postgres
SNAPSHOT_PATH=${PROJECT_ROOT}/develop/db_scripts/snapshots

COMPOSE_FILE=${PROJECT_ROOT}/develop/docker-compose.yml
BUILD_NAME=netbox-plugins

docker compose -f "${COMPOSE_FILE}" -p ${BUILD_NAME} up -d postgres

sleep 2

source "${PROJECT_ROOT}/develop/dev.env"
docker exec -it ${POSTGRES_CONTAINER} su - root -c 'rm -f /tmp/netbox.Z;PGPASSWORD="${POSTGRESQL_PASSWORD}";POSTGRES_USER="${POSTGRES_USER}" pg_dump --format=c -U '"${POSTGRES_USER}"' -d netbox -f /tmp/netbox.Z'
docker cp ${POSTGRES_CONTAINER}:/tmp/netbox.Z "${SNAPSHOT_PATH}/latest-netbox.Z"

docker compose -f "${COMPOSE_FILE}" -p ${BUILD_NAME} --profile netbox down

timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
cp "${SNAPSHOT_PATH}/latest-netbox.Z" "${SNAPSHOT_PATH}/$timestamp-netbox.Z"

echo
echo "✔ Snapshots in snapshots/ directory:"
echo
ls -la "${SNAPSHOT_PATH}/"
