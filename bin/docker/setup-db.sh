#/bin/bash

ENV_FILE_FULL=$(mktemp /tmp/XXXXXXX)

# Load deployment-specific settings.
cat .env.production >> ${ENV_FILE_FULL}

# Append settings for standard operation.
cat .env.base >> ${ENV_FILE_FULL}

. ${ENV_FILE_FULL}

# Export variables so they can be used here. Stop script at first error.
set -ae

# Do nested variables interpolation as the shell doesn't seem do it.
ENV_FILE=$(mktemp /tmp/XXXXXXX)
ENV_TMP_FILE=$(mktemp /tmp/XXXXXXX)
echo "#!/bin/sh" > ${ENV_TMP_FILE}
echo ". ${ENV_FILE_FULL}" >> ${ENV_TMP_FILE}
echo "cat <<_VARS_BLOCK_" >> ${ENV_TMP_FILE}
cat ${ENV_FILE_FULL} >> ${ENV_TMP_FILE}
echo "_VARS_BLOCK_" >> ${ENV_TMP_FILE}
echo >> ${ENV_TMP_FILE}
. ${ENV_TMP_FILE} > ${ENV_FILE}

# Setup mongoDB data store.
mongod --port ${DB_PORT} # --eval "var PORT='$DB_PORT', DB_COLLECTION='$DB_DBNAME', DB_USER='$DB_USERNAME', DB_PASS='$DB_PASSWORD'" ${CNTR_FOLDER_DEV}/docker/mongodb-init.js
