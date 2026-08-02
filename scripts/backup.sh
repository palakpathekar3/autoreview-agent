#!/bin/bash

PROJECT="$HOME/autoreview-agent"
BACKUP="$HOME/backups"

mkdir -p "$BACKUP"

DATE=$(date +"%Y-%m-%d_%H-%M-%S")

tar -czf "$BACKUP/autoreview_$DATE.tar.gz" "$PROJECT"

echo "Backup created:"
echo "$BACKUP/autoreview_$DATE.tar.gz"
