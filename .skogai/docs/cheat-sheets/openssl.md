# OpenSSL Commands Cheat Sheet

OpenSSL is the command line toolkit behind most TLS work on Linux, macOS, and Windows (it ships with Git for Windows). This sheet covers the openssl commands you actually type: reading and checking certificates, generating keys and CSRs, converting between PEM, DER, and PFX, and the odd hashing and encryption jobs.

Last updated September 11, 2026

On this page

- [Inspect a Certificate](#inspect-a-certificate)
- [Check a Live Server](#check-a-live-server)
- [Generate Keys](#generate-keys)
- [Create a CSR](#create-a-csr)
- [Self-Signed Certificate](#self-signed-certificate)
- [Convert Formats](#convert-formats)
- [Verify Chain and Key Match](#verify-chain-and-key-match)
- [CRL and OCSP](#crl-and-ocsp)
- [Create a CA](#create-a-ca)
- [Hash, Encrypt, Random](#hash-encrypt-random)
- [Ciphers and Providers](#ciphers-and-providers)
- [Install and Version](#install-and-version)
- [Gotchas](#gotchas)

## Inspect a Certificate

-noout stops OpenSSL echoing the PEM block after the fields you asked for. For a paste-and-read version, use the [certificate decoder](https://sshworkbench.com/tools/certificate-decoder).

[TABLE]

Read every certificate in a chain file, not just the first:

```
openssl crl2pkcs7 -nocrl -certfile fullchain.pem | openssl pkcs7 -print_certs -noout
```

Copy

## Check a Live Server

s_client opens a TLS connection and prints the handshake. Always pass -servername (SNI), or a host serving several sites hands you the default certificate instead of the one you wanted. The \</dev/null closes the session instead of leaving it waiting for input. The [SSL checker](https://sshworkbench.com/tools/ssl-checker) runs the same check from a browser.

[TABLE]

Print just the dates or the subject of the live certificate:

```
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -dates
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer
```

Copy

Save the live certificate to a file:

```
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -out example.pem
```

Copy

Look for Verify return code: 0 (ok) at the bottom of the output. 21 (unable to verify the first certificate) means the server is not sending its intermediate. curl -vI https://example.com shows the same verdict in fewer lines; see the [curl cheat sheet](https://sshworkbench.com/cheatsheets/curl).

## Generate Keys

genpkey is the current all-purpose generator. genrsa still works in OpenSSL 3 and is not going anywhere soon. For SSH login keys, use ssh-keygen instead, or the [SSH key generator](https://sshworkbench.com/tools/ssh-keygen).

[TABLE]

PuTTY cannot read these keys directly. The [PEM to PPK converter](https://sshworkbench.com/tools/pem-to-ppk-converter) and [PPK to PEM converter](https://sshworkbench.com/tools/ppk-to-pem-converter) go both ways.

## Create a CSR

A certificate signing request is what you send to a CA. Set the subject with -subj so it does not prompt, and put every hostname in a SAN, because browsers ignore the CN.

| Command | What it does |
|----|----|
| openssl req -new -key key.pem -out req.csr -subj "/CN=example.com/O=Example Ltd" | CSR from an existing key |
| openssl req -new -newkey rsa:2048 -nodes -keyout key.pem -out req.csr | New key and CSR in one go (prompts for the subject) |
| openssl req -in req.csr -noout -text | Read a CSR |
| openssl req -in req.csr -noout -subject | Just the subject |
| openssl req -in req.csr -noout -verify | Check the CSR signature |
| openssl req -in req.csr -noout -pubkey | Extract the public key |

With SANs, which every public CA now requires:

```
openssl req -new -key key.pem -out req.csr \
  -subj "/CN=example.com/O=Example Ltd/C=US" \
  -addext "subjectAltName=DNS:example.com,DNS:www.example.com"
```

Copy

-addext needs OpenSSL 1.1.1 or newer. On older builds, put the SANs in a config file and pass -config san.cnf.

## Self-Signed Certificate

For local development, internal services, and anything that will never face a public browser. A public hostname needs a certificate from a real CA, which for most people means a free Let's Encrypt one; the [certbot cheat sheet](https://sshworkbench.com/cheatsheets/certbot) covers issuing and renewing those.

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/CN=example.com" -addext "subjectAltName=DNS:example.com,DNS:localhost,IP:127.0.0.1"
```

Copy

| Command | What it does |
|----|----|
| openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=example.com" | Key plus self-signed certificate, no passphrase, one year |
| openssl req -x509 -key key.pem -out cert.pem -days 365 -subj "/CN=example.com" | Self-sign with a key you already have |
| openssl x509 -req -in req.csr -signkey key.pem -out cert.pem -days 365 | Self-sign an existing CSR |
| openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=example.com" | Same with an EC key |

-nodes means "no DES", that is, do not encrypt the key. OpenSSL 3 spells it -noenc and still accepts -nodes.

## Convert Formats

The extension tells you very little. .pem, .crt, .cer, and .key are usually PEM (text starting with -----BEGIN), .der and sometimes .cer are binary DER, and .pfx and .p12 are PKCS#12 bundles. Run head -1 file before converting.

[TABLE]

OpenSSL cannot read a Java keystore at all. Convert the .jks to a .p12 with keytool from the JDK, as above, then run it through the pkcs12 rows to get PEM. Going back, build a PFX with pkcs12 -export and import it the same way with -srcstoretype PKCS12.

If OpenSSL 3 refuses an old PFX with unsupported or digital envelope routines, the file uses RC2 or 40-bit ciphers; add -legacy. The same flag on -export makes a PFX that old Windows Server and Java 8 can import.

```
openssl pkcs12 -in old.pfx -out cert.pem -nodes -legacy
openssl pkcs12 -export -legacy -out cert.pfx -inkey key.pem -in cert.pem -certfile chain.pem
```

Copy

## Verify Chain and Key Match

| Command | What it does |
|----|----|
| openssl verify -CAfile chain.pem cert.pem | Verify a certificate against a chain file (root plus intermediates) |
| openssl verify -untrusted intermediate.pem -CAfile root.pem cert.pem | Verify with the intermediate supplied separately |
| openssl verify cert.pem | Verify against the system trust store |
| openssl verify -show_chain -CAfile chain.pem cert.pem | Print the chain it built |
| openssl x509 -noout -modulus -in cert.pem \| openssl md5 | RSA modulus hash of the certificate |
| openssl rsa -noout -modulus -in key.pem \| openssl md5 | RSA modulus hash of the key; must match the line above |
| openssl req -noout -modulus -in req.csr \| openssl md5 | RSA modulus hash of a CSR |
| openssl x509 -in cert.pem -noout -pubkey \| openssl sha256 | Public key hash of a certificate (works for EC and Ed25519 too) |
| openssl pkey -in key.pem -pubout \| openssl sha256 | Public key hash of a key; must match the line above |

Check that a full-chain file is in the right order (leaf first, then each issuer):

```
openssl crl2pkcs7 -nocrl -certfile fullchain.pem | openssl pkcs7 -print_certs -noout
```

Copy

Each certificate's issuer should be the next certificate's subject. To tell whether two files hold the same certificate, compare -fingerprint -sha256 on each rather than diffing the PEM, since the same certificate can be stored with different line endings.

When verify or s_client fails, the number in Verify return code says what went wrong:

[TABLE]

Codes 20 and 21 are the two you will actually meet in production, and both are server-side: the fix is to serve the full chain (fullchain.pem, not cert.pem), not to add anything on the client. The [SSL checker](https://sshworkbench.com/tools/ssl-checker) reports the same missing-intermediate problem in plain words.

## CRL and OCSP

Whether a certificate has been revoked is a separate question from whether it verifies.

[TABLE]

Revoking a certificate you issued yourself needs the ca subcommand and its database, not x509:

```
openssl ca -config ca.cnf -revoke server.crt
openssl ca -config ca.cnf -gencrl -out crl.pem
```

Copy

-revoke takes the certificate file. If you only have a serial number, the copy is in newcerts/\<serial\>.pem under the directory your config's new_certs_dir names, and index.txt lists every serial with its status.

## Create a CA

A private CA for internal hostnames, so you can sign as many certificates as you like and install one root on your machines.

```
# Root CA (10 years)
openssl req -x509 -newkey rsa:4096 -keyout ca.key -out ca.crt -days 3650 -nodes \
  -subj "/CN=Example Internal CA"

# CSR for a server, with SANs
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr \
  -subj "/CN=app.internal" -addext "subjectAltName=DNS:app.internal,DNS:app"

# Sign it, keeping the SANs from the CSR (OpenSSL 3)
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt -days 825 -copy_extensions copy
```

Copy

[TABLE]

Trust the root on a client: sudo cp ca.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates on Debian and Ubuntu, sudo trust anchor ca.crt on Fedora and RHEL, and Keychain Access on macOS.

## Hash, Encrypt, Random

[TABLE]

Always pass -pbkdf2 to enc. Without it OpenSSL derives the key with a single MD5 round and warns you about it. Files encrypted without -pbkdf2 must be decrypted without it too.

openssl passwd -apr1 covers one user at a time. For a whole file, the [htpasswd generator](https://sshworkbench.com/tools/htpasswd-generator) writes the lines for you.

## Ciphers and Providers

[TABLE]

OpenSSL 3 moved the old algorithms (RC2, RC4, DES, MD2, and the ciphers inside old PFX files) into a separate legacy provider that is not loaded by default. That is what unsupported, digital envelope routines, and error:0308010C mean. Load it for one command:

```
openssl <subcommand> -provider legacy -provider default ...
```

Copy

openssl list -providers confirms whether it loaded. -legacy on pkcs12 is a shorthand for the same thing.

## Install and Version

[TABLE]

Windows has no openssl.exe of its own, so 'openssl' is not recognized usually means PATH, not a missing install. Git for Windows already ships one at C:\Program Files\Git\usr\bin\openssl.exe, which works as-is inside Git Bash. On macOS, openssl version printing LibreSSL 3.x means you are on Apple's build, which is missing -legacy and, in older releases, -addext; Homebrew installs the real thing but leaves it off PATH, so call /opt/homebrew/opt/openssl@3/bin/openssl or add that directory yourself.

## Gotchas

- Forget
  -noout
  and
  x509
  prints the fields you asked for and then the whole PEM block again. Harmless, but it fills the screen.
- s_client
  without
  -servername
  gets the server's default certificate, which on a shared host is a different site's. Without
  \</dev/null
  it sits there waiting for you to type an HTTP request;
  Ctrl+C
  or
  Q
  ends it. In PowerShell, use
  echo "" \| openssl s_client ...
  since
  \</dev/null
  does not exist there.
- The modulus trick only compares RSA keys. For EC and Ed25519, hash the
  -pubkey
  output instead, as shown above.
- Chrome, Firefox, and Safari ignore the CN entirely. A certificate without a
  subjectAltName
  matching the hostname is rejected even when the CN is right, so always pass
  -addext "subjectAltName=..."
  .
- OpenSSL 3 changed a few defaults:
  pkcs12 -export
  uses AES-256 and SHA-256 (old Windows and Java need
  -legacy
  ), reading an old PFX needs
  -legacy
  ,
  -nodes
  is now
  -noenc
  , and
  genrsa
  is fine but
  genpkey
  is the documented path.
  openssl version
  tells you which you have.
- Can't open config file: /usr/local/ssl/openssl.cnf
  comes up on Windows when the binary looks where it was compiled to look.
  openssl version -d
  prints that path; point
  OPENSSL_CONF
  at the
  openssl.cnf
  your install actually shipped, for example
  set OPENSSL_CONF=C:\Program Files\OpenSSL-Win64\bin\openssl.cnf
  . Only
  req
  and
  ca
  need the config, so other commands work fine without it.
- unable to write 'random state'
  is an old 1.0.2 build failing to write
  .rnd
  into a home directory it cannot find. Set
  RANDFILE
  to a path you can write, or upgrade; OpenSSL 1.1.1 and later do not use that file.
- .crt
  ,
  .cer
  ,
  .pem
  , and
  .key
  are naming conventions, not formats. When a command says
  unable to load certificate
  , check
  head -1
  and add
  -inform DER
  if the file is binary.
- A key file from OpenSSL is not a PuTTY
  .ppk
  , and a
  .ppk
  is not a PEM. The [PEM to PPK](https://sshworkbench.com/tools/pem-to-ppk-converter) and [PPK to PEM](https://sshworkbench.com/tools/ppk-to-pem-converter) converters handle both directions.

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## OpenSSL FAQ

### Does Windows come with OpenSSL?

No. Windows has its own TLS stack (Schannel) and ships no openssl.exe, so the first thing most people see is 'openssl' is not recognized as an internal or external command. You may still have a copy: Git for Windows installs one at C:\Program Files\Git\usr\bin\openssl.exe that works as-is inside Git Bash. Otherwise install it with winget install --id ShiningLight.OpenSSL.Light or choco install openssl, then reopen the terminal so PATH refreshes. Two things then behave differently from Linux. PowerShell has no \</dev/null, so end an s_client command with echo "" \| openssl s_client ... instead. And Git Bash rewrites a -subj "/CN=example.com" argument into a Windows path, so prefix that command with MSYS_NO_PATHCONV=1.

### How do I check a certificate's expiration date with OpenSSL?

For a file, openssl x509 -in cert.pem -noout -enddate prints the notAfter line, and -dates prints both ends. For a script, openssl x509 -in cert.pem -noout -checkend 2592000 exits 1 if the certificate expires within 30 days (the number is seconds), so it slots into cron or a health check without parsing dates. For a live site, pipe s_client into the same command: openssl s_client -connect example.com:443 -servername example.com \</dev/null 2\>/dev/null \| openssl x509 -noout -enddate.

### How do I check that a private key matches a certificate?

Compare the public key each one carries. The classic way is to hash the RSA modulus of both: openssl x509 -noout -modulus -in cert.pem \| openssl md5 and openssl rsa -noout -modulus -in key.pem \| openssl md5 should print the same hash. That only works for RSA. The version that works for RSA, EC, and Ed25519 keys alike is openssl x509 -in cert.pem -noout -pubkey \| openssl sha256 against openssl pkey -in key.pem -pubout \| openssl sha256. Swap x509 for req -in req.csr to check a CSR the same way. If the hashes differ you have the wrong key, and the server will refuse to start or IIS will reject the import.

### How do I convert a PFX to PEM?

A PFX (PKCS#12) is one password-protected file holding the private key, the certificate, and the chain, which is what Windows, IIS, and Exchange hand you. openssl pkcs12 -in cert.pfx -out cert.pem -nodes writes all of it to a single PEM, but Linux servers usually want the parts separately: add -nocerts for just the key, -clcerts -nokeys for just the server certificate, and -cacerts -nokeys for just the chain. The output carries Bag Attributes and subject lines above each block; nginx and Apache ignore them, so there is no need to strip them. Going the other way is openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem -certfile chain.pem. If OpenSSL 3 refuses an old PFX, or the PFX it writes will not import on old Windows or Java 8, add -legacy at either end.

### How do I decrypt a private key with OpenSSL?

People asking this almost always mean removing the passphrase, not decrypting ciphertext. openssl pkey -in key.pem -out key-nopass.pem prompts for the current passphrase and writes the same key without one (openssl rsa -in key.pem -out key-nopass.pem does it for RSA keys). Nginx and Apache cannot start unattended with an encrypted key, which is why people do this, so treat the result like a password and keep it at chmod 600. The prompt that says Enter PEM pass phrase is asking for that passphrase, not for a new one. To go the other way, openssl pkey -in key.pem -aes256 -out key-enc.pem adds one, and generating a key with -nodes (or -noenc on OpenSSL 3) means it never asks in the first place.

---
Källa: https://sshworkbench.com/cheatsheets/openssl
