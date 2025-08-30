#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

sudo mkdir -p /var/log/real-state-leads-collector
sudo chown $USER:$USER /var/log/real-state-leads-collector

COLLECTOR_CRON_JOB="0 1 * * 1,4 cd $PROJECT_DIR && docker compose run --rm collector >> /var/log/real-state-leads-collector/collector-cron.log 2>&1"
MAILER_CRON_JOB="0 11 * * 1,4 cd $PROJECT_DIR && docker compose run --rm mailer >> /var/log/real-state-leads-collector/mailer-cron.log 2>&1"

echo "Setting up cron job for leads collector..."
echo "Project directory: $PROJECT_DIR"
echo "Collector cron job: $COLLECTOR_CRON_JOB"
echo "Mailer cron job: $MAILER_CRON_JOB"

if ! crontab -l 2>/dev/null | grep -q "docker compose run --rm collector"; then
    (crontab -l 2>/dev/null; echo "$COLLECTOR_CRON_JOB") | crontab -
    echo "Collector cron job added successfully"
else
    echo "Collector cron job already exists, skipping..."
fi

if ! crontab -l 2>/dev/null | grep -q "docker compose run --rm mailer"; then
    (crontab -l 2>/dev/null; echo "$MAILER_CRON_JOB") | crontab -
    echo "Mailer cron job added successfully"
else
    echo "Mailer cron job already exists, skipping..."
fi

echo ""
echo "Current crontab entries for leads collector:"
crontab -l 2>/dev/null | grep "docker compose run --rm collector" || echo "No collector cron jobs found"

echo ""
echo "Current crontab entries for leads mailer:"
crontab -l 2>/dev/null | grep "docker compose run --rm mailer" || echo "No mailer cron jobs found"

echo ""
echo "Next run times (approximate):"
echo "Every Monday and Thursday at 01:00 AM and 11:00 AM UTC"
echo "Logs will be written to: /var/log/real-state-leads-collector/collector-cron.log and /var/log/real-state-leads-collector/mailer-cron.log"