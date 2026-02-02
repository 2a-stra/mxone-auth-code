#!/usr/bin/python3
'''
Input file "mac.csv" with exactly 5 fields:
MAC,EXTENTION,CSP,Name1,Name2

Example "mac.csv":
14:00:E9:11:11:11,101,0,John,L

Input:
- "test_mac.csv" file UTF-8 w/o BOM
- "key_mitel" file with password for Mitel (string)
- "key_fanvil" file with password for Fanvil (64 hex chars)

Output:
- file with commands: "extensions-<date-time>.sh" (Unix LF)
- file with passwords: "auth-<date-time>.txt"
- <MAC_MITEL>.cfg config files
- <MAC_MITEL>.tuz encrypted files
- <MAC_FANVIL>.txt config files
- <MAC_FANVIL>.cfg encrypted files

Source:
https://github.com/2a-stra/mxone-auth-code
'''
import sys
from pathlib import Path
import random
from datetime import datetime
from subprocess import run

TEST = True

DELIM = ","    # CSV file separator
DIGITS = 14    # length of auth code
SIP_PROXY = "192.168.1.11"

MAC_MITEL = "1400E9"
MAC_FANVIL = "0C383E"


def gen_pass(DIGITS: int) -> str:

    d = "0123456789"
    s = "abcdefghijklmnopqrstuvwxyz"
    l = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    al = s + l + d

    a = ""
    for _ in range(DIGITS):
        symb = random.choice(al)
        a += symb

    return a


def gen_conf_mitel(mac: str, ext: str, code:str, DT:str, generated:list):

    out = '''sip line1 user name:{ext}
sip line1 auth name:{ext}
sip line1 password:{code}
sip proxy ip:{sip}
sip registrar ip:{sip}
'''.format(ext=ext, code=code, sip=SIP_PROXY)

    fn = "./%s/%s.cfg" % (DT, mac)

    with open(fn, "w") as fl:
        fl.write(out)

    generated.append(fn)

    return generated


def gen_conf_fanvil(mac: str, ext: str, code:str, DT:str, generated:list):

    out = '''#<Voip Config File>#
Version = 2.0000000000

sip.line.1.PhoneNumber = {ext}
sip.line.1.DisplayName = {ext}
sip.line.1.RegUser = {ext}
sip.line.1.SipName = {sip}
sip.line.1.RegAddr = {sip}
sip.line.1.RegPswd = {code}
sip.line.1.RegEnabled = 1
sip.line.1.ProxyAddr = {sip}
'''.format(ext=ext, code=code, sip=SIP_PROXY)

    fn = "./%s/%s.txt" % (DT, mac.lower())

    with open(fn, "w") as fl:
        fl.write(out)

    generated.append(fn)

    return generated


def gen_ext(ext: str, csp: str, mac:str, ext_cmd):

    start = int(ext)

    with open(ext_cmd, "a") as ac:  # append file
        #TODO: LIM number
        if mac[:6] == MAC_MITEL:
            ac.write("extension -i -d {start} --csp {csp} -l 1\n".format(start=start, csp=csp))
        else:  # Third party client
            ac.write("extension -i -d {start} --csp {csp} -l 1 --third-party-client yes\n".format(start=start, csp=csp))


def gen_ip_ext(ext: str, ext_cmd):

    start = int(ext)

    with open(ext_cmd, "a") as ac:  # append file
        ac.write("ip_extension -i -d {start} --protocol sip\n".format(start=start))


def gen_name(ext: str, name1: str, name2: str, ext_cmd):

    start = int(ext)
    parts = [f"name -i -d {start}"]

    if name1.strip():
        parts.append(f'--name1 "{name1}"')

    if name2.strip():
        parts.append(f'--name2 "{name2}"')

    parts.append("--number-type dir")
    nline = " ".join(parts) + "\n"

    with open(ext_cmd, "a") as ac:  # append file
        ac.write(nline)


def gen_auth(ext: str, code: str, csp: str, ext_cmd, auth_txt):

    start = int(ext)

    with open(auth_txt, "a") as f:  # append file

        with open(ext_cmd, "a") as ac:  # append file

            # md5a1 hash
            ac.write("auth_code -i -d {start} --csp {csp} --cil {start} --customer 0 --hash-type md5a1 --auth-code {code}\n".format(start=start, code=code, csp=csp))

            # clear text
            #print("auth_code -i -d {start} --csp {csp} --cil {start} --customer 0 --auth-code {code}".format(start=start, code=code))

            f.write("%s,%s\n" % (start,code))


