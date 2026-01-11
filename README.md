# Generate SIP and analog phones configuration files for MX-ONE

## SIP Phone Registration and Configuration with MX-ONE PBX

When SIP phones register with the MX-ONE PBX, you can link each phone's unique MAC address to a specific extension number. The phone then attempts to download its configuration file from the IP Phone Configuration Server (e.g., HTTP or HTTPS server). This configuration file contains the following:

- The assigned extension number for the phone
- Extension's first and second names
- Authentication code
- SIP server IP addresses

### Configuration File Generation with `gen_ext_conf2.py`

The `gen_ext_conf2.py` script automates the generation of configuration files for each phone. It creates a unique authentication code for each phone per each MAC address. The process relies on a pre-prepared file with default name `mac.csv`, which contains a list of MAC addresses, their corresponding extension numbers, Common Service Profile (CSP) numbers and names.

### MX-ONE Shell Commands for Authentication

In addition to generating configuration files, the `gen_ext_conf2.py` script also generates a set of MX-ONE shell commands. These commands, saved in the `extensions.sh` file, are used in the PBX CLI to set authentication codes for each extension. When using the `MD5a1` format for authentication codes, the passwords are securely hashed and are not visible in plain text. However, the clear-text passwords are saved in the `auth.txt` output file.

## Input file `mac.csv` format
MAC;EXTENTION;CSP;Name1;Name2

### Example of `mac.csv` input file
```
14:00:E9:11:11:11;1111;0;First Name;Second name
14:00:E9:22:22:22;2222;1;F.;SEC
14:00:E9:33:33:33;3333;5;First only;
14:00:E9:44:44:44;4444;5;First name very very long; Second very long long name
```

_Note_: The `Name1` and `Name2` fields are limited to 20 characters in MX-ONE and will be truncated by the script to avoid command input errors.

## gen_ext_conf2.py (v2)

The script allows you to configure the input CSV file separator, choose the desired password length and SIP proxy IP address.

```python
TEST = True

DELIM = ";" # CSV file separator
DIG = 14    # length of auth code
SIP_PROXY = "192.168.1.11"
```

If the constant `TEST` is set to `True`, the output will be generated in the `_test` folder, otherwise will be created a folder with a date as a name in `YYYYMMDD` format.

Run the script `gen_ext_conf2.py <mac.csv>`:
```
$ ./gen_ext_conf2.py test_mac.csv
20260000-112557
'First only' - without second name
'First name very very' - Truncated to 20 chars
'Second very long lon' - Truncated to 20 chars
==
Generated 4 config files
```

## Output files created in a sub-directory `<date>`

- `<MAC>.cfg` files
- file with passwords: `auth-<date-time>.txt`
- file with commands: `extensions-<date-time>.sh`
- `<MAC>.tuz` encrypted files (generated in a local dir)

### Generated config file `1400E9111111.cfg` example

```
sip line1 user name:1111
sip line1 auth name:1111
sip line1 password:renGk7aqkjvSWZ
sip proxy ip:"192.168.1.11"
sip registrar ip:"192.168.1.11"
```

### `auth-<date-time>.txt` output example

```
1111,renGk7aqkjvSWZ
2222,W8g7bWIWhThsKs
3333,eLa7vIaqjWDdie
4444,NaNNWOzCubf8iJ
```

### `extensions-<date-time>.sh` output example

```sh
extension -i -d 1111 --csp 0 -l 1
extension -i -d 2222 --csp 1 -l 1
extension -i -d 3333 --csp 5 -l 1
extension -i -d 4444 --csp 5 -l 1
ip_extension -i -d 1111 --protocol sip
ip_extension -i -d 2222 --protocol sip
ip_extension -i -d 3333 --protocol sip
ip_extension -i -d 4444 --protocol sip
name -i -d 1111 --name1 "First Name" --name2 "Second name" --number-type dir
name -i -d 2222 --name1 "F." --name2 "SEC" --number-type dir
name -i -d 3333 --name1 "First only" --number-type dir
name -i -d 4444 --name1 "First name very very" --name2 "Second very long lon" --number-type dir
auth_code -i -d 1111 --csp 0 --cil 1111 --customer 0 --hash-type md5a1 --auth-code renGk7aqkjvSWZ
auth_code -i -d 2222 --csp 1 --cil 2222 --customer 0 --hash-type md5a1 --auth-code W8g7bWIWhThsKs
auth_code -i -d 3333 --csp 5 --cil 3333 --customer 0 --hash-type md5a1 --auth-code eLa7vIaqjWDdie
auth_code -i -d 4444 --csp 5 --cil 4444 --customer 0 --hash-type md5a1 --auth-code NaNNWOzCubf8iJ
```

## Encrypting Configuration Files

For enhanced security, the generated configuration (`cfg`) files can be encrypted using the `anacrypt` utility. After encryption, the configuration files are stored as `tuz` files, which are then uploaded to the Configuration Server, replacing the original unencrypted `cfg` files.

The `anacrypt` utility, available from the vendor's SW Download Center, allows you to securely encrypt configuration files for SIP phones. It encrypts all `cfg` files in the current directory (`./`) into `tuz` format using a specified password.

### Steps to Encrypt and Deploy Configuration Files:

1. **Encrypt Configuration Files**: Use the `anacrypt` utility to encrypt all `cfg` files in the current directory into `tuz` files. This ensures that the configuration data is protected.
   
2. **Copy Encrypted Files**: After encryption, transfer the generated `tuz` files, along with the `security.tuz` file, to the Configuration Server.

3. **Download and Decrypt**: The SIP phone will then download the encrypted `tuz` files from the Configuration Server, decrypt them using the provided password, and automatically apply the configuration.

```sh
anacrypt -d ./ -m -p password1234 -i
```

The password for encryption can be read from the local file with the name `passw`.

Then copy all files to remote using `scp`.

This process ensures secure and efficient registration and configuration of SIP phones on the MX-ONE PBX, leveraging automated scripts and encryption for added security.


# Create analog extensions in a bulk

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

## Output extei.mdsh example

```
EXTEI:DIR=200,TYPE=EL6,EQU=1A-0-00-0,CSP=0,ICAT=8020000;
EXTEI:DIR=201,TYPE=EL6,EQU=1A-0-00-1,CSP=0,ICAT=8020000;
EXTEI:DIR=202,TYPE=EL6,EQU=1A-0-00-2,CSP=0,ICAT=8020000;
```


# Generate SIP and analog phones configuration files for MX-ONE (v1)

## Input file "mac.csv" format
MAC,EXTENTION,CSP

### Example "mac.csv"
```
14:00:E9:11:11:11,101,0
14:00:E9:11:11:12,102,0
14:00:E9:11:11:13,103,1
```

## gen_ext_conf.py (v1)

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
