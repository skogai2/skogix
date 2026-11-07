# SSH Commands

ssh is the OpenSSH client that ships with Linux, macOS, and Windows 10 and later. This sheet covers connecting, running remote commands, copying files, keys, the config file, tunnels, and the flags you reach for when a connection misbehaves.

Last updated September 11, 2026

On this page

- [Connecting](#connecting)
- [Syntax and Flags](#syntax-and-flags)
- [Remote Commands](#remote-commands)
- [Copying Files](#copying-files)
- [Keys](#keys)
- [Config File](#config-file)
- [Port Forwarding](#port-forwarding)
- [Agent](#agent)
- [Known Hosts](#known-hosts)
- [Windows](#windows)
- [X11 Forwarding](#x11-forwarding)
- [Debugging](#debugging)
- [Exit Codes](#exit-codes)
- [Gotchas](#gotchas)

## Connecting

Port 22 is the default. Every option below can also live in the [config file](https://sshworkbench.com/cheatsheets/ssh#config-file) so you only type ssh prod.

[TABLE]

If the connection is refused or hangs, check the port from outside with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker), then see [Connection refused](https://sshworkbench.com/fix/ssh-connection-refused) or [Could not resolve hostname](https://sshworkbench.com/fix/ssh-could-not-resolve-hostname).

## Syntax and Flags

Options go before the host. Anything after the host is treated as the command to run on the far end, so ssh host -v sends -v to the remote shell instead of turning on verbose output.

```
ssh [options] [user@]host [command]
```

Copy

[TABLE]

Short flags stack, so ssh -fNL 8080:localhost:80 host is the same as -f -N -L 8080:localhost:80. Every -o name also works as a plain line in [~/.ssh/config](https://sshworkbench.com/cheatsheets/ssh#config-file), which is where it belongs once you type it twice.

## Remote Commands

[TABLE]

For anything longer than one line, pipe a heredoc into a remote shell. Quoting the marker as 'EOF' stops your local shell touching the body:

```
ssh user@host 'bash -s' <<'EOF'
set -euo pipefail
cd /var/www/app
git pull --ff-only
sudo systemctl reload nginx
EOF
```

Copy

## Copying Files

scp and sftp use the same keys, ports, and config aliases as ssh. Remote paths are written user@host:/path.

[TABLE]

## Keys

[TABLE]

Generate a key in the browser with the [SSH key generator](https://sshworkbench.com/tools/ssh-keygen), check a key that refuses to work with the [SSH key validator](https://sshworkbench.com/tools/ssh-key-validator), and for PuTTY convert it with the [PEM to PPK converter](https://sshworkbench.com/tools/pem-to-ppk-converter). If the server still says [Permission denied (publickey)](https://sshworkbench.com/fix/ssh-permission-denied-publickey), it is almost always permissions or the wrong key being offered.

## Config File

~/.ssh/config turns a long command into ssh prod. It needs chmod 600. Build one with the [SSH config generator](https://sshworkbench.com/tools/ssh-config-generator).

```
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

Copy

[TABLE]

## Port Forwarding

Syntax is -L local_port:destination_host:destination_port, where the destination is named from the SSH server's point of view, so localhost means the server itself.

[TABLE]

For -R to accept connections from outside the server, GatewayPorts yes must be set in the server's sshd_config. Confirm the far end is actually listening with the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker) before you blame the tunnel.

## Agent

The agent holds decrypted keys so you type the passphrase once per login.

[TABLE]

## Known Hosts

| Command | What it does |
|----|----|
| ssh-keygen -R host | Remove a host's old key after a reinstall; fixes [Host key verification failed](https://sshworkbench.com/fix/ssh-host-key-verification-failed) |
| ssh-keygen -R '\[host\]:2222' | Same for a non-standard port |
| ssh-keygen -F host | Check whether a host is in known_hosts |
| ssh-keyscan host \>\> ~/.ssh/known_hosts | Pre-trust a host in scripts (compare the fingerprint first) |
| ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub | On the server: print its fingerprint to compare against the warning |
| ssh -o StrictHostKeyChecking=no user@host | Skip the check entirely; throwaway lab machines only |
| ssh -o UserKnownHostsFile=/dev/null user@host | Do not record the host at all (pair with the line above) |

## Windows

Windows 10 1809 and later ship the same OpenSSH client, so every command above works unchanged in cmd, PowerShell, and Windows Terminal. What differs is installing it, where it looks for config, and how you lock down a key file.

[TABLE]

PowerShell and Git Bash keep separate .ssh directories, so a key generated in one is invisible to the other. .ppk files from PuTTY do not work with this client at all; convert them with the [PPK to PEM converter](https://sshworkbench.com/tools/ppk-to-pem-converter) or use the [PuTTY commands](https://sshworkbench.com/cheatsheets/putty) sheet instead.

## X11 Forwarding

[TABLE]

The server needs X11Forwarding yes in /etc/ssh/sshd_config and the xauth package. macOS needs XQuartz, Windows needs VcXsrv or the PuTTY setup in [Cannot open display](https://sshworkbench.com/fix/putty-cannot-open-display).

## Debugging

[TABLE]

[TABLE]

## Exit Codes

echo \$? after ssh returns tells you whether ssh failed or your remote command did. In a script, ssh -o BatchMode=yes -o ConnectTimeout=5 user@host true is the cheapest reachability check: 0 means the login works.

[TABLE]

255 is the only ambiguous one, because a remote command is allowed to return it too. If you get 255 and the command definitely ran, rerun with -v and check whether the handshake completed before blaming the connection.

## Gotchas

- ssh takes
  -p
  for the port, scp and sftp take
  -P
  . Lowercase
  -p
  on scp means preserve timestamps, and the copy quietly goes to port 22.
- There is no password flag. If a script needs one, that is
  sshpass
  , and the better answer is a key plus
  ssh-copy-id
  .
- A private key readable by anyone else is silently skipped.
  ~/.ssh
  wants 700, keys and
  authorized_keys
  want 600, and the home directory must not be group-writable.
- Single-quote remote commands. In double quotes your local shell expands
  \$HOME
  and
  \*
  before ssh sends anything.
- Closing the terminal kills whatever the session was running. Start long jobs inside [tmux](https://sshworkbench.com/cheatsheets/tmux) or under
  nohup
  .
- A background tunnel started with
  -fN
  outlives the terminal.
  ps aux \| grep 'ssh -fN'
  finds it when a port is unexpectedly busy.
- On Windows,
  ssh
  in PowerShell is OpenSSH and reads
  C:\Users\you\\ssh\config
  , not PuTTY's saved sessions. See [Windows](https://sshworkbench.com/cheatsheets/ssh#windows) for the install check and the
  .ppk
  problem.
- Options belong before the host.
  ssh host -p 2222
  does not change the port, it passes
  -p 2222
  to the remote shell and connects on 22.

### Tired of typing all of this?

SSH Workbench turns your servers into a dashboard over plain SSH: files, services, Docker, logs, and cron with a click, and a real terminal when you want one.

[Try free for 7 days](https://sshworkbench.com/#install)

## SSH FAQ

### Can I pass a username and password in one ssh command?

Not with ssh itself. There is no password flag, on purpose: ssh reads the password from the terminal so it never lands in shell history or the process list. The username goes in the command as ssh user@host or ssh -l user host. If a script absolutely must supply a password, install sshpass and run sshpass -p 'secret' ssh user@host, or better, sshpass -f pwfile ssh user@host. The real fix is a key: ssh-keygen -t ed25519, then ssh-copy-id user@host, and the password prompt goes away for good.

### Why do I get ssh: command not found?

The client is not installed, or it is not on your PATH. On Windows 10 and 11 it is an optional feature: run Add-WindowsCapability -Online -Name OpenSSH.Client\~\~\~~0.0.1.0 in an admin PowerShell, then open a fresh terminal so PATH is re-read. On Debian and Ubuntu it is apt install openssh-client, on Fedora and RHEL dnf install openssh-clients with the s, and on Arch pacman -S openssh. macOS always ships it, so a missing ssh there points at something your ~/.zshrc did to PATH rather than a missing package. Run which -a ssh, or where.exe ssh on Windows, to see which copy you are getting: Git Bash and WSL each carry their own, with their own ~/.ssh directory.

### Why is my ssh command not working?

Read the last line before it gives up, because each failure has a different cause and they are not interchangeable. Connection refused means you reached the machine and nothing was listening on that port. A hang with no message at all is usually a firewall dropping packets, so check the port from outside instead of retrying. Permission denied (publickey) means the network is fine and the server turned your key down. Could not resolve hostname is DNS and never SSH. Run ssh -v and read the last few lines: the step it prints before stopping names the layer that broke. echo \$? right after settles it, since 255 means ssh itself failed and any other code came back from the remote command.

### How do I remove a host from known_hosts?

ssh-keygen -R hostname deletes every entry for that name or IP from ~/.ssh/known_hosts and keeps a backup as known_hosts.old. Use the same spelling you connect with; a host known as both a name and an IP needs two runs, and a non-standard port is written as ssh-keygen -R '\[hostname\]:2222'. You need this after a server is reinstalled or replaced, because its host key changes and ssh refuses to connect with Host key verification failed. If nothing was reinstalled and the key still changed, ask whoever runs the server before you delete anything.

### Is ssh command line only?

The OpenSSH ssh binary is, but the protocol is not. VS Code's Remote-SSH extension opens a folder on a server and reads your ~/.ssh/config, so an alias you set up for the command line works there with no extra setup. Most file managers speak sftp:// for drag-and-drop copies over the same connection scp uses. On Windows, PuTTY gives you a GUI for the same protocol. The one thing that does not carry over is PuTTY's own storage: it keeps sessions in the Windows registry rather than ~/.ssh/config, and it wants .ppk keys, so an OpenSSH key has to be converted first.

---
Källa: https://sshworkbench.com/cheatsheets/ssh
