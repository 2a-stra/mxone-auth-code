#!/usr/bin/env bash
#
# Show extension number full info
#
# Source:
# https://github.com/2a-stra/mxone-auth-code

# Exit if no argument is provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

ARG="$1"

# Validate that the argument contains only digits
if ! [[ "$ARG" =~ ^[0-9]+$ ]]; then
  echo "Error: argument must be digits only"
  exit 1
fi

# Run a command using the argument
echo "\nIP extension:"
ip_extension_info -d $ARG

echo "\nNames:"
name -p -d $ARG

echo "\nAuth code:"
auth_code -p -d $ARG

echo "\nExtension keys:"
extension_key -p -d $ARG

echo "\nDiversions:"
diversion -p -d $ARG
