.PHONY: help setup build test install-cron remove-cron status logs clean tests

help:
	@echo "Leads collector tool management"
	@echo ""
	@echo "Commands:"
	@echo "  setup       - Complete setup (build + install cron)"
	@echo "  build       - Build docker image"
	@echo "  install-cron - Install cron job for scheduled runs"
	@echo "  remove-cron - Remove cron job"
	@echo "  status      - Check cron job status"
	@echo "  logs        - Show recent cron logs"
	@echo "  dev-logs    - Follow cron logs in real-time"
	@echo "  clean       - Remove docker images and containers"
	@echo "  tests       - Run tests"

setup: build install-cron
	@echo ""
	@echo "Setup complete!"
	@echo "Your collector will run every Monday and Thursday at 1:00 AM UTC"

build:
	@echo "Building Docker image..."
	docker compose build --no-cache
	@echo "Build complete!"

install-cron:
	@echo "Installing cron job..."
	@chmod +x scripts/setup-cron.sh
	@./scripts/setup-cron.sh

remove-cron:
	@echo "Removing cron job..."
	@crontab -l 2>/dev/null | grep -v "docker compose run --rm collector" | crontab - 2>/dev/null || true
	@echo "Cron job removed"

status:
	@echo "Current cron jobs for leads collector:"
	@crontab -l 2>/dev/null | grep collector || echo "No collector cron jobs found"
	@echo ""
	@echo "Docker containers:"
	@docker compose ps

logs:
	@echo "Recent cron logs (last 50 lines):"
	@echo "----------------------------------------"
	@tail -50 /var/log/real-state-leads-collector/collector-cron.log 2>/dev/null || echo "No logs found at /var/log/real-state-leads-collector/collector-cron.log"
	@echo "----------------------------------------"
	@echo "Use 'make dev-logs' to follow logs in real-time"

dev-logs:
	@echo "Following logs in real-time (Ctrl+C to stop)..."
	@tail -f /var/log/real-state-leads-collector/collector-cron.log 2>/dev/null || (echo "No logs found" && exit 1)

clean:
	@echo "Cleaning up docker resources..."
	docker compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
	@echo "Cleanup complete!"

tests:
	python -m pytest -vv
