# Vim Cheat Sheet

Vim is the modal editor installed on practically every Linux server, so it is what opens when you edit a file over SSH. This sheet covers the shortcuts people actually look up: saving and quitting, copy and paste, search and replace, motions, splits, and macros.

## Save and Quit

Press Esc first: the : commands only work from normal mode.

| Command | What it does |
|---|---|
| `:w` | Write (save) current file to disk |
| `:q` | Quit Vim (fails if there are unsaved changes) |
| `:wq` or `:x` | Save changes and exit |
| `ZZ` | Save changes and exit (Normal mode shortcut) |
| `:q!` | Force quit and discard all unsaved changes |
| `ZQ` | Quit without saving (Normal mode shortcut) |
| `:w !sudo tee %` | Save file requiring root/sudo privileges |

## Copy and Paste

Vim calls copy yank and paste put. Deletes cut into the same place, so dd then p moves a line.

| Key | What it does |
|---|---|
| `yy` | Yank (copy) current line |
| `3yy` | Yank 3 lines starting from cursor |
| `yw` | Yank word from cursor |
| `y$` | Yank from cursor to end of line |
| `p` | Put (paste) clipboard content after cursor / below line |
| `P` | Put (paste) clipboard content before cursor / above line |
| `"+y` | Yank into system clipboard |
| `"+p` | Paste from system clipboard |

## Delete

| Key | What it does |
|---|---|
| `x` | Delete character under cursor |
| `dd` | Delete (cut) current line |
| `dw` | Delete word from cursor forward |
| `d$` or `D` | Delete from cursor to end of line |
| `d0` | Delete from cursor to start of line |
| `cw` | Change word (delete word and enter Insert mode) |
| `c$` or `C` | Change to end of line |
| `ci"` | Change inside double quotes |

## Search and Replace

| Command | What it does |
|---|---|
| `/pattern` | Search forward for pattern |
| `?pattern` | Search backward for pattern |
| `n` | Jump to next search match |
| `N` | Jump to previous search match |
| `:%s/old/new/g` | Replace all occurrences of `old` with `new` across entire file |
| `:%s/old/new/gc` | Replace occurrences across file with confirmation prompt for each |
| `:s/old/new/g` | Replace all occurrences on current line only |

## Regex

Vim's default pattern syntax needs backslashes where most languages do not. \v at the front of a pattern (very magic) makes it behave like the regex you already know.

| Pattern | Meaning |
|---|---|
| `\v` | Very magic mode (characters like `(`, `)`, `+`, `?` work without backslashes) |
| `\<` and `\>` | Word boundary start and end |
| `\d` | Digit (`[0-9]`) |
| `\s` | Whitespace character |
| `\zs` and `\ze` | Set start and end of matched replacement region |

```
:%s/\v(\w+)\s+(\w+)/\2 \1/g      " swap the first two words on every line
:%s/\v<(foo|bar)>/baz/g          " whole words foo or bar, nothing longer
:%s/\vhttps?:\/\/\S+//g          " strip URLs
:g/\v^\s*$/d                     " delete every blank line
:%s/error\zs.*//                 " keep the word error, drop the rest of the line
```

## Undo and Redo

| Key | Action |
|---|---|
| `u` | Undo last change |
| `Ctrl+R` | Redo last undone change |
| `U` | Undo all recent changes made on the current line |

## Navigation and Motions

A count multiplies any motion: 5j moves five lines down, 3w three words forward. Motions also feed d, y, and c, so d3w deletes three words.

| Key | Motion |
|---|---|
| `h / j / k / l` | Move cursor left / down / up / right |
| `w / b` | Jump forward / backward by word start |
| `e / ge` | Jump forward / backward to word end |
| `0 / ^ / $` | Jump to line start / first non-blank character / line end |
| `gg / G` | Jump to first line / last line of file |
| `:N` or `Ng` | Jump directly to line number `N` |
| `Ctrl+U / Ctrl+D` | Scroll half-page up / half-page down |
| `%` | Jump to matching bracket `()`, `{}`, `[]` |

## Modes

Vim starts in normal mode, where keys are commands, not text. Esc always gets you back there.

