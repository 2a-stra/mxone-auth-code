#!/usr/bin/python3
'''
Input file "mac.csv":
MAC,EXTENTION,CSP

Example "mac.csv":
14:00:E9:11:11:11,101,0

Output:
- <MAC>.cfg files.
- file with passwords: "auth.txt"
- file with commands: "auth_code.sh"

More:
github.com/2a-stra/
'''
import random

DELIM = "," # CSV file separator
DIG = 14    # length of auth code


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
sip proxy ip:"192.168.1.11"
sip registrar ip:"192.168.1.11"
'''.format(ext=ext, code=code)

    fn = "%s.cfg" % mac

    with open(fn, "w") as fl:
        fl.write(out)


def gen_auth(ext: str, code: str, csp: str):

    start = int(ext)

    with open("auth.txt", "a") as f:  # append file

        with open("auth_code.sh", "a") as ac:  # append file

            # md5a1 hash
            ac.write("auth_code -i -d {start} --csp {csp} --cil {start} --customer 0 --hash-type md5a1 --auth-code {code}\n".format(start=start, code=code, csp=csp))

            # clear text
            #print("auth_code -i -d {start} --csp {csp} --cil {start} --customer 0 --auth-code {code}".format(start=start, code=code))

            f.write("%s,%s\n" % (start,code))

f = open("auth.txt", "w")
f.close()
f = open("auth_code.sh", "w")
f.close()

n = 0
with open("mac.csv", "r") as fl:

    for line in fl:

        mac, ext, csp = line.split(DELIM)
        mac = mac.replace(":", "").strip()
        ext = ext.strip()
        csp = csp.strip()

        code = gen_pass(DIG)
        gen_conf(mac, ext, code)
        gen_auth(ext, code, csp)
        n += 1

print("Generated %s config files" % n)

