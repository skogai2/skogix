# chmod Cheat Sheet

chmod changes who can read, write, and execute a file on Linux and macOS. This sheet covers the octal numbers, symbolic syntax, recursive changes, SSH key permissions, the special bits, and the chown and umask companions.

## Octal Numbers

Three digits: owner, group, others. Each digit adds read 4, write 2, execute 1. Decode or build any mode with the [chmod calculator](https://sshworkbench.com/tools/chmod-calculator).

| Digit | Meaning                   |
|-------|---------------------------|
| 7     | rwx: read, write, execute |
| 6     | rw-: read and write       |
| 5     | r-x: read and execute     |
| 4     | r--: read only            |
| 0     | ---: nothing              |

The modes that cover almost every real case:

| Command | When to use it |
|----|----|
| chmod 755 dir/ | Directories, scripts, binaries: owner full, others read and enter |
| chmod 644 file.txt | Normal files: owner edits, others read |
| chmod 600 secrets.env | Private files: owner only (SSH keys, credentials) |
| chmod 700 ~/.ssh | Private directories: owner only |
| chmod 400 key.pem | Read-only key files (AWS .pem) |
| chmod 775 shared/ | Group-writable directory for a team |
| chmod 664 shared.txt | Group-writable file |
| chmod 777 anything | Almost never right; see Web Server Permissions below |

## Symbolic Syntax

Who (u owner, g group, o others, a all), then + add, - remove, = set exactly, then r, w, x.

| Command | What it does |
|----|----|
| chmod u+x script.sh | Owner may execute |
| chmod +x script.sh | Everyone may execute (the usual "make it runnable") |
| chmod go-w file.txt | Remove write from group and others |
| chmod a=r file.txt | Everyone gets exactly read, nothing else |
| chmod u=rwx,go=rx dir/ | Same as 755, spelled out |
| chmod g+w shared.txt | Let the group write |
| chmod o= private.txt | Others get nothing |
| chmod -R a+rX dir/ | Capital X: execute on directories only (see Recursive) |

## Make a File Executable

| Command | Action |
|---|---|
| `chmod +x script.sh` | Add execute permissions for User, Group, and Others |
| `chmod u+x script.sh` | Add execute permissions for file Owner (User) only |
| `chmod 755 script.sh` | Set `rwxr-xr-x` (owner full, group/others read and execute) |

The first line of the script should name its interpreter (#!/bin/bash or \#!/usr/bin/env python3), or you will get cannot execute binary file or the wrong shell.

## Recursive Changes

chmod -R hits every file and directory, and one number is usually wrong for one of them: -R 644 makes directories unenterable, -R 755 makes every file executable.

| Command | What it does |
|----|----|
| chmod -R 755 dir/ | Everything 755 (fine for a tree of scripts, wrong for docs) |
| find dir -type d -exec chmod 755 {} + | Directories to 755 only |
| find dir -type f -exec chmod 644 {} + | Files to 644 only |
| chmod -R u+rwX,go+rX dir/ | One pass: X sets execute on dirs (and already-executable files) only |

More find patterns in the [find cheat sheet](https://sshworkbench.com/cheatsheets/find).

## Multiple Files and Wildcards

The shell expands the wildcard before chmod runs, so chmod 755 *.sh reaches chmod as a plain list of filenames.

| Command | Action |
|---|---|
| `chmod 644 *.txt` | Set `rw-r--r--` on all matching `.txt` files in current directory |
| `chmod -R 755 /var/www/html` | Apply permissions recursively to directory and all contents |

## Directories vs Files

The same three letters mean different things on a directory.

| Command | What it does |
|---|---|
| `chmod -R u=rwX,go=rX .` | Capital `X` sets execute bit on directories only (leaves files non-executable) |
| `find . -type f -exec chmod 644 {} +` | Set standard `644` permissions on all files exclusively |
| `find . -type d -exec chmod 755 {} +` | Set standard `755` permissions on all directories exclusively |

Deleting a file needs w on the directory, not on the file. A directory without x blocks access to everything under it no matter what the files say.

## Symlinks

A symlink has no useful mode of its own on Linux: access is decided by the target.

| Command | Behavior |
|---|---|
| `chmod 755 symlink` | Follows symlink and changes permissions of the target file |
| `chmod -h` | Supported on BSD/macOS to alter symlink permissions directly (Linux ignores) |
| `chown -h user:group symlink` | Change ownership of the symbolic link itself |

cannot operate on dangling symlink means the link points at a path that no longer exists.

## setuid, setgid, Sticky Bit

A fourth leading digit, or s/t in symbolic form.

| Special Permission | Numeric Bit | Symbol | Description |
|---|---|---|---|
| SUID (Set User ID) | `4000` | `s` (in owner) | Executable runs with privileges of file owner (`chmod 4755`) |
| SGID (Set Group ID) | `2000` | `s` (in group) | Files created in dir inherit parent directory's group |
| Sticky Bit | `1000` | `t` (in others) | Users can only delete files they own (standard on `/tmp`) |

In ls -l, setuid/setgid show as s in the owner/group execute slot and the sticky bit as t at the end (drwxrwxrwt on /tmp). A capital S or T means the bit is set but execute is missing, which is usually a mistake.

## SSH Key Permissions

OpenSSH checks permissions before it will use a key. A private key that group or others can read is refused outright with UNPROTECTED PRIVATE KEY FILE, and on the server StrictModes (on by default) makes sshd ignore authorized_keys when the home directory, ~/.ssh, or the file itself is group- or world-writable. Full command list in the [SSH cheat sheet](https://sshworkbench.com/cheatsheets/ssh).

| Command | What it does |
|----|----|
| chmod 700 ~/.ssh | The .ssh directory, both ends |
| chmod 600 ~/.ssh/id_ed25519 | Private key (fixes "UNPROTECTED PRIVATE KEY") |
| chmod 644 ~/.ssh/id_ed25519.pub | Public key |
| chmod 600 ~/.ssh/authorized_keys | On the server; ignored if too open |
| chmod 600 ~/.ssh/config | Client config |
| chmod 644 ~/.ssh/known_hosts | Host key store (600 is fine too) |
| chmod 400 key.pem | AWS-style read-only key |
| chmod 700 ~ | Home directory, when a shared box left it group-writable |

The server side is silent about all of this: sshd logs the reason locally and sends the client nothing, so a permissions problem on the server reaches you only as [Permission denied (publickey)](https://sshworkbench.com/fix/ssh-permission-denied-publickey).

## Reading ls -l Output

```
-rwxr-xr--  1 alice developers  4096 Sep  5 10:30 deploy.sh
```

Type, then three triads: owner rwx, group r-x, others r--. That file is 754. Paste any drwxr-xr-x string into the [chmod calculator](https://sshworkbench.com/tools/chmod-calculator) to get the number back.

| First character | Meaning      |
|-----------------|--------------|
| \-              | Regular file |
| d               | Directory    |
| l               | Symlink      |

| Command               | What it does                           |
|-----------------------|----------------------------------------|
| ls -l                 | Long listing with permissions          |
| ls -ld dir/           | The directory itself, not its contents |
| stat -c '%a %n' file  | Show the octal mode (GNU/Linux)        |
| stat -f '%Lp %N' file | Show the octal mode (macOS)            |

A trailing + means ACLs are set (see below); on macOS @ means extended attributes.

## ACLs

When owner, group, and others cannot express who needs access, an ACL adds per-user entries on top of the mode bits. ls -l marks a file that has one with a trailing +.

| Command | What it does |
|---|---|
| `getfacl file.txt` | View extended Access Control Lists for file |
| `setfacl -m u:alice:rwx file.txt` | Grant user `alice` read, write, and execute permissions |
| `setfacl -m g:developers:rx file.txt` | Grant group `developers` read and execute |
| `setfacl -x u:alice file.txt` | Remove specific ACL entry for user |
| `setfacl -b file.txt` | Remove all extended ACLs from file |

Running chmod on a file with an ACL rewrites the ACL mask, which can quietly cut the extra entries down. Check with getfacl after any chmod on an ACL'd path.

## chown and chgrp

chmod changes what the owner, group, and others are allowed to do. chown changes who the owner and group are, and needs root. When a service cannot write a path, chown is almost always the right half of the pair.

| Command | What it does |
|----|----|
| sudo chown alice file.txt | Change the owner |
| sudo chown alice:developers file.txt | Owner and group at once |
| sudo chown -R www-data:www-data /var/www | Recursive, the web-uploads fix |
| chgrp developers file.txt | Group only (works without root for your own files) |
| ls -l file.txt | See current owner and group |

## umask

umask decides the default mode of new files: files start from 666 and directories from 777, minus the mask.

| Command   | What it does                                            |
|-----------|---------------------------------------------------------|
| umask     | Show the current mask (022 is the common default)       |
| umask 022 | New files 644, new directories 755                      |
| umask 077 | New files 600, new directories 700 (private by default) |
| umask 002 | Group-writable: files 664, directories 775              |

Set it in ~/.zshrc or ~/.bashrc to make it stick.

## Web Server Permissions

The convention on Debian/Ubuntu (nginx and Apache run as www-data; on RHEL it is nginx or apache):

| Command | What it does |
|----|----|
| sudo chown -R www-data:www-data /var/www/site | Server owns its files |
| find /var/www/site -type d -exec chmod 755 {} + | Directories 755 |
| find /var/www/site -type f -exec chmod 644 {} + | Files 644 |
| chmod 775 /var/www/site/uploads | Writable dirs: group-writable, with the right group |

When an app "needs" 777 to work, the real problem is ownership: the process user cannot write because it does not own the path. chown to the process user (or share a group) and keep 755/644. 777 hands write access to every account on the box.

## Options and Flags

| Option | What it does |
|----|----|
| -R | Recursive |
| -v | Report every file touched |
| -c | Report only files that actually changed |
| -f | Silence error messages |
| --reference=other | Copy another file's mode (GNU) |
| -h | Change a symlink itself instead of its target (macOS/BSD) |

## Fixing chmod Errors

| Error / Scenario | Solution |
|---|---|
| Locked out of `/bin/chmod` | Run `/lib64/ld-linux-x86-64.so.2 /bin/chmod 755 /bin/chmod` |
| Broken SSH key permissions | Run `chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_* ~/.ssh/authorized_keys` |
| Sudo corrupted | Run `pkexec chmod 4755 /usr/bin/sudo` |

## macOS and Windows

| Platform | Tool / Context |
|---|---|
| macOS | BSD chmod supports ACL syntax: `chmod +a "user:alice allow read" file` |
| Windows (NTFS) | Uses `icacls.exe`: `icacls file /grant Alice:(R,W)` |
| WSL | Mount option `metadata` enables Linux permissions on Windows drives (`/etc/wsl.conf`) |

To make chmod stick on Windows drives in WSL, add this and restart WSL with wsl --shutdown:

```
# /etc/wsl.conf
[automount]
options = "metadata,umask=22,fmask=11"
```

## Gotchas

- Modes survive reboots but not every copy. cp without -p, most unzip tools, and scp without -p reset the mode at the destination, and git records only the execute bit.
- chmod updates a file's ctime, not its mtime, so ls -l shows the old timestamp and backup tools that key on mtime can skip the change entirely.
- Bash wildcards never match dotfiles, so chmod 600 * quietly leaves.env and.ssh alone.
- Numbers are absolute, letters are relative. chmod 755 sets all nine bits and wipes any setuid, setgid, or sticky bit on the file; chmod u+x only adds one bit.
- root ignores the read and write bits, so chmod 000 hides nothing from a root process or from anyone with sudo.

## chmod FAQ

### What does chmod 755 mean?

Each digit is a sum of read (4), write (2), and execute (1) for one class of user: owner, group, others, in that order. 755 is 7 (4+2+1, rwx) for the owner and 5 (4+1, r-x) for group and others: the owner can do everything, everyone else can read and execute but not modify. It is the standard mode for directories, scripts, and binaries. 644 is the file equivalent: owner reads and writes, everyone else only reads, and nobody executes. If translating digits in your head gets old, the chmod calculator on this site converts between octal, symbolic, and checkbox form.

### Why is chmod 777 bad?

777 gives every user on the system write access, so any process or account, including a compromised web app, can replace the file with anything. On a web server that turns one small exploit into a persistent backdoor. 777 is usually reached for when the real problem is ownership: the web server runs as www-data but the files belong to root or your user. The correct fix is chown -R www-data:www-data on the writable directories plus 755/644 modes, or adding your user to the right group with 775/664. The only mostly-legitimate 777-style mode is 1777 on /tmp, where the sticky bit stops users deleting each other's files.

### What chmod do I use for an SSH key?

The private key must be readable by you alone: chmod 600 ~/.ssh/id_ed25519 (400 also works and is what AWS suggests for .pem files). The ~/.ssh directory itself needs 700, authorized_keys on the server needs 600, and your home directory must not be group- or world-writable. OpenSSH enforces this: a private key with loose permissions is refused with an UNPROTECTED PRIVATE KEY warning, and a server with StrictModes (the default) silently ignores authorized_keys when the path to it is too open. Nothing is logged to the client, so the server side shows up only as Permission denied (publickey).

### Does chmod require sudo?

Not for your own files. Only the owner and root may change a file's mode, and no permission setting changes that: a 777 file still refuses chmod from anyone but its owner, and group membership does not help. That is also how the two failures differ. Operation not permitted means you are not the owner, so you need sudo or chown. Permission denied usually means you cannot even reach the file, because some directory on the path lacks execute for you. Anything under /etc, /usr, or /var, or owned by a service account, needs sudo. chown always needs root, which is why chmod 777 gets reached for when handing the file to the right user is the real fix.

### How do I chmod all files in a directory recursively?

chmod -R applies a mode to everything under a directory, but one number is usually wrong for a tree: files want 644 and directories want 755, because execute on a directory means permission to enter it, and 644 directories become untraversable while 755 files become needlessly executable. Either run two find commands, find dir -type d -exec chmod 755 {} + and find dir -type f -exec chmod 644 {} +, or use the capital X in one pass: chmod -R u+rwX,go+rX dir, which sets execute only on directories and files that are already executable.

---
Source: https://sshworkbench.com/cheatsheets/chmod
