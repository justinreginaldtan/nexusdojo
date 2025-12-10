  • Here’s what bindkey -v changes and how to work with it:

• Here are three high‑leverage normal‑mode habits to grow into with bindkey
  -v:

  - Fast cursoring and jumps: w/b word hops, 0/^/$ line edges, f<char>/F find
    in line, ; repeat, , reverse. Combine with counts (3w, 2f.) and Ctrl+u/d
    half‑screen. Muscle memory for these kills arrow key dependence.
  - Surgical edits without typing mode: x delete char, dw/db delete word,
    de to end of word, D delete to line end, cw change word (drops you into
    insert to retype), r<char> single‑char replace, ~ flip case, C change to
    line end. These let you fix typos and reshape text quickly.
  - Command history/search power: In normal mode, /pattern forward search in
    history, ?pattern backward, then n/N to repeat; k/j moves through history
    lines; Ctrl+r and Ctrl+s may need enabling but give incremental search.
    Use with word motions to edit previous commands: e.g., ?git → n to the
    commit you want → cw on a branch name → re‑run.

  - Modes: insert vs normal (vicmd). Esc or jk → normal; any insert key
    (letters, i/a/A/I) → insert. Your prompt marker will show [I]/[N].
  - Movement in normal mode: h/j/k/l char/line nav; w/b/e word jumps; 0/^/$
    line start/first non-space/end; f/F find next/prev char on the line, t/T
    before it; ;/, repeat.
  - Editing in normal mode: x delete char, X delete left char; dd delete
    line; D delete to end; cw change word; cc change line; dw/db/de delete
    word variants. Put text back with p/P; change commands drop you into
    insert mode automatically.
  - Repeat/undo: . repeats last change; u undo, Ctrl-R redo.
  - History/search: k/j move through history in normal mode; Ctrl-R
    incremental search still works from insert; ? also searches backward.
  - Replace: r replaces one char; R is overwrite mode until Esc.
  - Misc handy: Ctrl-U/Ctrl-W in insert delete to start/back a word; Ctrl-A/
    Ctrl-E still go to start/end; Ctrl-K kill to end.
  - Your jk mapping: in insert, pressing j then k quickly returns to normal;
    not a literal “jk” input.
  - Cursor/prompt feedback: block cursor + [N] means normal; bar cursor +
    [I] means insert. If the cursor shape doesn’t show, rely on the [I]/
    [N] prompt.

  Workflow shift: type normally in insert; hit Esc/jk to navigate/edit with
  motions, then drop back into insert with i/a/A when ready to type again.
  Undo/redo and . repeat make quick edits faster once you lean on normal mode.
