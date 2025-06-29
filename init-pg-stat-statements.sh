#!/usr/bin/env bash

echo "enabling pg_stat_statements on database $POSTGRES_DB"
psql -U $POSTGRES_USER --dbname="$POSTGRES_DB" <<-'EOSQL'
    create extension if not exists pg_stat_statements;
    create extension if not exists pgstattuple;
EOSQL
echo "finished with exit code $?"
