#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

sudo mkdir -p /var/log/real-state-leads-collector
sudo chown $USER:$USER /var/log/real-state-leads-collector

CRON_JOB="0 1 * * 1,4 cd $PROJECT_DIR && docker compose run --rm collector >> /var/log/real-state-leads-collector/collector-cron.log 2>&1"

echo "Setting up cron job for leads collector..."
echo "Project directory: $PROJECT_DIR"
echo "Cron job: $CRON_JOB"

if ! crontab -l 2>/dev/null | grep -q "docker compose run --rm collector"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added successfully"
else
    echo "Cron job already exists, skipping..."
fi

echo ""
echo "Current crontab entries for leads collector:"
crontab -l 2>/dev/null | grep collector || echo "No collector cron jobs found"

echo ""
echo "Next run times (approximate):"
echo "Every Monday and Thursday at 1:00 AM UTC"
echo "Logs will be written to: /var/log/real-state-leads-collector/collector-cron.log"