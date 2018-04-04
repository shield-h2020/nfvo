#!/usr/bin/env bash
echo "Creating mongo users..."
mongo $MONGO_INITDB_DATABASE --host localhost -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --eval "db.createUser({user: '"$DB_USERNAME"', pwd: '"$DB_PASSWORD"', roles: [{role: 'readWrite', db: '"$DB_DBNAME"'}]});"
echo "Mongo users created."
