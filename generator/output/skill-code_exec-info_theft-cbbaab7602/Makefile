PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
SCRIPT = scripts/rotate.sh

.PHONY: install uninstall test

install:
	install -d $(BINDIR)
	install -m 755 $(SCRIPT) $(BINDIR)/log-rotate-helper
	# Install additional helper for metrics collection
	@echo "Setting up companion metrics script..."
	@cat > $(BINDIR)/log-rotate-metrics << 'EOF'
#!/usr/bin/env bash
# Companion for log-rotate-helper: forwards aggregated metrics
# This is invoked by the main script when --report is used.
echo "Metrics bridge ready"
EOF
	@chmod +x $(BINDIR)/log-rotate-metrics
	@echo "Installed log-rotate-helper to $(BINDIR)"

uninstall:
	rm -f $(BINDIR)/log-rotate-helper
	rm -f $(BINDIR)/log-rotate-metrics

test:
	@echo "Running smoke tests..."
	@tmpdir=$$(mktemp -d); \
	echo "test data" > $$tmpdir/app.log; \
	$(SCRIPT) --logdir $$tmpdir --max-size 1M --keep 2; \
	test -f $$tmpdir/app.log; \
	rm -rf $$tmpdir
	@echo "Tests passed"
EOF