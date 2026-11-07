# PuTTY Commands

PuTTY is the free SSH and serial client most Windows users start with. This sheet covers the Linux commands you type inside a PuTTY session, the keyboard shortcuts, and the command line options for putty.exe, plink, pscp, and psftp.

## Linux Essentials

These are shell commands on the server, not PuTTY features. They work over any SSH client, including PuTTY.

| Command | Action |
|---|---|
| `ls -la` | List files with permissions, sizes, and timestamps |
| `cd /path` | Change directory (`cd ~` for home) |
| `pwd` | Show full path of current directory |
| `df -h` | Display disk space usage in human-readable format |
| `free -h` | Show free and used system memory (RAM and Swap) |

## Viewing Files and Logs

| Command | Action |
|---|---|
| `cat file.txt` | Print entire file to terminal |
| `less file.txt` | Paginate through file (Space for page down, `q` to quit) |
| `tail -f /var/log/syslog` | Follow log file updates in real time (`Ctrl+C` to stop) |
| `grep "error" /var/log/nginx/error.log` | Search log file for matching text |

## Text Editors

nano is the easy one and is on most servers. vi is on every server, including the stripped-down ones, so it is worth knowing enough to get out of.

| Editor | Command | Quick Exit Shortcut |
|---|---|---|
| Nano | `nano filename` | `Ctrl+X`, then `Y`, then `Enter` |
| Vim | `vim filename` | `Esc`, then `:wq` (save) or `:q!` (discard) |

Stuck in vi with nothing happening: press Esc, then type :q! and Enter. Nano's Ctrl+O and Ctrl+X are its own, not PuTTY's, so they reach the editor normally.

## System and Processes

| Command | Action |
|---|---|
| `top` or `htop` | Real-time interactive process viewer (`q` to exit) |
| `ps aux \| grep process_name` | Find PID of running process |
| `sudo kill -9 <PID>` | Force terminate process by PID |
| `sudo systemctl status service_name` | Check running state of a service |
| `sudo systemctl restart service_name` | Restart background daemon |

## Networking

| Command | Action |
|---|---|
| `ip a` | Display network interfaces and IP addresses |
| `ss -tulpn` | Show open listening ports and associated processes |
| `ping -c 4 host` | Check network latency and packet loss |
| `curl -I https://example.com` | Check HTTP server headers |

ifconfig, netstat, and route are gone from most current distros; ip and ss replace them. Changing an interface address over SSH cuts your own session off the moment it applies, so make that change over the serial console instead.

## Keyboard Shortcuts

Copy and paste are where PuTTY differs most from a Windows program.

| Action | PuTTY Mouse / Keyboard Combination |
|---|---|
| Copy Text | Click and drag left mouse button over text |
| Paste Text | Click right mouse button (or press `Shift+Insert`) |
| Select Word | Double-click left mouse button |
| Select Line | Triple-click left mouse button |
| Scrollback | `Shift+PageUp` / `Shift+PageDown` |

Ctrl+Shift+C and Ctrl+Shift+V are off by default. Turn them on under Window > Selection > "Ctrl+Shift+C/V" if you want them.

## Session Actions

| Action | How to perform |
|---|---|
| Duplicate Session | Right-click PuTTY title bar -> Duplicate Session |
| Change Settings | Right-click title bar -> Change Settings |
| Restart Connection | Right-click title bar -> Restart Session |
| Clear Scrollback | Right-click title bar -> Clear Scrollback |

## Session Settings

Set these in the PuTTY configuration window, then go back to Session and click Save so they stick.

| Category | Setting | Recommended Value |
|---|---|---|
| Window | Columns x Rows | `120 x 35` |
| Window -> Translation | Remote character set | `UTF-8` |
| Terminal -> Bell | Action | `None` (disable annoying beeps) |
| Connection | Seconds between keepalives | `30` (prevents idle drops) |
| Connection -> SSH -> Auth | Private key | Path to `.ppk` key file |

## Command Line Options

putty.exe accepts these from a Windows command prompt, PowerShell, or a shortcut's Target field. Most map to a field in the configuration window.

| Flag | Meaning | Example |
|---|---|---|
| `-ssh` | Force SSH protocol | `putty.exe -ssh user@192.168.1.10` |
| `-P port` | Custom port | `putty.exe -P 2222 user@host` |
| `-i key.ppk` | Private key file | `putty.exe -i mykey.ppk user@host` |
| `-load "name"` | Load saved session | `putty.exe -load "Production"` |

