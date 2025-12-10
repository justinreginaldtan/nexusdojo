# 🟢 NVIM INTRO – Absolute Beginner Cheatsheet

Use this as your level-1 map for Neovim/Vim.

---

## What Neovim / Vim Is

Vim (and Neovim) is a **modal text editor**.

You are **not always typing text** – sometimes you are **giving commands** to move or change text.

Think of two main states:

- **Normal mode** → move around, run commands
- **Insert mode** → type text like a normal editor

You spend most of your time in **Normal**, and briefly drop into **Insert** to type.

---

## The Two Modes That Matter

### 1️⃣ Normal Mode

- Purpose: navigate and manipulate text
- Keys run actions instead of inserting characters
- This is the “default” mode

### 2️⃣ Insert Mode

- Purpose: type text
- Keys behave like any regular editor

---

## Switching Between Modes

- `i` → **Insert** mode (start typing at cursor)
- `a` → Insert **after** cursor
- `o` → Insert on a new line **below**
- `O` → Insert on a new line **above**
- `Esc` → return to **Normal** mode (stop typing)

Mnemonic:  
**i = insert**, **Esc = escape to safety**.

If you’re ever confused: press `Esc` twice.

---

## Core Flows (Use These First)

### Flow 1 – “I just want to type something”

1. Press `Esc`
2. Move cursor using arrow keys (for now) or `h j k l`
3. Press `i`
4. Type your text
5. Press `Esc` when done

---

### Flow 2 – “I want a new line and type there”

New line *below*:

1. Press `Esc`
2. Press `o`
3. Type your text
4. Press `Esc`

New line *above*:

1. Press `Esc`
2. Press `O`
3. Type your text
4. Press `Esc`

---

### Flow 3 – “Save and quit without panic”

- Save: `:w` then Enter  
- Quit: `:q` then Enter  
- Save + quit: `:wq` then Enter

If things feel weird:

1. Press `Esc`  
2. Type `:wq`  
3. Press Enter  

You are out.

---

### Flow 4 – “I messed up”

- Undo last change: `u`
- Redo: `Ctrl + r`

You can undo multiple times – mistakes are cheap.

---

## What `:` Does (Command-Line Mode)

When you press `:`, Vim opens a **command line** at the bottom.

Think of it as:

> “Talk directly to the editor.”

These are **editor commands**, not text edits.

Common ones:

- `:w` → write (save file)
- `:q` → quit
- `:wq` → save and quit
- `:q!` → quit and throw away changes
- `:42` → jump to line 42

Mnemonic:  
`:` = “command prompt for Vim itself.”

---

## Movement in Normal Mode (Basics)

- `h` → left  
- `j` → down  
- `k` → up  
- `l` → right  

Word movement:

- `w` → next word  
- `b` → previous word  
- `e` → end of word  

Line movement:

- `0` → beginning of line  
- `$` → end of line  

These motions are used both for moving **and** for telling Vim *how far* to act.

---

## Operators + Motions (Vim’s Big Idea)

Vim uses a **verb + object** system:

> **operator + motion**

### Common operators (verbs)

- `d` → delete  
- `c` → change (delete then go to Insert mode)  
- `y` → yank (copy)

### Common motions (objects)

- `w` → to next word  
- `b` → back a word  
- `e` → to end of word  
- `$` → to end of line  
- `0` → to start of line  

### Putting them together

- `dw` → delete word  
- `cw` → change word  
- `d$` → delete to end of line  
- `c$` → change to end of line  
- `ciw` → change inner word (no surrounding spaces)

You already noticed this pattern:  
**`d` + `w` = delete word**.  
This is intentional and is how Vim is designed to be remembered.

---

## What This Memory Style Is Called

You naturally remember things like:

- `i = insert`
- `dw = delete word`
- `ciw = change inner word`

That’s a mix of:

- **Mnemonic learning** – tying a letter to a meaning (`i` = insert)  
- **Compositional learning** – combining small pieces into meaningful chunks (`d` + `w`)  
- **Chunking** – treating `dw` as one mental unit

Vim is designed around **composable commands** so this style works extremely well.

---

## Panic Protocol (When Everything Feels Wrong)

If you feel stuck or lost:

1. Press `Esc`  
2. Press `Esc` again (just to be sure you’re in Normal mode)  
3. Type `:wq`  
4. Press Enter  

You are saved and out.

---

## What You Do NOT Need Yet

Ignore all of this for now:

- Visual mode
- Buffers, windows, tabs
- Plugins
- Custom configuration
- Advanced registers and macros

---

## One-Sentence Mental Model

> **Normal mode manipulates text, Insert mode types text, and `:` talks to the editor.**

Live in this model first – everything else in Vim/Neovim builds on top of it.
