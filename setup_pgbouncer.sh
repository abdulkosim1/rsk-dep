#!/bin/bash

echo "Waiting for the database to be ready..."
until psql -h "$DB_HOST" -U "$DB_USER" -c '\q' &>/dev/null; do
  sleep 1
done
echo "Database is ready, proceeding..."

generate_pgbouncer_ini() {
  cat << EOF > /pgbouncer/pgbouncer.ini
[databases]
* = host=$DB_HOST port=$DB_PORT

[pgbouncer]
pool_mode = transaction
listen_addr = $PGBOUNCER_LISTEN_ADDR
listen_port = $PGBOUNCER_LISTEN_PORT
auth_type = $PGBOUNCER_AUTH_TYPE
auth_file = /pgbouncer/userlist.txt
max_client_conn = $PGBOUNCER_MAX_CLIENT_CONN
default_pool_size = $PGBOUNCER_DEFAULT_POOL_SIZE
min_pool_size = $PGBOUNCER_MIN_POOL_SIZE
reserve_pool_size = $PGBOUNCER_RESERVE_POOL_SIZE
max_db_connections = $PGBOUNCER_MAX_DB_CONNECTIONS
max_user_connections = $PGBOUNCER_MAX_USER_CONNECTIONS
ignore_startup_parameters = extra_float_digits

# Log settings
log_connections = $PGBOUNCER_LOG_CONNECTIONS
log_disconnections = $PGBOUNCER_LOG_DISCONNECTIONS
admin_users = $PGBOUNCER_ADMIN_USERS
EOF
}

generate_userlist_txt() {
  cat << EOF > /pgbouncer/userlist.txt
"$DB_USER" "$DB_PASSWORD"
EOF
}

generate_pgbouncer_ini
generate_userlist_txt

exec pgbouncer /pgbouncer/pgbouncer.ini
