# tmux Essentials for NexusDojo: Your Survival Guide

Welcome to the deep end, Reginald. `tmux` is the single most important tool for a CLI engineer after the shell itself.

This guide provides the absolute minimum you need to know about `tmux` to unlock the full potential of your NexusDojo and your command-line workflow. **Focus on these three commands only for the next 7 days.**

---

### 1. 🚀 How to Get Started (The Garage Door)

This is how you open your `tmux` session. You do this once at the beginning of your coding session.

*   **What it is:** `tmux` creates a persistent, multi-pane terminal environment. You must be inside `tmux` for NexusDojo's automatic split-screen feature to work.
*   **Command:** `tmux`
*   **How to use:** Open your terminal, type `tmux`, and press `Enter`.
*   **Confirmation:** You will see a green status bar at the very bottom of your terminal window (its appearance might vary slightly depending on your terminal's theme). This confirms you are "inside the garage."
*   **Why it's important:** Without this step, NexusDojo cannot perform the auto-split of your screen for the `dojo watch` feature.

---

### 2. ⏸️ How to Leave (The Pause Button)

This lets you temporarily exit your `tmux` session without closing it. All your programs (like Neovim and `dojo watch`) will continue running in the background.

*   **What it is:** "Detaching" from a `tmux` session. Your work keeps running even if you close your terminal window or your laptop.
*   **Command:** `Ctrl` + `b`, then `d`
    *   **How to use:** Hold down the `Ctrl` key, press the `b` key, then release both keys. After that, press the `d` key.
*   **Confirmation:** Your terminal will return to your normal shell, and you'll see a message like `[detached (from session 0)]`.
*   **Why it's important:** You don't lose your place. You can close your laptop, reboot, come back tomorrow, and your entire work environment (panes, open files, running tests) will be exactly as you left it.

---

### 3. ▶️ How to Come Back (The Re-Entry)

This brings you back into your last `tmux` session, precisely where you left off.

*   **What it is:** "Attaching" to a `tmux` session.
*   **Command:** `tmux a`
*   **How to use:** Type `tmux a` (short for "attach") and press `Enter`.
*   **Confirmation:** Your `tmux` session will reappear, showing all the panes and programs you had running.
*   **Why it's important:** Pick up exactly where you left off, even if you stepped away for hours or days.

---

### Your Daily `tmux` Flow with NexusDojo (Next 7 Days)

1.  **At the start of your coding day:**
    *   Open your terminal application.
    *   Type `tmux` and press `Enter`. (You are now in `tmux`).
2.  **Inside `tmux`:**
    *   Navigate to your NexusDojo project folder (e.g., `cd ~/labubucode/nexusdojo`).
    *   Run `dojo menu` -> `⚡ Quick Train`.
    *   Witness NexusDojo automatically split your screen and launch your coding environment.
3.  **When you need to stop or take a break:**
    *   Press `Ctrl` + `b`, then `d`. (You are now detached).
4.  **When you want to resume your work:**
    *   Open your terminal application (if closed).
    *   Type `tmux a` and press `Enter`. (You are back in your session).

**Ignore all other `tmux` commands and concepts for now.** Just get comfortable with entering, detaching, and re-attaching. This minimal set will unlock a powerful, uninterrupted workflow that will significantly boost your productivity.

---
**Remember:** `tmux` is a power tool. Focus on these essentials, and you'll be well on your way to mastering your terminal environment.
