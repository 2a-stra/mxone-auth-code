#!/usr/bin/python3
from datetime import datetime
from pathlib import Path
from subprocess import call

BOARD = "1A-0-00-%s"
START_PORT = 0
END_PORT = 31
START_EXT = 200

now = datetime.now() # current date and time
dt = now.strftime("%Y%m%d")
print(dt)

Path("./%s" % dt).mkdir(parents=True, exist_ok=True)
EXTEI_FILE = "./%s/extei-%s--%s.mdsh" % (dt, BOARD % START_PORT, END_PORT)

cmd = ""
ext = START_EXT
with open(EXTEI_FILE, "w") as fl:

    for port in range(START_PORT, END_PORT+1):
        equ = BOARD % port
        cmd = "EXTEI:DIR={ext},TYPE=EL6,EQU={equ},CSP={csp},ICAT=8020000;\n".format(ext=ext, equ=equ, csp=0)
        fl.write(cmd)
        ext += 1

# Copy to node1
call(["scp", EXTEI_FILE, "node1:~/"])