#!/bin/sh
# wait-for-db.sh

set -e

host="$1"
shift
cmd="$@"

echo "Waiting for $host to be ready..."

until nc -z "$host" 3306; do
  echo "Waiting for MySQL at $host..."
  sleep 2
done

echo "$host is ready! Running command..."
exec $cmd