| Mode | Key to Enter | Description |
|---|---|---|
| Normal | `Esc` | Default mode for navigation and commands |
| Insert | `i` (before), `a` (after), `o` (line below) | Typing inserts text |
| Visual | `v` (char), `V` (line), `Ctrl+V` (block) | Highlight and select text |
| Command | `:` | Execute ex-commands, search, and configuration |

## Visual Mode and Visual Block

| Key | Action |
|---|---|
| `v` | Start character-wise visual selection |
| `V` | Start line-wise visual selection |
| `Ctrl+V` | Start rectangular column visual block selection |
| `I#<Esc>` | Insert `#` at start of every selected line in visual block |
| `d` | Delete selected visual block |
| `gv` | Reselect previous visual selection |

## Splits

All the window commands live on Ctrl+w: press it, release, then the key.

| Keybinding | Action |
|---|---|
| `Ctrl+W s` | Split window horizontally (`:sp`) |
| `Ctrl+W v` | Split window vertically (`:vsp`) |
| `Ctrl+W h/j/k/l` | Move focus to left / bottom / top / right split |
| `Ctrl+W q` | Close current split window |
| `Ctrl+W =` | Resize all split windows to equal dimensions |

## Buffers and Tabs

Every open file is a buffer; splits and tabs are just views onto them.

| Command | What it does |
|---|---|
| `:ls` | List all open buffers |
| `:b <name>` or `:b <num>` | Switch to buffer by name or number |
| `:bnext` / `:bprev` | Switch to next / previous buffer |
| `:bd` | Delete (close) current buffer |
| `:tabnew` | Open new tab page |
| `gt` / `gT` | Switch to next / previous tab page |

## Macros

Record keystrokes once, replay them everywhere. Start the recording with a motion like 0 so it works from any column, and end it with j so replays walk down the file.

| Key | Action |
|---|---|
| `qa` | Start recording macro keystrokes into register `a` |
| `q` | Stop macro recording |
| `@a` | Replay macro stored in register `a` |
| `10@a` | Replay macro 10 times consecutively |
| `@@` | Replay most recently executed macro |

## Comment and Indent

Plain Vim has no comment toggle; visual block fills the gap. Neovim 0.10+ ships gcc to toggle a comment (Vim 9.1 gets it after packadd comment).

| Key | Action |
|---|---|
| `>>` / `<<` | Indent / unindent current line one shiftwidth |
| `==` | Auto-indent current line based on syntax rules |
| `=%` | Auto-indent entire bracketed block |
| `gcc` | Toggle line comment (Neovim 0.10+ or Vim 9.1 `packadd comment`) |

In visual mode > indents one level and drops the selection; use 2> for two levels or gv> to hit it again.

## Transform Text

! runs the file, or a range of it, through an outside command and puts the output back. That is how Vim formats JSON without a plugin.

| Command / Key | Action |
|---|---|
| `~` | Toggle letter case under cursor |
| `gUaw` | Make entire current word UPPERCASE |
| `guaw` | Make entire current word lowercase |
| `!sort` | Filter visual selection through external `sort` utility |
| `!jq .` | Format JSON visually selected lines with external `jq` |

## Grep and Quickfix

The quickfix list holds a set of file-and-line results. :vimgrep fills it from a search, and :cdo then runs an edit on every hit, which is how a replace crosses more than one file.

| Command | What it does |
|---|---|
| `:grep pattern *` | Search files using external grep |
| `:copen` | Open the Quickfix window listing search results |
| `:cnext` / `:cprev` | Jump to next / previous match in Quickfix list |
| `:cclose` | Close the Quickfix window |

## Text Objects

Text objects target the thing around the cursor: an operator (d, c, y, v), then i for inside or a for around, then the object. i stops at the delimiters, a takes them too.

| Key | Target |
|---|---|
| `iw` / `aw` | Inner word / a word (including surrounding whitespace) |
| `i"` / `a"` | Inside quotes / around quotes |
| `i(` / `a(` | Inside parentheses / around parentheses |
| `i{` / `a{` | Inside curly braces / around braces |
| `it` / `at` | Inside XML/HTML tag / around tag |

## Folding

Folding collapses blocks so long files scan faster. The default foldmethod is manual; :set foldmethod=indent folds by indentation, which suits YAML and Python.

