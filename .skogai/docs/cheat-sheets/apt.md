# apt Commands

apt is the package manager on Debian, Ubuntu, and their derivatives, including Raspberry Pi OS and Mint. This apt commands cheat sheet covers updating, installing, and removing packages, repositories and keys, held packages, and the errors apt update likes to throw.

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

| Command | What it does |
|---|---|
| `sudo apt install nginx` | Install a package |
| `sudo apt install -y nginx` | Install without prompting for confirmation |
| `sudo apt install nginx curl htop` | Install multiple packages at once |
| `sudo apt install ./package.deb` | Install a local `.deb` file, resolving dependencies |
| `sudo apt remove nginx` | Remove package binaries but leave configuration files |
| `sudo apt purge nginx` | Remove package completely, including configuration files |
| `sudo apt autoremove` | Remove packages that were installed as dependencies but are no longer needed |
| `sudo apt autoremove --purge` | Remove unneeded dependencies and delete their config files |
| `sudo apt reinstall nginx` | Reinstall an existing package |

## Common Options

The shape of every command is apt [options] <subcommand> [package...], and the options below work on most subcommands.

| Option | Meaning |
|---|---|
| `-y`, `--yes` | Assume "yes" to all prompts and run non-interactively |
| `-s`, `--simulate`, `--dry-run` | Perform a simulation without making any actual system changes |
| `-q`, `-qq` | Quiet mode (less output; `-qq` produces no output except on error) |
| `-o Option=Value` | Set an APT configuration option on the fly |
| `--no-install-recommends` | Do not treat recommended packages as dependencies to install |
| `--only-upgrade` | Upgrade specified package only if it is already installed |

```bash
DEBIAN_FRONTEND=noninteractive apt-get -y install postfix
```

## Search and Show

| Command | What it does |
|---|---|
| `apt search nginx` | Search package names and descriptions for a term |
| `apt show nginx` | Display detailed package info (version, dependencies, maintainer, size) |
| `apt-cache search ^nginx$` | Search with regular expressions |
| `apt-cache policy nginx` | Show installed vs available versions and repository priorities |
| `apt-cache madison nginx` | Show available versions and source repositories in tabular format |

## Dependencies

| Command | What it does |
|---|---|
| `apt-cache depends nginx` | List all direct dependencies and recommendations for a package |
| `apt-cache rdepends nginx` | Reverse dependencies: list what packages depend on `nginx` |
| `apt-cache rdepends --installed nginx` | Reverse dependencies among currently installed packages |
| `apt-mark showmanual` | List packages installed explicitly (not pulled in as dependencies) |
| `apt-mark showauto` | List packages marked as automatically installed dependencies |

## List Installed Packages

| Command | What it does |
|----|----|
| apt list --installed | Every installed package |
| apt list --installed 2>/dev/null \| grep nginx | Check whether a package is installed |
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

| Command | What it does |
|---|---|
| `sudo apt install nginx=1.18.0-0ubuntu1` | Install or downgrade to a specific package version |
| `apt download nginx` | Download `.deb` file to current directory without installing |
| `apt-get source nginx` | Download source code package for `nginx` |

## Repositories and Keys

Current releases (Debian 12+, Ubuntu 24.04+) use deb822 .sources files under /etc/apt/sources.list.d/ instead of one-line deb entries:

```bash
# /etc/apt/sources.list.d/example.sources
Types: deb
URIs: https://packages.example.com/apt
Suites: stable
Components: main
Signed-By: /etc/apt/keyrings/example.gpg
```

apt-key is deprecated and gone from the newest releases. Keys go into /etc/apt/keyrings/ and are referenced by Signed-By:

```bash
curl -fsSL https://packages.example.com/key.asc | sudo gpg --dearmor -o /etc/apt/keyrings/example.gpg
```

| Command / Path | What it does |
|---|---|
| `/etc/apt/sources.list.d/` | Directory for repository definition files (`.sources` or `.list`) |
| `/etc/apt/keyrings/` | Standard directory for repository GPG public keys |
| `sudo add-apt-repository ppa:user/repo` | Add an Ubuntu PPA repository (Ubuntu only) |
| `sudo add-apt-repository --remove ppa:user/repo` | Remove a previously added PPA |

## Clean Up and Fix Broken

| Command | What it does |
|---|---|
| `sudo apt --fix-broken install` | Fix broken dependencies and finish incomplete installs (`-f`) |
| `sudo dpkg --configure -a` | Configure any unpacked but unconfigured packages |
| `sudo apt clean` | Clear out the entire local cache of downloaded `.deb` files |
| `sudo apt autoclean` | Remove downloaded `.deb` packages that can no longer be downloaded |

## Proxy and Offline

http_proxy in your shell does not survive sudo unless you pass sudo -E, which is why a proxy that works for curl often does not work for apt. Set it in apt's own config instead:

```bash
# /etc/apt/apt.conf.d/95proxy
Acquire::http::Proxy "http://proxy:3128";
Acquire::https::Proxy "http://proxy:3128";
```

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
| zgrep "Install:" /var/log/apt/history.log* | Search the rotated history too |
| less /var/log/apt/term.log | Full terminal output of past apt runs |
| grep " install " /var/log/dpkg.log | dpkg's own log, one line per package action |

## Common apt update Errors

| Error Message | Cause | Solution |
|---|---|---|
| `Could not get lock /var/lib/dpkg/lock-frontend` | Another process is holding the apt/dpkg lock | Wait for it to finish or inspect with `ps aux \| grep apt` |
| `NO_PUBKEY <KEY_ID>` | Repository public key is missing or expired | Import key into `/etc/apt/keyrings/` or fetch via `gpg` |
| `The repository ... does not have a Release file` | Old/unsupported distro release or dead PPA | Remove offending file from `/etc/apt/sources.list.d/` |
| `Failed to fetch ... 404 Not Found` | Package lists point to non-existent URL | Update repository sources URL or move to archive |
| `Certificate verification failed` | System clock out of sync or missing CA certs | Run `sudo apt install --reinstall ca-certificates` and sync time |

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

- Security patches can install themselves: sudo apt install unattended-upgrades, then sudo dpkg-reconfigure -plow unattended-upgrades. It is also the usual holder of the dpkg lock right after boot.
- In scripts and Dockerfiles, use apt-get -y with DEBIAN_FRONTEND=noninteractive so a config prompt cannot hang the run.
- apt upgrade never removes packages, which means it can also silently hold some back; when it reports packages "kept back", apt full-upgrade will resolve them.
- Removing a package does not stop its service first in every case; check with systemctl status (see the [systemctl cheat sheet](https://sshworkbench.com/cheatsheets/systemctl)).

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
Source: https://sshworkbench.com/cheatsheets/apt
