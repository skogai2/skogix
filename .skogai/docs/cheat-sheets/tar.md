# tar Command Examples

tar bundles files into a single archive and, with one more flag, compresses it. These tar command examples cover creating, extracting and unzipping archives, tar.gz, bz2 and xz, listing and excluding files, progress output, and the tar built into Windows 10 and 11.

Last updated September 11, 2026

On this page

- [Create an Archive](#create-an-archive)
- [Extract an Archive](#extract-an-archive)
- [Extract to a Directory](#extract-to-a-directory)
- [gzip and tar.gz](#gzip-and-targz)
- [bz2 and xz](#bz2-and-xz)
- [Zip and Unzip](#zip-and-unzip)
- [List Contents](#list-contents)
- [Exclude Files](#exclude-files)
- [Progress and Verbose](#progress-and-verbose)
- [Permissions and Overwriting](#permissions-and-overwriting)
- [Append to an Archive](#append-to-an-archive)
- [Flags Explained](#flags-explained)
- [tar on Windows 10 and 11](#tar-on-windows-10-and-11)
- [Gotchas](#gotchas)

## Create an Archive

c creates, v prints each file, f names the archive. Keep f last: the word after it is the file name.

| Command | What it does |
|----|----|
| tar -cvf archive.tar dir/ | Archive a directory, no compression |
| tar -cvf archive.tar file1.txt file2.txt | Archive specific files |
| tar -cvf archive.tar dir1 dir2 notes.txt | Mix directories and files in one archive |
| tar cvf archive.tar dir/ | Same command, classic Unix style without the hyphen |
| tar -cvf archive.tar -T filelist.txt | Archive the paths listed in a file, one per line |
| find . -name '\*.log' \| tar -cvf logs.tar -T - | Archive files another command found (see the [find cheat sheet](https://sshworkbench.com/cheatsheets/find)) |
| tar -cf archive.tar --ignore-failed-read dir/ | Keep going instead of failing on a file you cannot read |

## Extract an Archive

| Command | What it does |
|----|----|
| tar -xvf archive.tar | Extract into the current directory |
| tar -xf archive.tar | Same, without listing every file |
| tar -xvf archive.tar docs/readme.txt | Extract one file, named by its path as stored |
| tar -xvf archive.tar --wildcards '\*.conf' | Extract only files matching a pattern |
| tar -xzf archive.tar.gz | Extract a tar.gz |
| tar -xf archive.tar.gz | Also fine: extraction detects the compression on its own |
| tar -xvkf archive.tar | Keep existing files instead of overwriting them |

## Extract to a Directory

tar never creates the target directory, so make it first.

| Command | What it does |
|----|----|
| tar -xf archive.tar -C /opt/app | Extract into /opt/app instead of the current directory |
| mkdir -p /opt/app && tar -xzf app.tar.gz -C /opt/app | Create the target, then extract into it |
| tar -xzf app.tar.gz -C /opt/app --strip-components=1 | Drop the archive's top-level folder while extracting |
| tar -xzf app.tar.gz -C /opt/app --strip-components=2 | Drop two levels, for archives nested deeper |
| tar -czf site.tar.gz -C /var/www . | Archive from another directory without the path prefix |

-C works on both sides: on extract it is where files land, on create it is where tar looks for them.

## gzip and tar.gz

[TABLE]

Streaming to another machine compresses and transfers in one step, with nothing written locally:

```
tar -czf - /var/www | ssh user@backup "cat > www-$(date +%F).tar.gz"
```

Copy

For a backup you repeat, [rsync](https://sshworkbench.com/cheatsheets/rsync) is usually the better tool: it sends only what changed.

## bz2 and xz

Same verbs, different letter: j for bzip2, capital J for xz. gzip is the fastest, xz the smallest.

| Command | What it does |
|----|----|
| tar -cjf archive.tar.bz2 dir/ | Create a bzip2 archive |
| tar -xjf archive.tar.bz2 | Extract it |
| tar -cJf archive.tar.xz dir/ | Create an xz archive (capital J) |
| tar -xJf archive.tar.xz | Extract it |
| tar -xf archive.tar.xz | Extraction auto-detects the format either way |

## Zip and Unzip

On Linux, "zip a folder" almost always means make a tar.gz. Real .zip files are a different format, and only bsdtar reads them.

| Command | What it does |
|----|----|
| tar -czf folder.tar.gz folder/ | Zip a folder the tar way, one compressed file |
| tar -xzf folder.tar.gz | Unzip it again into the current directory |
| tar -xf archive.zip | Open a real .zip, but only with bsdtar (macOS, Windows) |
| unzip archive.zip | Unzip a .zip on Linux, where GNU tar cannot |
| zip -r out.zip folder/ | Make a real .zip when the other side needs one |

## List Contents

[TABLE]

## Exclude Files

Quote the patterns so the shell does not expand them first.

| Command | What it does |
|----|----|
| tar -czf site.tar.gz --exclude='\*.log' site/ | Skip files matching a pattern |
| tar -czf site.tar.gz --exclude='site/node_modules' site/ | Skip a directory, named as tar would store it |
| tar -czf site.tar.gz --exclude-vcs site/ | Skip .git, .svn, and other VCS directories |
| tar -czf site.tar.gz -X skip.txt site/ | Read exclude patterns from a file |
| tar -czf site.tar.gz --exclude='\*.log' --exclude='tmp' site/ | Repeat the flag for each pattern you want gone |

## Progress and Verbose

tar says nothing while it works unless you ask. -v names every file, which is noisy on a large archive; the alternatives below give you a pulse instead.

[TABLE]

For a real percentage and an ETA, pipe through pv and tell it the expected size:

```
tar -czf - dir/ | pv -s "$(du -sb dir/ | cut -f1)" > backup.tar.gz
```

Copy

pv is not installed by default (apt install pv, dnf install pv, brew install pv).

## Permissions and Overwriting

[TABLE]

## Append to an Archive

Appending only works on an uncompressed .tar; tar refuses to append to a .tar.gz.

| Command | What it does |
|----|----|
| tar -rvf archive.tar extra.txt | Append a file to the end of the archive |
| tar -uvf archive.tar dir/ | Append only files newer than their archived copy |
| tar -Avf archive.tar other.tar | Append another archive's contents |

To add a file to a compressed archive, decompress, append, recompress:

```
gzip -d archive.tar.gz && tar -rvf archive.tar extra.txt && gzip archive.tar
```

Copy

## Flags Explained

| Flag | Meaning |
|----|----|
| -c | Create an archive |
| -x | Extract an archive |
| -t | List contents |
| -f | The archive file; keep it last, the next word is the name |
| -v | Verbose, print each file as it is processed |
| -z | gzip compression (.tar.gz) |
| -j | bzip2 compression (.tar.bz2) |
| -J | xz compression (.tar.xz) |
| -a | Choose compression from the archive's extension (create only) |
| -C dir | Change to dir before archiving or extracting |
| -r | Append files to an existing .tar |
| -u | Append only files newer than the archived copy |
| -p | Preserve permissions on extract (the default when root) |
| -k | Keep existing files, never overwrite |
| -O | Extract to standard output instead of the disk |
| -T file | Read the list of files to archive from file |
| --strip-components=N | Drop the first N path levels on extract |
| --exclude='pattern' | Skip matching files |
| --totals | Print the bytes written when the archive is done |
| --checkpoint=.N | Print a dot every N records, as a progress sign |
| --ignore-failed-read | Do not fail the whole run on an unreadable file |
| --no-same-owner | Do not restore the stored owner when extracting as root |
| --remove-files | Delete each file after it has been archived |

## tar on Windows 10 and 11

Windows has shipped bsdtar since the April 2018 update of Windows 10, so these run in Command Prompt and PowerShell with nothing installed.

| Command | What it does |
|----|----|
| tar -xf archive.tar.gz | Extract into the current folder |
| tar -xf archive.tar.gz -C C:\output | Extract into a folder that already exists |
| tar -czf backup.tar.gz Documents | Create a tar.gz of a folder |
| tar -tf archive.tar.gz | List the contents |
| tar -xf archive.zip | bsdtar extracts .zip files too |
| tar --version | Says which tar you have; the built-in prints bsdtar |

The Linux sections above apply as-is; only the paths look different.

## Gotchas

- Flag order bites everyone once:
  f
  must be last in the cluster.
  tar -czvf out.tar.gz dir
  is right;
  tar -czfv out.tar.gz dir
  creates an archive literally named
  v
  .
- tar: Removing leading '/' from member names
  is not an error. tar stores relative paths on purpose so an extraction cannot overwrite system files at their original absolute paths.
- Archive the folder, not its contents: run
  tar -czf site.tar.gz site/
  from the parent directory. An archive of loose files scatters them all over whatever directory it is extracted in.
- Ownership depends on who extracts: root restores the original owners, a normal user gets every file as their own. Add
  -p
  to keep permissions when extracting as a normal user.
- macOS ships bsdtar too. Everyday commands match GNU tar, but
  --wildcards
  is missing there (patterns work without it) and
  --exclude
  should come before the paths, as written above.
- tar has no password option. For an encrypted archive, pipe it through gpg:
  tar -czf - dir/ \| gpg -c \> dir.tar.gz.gpg
  , and reverse it with
  gpg -d dir.tar.gz.gpg \| tar -xzf -
  .

### Stop memorizing commands

SSH Workbench puts the common server tasks behind buttons: services, Docker, files, cron, firewall. The terminal is still there when you want it.

[Try free for 7 days](https://sshworkbench.com/#install)

## tar FAQ

### Which tar command switch compresses the archive?

z for gzip (.tar.gz), j for bzip2 (.tar.bz2), and capital J for xz (.tar.xz). Without one of those, tar only bundles files at full size. -a picks the compressor from the file name you typed, so tar -caf out.tar.xz dir works out the rest. The other letters are the verbs around it: c creates, x extracts, t lists, v prints each file name, and f means the next word is the archive name. That is all tar -czvf is, four separate switches stuck together, and f has to come last or tar treats the following letter as the file name.

### Can the tar command unzip a zip file?

It depends on which tar you have. The bsdtar that ships with macOS, Windows 10 and Windows 11 reads .zip fine, so tar -xf archive.zip works there. GNU tar on Linux does not; it fails with an unrecognized archive format error, and the tool you want is unzip archive.zip. Going the other way, tar cannot write .zip at all, so use zip -r out.zip folder when the other side insists on one. On Linux, unzip usually just means extracting a .tar.gz, which is plain tar -xzf.

### Does the tar command delete the original files?

No. Creating an archive copies the files and leaves the originals where they are, which is why a tar.gz of a big directory briefly needs room for both. Add --remove-files if you actually want tar to delete each file after it is safely archived. The confusion comes from gzip on its own, which does replace file with file.gz. Extraction is the direction that destroys things: tar overwrites same-named files in the target without asking, so use -k to keep what is already there.

### How do I extract a tar.gz file to a specific directory?

Pass -C with the target: tar -xzf app.tar.gz -C /opt/app. tar changes into that directory before unpacking, so it must already exist; create it first with mkdir -p /opt/app. If the archive wraps everything in a single top-level folder you do not want, add --strip-components=1 to drop it, so the files land directly in /opt/app instead of /opt/app/app-1.2.3.

### How do I use the tar command in Windows?

Open Command Prompt or PowerShell and run it exactly as you would on Linux. Windows 10 (since the April 2018 update) and Windows 11 ship bsdtar, so there is no WSL, Git Bash or 7-Zip to install: tar -xf archive.tar.gz extracts, tar -czf out.tar.gz Documents creates, tar -tf lists. Paths use backslashes, and -C C:\output still needs the folder to exist first. Run tar --version to see which one you have; the built-in reports bsdtar, and unlike GNU tar it opens .zip files too.

---
Källa: https://sshworkbench.com/cheatsheets/tar
