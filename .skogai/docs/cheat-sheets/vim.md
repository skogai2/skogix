# Vim Cheat Sheet

Vim is the modal editor installed on practically every Linux server, so it is what opens when you edit a file over SSH. This sheet covers the shortcuts people actually look up: saving and quitting, copy and paste, search and replace, motions, splits, and macros.

Last updated September 11, 2026

On this page

- [Save and Quit](#save-and-quit)
- [Copy and Paste](#copy-and-paste)
- [Delete](#delete)
- [Search and Replace](#search-and-replace)
- [Regex](#regex)
- [Undo and Redo](#undo-and-redo)
- [Navigation and Motions](#navigation-and-motions)
- [Modes](#modes)
- [Visual Mode and Visual Block](#visual-mode-and-visual-block)
- [Splits](#splits)
- [Buffers and Tabs](#buffers-and-tabs)
- [Macros](#macros)
- [Comment and Indent](#comment-and-indent)
- [Transform Text](#transform-text)
- [Grep and Quickfix](#grep-and-quickfix)
- [Text Objects](#text-objects)
- [Folding](#folding)
- [Vimdiff](#vimdiff)
- [Settings](#settings)
- [Plugins](#plugins)
- [Help](#help)
- [Gotchas](#gotchas)

## Save and Quit

Press Esc first: the : commands only work from normal mode.

[TABLE]

## Copy and Paste

Vim calls copy yank and paste put. Deletes cut into the same place, so dd then p moves a line.

[TABLE]

## Delete

[TABLE]

## Search and Replace

[TABLE]

## Regex

Vim's default pattern syntax needs backslashes where most languages do not. \v at the front of a pattern (very magic) makes it behave like the regex you already know.

[TABLE]

```
:%s/\v(\w+)\s+(\w+)/\2 \1/g      " swap the first two words on every line
:%s/\v<(foo|bar)>/baz/g          " whole words foo or bar, nothing longer
:%s/\vhttps?:\/\/\S+//g          " strip URLs
:g/\v^\s*$/d                     " delete every blank line
:%s/error\zs.*//                 " keep the word error, drop the rest of the line
```

Copy

## Undo and Redo

[TABLE]

## Navigation and Motions

A count multiplies any motion: 5j moves five lines down, 3w three words forward. Motions also feed d, y, and c, so d3w deletes three words.

[TABLE]

## Modes

Vim starts in normal mode, where keys are commands, not text. Esc always gets you back there.

[TABLE]

## Visual Mode and Visual Block

[TABLE]

## Splits

All the window commands live on Ctrl+w: press it, release, then the key.

[TABLE]

## Buffers and Tabs

Every open file is a buffer; splits and tabs are just views onto them.

[TABLE]

## Macros

Record keystrokes once, replay them everywhere. Start the recording with a motion like 0 so it works from any column, and end it with j so replays walk down the file.

[TABLE]

## Comment and Indent

Plain Vim has no comment toggle; visual block fills the gap. Neovim 0.10+ ships gcc to toggle a comment (Vim 9.1 gets it after packadd comment).

[TABLE]

In visual mode \> indents one level and drops the selection; use 2\> for two levels or gv\> to hit it again.

## Transform Text

! runs the file, or a range of it, through an outside command and puts the output back. That is how Vim formats JSON without a plugin.

[TABLE]

## Grep and Quickfix

The quickfix list holds a set of file-and-line results. :vimgrep fills it from a search, and :cdo then runs an edit on every hit, which is how a replace crosses more than one file.

[TABLE]

## Text Objects

Text objects target the thing around the cursor: an operator (d, c, y, v), then i for inside or a for around, then the object. i stops at the delimiters, a takes them too.

[TABLE]

## Folding

Folding collapses blocks so long files scan faster. The default foldmethod is manual; :set foldmethod=indent folds by indentation, which suits YAML and Python.

[TABLE]

## Vimdiff

vimdiff a.conf b.conf opens both files side by side with the differences highlighted. do and dp move a change between them, which is the fast way to reconcile a config against its .rpmnew or .dpkg-dist copy.

[TABLE]

## Settings

:set changes a setting for this session only. The same line without the colon in ~/.vimrc makes it stick. Neovim reads ~/.config/nvim/init.vim instead.

[TABLE]

A usable starting ~/.vimrc:

```
" ~/.vimrc
set number relativenumber
set ignorecase smartcase incsearch hlsearch
set expandtab tabstop=4 shiftwidth=4 autoindent
set list listchars=tab:>-,trail:.
syntax on
```

Copy

## Plugins

Vim 8 and later load plugins on their own, so a manager is optional: anything dropped in ~/.vim/pack/\*/start/ loads at startup.

[TABLE]

With vim-plug, list the plugins between call plug#begin() and call plug#end() in ~/.vimrc, then :PlugInstall; :PlugUpdate upgrades them and :PlugClean removes the ones you deleted from the list.

## Help

Vim carries its own manual, and the help topic names are not always what you would guess.

[TABLE]

## Gotchas

- If typing produces commands instead of text, or text instead of commands, check the mode. Esc puts you in normal mode from anywhere; the
  -- INSERT --
  tag at the bottom says you are typing text.
- Backspace that refuses to delete past the point where you started typing means Vim is in vi-compatible mode.
  :set backspace=indent,eol,start
  restores the behaviour everyone expects; put the line in
  ~/.vimrc
  so it sticks.
- Vim has no multiple cursors. Visual block covers the column case, and for everything else make the change once, then repeat it with
  .
  or record it as a macro.
- A
  recording @q
  message in the status line means you pressed
  q
  by accident and every keystroke is being recorded. Press
  q
  once to stop; nothing is harmed.
- "+y
  silently does nothing on a Vim built without clipboard support, which includes most server installs (
  vim --version
  shows
  -clipboard
  ). Over SSH the clipboard is on the wrong machine anyway: select with the mouse in your terminal, or run the session inside [tmux](https://sshworkbench.com/cheatsheets/tmux) and use its copy mode.
- On macOS the system
  vim
  in
  /usr/bin
  is built without clipboard support, so
  "+y
  does nothing there either. Pipe instead:
  :w !pbcopy
  copies the file and
  :'\<,'\>w !pbcopy
  copies a visual selection.
  brew install vim
  gets a build with
  +clipboard
  .
- :set mouse=a
  makes Vim grab the mouse, so terminal selection stops working. Hold Shift while dragging to select with the terminal again.
- E325: ATTENTION
  with a swap file warning means a crashed or still-open session left a
  .swp
  file behind. Recover the unsaved changes with
  vim -r file
  , then delete the
  .swp
  ; if another terminal really has the file open, edit it there instead.
- Pasting into an old Vim over SSH can cascade the indentation.
  :set paste
  before pasting and
  :set nopaste
  after fixes it; Vim 8+ handles bracketed paste on its own.

### Edit server files without the modal maze

SSH Workbench opens any file on your server in a proper editor over SSH: browse, edit, save. Vim and nano are still one click away in the terminal.

[Try free for 7 days](https://sshworkbench.com/#install)

## Vim FAQ

### What are the basic Vim commands?

Ten carry most of a session: i to start typing, Esc to stop, :w to save, :q to quit, dd to delete a line, yy to copy one, p to paste, u to undo, / to search, and gg and G for the top and bottom of the file. The habit that matters more than the list is leaving insert mode the moment you stop typing, because every other key only works from normal mode. Vim also ships its own tutorial: run vimtutor from the shell for a 30-minute walkthrough on a scratch copy you cannot damage.

### How do I save and exit Vim?

Press Esc first, then type :wq and Enter to save and quit, or ZZ without the colon. :q! quits and throws the changes away. :x and ZZ do the same job as :wq with one difference: they skip the write when nothing changed, so the file keeps its old timestamp and make or a file watcher stays quiet. If typing :wq just prints the letters, you were still in insert mode; press Esc and try again. If the status line says recording, you pressed q earlier; press q once to stop, then quit. If Vim refuses with E45 (readonly), you opened a root-owned file without sudo: force it with :w !sudo tee % and then :q!, or quit and reopen with sudo.

### How do I copy and paste in Vim?

Inside Vim, yy copies a line and p pastes it. For the system clipboard, yank with "+y ("+yy for a line) and paste with "+p. That needs a Vim built with clipboard support: vim --version shows +clipboard or -clipboard, and most server builds and the macOS system vim have the minus. Over SSH there is a second catch, since the + register lives on the server, not your machine. The practical fixes are selecting with the mouse in your terminal (hold Shift if Vim has mouse mode on), piping to a local tool such as :w !pbcopy on macOS, or OSC 52 support in Vim 9.1 and Neovim, which sends yanks through the terminal to your own clipboard.

### How do I search and replace in Vim?

:%s/old/new/g replaces every occurrence in the file; add c to confirm each one (:%s/old/new/gc) and i to ignore case. Without the %, the replace only touches the current line, which is the usual reason it looks like nothing happened. The delimiter does not have to be a slash: :%s#/var/www#/srv/site#g avoids escaping paths. After searching with /, :%s//new/g reuses that search as the pattern.

### What is the difference between vi and Vim?

Vim is a rewrite of vi that adds multi-level undo, syntax highlighting, visual mode, macros, and split windows. On most Linux systems typing vi starts Vim anyway, through a symlink or through the vim.tiny build that Debian and Ubuntu install by default, and that tiny build is where people meet one-level undo and arrow keys that insert letters instead of moving. :version names the build and lists which features it was compiled with; if the first line says Small or Tiny, install the full vim package. Neovim is a later fork of Vim that keeps the same keys and commands, so everything on this page works there too; what it changes is the config file, the plugin API, and the defaults. Everything here assumes the full Vim build.

---
Källa: https://sshworkbench.com/cheatsheets/vim
