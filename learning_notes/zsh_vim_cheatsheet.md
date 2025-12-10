# 🧠 ZSH + VIM-MODE MASTER CHEATSHEET

## MODES (critical)
| Mode | Visual | Meaning |
|------|--------|---------|
| Insert | Thin cursor | Text is typed |
| Normal | Block cursor | Commands apply |

### Switch modes
| Action | Keys |
|--------|------|
| Insert → Normal | `Esc` or `jk` |
| Normal → Insert | `i`, `a`, `A` |

---

## CORE MOVEMENT (Normal mode)
| Key | Action |
|-----|--------|
| `h j k l` | Left / Down / Up / Right |
| `w` | Next word |
| `b` | Previous word |
| `e` | End of word |
| `0` | Start of line |
| `$` | End of line |
| `f x` | Jump to character `x` |
| `t x` | Jump *before* character `x` |

---

## EDITING (Normal mode)
| Command | Result |
|---------|--------|
| `x` | Delete character |
| `dw` | Delete word |
| `cw` | Change word |
| `ciw` | Change entire word |
| `di"` | Delete inside quotes |

**Rule:** operator + motion

---

## SHELL-SPECIFIC HELPERS
| Command | Effect |
|---------|--------|
| `mkcd dir` | mkdir + cd |
| `extract file` | Unpack most archives |
| `path` | Show PATH line-by-line |

---

## SAFE FILE OPERATIONS (aliases)
| Command | Behavior |
|---------|----------|
| `cp` | Prompt + verbose |
| `mv` | Prompt + verbose |
| `ln` | Prompt + verbose |
| `rm` | Moves to Trash |
| `\rm` | Real rm (no safety) |

---

## ADMIN / DEBUG
| Command | Purpose |
|---------|---------|
| `ports` | Show listening ports |
| `pls` | Retry last command with sudo |
| `ragdiag` | Project diagnostics |

---

## CONFIG MANAGEMENT
| Command | Purpose |
|---------|---------|
| `zshrc` | Open `~/.zshrc` |
| `reload` | Reload config |
| `source ~/.zshrc` | Manual reload |

---

## VIM-LEARNING TRAINING RULES 🧠
1. When confused: press `Esc`
2. Leave insert mode often
3. Prefer motions over Backspace
4. If lost → `Esc`, then start again
5. Cursor shape tells the truth

---

## WHAT’S DISABLED (on purpose)
| Key | Why |
|-----|-----|
| `Q` | Prevent accidental weird states |
| `ZZ` | Prevent accidental shell exit |

---

## ONE-LINE MENTAL MODEL
> Think in motions. Normal mode is navigation and editing. Insert mode is brief.