| Key | Action |
|---|---|
| `zf` | Create manual fold over visual selection |
| `zo` | Open fold under cursor |
| `zc` | Close fold under cursor |
| `za` | Toggle fold open/closed |
| `zR` | Open all folds across entire buffer |
| `zM` | Close all folds across entire buffer |

## Vimdiff

vimdiff a.conf b.conf opens both files side by side with the differences highlighted. do and dp move a change between them, which is the fast way to reconcile a config against its .rpmnew or .dpkg-dist copy.

| Key / Command | Action |
|---|---|
| `vimdiff f1 f2` | Open two files in side-by-side diff mode |
| `do` | Diff obtain: copy changes from other window into current |
| `dp` | Diff put: push changes from current window into other |
| `]c` / `[c` | Jump to next / previous diff change block |

## Settings

:set changes a setting for this session only. The same line without the colon in ~/.vimrc makes it stick. Neovim reads ~/.config/nvim/init.vim instead.

| Command | What it does |
|---|---|
| `:set number` | Display line numbers |
| `:set relativenumber` | Display relative line numbers for easy motion counts |
| `:set expandtab` | Use spaces instead of tab characters |
| `:set tabstop=4 shiftwidth=4` | Set tab width and indent shift width to 4 spaces |
| `:set paste` | Enable paste mode (disables autoindent when pasting) |

A usable starting ~/.vimrc:

```
" ~/.vimrc
set number relativenumber
set ignorecase smartcase incsearch hlsearch
set expandtab tabstop=4 shiftwidth=4 autoindent
set list listchars=tab:>-,trail:.
syntax on
```

## Plugins

Vim 8 and later load plugins on their own, so a manager is optional: anything dropped in ~/.vim/pack/*/start/ loads at startup.

| Package / Manager | Purpose |
|---|---|
| `~/.vim/pack/.../start/` | Vim 8+ native package directory (no manager required) |
| `vim-plug` | Minimalist, fast Vim plugin manager |
| `lazy.nvim` | Modern plugin manager for Neovim |
| `packer.nvim` | Lua-based package manager for Neovim |

With vim-plug, list the plugins between call plug#begin() and call plug#end() in ~/.vimrc, then :PlugInstall; :PlugUpdate upgrades them and :PlugClean removes the ones you deleted from the list.

## Help

Vim carries its own manual, and the help topic names are not always what you would guess.

| Command | Action |
|---|---|
| `:help` | Open main documentation help index |
| `:help <topic>` | Open help topic (e.g. `:help user-manual`) |
| `Ctrl+]` | Follow help hyperlink tag under cursor |
| `Ctrl+T` | Jump back from followed help tag |

## Gotchas

- If typing produces commands instead of text, or text instead of commands, check the mode. Esc puts you in normal mode from anywhere; the -- INSERT -- tag at the bottom says you are typing text.
- Backspace that refuses to delete past the point where you started typing means Vim is in vi-compatible mode.:set backspace=indent,eol,start restores the behaviour everyone expects; put the line in ~/.vimrc so it sticks.
- Vim has no multiple cursors. Visual block covers the column case, and for everything else make the change once, then repeat it with. or record it as a macro.
- A recording @q message in the status line means you pressed q by accident and every keystroke is being recorded. Press q once to stop; nothing is harmed.
- "+y silently does nothing on a Vim built without clipboard support, which includes most server installs ( vim --version shows -clipboard). Over SSH the clipboard is on the wrong machine anyway: select with the mouse in your terminal, or run the session inside [tmux](https://sshworkbench.com/cheatsheets/tmux) and use its copy mode.
- On macOS the system vim in /usr/bin is built without clipboard support, so "+y does nothing there either. Pipe instead::w !pbcopy copies the file and:'<,'>w !pbcopy copies a visual selection. brew install vim gets a build with +clipboard.
- :set mouse=a makes Vim grab the mouse, so terminal selection stops working. Hold Shift while dragging to select with the terminal again.
- E325: ATTENTION with a swap file warning means a crashed or still-open session left a.swp file behind. Recover the unsaved changes with vim -r file, then delete the.swp; if another terminal really has the file open, edit it there instead.
- Pasting into an old Vim over SSH can cascade the indentation.:set paste before pasting and:set nopaste after fixes it; Vim 8+ handles bracketed paste on its own.

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
Source: https://sshworkbench.com/cheatsheets/vim