def read_rows(file_name):

    rows = []
    warnings = []
    errors = []

    with open(file_name, "r") as fl:
        for lineno, line in enumerate(fl, start=1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Remove inline comments
            if "#" in line:
                line = line.split("#", 1)[0].rstrip()

            parts = line.split(DELIM)
            if len(parts) != 5:
                errors.append(
                    f"Line {lineno}: Expected 5 fields, got {len(parts)} -> {line}"
                )
                continue

            mac, ext, csp, name1, name2 = parts

            # Required fields: mac, ext, csp
            if not mac.strip() or not ext.strip() or not csp.strip():
                errors.append(
                    f"Line {lineno}: Missing required field (mac/ext/csp) -> {line.strip()}"
                )
                continue

            # Normalize and check MACs
            mac = mac.replace(":", "").strip()

            if not (mac[:6] == MAC_MITEL or mac[:6] == MAC_FANVIL):
                errors.append(
                f"Line {lineno}: Unknown MAC ({mac[:6]})"
                )
                continue

            # Normalize + trim names (max 20 chars)
            raw_name1 = name1.strip()
            raw_name2 = name2.strip()

            name1 = raw_name1[:20] if raw_name1 else ""
            name2 = raw_name2[:20] if raw_name2 else ""

            # Warning if trimmed
            if raw_name1 and len(raw_name1) > 20:
                warnings.append(
                    f"Line {lineno}: name1 trimmed to 20 characters"
                )

            if raw_name2 and len(raw_name2) > 20:
                warnings.append(
                    f"Line {lineno}: name2 trimmed to 20 characters"
                )

            # Warning if both names empty
            if not name1 and not name2:
                warnings.append(
                    f"Line {lineno}: Both name1 and name2 are empty"
                )

            rows.append({
                "lineno": lineno,
                "mac": mac.strip(),
                "ext": ext.strip(),
                "csp": csp.strip(),
                "name1": name1.strip(),
                "name2": name2.strip(),
            })

    return rows, warnings, errors


def process_rows(rows, DT, ext_sh, auth_txt):

    generated = []
    errors = []

    # -------- Phase 1 --------
    for r in rows:
        try:
            gen_ext(r["ext"], r["csp"], r["mac"], ext_sh)
        except Exception as e:
            errors.append(
                f"Line {r['lineno']}: gen_ext failed ({e})"
            )

    # -------- Phase 2 --------
    for r in rows:
        try:
            gen_ip_ext(r["ext"], ext_sh)
        except Exception as e:
            errors.append(
                f"Line {r['lineno']}: gen_ip_ext failed ({e})"
            )

    # -------- Phase 3 --------
    for r in rows:
        # Skip gen_name if both names are empty
        if not r["name1"] and not r["name2"]:
             continue

        try:
            gen_name(r["ext"], r["name1"], r["name2"], ext_sh)
        except Exception as e:
            errors.append(
                f"Line {r['lineno']}: gen_name failed ({e})"
            )

    # -------- Phase 4 --------
    for r in rows:
        try:
            code = gen_pass(DIGITS)

            if r["mac"][:6] == MAC_MITEL:
                gen_conf_mitel(r["mac"], r["ext"], code, DT, generated)
            elif r["mac"][:6] == MAC_FANVIL:
                gen_conf_fanvil(r["mac"], r["ext"], code, DT, generated)
            else:
                errors.append(
                f"Line {r['lineno']}: Unknown MAC? ({mac})"
                )

            gen_auth(r["ext"], code, r["csp"], ext_sh, auth_txt)

        except Exception as e:
            errors.append(
                f"Line {r['lineno']}: config/auth generation failed ({e})"
            )

    generated.append(ext_sh)
    generated.append(auth_txt)

    return generated, errors


def encrypt_config(rows, DT):
    errors = []
    outputs = []

    # Encrypt Mitel
    try:
        with open("key_mitel", "r") as fl:
            PASSW = fl.readline().strip()

        result = run(
            ["./anacrypt", "-d", f"./{DT}", "-m", "-p", PASSW],
            capture_output=True,
            text=True
        )

        outputs.append(result.stdout)

        if result.returncode != 0:
            err = result.stderr.strip()
            if err:
                errors.append(err)

    except Exception as e:
        errors.append(str(e))

    # Encrypt Fanvil
    try:
        for r in rows:
            if r["mac"][:6] == MAC_FANVIL:
                txt = r["mac"].lower() + ".txt"
                encrypted = r["mac"].lower() + ".cfg"

                result = run(
                    ["./dsc", "key_fanvil", "e", f"./{DT}/{txt}", f"./{encrypted}"],
                    capture_output=True,
                    text=True
                )

                outputs.append(result.stdout)

                if result.returncode != 0:
                    err = result.stderr.strip()
                    if err:
                        errors.append(err)

    except Exception as e:
        errors.append(str(e))

    return outputs, errors


def encr_files(generated: list[str], pre: str) -> list[str]:
    return [
        s.replace(pre, "")
         .replace(".cfg", ".tuz")
         .replace(".txt", ".cfg")
        for s in generated
        if "exten" not in s and "auth" not in s
    ]


if __name__ == "__main__":

    try:
        MAC_FNAME = sys.argv[1]
    except:
        print("Using default 'test_mac.csv' file for input")
        MAC_FNAME = "test_mac.csv"

    now = datetime.now()  # current date and time
    DT = now.strftime("%Y%m%d")
    DATE_TIME = now.strftime("%Y%m%d-%H%M%S")
    print(DATE_TIME)

    if TEST:
        DT = "_test"

    Path("./%s" % DT).mkdir(parents=True, exist_ok=True)
    EXTENSION_FILE = "./%s/extensions-%s.sh" % (DT, DATE_TIME)
    AUTH_TXT = "./%s/auth-%s.txt" % (DT, DATE_TIME)

    rows, warnings, errors = read_rows(MAC_FNAME)
    generated, gen_errors = process_rows(rows, DT, EXTENSION_FILE, AUTH_TXT)

    # -------- Summary --------
    print(f"Generated {len(generated)} config files")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print("  -", w)

    if errors:
        print(f"\nCompleted with {len(errors)} errors:")
        for err in errors:
            print("  -", err)
    else:
        print("Completed with no errors.")

    if gen_errors:
        print(f"\nCompleted with {len(errors)} generation errors:")
        for err in gen_errors:
            print("  -", err)


    # TEST
    if TEST:
        print(encr_files(generated, "%s/"%DT))
        print("\nTest exit!")
        sys.exit(0)

    encrypt_config(rows, DT)

    # Copy to node1
    run(["scp", EXTENSION_FILE, "node1:~/"])

    # Rsync to ipc
    #call(["scp", "./*.tuz", "ipc:~/config/"])
    run(["./scp_ipc.sh"])
