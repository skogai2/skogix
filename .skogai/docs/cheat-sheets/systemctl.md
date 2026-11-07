# systemctl Commands

systemctl is the command that talks to systemd, the init system on nearly every current Linux distro. This systemd cheat sheet covers the systemctl commands for starting, enabling and inspecting services, the journalctl commands for reading their logs, timers, unit file editing, and reboot and power.

Most state-changing commands need sudo; reading status and listing units does not. Unit names can drop the .service suffix (systemctl status nginx and systemctl status nginx.service are the same).

## Manage a Service

| Command | What it does |
|---|---|
| `sudo systemctl start nginx` | Start a stopped service immediately |
| `sudo systemctl stop nginx` | Stop a running service |
| `sudo systemctl restart nginx` | Stop and start service |
| `sudo systemctl reload nginx` | Reload configuration without stopping process |
| `systemctl status nginx` | Show current status, active state, and recent log entries |
| `systemctl is-active nginx` | Check active status (returns exit code 0 if running) |

restart and reload differ: reload sends the service its reload signal (nginx re-reads its config with no dropped connections), restart kills and relaunches it. systemctl status exits non-zero when the service is not running, which trips up scripts that only wanted the output.

## Enable and Disable

Enabling controls what happens at boot. It does not start anything on its own, and starting does not enable anything.

| Command | What it does |
|---|---|
| `sudo systemctl enable nginx` | Enable service to start automatically on system boot |
| `sudo systemctl disable nginx` | Disable service from starting on boot |
| `sudo systemctl enable --now nginx` | Enable for boot and start immediately in one step |
| `sudo systemctl disable --now nginx` | Stop service and disable from boot |
| `systemctl is-enabled nginx` | Check if service is configured to start on boot |
| `sudo systemctl mask nginx` | Completely mask service (links to `/dev/null`, prevents start) |
| `sudo systemctl unmask nginx` | Unmask previously masked service |

static means the unit has no [Install] section and is pulled in by something else; you cannot enable it and do not need to. Failed to start nginx.service: Unit nginx.service is masked means someone masked it, on purpose or by a package; unmask restores it.

## List Units

| Command | What it does |
|---|---|
| `systemctl list-units --type=service` | List all active service units loaded in memory |
| `systemctl list-units --state=failed` | List units currently in a failed error state |
| `systemctl list-unit-files --type=service` | List all installed service files and their enabled status |
| `systemctl list-sockets` | List all listening sockets managed by systemd |

list-units shows what systemd has loaded; list-unit-files shows what is installed on disk. A service that is installed but has never started shows up only in the second.

## Logs

