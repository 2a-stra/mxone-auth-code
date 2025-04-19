#!/usr/bin/python3
'''
Input file "mac.csv":
MAC;EXTENTION;CSP

Example "mac.csv":
14:00:E9:11:11:11;101;0

Input:
- mac.csv file UTF-8 w/o BOM
- passw

Output:
- file with commands: "extensions-<date-time>.sh"
- file with passwords: "auth-<date-time>.txt"
- <MAC>.cfg files
- <MAC>.tuz encrypted files

More:
github.com/2a-stra/
'''
import sys
from pathlib import Path
import random
from datetime import datetime
from subprocess import call

try:
    MAC_FNAME = sys.argv[1]
except:
    print("Using default 'mac.csv' file for input")
    MAC_FNAME = "mac.csv"

now = datetime.now() # current date and time
dt = now.strftime("%Y%m%d")
date_time = now.strftime("%Y%m%d-%H%M%S")
print(date_time)

Path("./%s" % dt).mkdir(parents=True, exist_ok=True)
EXTENSION_FILE = "./%s/extensions-%s.sh" % (dt, date_time)
AUTH_TXT = "./%s/auth-%s.txt" % (dt, date_time)

DELIM = "," # CSV file separator
DIG = 14    # length of auth code
SIP_PROXY = "192.168.1.11"

def gen_pass(DIG: int) -> str:

    d = "0123456789"
    s = "abcdefghijklmnopqrstuvwxyz"
    l = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    al = s + l + d

    a = ""
    for _ in range(DIG):
        symb = random.choice(al)
        a += symb

    return a


def gen_conf(mac: str, ext: str, code:str):

    out = '''sip line1 user name:{ext}
sip line1 auth name:{ext}
sip line1 password:{code}
sip proxy ip:"{sip}"
sip registrar ip:"{sip}"
'''.format(ext=ext, code=code, sip=SIP_PROXY)

    fn = "./%s/%s.cfg" % (dt, mac)

    with open(fn, "w") as fl:
        fl.write(out)


def gen_ext(ext: str, csp: str):

    start = int(ext)

    with open(EXTENSION_FILE, "a") as ac:  # append file
        ac.write("extension -i -d {start} --csp {csp} -l 1\n".format(start=start, csp=csp))


def gen_ip_ext(ext: str):

    start = int(ext)

    with open(EXTENSION_FILE, "a") as ac:  # append file
        ac.write("ip_extension -i -d {start} --protocol sip\n".format(start=start))


def gen_auth(ext: str, code: str, csp: str):

    start = int(ext)

    with open(AUTH_TXT, "a") as f:  # append file

        with open(EXTENSION_FILE, "a") as ac:  # append file

            # md5a1 hash
            ac.write("auth_code -i -d {start} --csp {csp} --cil {start} --customer 0 --hash-type md5a1 --auth-code {code}\n".format(start=start, code=code, csp=csp))

            # clear text
            #print("auth_code -i -d {start} --csp {csp} --cil {start} --customer 0 --auth-code {code}".format(start=start, code=code))

            f.write("%s,%s\n" % (start,code))

#f = open("auth.txt", "w"); f.close()
#f = open("extensions.sh", "w"); f.close()

n = 0
#csp = 0

with open(MAC_FNAME, "r") as fl:
    for line in fl:
        mac, ext, csp = line.split(DELIM)
        gen_ext(ext.strip(), csp.strip())

with open(MAC_FNAME, "r") as fl:
    for line in fl:
        mac, ext, csp = line.split(DELIM)
        gen_ip_ext(ext.strip())

with open(MAC_FNAME, "r") as fl:
    for line in fl:

        mac, ext, csp = line.split(DELIM)
        mac = mac.replace(":", "").strip()
        ext = ext.strip()

        code = gen_pass(DIG)
        gen_conf(mac, ext, code)
        gen_auth(ext, code, csp.strip())
        n += 1

print("Generated %s config files" % n)

# Encrypt
with open("passw", "r") as fl:
    PASSW = fl.readline().strip()
    call(["./anacrypt", "-d", "./%s" % dt, "-m", "-p", PASSW])

# Copy to node1
call(["scp", EXTENSION_FILE, "node1:~/"])

# Copy to ipc
#call(["scp", "./*.tuz", "ipc:~/config/"])
call(["./scp_ipc.sh"])

