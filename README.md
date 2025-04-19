# Generate SIP and analog phones configuration files for MX-ONE

## SIP Phone Registration and Configuration with MX-ONE PBX

When SIP phones register with the MX-ONE PBX, you can link each phone's unique MAC address to a specific extension number. The phone then attempts to download its configuration file from the IP Phone Configuration Server (e.g., HTTP or HTTPS server). This configuration file contains the following:

- The phone's assigned extension number
- Authentication code
- SIP server IP addresses

### Config File Generation with `gen_ext_conf.py`

The `gen_ext_conf.py` script automates the generation of configuration files for each phone. It creates a unique authentication code for each phone per each MAC address. The process relies on a pre-prepared `mac.csv` file, which contains a list of MAC addresses, their corresponding extension numbers, and Common Service Profile (CSP) numbers.

### MX-ONE Shell Commands for Authentication

In addition to generating configuration files, the `gen_ext_conf.py` script also generates a set of MX-ONE shell commands. These commands, saved in the `extensions.sh` file, are used in the PBX CLI to set authentication codes for each extension. When using the `MD5a1` format for authentication codes, the passwords are securely hashed and are not visible in plain text. However, the clear-text passwords are saved in the `auth.txt` output file.

## Input file "mac.csv" format
MAC,EXTENTION,CSP

### Example "mac.csv"
```
14:00:E9:11:11:11,101,0
14:00:E9:11:11:12,102,0
14:00:E9:11:11:13,103,1
```

## gen_ext_conf.py

The script allows you to configure the input CSV file separator, choose the desired password length and SIP proxy IP address.

```python
DELIM = "," # CSV file separator
DIG = 14    # length of auth code
SIP_PROXY = "192.168.1.11"
```

Run the script:
```
$ python3 gen_ext_conf.py
Generated 3 config files
```

## Output files created in a sub-directory `<date>`
- `<MAC>.cfg` files
- `<MAC>.tuz` encrypted files
- file with passwords: `auth-<date-time>.txt`
- file with commands: `extensions-<date-time>.sh`

### `1400E9111111.cfg`

```
sip line1 user name:101
sip line1 auth name:101
sip line1 password:n0l0VoB11QNkxU
sip proxy ip:"192.168.1.11"
sip registrar ip:"192.168.1.11"
```

### `auth-<date-time>.txt`

```
101,n0l0VoB11QNkxU
102,pY9BwjbJHXVmFq
103,Y6cN2O144k7QyX
```

### `extensions-<date-time>.sh`

```sh
extension -i -d 101 --csp 0 -l 1
extension -i -d 102 --csp 0 -l 1
extension -i -d 103 --csp 1 -l 1
ip_extension -i -d 101 --protocol sip
ip_extension -i -d 102 --protocol sip
ip_extension -i -d 103 --protocol sip
auth_code -i -d 101 --csp 0 --cil 101 --customer 0 --hash-type md5a1 --auth-code n0l0VoB11QNkxU
auth_code -i -d 102 --csp 0 --cil 102 --customer 0 --hash-type md5a1 --auth-code pY9BwjbJHXVmFq
auth_code -i -d 103 --csp 1 --cil 103 --customer 0 --hash-type md5a1 --auth-code Y6cN2O144k7QyX
```

## Encrypting Configuration Files

For enhanced security, the generated configuration (`cfg`) files can be encrypted using the `anacrypt` utility. After encryption, the configuration files are stored as `tuz` files, which are then uploaded to the Configuration Server, replacing the original unencrypted `cfg` files.

The `anacrypt` utility, available from the vendor's Download Center, allows you to securely encrypt configuration files for SIP phones. It encrypts all `cfg` files in the current directory (`./`) into `tuz` format using a specified password (located in a file with the name `passw`).

### Steps to Encrypt and Deploy Configuration Files:

1. **Encrypt Configuration Files**: Use the `anacrypt` utility to encrypt all `cfg` files in the current directory into `tuz` files. This ensures that the configuration data is protected.
   
2. **Copy Encrypted Files**: After encryption, transfer the generated `tuz` files, along with the `security.tuz` file, to the Configuration Server.

3. **Download and Decrypt**: The SIP phone will then download the encrypted `tuz` files from the Configuration Server, decrypt them using the provided password, and automatically apply the configuration.

```sh
anacrypt -d ./ -m -p password1234 -i
```

Then copy all files to remote using `scp`.

This process ensures secure and efficient registration and configuration of SIP phones on the MX-ONE PBX, leveraging automated scripts and encryption for added security.

## Create analog extensions in a bulk

Configuration:
```
BOARD = "1A-0-00-%s"
START_PORT = 0
END_PORT = 31
START_EXT = 200
```

Run the script:
```
$ python3 extei.py
```

### Output extei.mdsh example

```
EXTEI:DIR=200,TYPE=EL6,EQU=1A-0-00-0,CSP=0,ICAT=8020000;
EXTEI:DIR=201,TYPE=EL6,EQU=1A-0-00-1,CSP=0,ICAT=8020000;
EXTEI:DIR=202,TYPE=EL6,EQU=1A-0-00-2,CSP=0,ICAT=8020000;
```
