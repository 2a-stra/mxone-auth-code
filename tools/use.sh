#!/usr/bin/env bash
#
# Check user licenses usage and count registered SIP-phones
#
# Source:
# https://github.com/2a-stra/mxone-auth-code

PRE="192.168.1."

echo "User license usage:"
license_status | grep -E " USER " | awk '{printf "%-25s %s\n", $1, $NF}'

echo "Including:"
license_status | grep -E " SIP-EXTENSION |3RD-PARTY-SIP-EXTENSION|ANALOGUE-EXTENSION" | awk '{printf "%-25s %s\n", $1, $NF}'

echo "Registered SIP-phones:" && ip_extension_info -p | grep $PRE | wc -l

