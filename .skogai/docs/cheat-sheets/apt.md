# apt Commands

apt is the package manager on Debian, Ubuntu, and their derivatives, including Raspberry Pi OS and Mint. This apt commands cheat sheet covers updating, installing, and removing packages, repositories and keys, held packages, and the errors apt update likes to throw.

Last updated September 11, 2026

On this page

- [Update and Upgrade](#update-and-upgrade)
- [Install and Remove](#install-and-remove)
- [Common Options](#common-options)
- [Search and Show](#search-and-show)
- [Dependencies](#dependencies)
- [List Installed Packages](#list-installed-packages)
- [Hold Packages](#hold-packages)
- [Downgrade and Download](#downgrade-and-download)
- [Repositories and Keys](#repositories-and-keys)
- [Clean Up and Fix Broken](#clean-up-and-fix-broken)
- [Proxy and Offline](#proxy-and-offline)
- [apt vs apt-get](#apt-vs-apt-get)
- [History and Logs](#history-and-logs)
- [Common apt update Errors](#common-apt-update-errors)
- [apt, dnf and pacman](#apt-dnf-and-pacman)
- [Tips](#tips)

## Update and Upgrade

apt update refreshes the package lists and installs nothing; apt upgrade installs the new versions. Run them in that order.

| Command | What it does |
|----|----|
| sudo apt update | Refresh the package lists from every repository |
| sudo apt upgrade | Upgrade everything that can be upgraded without removing packages |
| sudo apt full-upgrade | Upgrade and allow removals when the upgrade needs them |
| sudo apt-get dist-upgrade | Old name for full-upgrade, same behaviour |
| sudo apt update && sudo apt upgrade -y | The usual pair in one line |
| apt list --upgradable | See what an upgrade would touch, after an update |
| sudo apt install --only-upgrade nginx | Upgrade a single package and nothing else |
| sudo apt upgrade -s | Dry run: print the plan without doing any of it |

## Install and Remove

[TABLE]

## Common Options

The shape of every command is apt \[options\] \<subcommand\> \[package...\], and the options below work on most subcommands.

[TABLE]

```
DEBIAN_FRONTEND=noninteractive apt-get -y install postfix
```

Copy

## Search and Show

[TABLE]

## Dependencies

[TABLE]

## List Installed Packages

| Command | What it does |
|----|----|
| apt list --installed | Every installed package |
| apt list --installed 2\>/dev/null \| grep nginx | Check whether a package is installed |
| dpkg -s nginx | Status and version of one package; non-zero exit if absent |
| dpkg -l | The classic full listing with status flags |
| dpkg -L nginx | Files a package installed |
| apt-mark showmanual | Packages you installed on purpose, not as dependencies |

## Hold Packages

A held package keeps its current version through every upgrade until you release it.

| Command                    | What it does              |
|----------------------------|---------------------------|
| sudo apt-mark hold nginx   | Pin the installed version |
| sudo apt-mark unhold nginx | Release it                |
| apt-mark showhold          | List held packages        |

## Downgrade and Download

Downgrading only works while the repository still carries the older version; apt list -a nginx shows what is left. Hold the package afterwards or the next upgrade puts the new version straight back.

[TABLE]

## Repositories and Keys

Current releases (Debian 12+, Ubuntu 24.04+) use deb822 .sources files under /etc/apt/sources.list.d/ instead of one-line deb entries:

```
# /etc/apt/sources.list.d/example.sources
Types: deb
URIs: https://packages.example.com/apt
Suites: stable
Components: main
Signed-By: /etc/apt/keyrings/example.gpg
```

Copy

apt-key is deprecated and gone from the newest releases. Keys go into /etc/apt/keyrings/ and are referenced by Signed-By:

```
curl -fsSL https://packages.example.com/key.asc | sudo gpg --dearmor -o /etc/apt/keyrings/example.gpg
```

Copy

[TABLE]

## Clean Up and Fix Broken

[TABLE]

## Proxy and Offline

http_proxy in your shell does not survive sudo unless you pass sudo -E, which is why a proxy that works for curl often does not work for apt. Set it in apt's own config instead:

```
# /etc/apt/apt.conf.d/95proxy
Acquire::http::Proxy "http://proxy:3128";
Acquire::https::Proxy "http://proxy:3128";
```

Copy

| Command | What it does |
|----|----|
| sudo apt -o Acquire::http::Proxy="http://proxy:3128" update | Use a proxy for one run, without touching the config |
| sudo apt -o Acquire::http::Proxy=DIRECT update | Bypass a configured proxy for one run |
| apt-get --print-uris -qq install nginx | Print the download URLs so you can fetch them on another machine |
| sudo apt install --no-download nginx | Install from the local cache only, no network |

## apt vs apt-get

apt is the human-facing command: it merges the most used parts of apt-get and apt-cache and adds a progress bar. Its output can change between releases, so scripts should stick to apt-get and apt-cache, whose interfaces are stable.

| apt                  | Script equivalent      |
|----------------------|------------------------|
| apt update           | apt-get update         |
| apt install nginx    | apt-get install nginx  |
| apt full-upgrade     | apt-get dist-upgrade   |
| apt search nginx     | apt-cache search nginx |
| apt show nginx       | apt-cache show nginx   |
| apt list --installed | dpkg -l                |

## History and Logs

apt has no history subcommand the way dnf does. The record lives in /var/log/apt/.

| Command | What it does |
|----|----|
| less /var/log/apt/history.log | What was installed, upgraded, or removed, and when |
| zgrep "Install:" /var/log/apt/history.log\* | Search the rotated history too |
| less /var/log/apt/term.log | Full terminal output of past apt runs |
| grep " install " /var/log/dpkg.log | dpkg's own log, one line per package action |

## Common apt update Errors

[TABLE]

## apt, dnf and pacman

If the shell answers apt: command not found, the machine is almost certainly not Debian-based; cat /etc/os-release says which one it is. The same tasks on RHEL and Fedora are in the [DNF cheat sheet](https://sshworkbench.com/cheatsheets/dnf-yum), and on Arch in the [pacman cheat sheet](https://sshworkbench.com/cheatsheets/pacman).

| Task | apt | dnf | pacman |
|----|----|----|----|
| Refresh and upgrade | apt update && apt upgrade | dnf upgrade | pacman -Syu |
| Install | apt install x | dnf install x | pacman -S x |
| Remove with dependencies | apt remove x && apt autoremove | dnf remove x | pacman -Rs x |
| Search | apt search x | dnf search x | pacman -Ss x |
| Who owns a file | dpkg -S /path | dnf provides /path | pacman -Qo /path |
| List installed | apt list --installed | dnf list installed | pacman -Q |
| Clean cache | apt clean | dnf clean all | pacman -Sc |

## Tips

- Security patches can install themselves:
  sudo apt install unattended-upgrades
  , then
  sudo dpkg-reconfigure -plow unattended-upgrades
  . It is also the usual holder of the dpkg lock right after boot.
- In scripts and Dockerfiles, use
  apt-get -y
  with
  DEBIAN_FRONTEND=noninteractive
  so a config prompt cannot hang the run.
- apt upgrade
  never removes packages, which means it can also silently hold some back; when it reports packages "kept back",
  apt full-upgrade
  will resolve them.
- Removing a package does not stop its service first in every case; check with
  systemctl status
  (see the [systemctl cheat sheet](https://sshworkbench.com/cheatsheets/systemctl)).

### Patch every server from one place

SSH Workbench shows pending updates across all your servers at once and runs them over plain SSH, so a security patch is a click instead of a loop over hostnames.

[Try free for 7 days](https://sshworkbench.com/#install)

## apt FAQ

### What does the apt update command do?

It downloads the current package lists from every repository in your sources and writes them to /var/lib/apt/lists. It installs and changes nothing, so it is safe to run at any time. apt upgrade is the step that installs the newer versions those lists describe, which is why the order matters: an upgrade run on stale lists installs stale versions, and on a machine that has been off for a month apt update alone can take longer than the upgrade.

### Why does the shell say 'apt: command not found'?

apt ships only on Debian and its derivatives, so the usual cause is that the machine is not one. Run cat /etc/os-release to check. On Fedora, RHEL, Rocky, and Amazon Linux the equivalent is dnf; on Arch and Manjaro it is pacman; on Alpine apk; on macOS there is no apt at all, use Homebrew. WSL follows whichever distro image you installed, not Windows.

### What is the apt-get command, and should I use it instead of apt?

apt-get is the older front end, and apt is a friendlier wrapper that merges the most used parts of apt-get and apt-cache and adds a progress bar. Both call the same library and leave you with the same packages. Use apt by hand and apt-get in scripts, Dockerfiles, and CI: apt-get keeps its options and output stable across releases, and apt prints a warning that its own interface does not.

### How do I fix broken or held-back packages?

For a broken or interrupted install, sudo apt --fix-broken install, then sudo dpkg --configure -a to finish anything left half configured; add --fix-missing when the cause was a failed download. Packages reported as 'kept back' are a different thing: they are not held. apt upgrade refuses to remove packages, so it skips those, and apt full-upgrade resolves them. On Ubuntu they can also be a phased update, which holds the new version back for a few days on purpose. Real holds only come from apt-mark hold and show in apt-mark showhold.

### What does apt stand for?

Advanced Package Tool. apt, apt-get, apt-cache, apt-mark, and apt-config are all front ends over the same library, which is why they share a cache and a configuration. dpkg sits underneath and does the actual unpacking of a single .deb; apt is the layer that knows about repositories, dependency resolution, and versions.

---
Källa: https://sshworkbench.com/cheatsheets/apt