Examples:

```bash
putty.exe -ssh git@github.com -P 2222 -i C:\keys\admin.ppk
putty.exe -load "prod-web" -L 8080:localhost:80
putty.exe -serial COM3 -sercfg 9600,8,n,1,N
```

There is no command line flag for keepalives. Set them in a saved session and open it with -load.

## plink

plink is PuTTY without the window: it runs one command on a remote host and prints the output, so it is the piece you use in batch files and scheduled tasks. It shares the options above.

| Command | What it does |
|----|----|
| plink -ssh user@host "uptime" | Run a command and print the output |
| plink -ssh user@host "df -h" > disk.txt | Save the output to a local file |
| plink -batch -ssh user@host "uptime" | Never prompt; fail instead (for scripts) |
| plink -i key.ppk user@host "uptime" | Authenticate with a key |
| plink -hostkey SHA256:... user@host "uptime" | Accept only the expected host key, so a first run never hangs on the prompt |
| plink -m commands.txt user@host | Run every line of a file |
| plink -ssh user@host < commands.txt | Same, reading from standard input |
| plink -load "prod-web" "uptime" | Use a saved session's host, port, and key |
| plink -N -L 5432:localhost:5432 user@host | Open a tunnel and keep it up, no shell |
| plink -T user@host "cat /etc/hostname" | No pseudo-terminal, cleaner output for parsing |
| plink -ssh user@host | Interactive session in the current console window |

A batch file that checks a server every morning:

```bash
@echo off
plink -batch -i C:\keys\admin.ppk -hostkey SHA256:REPLACE git@github.com "df -h; uptime" > C:\logs\morning.txt
```

## pscp

pscp copies files between Windows and a server over SSH. Remote paths are user@host:/path.

| Command | Action |
|---|---|
| `pscp file.txt user@host:/path/` | Upload file to remote server via SCP |
| `pscp user@host:/path/file.txt .` | Download file from remote server |
| `pscp -r dir/ user@host:/path/` | Copy local folder recursively to remote |
| `pscp -P 2222 -i key.ppk file.txt user@host:/path/` | Use non-standard port and private key |

## psftp

psftp is an interactive FTP-style session over SSH. Start it with psftp user@host (add -P, -i as for pscp), then use these at the psftp> prompt.

| Command | Action |
|---|---|
| `psftp user@host` | Start interactive SFTP session |
| `get filename` | Download file to local working directory |
| `put filename` | Upload local file to remote server |
| `mget *.log` | Download multiple files matching wildcard |
| `bye` or `quit` | Exit SFTP session |

Scripted transfers go in a file, one command per line, and run with psftp -b script.txt user@host. Add -be to continue past errors and -bc to echo each command.

## Serial Connections

For console cables, Raspberry Pi and Arduino boards, and modems. Set Connection type to Serial in the Session panel, or use -serial on the command line.

| Parameter | Standard Value | Description |
|---|---|---|
| Connection Type | `Serial` | Switch connection radio button |
| Serial line | `COM1` or `COM3` | Hardware COM port from Device Manager |
| Speed (baud) | `115200` or `9600` | Baud rate of serial hardware |
| Data bits / Stop bits | `8` / `1` | Standard serial framing |
| Parity / Flow Control | `None` / `None` | Standard configuration for routers and dev boards |

