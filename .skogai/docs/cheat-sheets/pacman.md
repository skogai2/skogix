# pacman Commands

pacman is the package manager on Arch Linux and its derivatives: Manjaro, EndeavourOS, CachyOS, and the MSYS2 environment on Windows. This pacman commands cheat sheet covers the flag combinations that do the daily work, from -Syu to orphan cleanup and downgrades, plus the errors and the traps that break Arch systems.

Last updated September 11, 2026

On this page

- [Update the System](#update-the-system)
- [Install Packages](#install-packages)
- [Remove Packages](#remove-packages)
- [Search Packages](#search-packages)
- [Package Info](#package-info)
- [List Installed Packages](#list-installed-packages)
- [Clean the Cache](#clean-the-cache)
- [Downgrade a Package](#downgrade-a-package)
- [Force and Overwrite](#force-and-overwrite)
- [Skip Prompts](#skip-prompts)
- [Keyring](#keyring)
- [Mirrors](#mirrors)
- [pacman.conf](#pacmanconf)
- [The AUR](#the-aur)
- [yay and paru](#yay-and-paru)
- [History and Logs](#history-and-logs)
- [Flags Explained](#flags-explained)
- [Common pacman Errors](#common-pacman-errors)
- [pacman, apt and dnf](#pacman-apt-and-dnf)
- [Gotchas](#gotchas)

## Update the System

pacman -Syu syncs the package databases and upgrades everything in one transaction. Never run pacman -Sy on its own and install something afterwards: new packages against old databases is a partial upgrade, and partial upgrades break Arch systems.

| Command | What it does |
|----|----|
| sudo pacman -Syu | Refresh the databases and upgrade every package |
| sudo pacman -Syu nginx | Upgrade the system and install a package in the same safe transaction |
| sudo pacman -Su | Upgrade using the databases you already have, without refreshing |
| sudo pacman -Syyu | Force-redownload the databases too, after changing mirrors |
| checkupdates | List pending updates without touching the databases (pacman-contrib) |

## Install Packages

[TABLE]

## Remove Packages

| Command | What it does |
|----|----|
| sudo pacman -R nginx | Remove just the package |
| sudo pacman -Rs nginx | Remove it and its now-unneeded dependencies |
| sudo pacman -Rns nginx | Also skip the .pacsave config backups; the usual full removal |
| sudo pacman -Rc nginx | Cascade: remove it and everything that depends on it (read the list first) |
| pacman -Qdt | List orphaned dependencies |

Remove every orphan in one go:

```
pacman -Qdtq | sudo pacman -Rns -
```

Copy

## Search Packages

[TABLE]

## Package Info

| Command | What it does |
|----|----|
| pacman -Si nginx | Repo info: version, size, dependencies |
| pacman -Qi nginx | Installed info, including install date, reason, and what requires it |
| pacman -Ql nginx | Files the package installed |
| pactree nginx | Dependency tree (pacman-contrib) |

## List Installed Packages

| Command | What it does |
|----|----|
| pacman -Q | Every installed package with its version |
| pacman -Qe | Explicitly installed packages, what you actually asked for |
| pacman -Qm | Foreign packages: AUR and local installs |
| pacman -Qnq | Native packages only, names only |
| sudo pacman -D --asdeps nginx | Re-mark it as a dependency so orphan cleanup can take it later |
| pacman -Q \| wc -l | Count them |

## Clean the Cache

Every downloaded package stays in /var/cache/pacman/pkg until you clean it.

| Command | What it does |
|----|----|
| sudo pacman -Sc | Delete cached packages that are no longer installed |
| sudo pacman -Scc | Empty the whole cache; you lose downgrade-from-cache |
| paccache -r | Keep the newest 3 versions of each package, delete the rest (pacman-contrib, the better habit) |
| paccache -rk1 | Keep only the newest version |
| sudo pacman -U /var/cache/pacman/pkg/pkg-1.0-1-x86_64.pkg.tar.zst | Downgrade by reinstalling an older version straight from the cache |

## Downgrade a Package

pacman has no rollback. You go back by installing an older package file, from your cache or from the Arch Linux Archive.

[TABLE]

The next pacman -Syu pulls the new version straight back. Hold it with IgnorePkg = nginx in /etc/pacman.conf until the upstream bug is fixed, and treat that hold as temporary: a pinned package whose dependencies keep moving is a partial upgrade waiting to happen.

## Force and Overwrite

There is no --force any more; it was split into narrower flags. Use them when you know exactly which file or dependency is in the way.

| Command | What it does |
|----|----|
| sudo pacman -S nginx | Reinstall a package that is already installed, restoring deleted files |
| sudo pacman -S --overwrite '/usr/lib/foo/\*' nginx | Install over untracked files, for the exact paths the error named |
| sudo pacman -Rdd nginx | Remove without dependency checks, leaving whatever needed it broken |
| sudo pacman -Syu --overwrite '\*' | Last resort; ignores every file conflict on the system |

Reinstall every native package, after a half-finished upgrade or a mangled /usr:

```
sudo pacman -S $(pacman -Qnq)
```

Copy

## Skip Prompts

| Command | What it does |
|----|----|
| sudo pacman -Syu --noconfirm | Answer yes to every prompt, for scripts and provisioning |
| sudo pacman -S --noconfirm --needed git base-devel | Install unattended, skipping what is already current |
| sudo pacman -Rns --noconfirm nginx | Remove without the confirmation |
| sudo pacman -Syu --noprogressbar | Quieter output for logs and CI |

--noconfirm takes the default answer to every question, and on a replace-this-with-that or pick-a-provider prompt the default is not always the one you want. Keep it for containers and scripts, not for your daily upgrade.

## Keyring

| Command | What it does |
|----|----|
| sudo pacman -S archlinux-keyring | Update the signing keys before a big upgrade on a stale system |
| sudo pacman-key --init | Create the keyring on a fresh install |
| sudo pacman-key --populate archlinux | Load the Arch master keys |
| sudo pacman-key --refresh-keys | Pull key updates from a keyserver (slow, and rarely the actual fix) |

When the keyring itself is broken and signatures still fail, rebuild it from scratch:

```
sudo rm -r /etc/pacman.d/gnupg
sudo pacman-key --init
sudo pacman-key --populate archlinux
sudo pacman -Sy archlinux-keyring
```

Copy

## Mirrors

Mirrors live in /etc/pacman.d/mirrorlist and are tried top to bottom. reflector (sudo pacman -S reflector) ranks and rewrites the list; after changing mirrors, run pacman -Syyu.

```
sudo reflector --latest 20 --protocol https --sort rate --save /etc/pacman.d/mirrorlist
```

Copy

## pacman.conf

/etc/pacman.conf holds the repositories and pacman's behaviour.

[TABLE]

Enabling multilib means uncommenting both lines, then refreshing the databases:

```
[multilib]
Include = /etc/pacman.d/mirrorlist
```

Copy

A third-party repo is the same shape, appended at the end of the file, and the lower it sits the lower its priority:

```
[myrepo]
SigLevel = Optional TrustAll
Server = https://example.com/repo/$arch
```

Copy

Run sudo pacman -Syu after either change. Custom post-install actions go in /etc/pacman.d/hooks/\*.hook rather than in this file.

## The AUR

pacman itself cannot install from the AUR: the AUR ships build recipes, not packages. A helper builds them and wraps the upgrade.

| Command        | What it does                                           |
|----------------|--------------------------------------------------------|
| yay -S package | Build and install an AUR package (paru works the same) |
| yay            | Full system upgrade including AUR packages             |
| pacman -Qm     | The AUR packages currently installed                   |

Building by hand, without a helper:

```
git clone https://aur.archlinux.org/package.git
cd package && makepkg -si
```

Copy

## yay and paru

Helpers pass repo packages straight to pacman and build AUR ones with makepkg. Install one with the same manual build, since the helper is itself an AUR package:

```
sudo pacman -S --needed git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si
```

Copy

[TABLE]

Run helpers as your normal user, never with sudo: they call sudo themselves at the install step, and building as root breaks file ownership. Everything in the AUR is a user submission with no review, so read the PKGBUILD for anything with few votes.

## History and Logs

pacman logs every transaction to /var/log/pacman.log. There is no history undo like DNF has; rolling back means reinstalling the older package file.

| Command | What it does |
|----|----|
| tail -50 /var/log/pacman.log | What pacman did last |
| grep -i installed /var/log/pacman.log | Every install, with dates |
| grep -i upgraded /var/log/pacman.log \| tail -40 | The last batch of upgrades, to find what broke something |
| paclog --action=upgraded | The same, filtered properly (pacman-contrib) |
| expac --timefmt='%F' '%l %n' \| sort | Installed packages ordered by install date |

## Flags Explained

pacman flags compose: one capital operation letter plus lowercase modifiers.

[TABLE]

## Common pacman Errors

[TABLE]

## pacman, apt and dnf

The same tasks on Debian and Ubuntu are in the [apt cheat sheet](https://sshworkbench.com/cheatsheets/apt), and on RHEL and Fedora in the [DNF cheat sheet](https://sshworkbench.com/cheatsheets/dnf-yum).

| Task | pacman | apt | dnf |
|----|----|----|----|
| Refresh and upgrade | pacman -Syu | apt update && apt upgrade | dnf upgrade |
| Install | pacman -S x | apt install x | dnf install x |
| Remove with dependencies | pacman -Rs x | apt remove x && apt autoremove | dnf remove x |
| Search | pacman -Ss x | apt search x | dnf search x |
| Who owns a file | pacman -Qo /path | dpkg -S /path | dnf provides /path |
| List installed | pacman -Q | apt list --installed | dnf list installed |
| Clean cache | pacman -Sc | apt clean | dnf clean all |

## Gotchas

- Partial upgrades break Arch. Either
  pacman -Syu
  or nothing; never
  -Sy
  followed by an install later, and that includes an AUR helper refreshing the databases for you.
- When you have edited a config file, pacman writes the new default next to it as
  file.pacnew
  instead of overwriting. Merge them after upgrades with
  pacdiff
  (pacman-contrib), or at least look for them:
  find /etc -name '\*.pacnew'
  .
- Signature errors after months without updates mean a stale keyring, not corrupt mirrors:
  sudo pacman -Sy archlinux-keyring && sudo pacman -Su
  .
- Downloads crawling is nearly always the mirrorlist, not pacman. Re-rank with reflector and raise
  ParallelDownloads
  in
  /etc/pacman.conf
  .
- Queries need no root.
  -Q
  ,
  -Ss
  ,
  -Si
  , and
  -Qo
  all run as a normal user; only
  -S
  ,
  -R
  , and
  -U
  need sudo.
- Manjaro holds Arch packages back about two weeks, so AUR builds that assume Arch-current libraries can fail there on version skew alone.
- MSYS2 on Windows uses pacman with its own repositories: the flags on this page work, the Arch repos and the AUR do not.

### Patch every server from one place

SSH Workbench shows pending updates across all your servers at once and runs them over plain SSH, so a security patch is a click instead of a loop over hostnames.

[Try free for 7 days](https://sshworkbench.com/#install)

## pacman FAQ

### How do I update Arch Linux with pacman?

sudo pacman -Syu, and that is the whole procedure. There is no separate update-then-upgrade step like apt: -S sync, -y refresh the databases, -u upgrade, all in one transaction. Two habits make it boring instead of exciting. Run checkupdates from pacman-contrib first to see what is coming without touching the databases, and skim archlinux.org for a manual intervention notice before a big upgrade after weeks away. Afterwards, look for .pacnew files so your edited configs do not drift away from the new defaults.

### Is it safe to install one package without a full upgrade?

Installing with sudo pacman -S is fine on a system that is already current. What breaks Arch is running pacman -Sy, or any helper that refreshes the databases, and then installing later that day. You get a package built against today's libraries on a system that still has last month's, and the usual result is a broken glibc or a system that will not boot. There is no supported way to upgrade a single package on its own: use sudo pacman -Syu nginx, which upgrades everything and installs nginx in the same transaction.

### What does the archlinux-keyring package do?

It ships the PGP keys of the Arch packagers, and pacman checks every package against it before installing. Packagers rotate and add keys, so on a machine that has not updated in months the keyring is too old to recognise current signatures and perfectly good packages look corrupt. Update it on its own first, then the system: sudo pacman -Sy archlinux-keyring && sudo pacman -Su. A wrong system clock causes the same symptom, since keys look not yet valid or expired. Never disable SigLevel to get past it.

### Should I use pacman or yay for AUR packages?

pacman cannot install from the AUR at all. The AUR distributes PKGBUILD build recipes, not built packages, so you either clone the repo and run makepkg -si yourself or use a helper. yay and paru do the same job: fetch the PKGBUILD, build it, and hand the result to pacman, with AUR updates folded into the system upgrade. Run the helper as your normal user, never with sudo, and read the PKGBUILD before building anything with few votes. AUR packages are user submissions with no review.

### Where is the pacman config file?

/etc/pacman.conf holds the repositories and pacman's own behaviour, and /etc/pacman.d/mirrorlist holds the servers it downloads from. Drop-in hooks live in /etc/pacman.d/hooks. Upgrades never overwrite your edits: pacman writes the new default next to the file as pacman.conf.pacnew, which is why enabling multilib or ParallelDownloads sometimes looks like it silently reverted after an upgrade. Merge pacnew files with pacdiff from pacman-contrib.

---
Källa: https://sshworkbench.com/cheatsheets/pacman
