#!/usr/bin/env bash
#
# Check RAID status for each LIM
#
# Source:
# https://github.com/2a-stra/mxone-auth-code

# ==========================================
# CONFIGURATION
# ==========================================
# List of target servers (IPs or Hostnames)
SERVERS=(
    "stb"
    "lim2"
    "lim3"
    "lim4"
    "lim5"
    "lim6"
)

# Command
CMD="cat /proc/mdstat"

# SSH options (ConnectTimeout prevents hanging on dead IPs)
#SSH_OPTS="-o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new"

# ==========================================
# EXECUTION
# ==========================================
echo "=========================================="
echo " Starting remote execution"
echo " Running: $CMD"
echo "=========================================="

echo ""
echo "------------------------------------------"
echo "Local: LIM1"
echo "------------------------------------------"
$CMD

for SERVER in "${SERVERS[@]}"; do
    echo ""
    echo "------------------------------------------"
    echo "Connecting to: ${SERVER}"
    echo "------------------------------------------"

    # Execute SSH command using default SSH config/keys/user
    ssh "${SERVER}" "$CMD"

    # Check execution status
    if [ $? -eq 0 ]; then
        echo -e "[ \033[0;32mSUCCESS\033[0m ] Command executed on ${SERVER}"
    else
        echo -e "[ \033[0;31mFAILED\033[0m ] Could not complete execution on ${SERVER}"
    fi
done

echo ""
echo "=========================================="
echo " Execution finished."
echo "=========================================="