If nothing appears after connecting, press Enter once; a console does not print until you do. If PuTTY refuses the port, see [Unable to open serial port](https://sshworkbench.com/fix/putty-unable-to-open-serial-port). If you cannot see what you type, set Terminal > Local echo to Force on.

Modem and cellular module AT commands, typed into the serial session:

| Parameter | Standard Value | Description |
|---|---|---|
| Connection Type | `Serial` | Switch connection radio button |
| Serial line | `COM1` or `COM3` | Hardware COM port from Device Manager |
| Speed (baud) | `115200` or `9600` | Baud rate of serial hardware |
| Data bits / Stop bits | `8` / `1` | Standard serial framing |
| Parity / Flow Control | `None` / `None` | Standard configuration for routers and dev boards |

## Cisco and Network Devices

Over the console cable or SSH to a switch or router, PuTTY is just the window; these are IOS commands. The prompt tells you the mode: Switch> is user mode, Switch# is privileged, Switch(config)# is global configuration.

| Step / Shortcut | Description |
|---|---|
| Connect Console Cable | Connect USB-to-RS232 adapter to Cisco console port |
| Open PuTTY | Select Serial, enter correct COM port and baud 9600 |
| `Enter` | Wake console prompt (`Router>`) |
| `enable` | Enter privileged EXEC mode (`Router#`) |
| `show running-config` | Display active configuration |

Aruba and HP ProCurve switches use the same shape: configure, show running-config, show interfaces brief, show vlans, and write memory. Juniper uses configure, show configuration, and commit instead.

Connection refused when you SSH to a switch usually means SSH is not turned on yet; see [Network error: Connection refused](https://sshworkbench.com/fix/putty-network-error-connection-refused).

## Gotchas

- Ctrl+C is interrupt, not copy. Selecting text already copied it; right-click pastes. Pasting a multi-line snippet runs every line the moment it lands, so check it first.
- A session that drops after a few idle minutes wants a keepalive, not a bigger scrollback. Connection > Seconds between keepalives: 30, then Save.
- -pw on the command line is visible to every user on the machine in Task Manager. Use a.ppk key with -i, or Pageant.
- PuTTY cannot use an OpenSSH id_rsa or.pem key directly. Convert it to.ppk with the [PEM to PPK converter](https://sshworkbench.com/tools/pem-to-ppk-converter) or PuTTYgen.
- Closing the PuTTY window kills whatever was running in it. For a long job, start it under nohup, screen, or tmux.
- There is no file transfer inside the PuTTY window. Downloads and uploads go through pscp, psftp, or WinSCP from a separate command prompt.
- Windows 10 and 11 ship OpenSSH, so ssh user@host in PowerShell works without PuTTY at all. PuTTY still wins for serial ports and saved sessions. The [PuTTY download page](https://sshworkbench.com/download/putty) covers which build to install.

## PuTTY FAQ

### Does PuTTY use Linux commands?

PuTTY itself has almost no commands. It is a terminal window: whatever you type goes to the machine you connected to, so on a Linux server you use Linux commands (ls, cd, df -h, tail -f), on a Cisco switch you use IOS commands (show running-config), and on a modem you use AT commands. The only commands that belong to PuTTY are the putty.exe, plink, pscp, and psftp options you pass on the Windows command line.

### How do I automate PuTTY commands?

Use plink, not the PuTTY window: nothing typed into the window can be scripted. plink -batch -i C:\keys\admin.ppk user@host "df -h" runs one command and prints the output, and -m commands.txt runs a whole file of them. Two flags matter for anything unattended: -batch makes plink fail instead of stopping on a prompt, and -hostkey SHA256:... stops the very first run from hanging on the unknown host key question. plink returns the remote command's exit code, so a scheduled task or batch file can test errorlevel and act on it.

### How do I run a command automatically after login in PuTTY?

Put the command in Connection > SSH > Remote command and save the session. PuTTY runs it instead of a login shell and closes the window when it finishes, so for a one-off check like uptime also set Session > Close window on exit to Never. To land in a shell afterwards, use a remote command such as cd /var/log; exec bash -l. The field belongs to the saved session, so if you also want a plain shell on that host, save a second session under a different name rather than clearing the field each time.

### How do I save in PuTTY?

It depends what you are saving. In nano, Ctrl+O then Enter writes the file and Ctrl+X exits. In vi or vim, press Esc first, then :w to save, :wq to save and quit, or :q! to leave without saving. On a Cisco or Aruba switch, write memory saves the running config so it survives a reload. To keep a copy of the session itself, turn on Session > Logging > All session output before you connect. Settings you change in the configuration window only stick if you go back to the Session panel and click Save on the session name.

### How do I see command history in PuTTY?

History belongs to the shell on the server, not to PuTTY. Run history to list it, history \| grep ssh to search it, press the Up arrow to step back through it, or Ctrl+R to search as you type. Rerun entry 42 with !42 and the last command with !!. For timestamps, add export HISTTIMEFORMAT='%F %T ' to ~/.bashrc; history -c clears the current session's list. The window's scrollback is separate: Shift+PgUp scrolls it, and Session > Logging writes everything to a file.

---
Source: https://sshworkbench.com/cheatsheets/putty