systemd services log to the journal, and journalctl reads it. These are the calls you need alongside systemctl; the [journalctl cheat sheet](https://sshworkbench.com/cheatsheets/journalctl) covers the full toolkit.

| Command | What it does |
|---|---|
| `journalctl -u nginx` | View full systemd log journal for specified unit |
| `journalctl -u nginx -f` | Follow log output in real time |
| `journalctl -u nginx -n 50` | View last 50 log lines for service |
| `systemctl status -l nginx` | Show status with full un-truncated log lines |

systemctl status shows the last ten lines. When the service failed to start and those lines do not explain why, journalctl -u name -b -p err usually does. If journalctl shows nothing for a unit, the service may be writing to its own log file under /var/log instead of stdout.

## Failed Services

| Command | What it does |
|---|---|
| `systemctl --failed` | List all system units currently in failed state |
| `systemctl reset-failed nginx` | Reset the failed state flag for a specific service |
| `systemctl reset-failed` | Clear failed state flag across all units |

The status= code on the failure line narrows it down before you read a single log line:

| Command | What it does |
|---|---|
| `systemctl --failed` | List all system units currently in failed state |
| `systemctl reset-failed nginx` | Reset the failed state flag for a specific service |
| `systemctl reset-failed` | Clear failed state flag across all units |

Unit nginx.service could not be found means either a typo in the name or a new file that systemd has not read yet, so run daemon-reload first. Start request repeated too quickly is the rate limit rather than the real error: read the journal for the original crash, fix it, then reset-failed before starting again.

## Timers

Timers are systemd's cron: a .timer unit that starts a matching .service on a schedule.

| Command | What it does |
|---|---|
| `systemctl list-timers` | List all active systemd timers, next trigger time, and last run |
| `systemctl list-timers --all` | List all timers including inactive ones |
| `sudo systemctl start foo.timer` | Start a timer immediately |
| `sudo systemctl enable --now foo.timer` | Enable and start timer |

A timer that runs a script every night at 03:00, in two files:

```
# /etc/systemd/system/backup.service
[Unit]
Description=Nightly backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

```
# /etc/systemd/system/backup.timer
[Unit]
Description=Run backup nightly

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Persistent=true runs a missed job at the next boot, which cron never did. Have a crontab line already? The [cron to systemd timer converter](https://sshworkbench.com/tools/cron-to-systemd-timer) turns it into these two files, and the [cron generator](https://sshworkbench.com/tools/cron-generator) helps with the schedule itself.

## Edit Unit Files

Your units go in /etc/systemd/system. Package units live in /usr/lib/systemd/system (or /lib/systemd/system on Debian and Ubuntu, which is the same directory) and get overwritten on upgrade, so never edit those directly. A file in /etc with the same name wins over the one in /usr/lib.

| Command | What it does |
|---|---|
| `sudo systemctl edit nginx` | Create/edit drop-in override file (`/etc/systemd/system/nginx.service.d/override.conf`) |
| `sudo systemctl edit --full nginx` | Open full copy of original unit file in `/etc/systemd/system/` for editing |
| `sudo systemctl daemon-reload` | Reload systemd manager configuration (required after editing unit files) |
| `systemctl cat nginx` | Display contents of service unit file and all drop-in overrides |

systemctl edit opens an empty drop-in in $EDITOR; whatever you type is layered on top of the original, and it runs daemon-reload for you. It does not restart the service, so follow with systemctl restart. Overriding ExecStart in a drop-in needs an empty line first, because ExecStart lines add up:

```
[Service]
ExecStart=
ExecStart=/usr/sbin/nginx -c /etc/nginx/custom.conf
```

A minimal service unit for your own program:

```
[Unit]
Description=My app
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=app
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/server --port 3000
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Save it as /etc/systemd/system/myapp.service, then sudo systemctl daemon-reload and sudo systemctl enable --now myapp. The [systemd unit generator](https://sshworkbench.com/tools/systemd-unit-generator) writes this for you and the [systemd unit validator](https://sshworkbench.com/tools/systemd-unit-validator) checks one you already have. Moving a Node app off pm2? The [pm2 to systemd converter](https://sshworkbench.com/tools/pm2-to-systemd) turns an ecosystem file into units.

## Remove a Service

| Step | Command | Action |
|---|---|---|
| 1. Stop & Disable | `sudo systemctl disable --now foo` | Halt running process and remove boot symlinks |
| 2. Remove File | `sudo rm /etc/systemd/system/foo.service` | Delete custom unit file |
| 3. Reload Daemon | `sudo systemctl daemon-reload` | Re-read system unit files |
| 4. Clear State | `sudo systemctl reset-failed` | Flush cached failed state |

Only delete files under /etc/systemd/system. A unit that came from a package lives in /usr/lib/systemd/system, so deleting it there gets undone by the next upgrade; disable it, or mask it if something else keeps pulling it in, and remove the package if you want it gone for good. Skipping reset-failed leaves a ghost entry that still shows up as failed after the file is gone.

## Dependencies and Order

| Directive | Context | Meaning |
|---|---|---|
| `After=network.target` | `[Unit]` | Start this unit strictly after network is online |
| `Before=bar.service` | `[Unit]` | Start this unit before `bar.service` |
| `Requires=db.service` | `[Unit]` | Strict dependency: fails if `db.service` fails to start |
| `Wants=db.service` | `[Unit]` | Weak dependency: starts `db.service` but does not fail if it errors |

Ordering and requirement are separate: After= only says when, Requires= and Wants= say what has to be pulled in, and a unit with Requires= but no After= can start before its dependency is ready. Wants= tolerates the other unit failing, Requires= does not, and BindsTo= also stops your unit when the other one goes away. Use After=network-online.target with a matching Wants= when a service needs a routable address, since network.target only means the stack has been set up.

## Boot and Power

| Command | What it does |
|---|---|
| `systemctl reboot` | Reboot the operating system |
| `systemctl poweroff` | Shut down and power off hardware |
| `systemd-analyze` | Show total boot time breakdown (kernel vs userspace) |
| `systemd-analyze blame` | Print list of services ordered by startup delay time |

systemd-analyze blame shows time spent, not time that delayed the boot; a unit can take 30 seconds in parallel without slowing anything. critical-chain shows the ones that actually held things up.

## User Services

--user manages units under your own account, without sudo, from ~/.config/systemd/user/. Handy for a personal sync client, an editor daemon, or a dev server.

| Command | What it does |
|---|---|
| `systemctl --user status myapp` | Check user-space service status |
| `systemctl --user start myapp` | Start user-space service (lives in `~/.config/systemd/user/`) |
| `loginctl enable-linger $USER` | Allow user services to run even when user is not logged in |

Without enable-linger, user services stop when your last session closes, which is the usual reason a --user service dies as soon as you disconnect from SSH.

## service and chkconfig

The old SysV commands still exist on most distros and forward to systemd, so they work but hide what is happening and drop the useful output.

| Action | Systemd (`systemctl`) | SysVinit (`service` / `chkconfig`) |
|---|---|---|
| Start service | `systemctl start nginx` | `service nginx start` |
| Stop service | `systemctl stop nginx` | `service nginx stop` |
| Restart | `systemctl restart nginx` | `service nginx restart` |
| Enable on boot | `systemctl enable nginx` | `chkconfig nginx on` |
| Check status | `systemctl status nginx` | `service nginx status` |

systemctl is not sysctl, which reads and writes kernel parameters and has nothing to do with services.

## Gotchas

- start is now, enable is at boot. A service you enabled but never started is still stopped until you reboot; enable --now does both.
- After editing any unit file by hand, run sudo systemctl daemon-reload, or systemd keeps using the old version and warns Warning: The unit file ... changed on disk. systemctl edit reloads for you but does not restart.
- A drop-in that sets ExecStart needs ExecStart= on its own line first to clear the original, or the unit fails with Service has more than one ExecStart= setting.
- Start request repeated too quickly is the start rate limit, not the real error. Read journalctl -u name -b for the crash that caused it, fix that, then systemctl reset-failed name before starting again.
- Unit is masked means someone ran mask, or the package masks it by design. unmask first, then enable.
- systemctl status truncates long lines and pages its output. Add --no-pager -l when you want to copy from it or pipe it.
- systemctl: command not found means no systemd: most Docker containers, macOS, Alpine, and WSL without systemd=true in /etc/wsl.conf. Inside a container, run the process directly and let the container's restart policy handle failures; the [docker commands](https://sshworkbench.com/cheatsheets/docker) sheet covers that side.
- ExecStart needs an absolute path and does not understand shell syntax. ExecStart=cd /app && ./run fails; use WorkingDirectory=/app and ExecStart=/app/run, or call /bin/sh -c explicitly.

## systemctl FAQ

### What is the difference between systemctl start and systemctl enable?

start runs the service now and does nothing about the next boot. enable does the opposite: it creates the symlink under /etc/systemd/system that makes the service start at boot, but does not start it now. A freshly installed service that you only enabled is still stopped until you start it or reboot, and a service you only started is gone after a reboot. systemctl enable --now nginx does both in one step, and disable --now stops it and removes it from boot. Check either state with systemctl is-active nginx and systemctl is-enabled nginx.

### How do I list all running services with systemctl?

systemctl list-units --type=service --state=running shows only services that are currently running, one per line with their description. Drop --state=running to include loaded services that are inactive or failed, add --all to include ones that never loaded, and use --state=failed (or the shortcut systemctl --failed) for the ones that crashed. list-units shows what systemd has in memory; list-unit-files --type=service shows every installed service file and whether it is enabled, disabled, static or masked, which is the list to read when you want to know what will start at boot. Add --no-pager when you are piping into grep.

### Why does systemctl say command not found?

The machine is not running systemd. That is the case inside most Docker containers, which run a single process rather than an init system, so start the app directly or use the container's restart policy instead. It is also true on macOS, which uses launchctl, on Alpine and Devuan, which use OpenRC and sysvinit, on WSL 1 and on WSL 2 unless systemd=true is set in /etc/wsl.conf, and on very old CentOS 6 and Ubuntu 14.04 hosts, where the equivalent is service nginx start and chkconfig or update-rc.d. If systemctl exists but every call fails with Failed to connect to bus, you are in a chroot or container with systemd installed but not running as PID 1.

### What does systemctl daemon-reload do?

It makes systemd re-read every unit file on disk, re-run the unit generators, and rebuild its dependency graph in memory. It starts, stops and restarts nothing, so it is safe to run on a busy production host, and a service that is already running keeps the settings it started with until you restart it. Run it after you create, edit or delete a unit file by hand; you do not need it after systemctl edit, which reloads for you, or after a package install, which does it in its own post-install script. If you skip it, systemd keeps using the cached copy and prints Warning: The unit file, source configuration file or drop-ins of nginx.service changed on disk. The related daemon-reexec is a different thing: it re-executes the systemd binary itself, which is only for after a systemd package upgrade.

### Where are systemctl service files stored?

Three directories, in falling order of precedence: /run/systemd/system for transient units, /etc/systemd/system for yours and anything you overrode, and /usr/lib/systemd/system for the ones packages ship (/lib/systemd/system on Debian and Ubuntu is the same directory through a symlink). A file in /etc with the same name completely replaces the packaged one, which is why local edits belong there and never in /usr/lib. Drop-in overrides sit in a nginx.service.d directory next to the unit and are merged on top rather than replacing it. User units live in ~/.config/systemd/user. To find which file a running unit actually came from, run systemctl show nginx -p FragmentPath,DropInPaths, or systemctl cat nginx to print the contents of all of them in merge order.

---
Source: https://sshworkbench.com/cheatsheets/systemctl
