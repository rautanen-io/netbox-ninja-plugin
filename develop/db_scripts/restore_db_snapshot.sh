#! /bin/bash
# Run this script from the project root with Make
#
# Usage:
# - make restore_snapshot
# - make restore_snapshot ARGS="2025-05-07_09-42-10-netbox.Z"

set -e

PROJECT_ROOT=$(pwd)
POSTGRES_CONTAINER=netbox-ninja-postgres
SNAPSHOT_PATH=${PROJECT_ROOT}/develop/db_scripts/snapshots

COMPOSE_FILE=${PROJECT_ROOT}/develop/docker-compose.yml
BUILD_NAME=netbox-plugins

docker compose -f "${COMPOSE_FILE}" -p ${BUILD_NAME} up -d postgres

sleep 2

filename=${SNAPSHOT_PATH}/latest-netbox.Z
if [ "${1+set}" = "set" ]; then
    filename="${SNAPSHOT_PATH}/$1"
fi

echo
echo "✔ Restoring snapshot $filename"
echo

source "${PROJECT_ROOT}/develop/dev.env"
docker cp "${filename}" ${POSTGRES_CONTAINER}:/tmp/netbox.Z

# Disable exit on error temporary. The following command returns an errors
# if database is empty. However, backup should still be restored:
set +e
cat <<EOF | docker exec --interactive ${POSTGRES_CONTAINER} sh
su postgres
pg_restore -c -d netbox -U ${POSTGRES_USER} /tmp/netbox.Z
EOF
set -e

docker compose -f "${COMPOSE_FILE}" -p ${BUILD_NAME} --profile netbox down

echo
echo "✔ Snapshot restored (I hope)."
echo
