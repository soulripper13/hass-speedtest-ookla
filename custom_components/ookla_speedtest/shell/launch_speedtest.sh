#!/bin/bash
# Run speedtest-cli with JSON output
/config/shell/speedtest.bin --accept-license --accept-gdpr --format=json "$@"
