# DNF Commands

dnf is the package manager on RHEL, Fedora, CentOS Stream, Rocky, and Alma, and on every current release yum is a symlink to it: same program, same options. These dnf commands cover installing, upgrading, searching, transaction history, groups, repositories, and the things that changed in dnf5, and every one of them works if you type yum instead.

Last updated September 11, 2026

On this page

- [Install and Remove](#install-and-remove)
- [Update and Upgrade](#update-and-upgrade)
- [Search, Info and provides](#search-info-and-provides)
- [Missing Commands](#missing-commands)
- [List Packages](#list-packages)
- [History and Undo](#history-and-undo)
- [Common Options](#common-options)
- [Groups](#groups)
- [Repositories](#repositories)
- [Plugins](#plugins)
- [Modules](#modules)
- [Version Lock](#version-lock)
- [Cache and Clean](#cache-and-clean)
- [dnf5 Changes](#dnf5-changes)
- [dnf, apt and pacman](#dnf-apt-and-pacman)
- [Gotchas](#gotchas)

## Install and Remove

Every command on this page also works with yum in place of dnf; on current systems they are the same program.

| Command | What it does |
|----|----|
| sudo dnf install nginx | Install a package and its dependencies |
| sudo dnf install ./package.rpm | Install a local RPM with dependency resolution |
| sudo dnf install -y nginx | Assume yes to the confirmation prompt (scripts) |
| sudo dnf reinstall nginx | Reinstall the current version |
| sudo dnf remove nginx | Remove a package, and by default the dependencies it pulled in |
| sudo dnf autoremove | Remove leftover dependencies nothing needs |
| sudo dnf swap ffmpeg-free ffmpeg | Replace one package with another in a single transaction |
| sudo dnf downgrade nginx | Step back to the previous version the repos still carry |
| sudo dnf remove --oldinstallonly | Drop the old kernels, keep the newest ones |
| dnf download nginx | Download the .rpm only, no install |
| sudo dnf install --downloadonly nginx | Fetch into the cache now, install later |

localinstall and groupinstall are dead names. dnf install ./file.rpm and dnf group install have replaced them, and dnf5 removed the old spellings outright.

## Update and Upgrade

dnf check-update looks, dnf upgrade acts. There is no separate refresh step like apt update; dnf refreshes metadata by itself when the cache expires.

[TABLE]

## Search, Info and provides

dnf provides is the feature worth memorizing: it tells you which package owns a file or ships a command, even for packages you have not installed.

| Command | What it does |
|----|----|
| dnf search nginx | Search package names and summaries |
| dnf info nginx | Version, repo, size, description |
| dnf provides '\*/htpasswd' | Which package ships a command, wherever it lives |
| dnf provides /etc/nginx/nginx.conf | Which package owns a file |
| dnf whatprovides '\*/dig' | Same command under its other name |
| rpm -qf /usr/bin/ssh | Which installed package owns a file already on disk |
| dnf repoquery -l nginx | List the files a package installs |
| dnf repoquery --whatrequires nginx | What depends on a package |

## Missing Commands

Minimal RHEL installs and container images leave out tools people assume are always there. These are the ones dnf provides gets asked about most.

[TABLE]

## List Packages

| Command | What it does |
|----|----|
| dnf list installed | Every installed package |
| dnf list installed 'nginx\*' | Check whether something is installed |
| dnf list available 'php\*' | What the enabled repos offer |
| dnf list --upgrades | Just the packages with a newer version waiting |
| dnf repoquery --userinstalled | Packages you asked for, not dependencies |
| rpm -qa \| grep nginx | The classic rpm listing still works |

## History and Undo

Every transaction gets an ID you can inspect and reverse. This is the thing apt and pacman cannot do.

| Command                      | What it does                               |
|------------------------------|--------------------------------------------|
| dnf history                  | Recent transactions with their IDs         |
| dnf history info 42          | Exactly what transaction 42 changed        |
| dnf history list nginx       | Every transaction that touched one package |
| sudo dnf history undo 42     | Reverse that one transaction               |
| sudo dnf history undo last   | Reverse the most recent one                |
| sudo dnf history rollback 42 | Undo every transaction after 42            |

## Common Options

These work on any subcommand.

[TABLE]

A permanent proxy belongs in /etc/dnf/dnf.conf instead:

```
[main]
proxy=http://proxy.example.com:3128
proxy_username=user
proxy_password=secret
```

Copy

## Groups

[TABLE]

## Repositories

| Command | What it does |
|----|----|
| dnf repolist | Enabled repositories |
| dnf repolist --all | Including disabled ones |
| sudo dnf config-manager --set-enabled crb | Enable a repo (CRB/PowerTools carries build dependencies on RHEL clones) |
| sudo dnf config-manager --set-disabled reponame | Disable one |
| sudo dnf config-manager --add-repo https://example.com/example.repo | Add a repo from a .repo file URL |
| sudo dnf install epel-release | EPEL on Rocky, Alma, and CentOS Stream: the big pool of extra packages |

config-manager comes from dnf-plugins-core, and its syntax changed in dnf5: see below. On RHEL itself, enable the CodeReady Builder repo through subscription-manager first, then install the epel-release RPM from the Fedora project.

## Plugins

dnf-plugins-core ships the subcommands most people assume are built in. When one is missing, install the package that provides it rather than hunting for the name.

| Command | What it does |
|----|----|
| sudo dnf install dnf-plugins-core | config-manager, copr, download, reposync, builddep, needs-restarting |
| sudo dnf install 'dnf-command(versionlock)' | Install whatever package provides a missing subcommand |
| sudo dnf copr enable owner/project | Enable a Fedora COPR repo |
| dnf download --resolve nginx | Download an RPM plus the dependencies you are missing |
| sudo dnf builddep nginx | Install the build dependencies of a package or .spec file |
| dnf reposync --repoid=baseos --download-metadata -p /srv/mirror | Mirror a repo to disk |
| dnf repoclosure --repo=epel | Find packages whose dependencies no longer resolve |

On dnf5 these live in dnf5-plugins, which is why a fresh Fedora 41+ install answers No such command: download.

## Modules

RHEL 8 and 9 ship some packages (nodejs, postgresql, php) as module streams with selectable major versions. Fedora and RHEL 10 dropped the mechanism, and dnf5 has no module command at all.

| Command                           | What it does                           |
|-----------------------------------|----------------------------------------|
| dnf module list nodejs            | Available streams and which is enabled |
| sudo dnf module enable nodejs:20  | Pick a stream                          |
| sudo dnf module install nodejs:20 | Enable and install in one go           |
| sudo dnf module reset nodejs      | Back to the default stream             |

## Version Lock

Needs the plugin: sudo dnf install python3-dnf-plugin-versionlock on dnf4, sudo dnf install dnf5-plugin-versionlock on dnf5.

| Command | What it does |
|----|----|
| sudo dnf versionlock add nginx | Hold the installed version through upgrades |
| dnf versionlock list | Locked packages |
| sudo dnf versionlock delete nginx | Release one |
| sudo dnf versionlock clear | Release everything |

## Cache and Clean

| Command                 | What it does                                   |
|-------------------------|------------------------------------------------|
| sudo dnf clean all      | Drop cached metadata and downloaded packages   |
| sudo dnf clean metadata | Drop just the repo metadata, keep the packages |
| sudo dnf makecache      | Rebuild the metadata cache now                 |

clean all frees space under /var/cache/dnf, or /var/cache/libdnf5 on dnf5, and forces a fresh download next run. Installed packages are untouched. Reach for it when metadata is corrupt, after changing repositories, or when a mirror is serving stale data.

## dnf5 Changes

Fedora 41 and later ship dnf5 as /usr/bin/dnf. It is mostly compatible, and these are the places it is not.

[TABLE]

## dnf, apt and pacman

The same tasks on Debian and Ubuntu are in the [apt cheat sheet](https://sshworkbench.com/cheatsheets/apt), and on Arch in the [pacman cheat sheet](https://sshworkbench.com/cheatsheets/pacman).

| Task | dnf | apt | pacman |
|----|----|----|----|
| Refresh and upgrade | dnf upgrade | apt update && apt upgrade | pacman -Syu |
| Install | dnf install x | apt install x | pacman -S x |
| Remove with dependencies | dnf remove x | apt remove x && apt autoremove | pacman -Rs x |
| Remove config files too | no equivalent | apt purge x | pacman -Rns x |
| Search | dnf search x | apt search x | pacman -Ss x |
| Who owns a file | dnf provides /path | dpkg -S /path | pacman -Qo /path |
| List installed | dnf list installed | apt list --installed | pacman -Q |
| Undo a transaction | dnf history undo \<id\> | no equivalent | no equivalent |

## Gotchas

- dnf remove
  also removes the dependencies that came with the package (
  clean_requirements_on_remove
  defaults to on), where apt needs a separate
  autoremove
  . Check the transaction summary before confirming.
- There is no
  dnf purge
  . Removing a package leaves your edited config files behind as
  .rpmsave
  ; find them with
  find /etc -name '\*.rpmsave'
  .
- dnf history undo
  fails once the old package versions have left the repositories, which happens fast on Fedora. Undo soon or not at all.
- check-update
  's exit code 100 is a feature, not an error: scripts should treat 0 as "nothing to do", 100 as "updates available", 1 as a real failure.
- Kernel updates install side by side rather than replacing, so
  /boot
  can fill up; dnf keeps the newest three by default (
  installonly_limit
  in
  /etc/dnf/dnf.conf
  ).

### Patch every server from one place

SSH Workbench shows pending updates across all your servers at once and runs them over plain SSH, so a security patch is a click instead of a loop over hostnames.

[Try free for 7 days](https://sshworkbench.com/#install)

## DNF & YUM FAQ

### What is the difference between dnf and yum?

None, on anything still supported. DNF is Dandified YUM, a rewrite of yum on the libsolv dependency solver, and since RHEL 8 and Fedora 22 /usr/bin/yum has been a symlink to dnf: same code, same options, same output. Typing yum out of habit is harmless and old yum scripts keep running. The real yum survives only on RHEL and CentOS 7 and Amazon Linux 2, all past end of life. Fedora 41 and later ship dnf5, a second rewrite in C++, which is where the differences actually live.

### Why do I get dnf: command not found?

Usually because the machine is not RHEL-family: Debian, Ubuntu, and Raspberry Pi OS use apt, Arch uses pacman, Alpine uses apk. On RHEL and CentOS 7 and on Amazon Linux 2 the command is yum, since dnf only became the default in RHEL 8; Amazon Linux 2023 has dnf. Minimal container images often ship microdnf instead, the same package manager with fewer features, and it is dnf5 under the hood on recent UBI images. If dnf runs for root but sudo dnf says command not found, /usr/bin is missing from secure_path in /etc/sudoers.

### What is the dnf command to update all packages?

sudo dnf upgrade. dnf update is the same command under an older name, not a separate step, and there is no equivalent of apt update because dnf refreshes repository metadata itself once the cache expires; --refresh forces it early. check-update only reports, exiting 100 when updates exist, which is the exit code scripts should test for. dnf distro-sync is the heavier version: it moves every installed package to whatever the repos carry now, downgrading where needed, which is how you recover after adding or dropping a third-party repo.

### How do I find which package provides a command?

dnf provides '\*/dig' searches every enabled repo, installed or not, for a package shipping a file called dig in any directory; dnf whatprovides is the same command. Quote the pattern so the shell leaves it alone. A full path works too: dnf provides /etc/nginx/nginx.conf. The reverse lookups are in repoquery: dnf repoquery -l \<pkg\> lists what a package ships and dnf repoquery --whatrequires \<pkg\> shows what breaks if you remove it. For a file already on disk, rpm -qf /path answers instantly without touching the network.

### How do I undo a dnf transaction?

Find the ID with dnf history, check it with dnf history info \<id\>, then sudo dnf history undo \<id\> reverses exactly that transaction: installs removed, removals reinstalled, upgrades downgraded. dnf history undo last takes the most recent one, and dnf history rollback \<id\> unwinds everything after that point instead. Undo needs the old versions to still exist in the repos, so it gets less reliable with age, fast on Fedora. Neither apt nor pacman has anything like it.

---
Källa: https://sshworkbench.com/cheatsheets/dnf-yum
