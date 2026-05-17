'''
Input file "test_mac.csv" with exactly 6 fields:
MAC,EXTENTION,CSP,LIM,Name1,Name2

Example "test_mac.csv":
14:00:E9:11:11:11,101,0,1,John,L
'''
COLS = 6
DELIM = ","    # CSV file separator
DIGITS = 14    # length of auth code

MAC_MITEL = "1400E9"
MAC_FANVIL = "0C383E"

SIP_PROXY = {  # LIM: IP
    "1": "192.168.1.11",
    "2": "192.168.2.11",
    "3": "192.168.3.11",
    "4": "192.168.4.11"
}

BACKUP_1 = True  # Add LIM1 as a backup SIP proxy/registrar
