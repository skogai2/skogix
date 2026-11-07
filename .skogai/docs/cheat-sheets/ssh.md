# SSH Commands

ssh is the OpenSSH client that ships with Linux, macOS, and Windows 10 and later. This sheet covers connecting, running remote commands, copying files, keys, the config file, tunnels, and the flags you reach for when a connection misbehaves.

## Connecting

Port 22 is the default. Every option below can also live in the [config file](https://sshworkbench.com/cheatsheets/ssh#config-file) so you only type ssh prod.

| Command | What it does |
|---|---|
| `ssh user@hostname` | Connect to remote server on default port 22 |
| `ssh -p 2222 user@hostname` | Connect over custom SSH port 2222 |
| `ssh -i ~/.ssh/id_ed25519 user@host` | Authenticate using specific private key |
| `ssh host_alias` | Connect using configuration entry from `~/.ssh/config` |

If the connection is refused or hangs, check the port from outside with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker), then see [Connection refused](https://sshworkbench.com/fix/ssh-connection-refused) or [Could not resolve hostname](https://sshworkbench.com/fix/ssh-could-not-resolve-hostname).

## Syntax and Flags

Options go before the host. Anything after the host is treated as the command to run on the far end, so ssh host -v sends -v to the remote shell instead of turning on verbose output.

```bash
ssh [options] [user@]host [command]
```

| Flag | Meaning | Description |
|---|---|---|
| `-p port` | Port | Connect to specified port |
| `-i identity` | Identity File | Select private key identity file |
| `-v` / `-vvv` | Verbose | Debug connection negotiation and key authentication |
| `-C` | Compression | Enable gzip compression on transfer |
| `-N` | No command | Do not execute remote shell (used for port forwarding) |
| `-f` | Fork | Run SSH process in background right before command execution |
| `-t` | Force TTY | Allocate pseudo-terminal (required for interactive remote tools) |

Short flags stack, so ssh -fNL 8080:localhost:80 host is the same as -f -N -L 8080:localhost:80. Every -o name also works as a plain line in [~/.ssh/config](https://sshworkbench.com/cheatsheets/ssh#config-file), which is where it belongs once you type it twice.

## Remote Commands

| Command | What it does |
|---|---|
| `ssh user@host "uptime && df -h"` | Run command on remote server and display output locally |
| `ssh -t user@host "htop"` | Run interactive full-screen program remotely |
| `ssh user@host "cat > remote.txt" < local.txt` | Pipe local file into remote file over SSH |
| `ssh user@host "sudo systemctl restart nginx"` | Run privileged command remotely |

For anything longer than one line, pipe a heredoc into a remote shell. Quoting the marker as 'EOF' stops your local shell touching the body:

```bash
ssh user@host 'bash -s' <<'EOF'
set -euo pipefail
cd /var/www/app
git pull --ff-only
sudo systemctl reload nginx
EOF
```

## Copying Files

scp and sftp use the same keys, ports, and config aliases as ssh. Remote paths are written user@host:/path.

| Tool | Command | Description |
|---|---|---|
| `scp` | `scp file.txt user@host:/path/` | Copy local file to remote server |
| `scp` | `scp -r user@host:/path/ ./local_dir/` | Copy remote directory recursively to local host |
| `rsync` | `rsync -avz -e "ssh -p 2222" src/ user@host:/dest/` | Fast delta-transfer sync over SSH |

## Keys

| Command | What it does |
|---|---|
| `ssh-keygen -t ed25519 -C "email@example.com"` | Generate modern, secure Ed25519 SSH keypair |
| `ssh-keygen -t rsa -b 4096` | Generate legacy 4096-bit RSA keypair |
| `ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host` | Copy public key to remote `~/.ssh/authorized_keys` |
| `ssh-keygen -y -f ~/.ssh/id_ed25519` | Extract public key from private key |
| `ssh-keygen -l -f ~/.ssh/id_ed25519` | View key fingerprint and bit length |

Generate a key in the browser with the [SSH key generator](https://sshworkbench.com/tools/ssh-keygen), check a key that refuses to work with the [SSH key validator](https://sshworkbench.com/tools/ssh-key-validator), and for PuTTY convert it with the [PEM to PPK converter](https://sshworkbench.com/tools/pem-to-ppk-converter). If the server still says [Permission denied (publickey)](https://sshworkbench.com/fix/ssh-permission-denied-publickey), it is almost always permissions or the wrong key being offered.

## Config File

~/.ssh/config turns a long command into ssh prod. It needs chmod 600. Build one with the [SSH config generator](https://sshworkbench.com/tools/ssh-config-generator).

```bash
Host prod
    HostName 203.0.113.10
    User deploy
    Port 2222
    IdentityFile ~/.ssh/prod_ed25519
    IdentitiesOnly yes
    ProxyJump bastion

Host bastion
    HostName bastion.example.com
    User admin

Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
```

| Directive | Value Example | Description |
|---|---|---|
| `Host` | `prod` | Nickname / alias for the remote connection |
| `HostName` | `192.168.1.50` | Real IP address or fully qualified domain name |
| `User` | `deploy` | Default remote username |
| `Port` | `2222` | Non-standard SSH port |
| `IdentityFile` | `~/.ssh/id_ed25519` | Private key to use for authentication |
| `ProxyJump` | `bastion.example.com` | Jump host / bastion server to route through |

## Port Forwarding

Syntax is -L local_port:destination_host:destination_port, where the destination is named from the SSH server's point of view, so localhost means the server itself.

| Forwarding Type | Syntax | Description |
|---|---|---|
| Local (`-L`) | `ssh -L 8080:localhost:80 user@host` | Forward `localhost:8080` to remote port `80` |
| Remote (`-R`) | `ssh -R 9000:localhost:3000 user@host` | Forward remote port `9000` back to local port `3000` |
| Dynamic (`-D`) | `ssh -D 1080 user@host` | Create local SOCKS5 proxy on port `1080` |

For -R to accept connections from outside the server, GatewayPorts yes must be set in the server's sshd_config. Confirm the far end is actually listening with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker) before you blame the tunnel.

## Agent

The agent holds decrypted keys so you type the passphrase once per login.

| Command | What it does |
|---|---|
| `eval $(ssh-agent -s)` | Start the SSH agent daemon in current shell |
| `ssh-add ~/.ssh/id_ed25519` | Add private key into running SSH agent |
| `ssh-add -l` | List all keys currently managed by agent |
| `ssh-add -D` | Delete all keys from agent |
| `ssh -A user@host` | Forward SSH agent to remote server |

## Known Hosts

| Command | What it does |
|----|----|
| ssh-keygen -R host | Remove a host's old key after a reinstall; fixes [Host key verification failed](https://sshworkbench.com/fix/ssh-host-key-verification-failed) |
| ssh-keygen -R '[host]:2222' | Same for a non-standard port |
| ssh-keygen -F host | Check whether a host is in known_hosts |
| ssh-keyscan host >> ~/.ssh/known_hosts | Pre-trust a host in scripts (compare the fingerprint first) |
| ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub | On the server: print its fingerprint to compare against the warning |
| ssh -o StrictHostKeyChecking=no user@host | Skip the check entirely; throwaway lab machines only |
| ssh -o UserKnownHostsFile=/dev/null user@host | Do not record the host at all (pair with the line above) |

## Windows

Windows 10 1809 and later ship the same OpenSSH client, so every command above works unchanged in cmd, PowerShell, and Windows Terminal. What differs is installing it, where it looks for config, and how you lock down a key file.

| Feature | Details |
|---|---|
| Native OpenSSH | Built into Windows 10/11 (`ssh` in PowerShell & CMD) |
| Config Path | `C:\Users\<Username>\.ssh\config` |
| SSH Agent Service | Windows service `ssh-agent` (set Startup type to Automatic) |
| Permissions Fix | Windows requires restricting `.ssh` files to current user only |

PowerShell and Git Bash keep separate .ssh directories, so a key generated in one is invisible to the other. .ppk files from PuTTY do not work with this client at all; convert them with the [PPK to PEM converter](https://sshworkbench.com/tools/ppk-to-pem-converter) or use the [PuTTY commands](https://sshworkbench.com/cheatsheets/putty) sheet instead.

## X11 Forwarding

| Command | What it does |
|---|---|
| `ssh -X user@host` | Enable standard X11 forwarding for graphical apps |
| `ssh -Y user@host` | Enable trusted X11 forwarding (bypasses security extensions) |

The server needs X11Forwarding yes in /etc/ssh/sshd_config and the xauth package. macOS needs XQuartz, Windows needs VcXsrv or the PuTTY setup in [Cannot open display](https://sshworkbench.com/fix/putty-cannot-open-display).

## Debugging

| Flag / Command | Purpose |
|---|---|
| `ssh -v user@host` | Level 1: prints connection and key negotiation steps |
| `ssh -vvv user@host` | Level 3: maximum debug output (handshakes, ciphers, auth) |
| `ssh -G host_alias` | Dump fully resolved configuration options without connecting |

| Flag / Command | Purpose |
|---|---|
| `ssh -v user@host` | Level 1: prints connection and key negotiation steps |
| `ssh -vvv user@host` | Level 3: maximum debug output (handshakes, ciphers, auth) |
| `ssh -G host_alias` | Dump fully resolved configuration options without connecting |

## Exit Codes

echo $? after ssh returns tells you whether ssh failed or your remote command did. In a script, ssh -o BatchMode=yes -o ConnectTimeout=5 user@host true is the cheapest reachability check: 0 means the login works.

| Exit Code | Meaning |
|---|---|
| `0` | Success |
| `255` | SSH connection error (host unreachable, auth failure, connection lost) |
| `1` .. `127` | Exit status of the command executed on the remote system |

255 is the only ambiguous one, because a remote command is allowed to return it too. If you get 255 and the command definitely ran, rerun with -v and check whether the handshake completed before blaming the connection.

## Gotchas

- ssh takes -p for the port, scp and sftp take -P. Lowercase -p on scp means preserve timestamps, and the copy quietly goes to port 22.
- There is no password flag. If a script needs one, that is sshpass, and the better answer is a key plus ssh-copy-id.
- A private key readable by anyone else is silently skipped. ~/.ssh wants 700, keys and authorized_keys want 600, and the home directory must not be group-writable.
- Single-quote remote commands. In double quotes your local shell expands $HOME and * before ssh sends anything.
- Closing the terminal kills whatever the session was running. Start long jobs inside [tmux](https://sshworkbench.com/cheatsheets/tmux) or under nohup.
- A background tunnel started with -fN outlives the terminal. ps aux \| grep 'ssh -fN' finds it when a port is unexpectedly busy.
- On Windows, ssh in PowerShell is OpenSSH and reads C:\Users\you\\ssh\config, not PuTTY's saved sessions. See [Windows](https://sshworkbench.com/cheatsheets/ssh#windows) for the install check and the.ppk problem.
- Options belong before the host. ssh host -p 2222 does not change the port, it passes -p 2222 to the remote shell and connects on 22.

## SSH FAQ

### Can I pass a username and password in one ssh command?

Not with ssh itself. There is no password flag, on purpose: ssh reads the password from the terminal so it never lands in shell history or the process list. The username goes in the command as ssh user@host or ssh -l user host. If a script absolutely must supply a password, install sshpass and run sshpass -p 'secret' ssh user@host, or better, sshpass -f pwfile ssh user@host. The real fix is a key: ssh-keygen -t ed25519, then ssh-copy-id user@host, and the password prompt goes away for good.

### Why do I get ssh: command not found?

The client is not installed, or it is not on your PATH. On Windows 10 and 11 it is an optional feature: run Add-WindowsCapability -Online -Name OpenSSH.Client\~\~\~~0.0.1.0 in an admin PowerShell, then open a fresh terminal so PATH is re-read. On Debian and Ubuntu it is apt install openssh-client, on Fedora and RHEL dnf install openssh-clients with the s, and on Arch pacman -S openssh. macOS always ships it, so a missing ssh there points at something your ~/.zshrc did to PATH rather than a missing package. Run which -a ssh, or where.exe ssh on Windows, to see which copy you are getting: Git Bash and WSL each carry their own, with their own ~/.ssh directory.

### Why is my ssh command not working?

Read the last line before it gives up, because each failure has a different cause and they are not interchangeable. Connection refused means you reached the machine and nothing was listening on that port. A hang with no message at all is usually a firewall dropping packets, so check the port from outside instead of retrying. Permission denied (publickey) means the network is fine and the server turned your key down. Could not resolve hostname is DNS and never SSH. Run ssh -v and read the last few lines: the step it prints before stopping names the layer that broke. echo $? right after settles it, since 255 means ssh itself failed and any other code came back from the remote command.

### How do I remove a host from known_hosts?

ssh-keygen -R hostname deletes every entry for that name or IP from ~/.ssh/known_hosts and keeps a backup as known_hosts.old. Use the same spelling you connect with; a host known as both a name and an IP needs two runs, and a non-standard port is written as ssh-keygen -R '[hostname]:2222'. You need this after a server is reinstalled or replaced, because its host key changes and ssh refuses to connect with Host key verification failed. If nothing was reinstalled and the key still changed, ask whoever runs the server before you delete anything.

### Is ssh command line only?

The OpenSSH ssh binary is, but the protocol is not. VS Code's Remote-SSH extension opens a folder on a server and reads your ~/.ssh/config, so an alias you set up for the command line works there with no extra setup. Most file managers speak sftp:// for drag-and-drop copies over the same connection scp uses. On Windows, PuTTY gives you a GUI for the same protocol. The one thing that does not carry over is PuTTY's own storage: it keeps sessions in the Windows registry rather than ~/.ssh/config, and it wants .ppk keys, so an OpenSSH key has to be converted first.

---
Source: https://sshworkbench.com/cheatsheets/ssh
