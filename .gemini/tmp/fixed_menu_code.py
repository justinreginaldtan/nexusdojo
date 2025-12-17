def print_splash():
    """Prints a premium ASCII banner with a slight delay."""
    banner = """
    [bold cyan]
     _   _  ____  __  __  _   _  ____    ____   ___      _  ___  
    | \ | || ===| \ \/ / | | | |/ ___|  |  _ \ / _ \    | |/ _ \ 
    |  \| ||  __|  >  <  | |_| |\___ \  | | | | | | |_  | | | | |
    | |\  || |___ /_/\_\ |  _  | ___) | | |_| | |_| | |_| | |_| |
    |_| \_||_____/_/  \_\ \_| |_|____/  |____/ \___/ \___/ \___/ 
    [/bold cyan]"""
    console.clear()
    console.print(Align.center(banner))
    console.print(Align.center("[dim]System Online... v0.2[/dim]"))
    time.sleep(1.0) # The "Premium" pause

def get_last_session(kata_root: Path) -> Optional[str]:
    """Retrieves the slug of the most recently accessed kata."""
    # This is a placeholder; a more robust solution would track last active session in a file.
    # For now, it will return the last modified directory in kata_root.
    try:
        katas = [d for d in kata_root.iterdir() if d.is_dir() and not d.name.startswith(".")]
        if not katas:
            return None
        katas.sort(key=lambda d: d.stat().st_mtime, reverse=True)
        return katas[0].name
    except Exception:
        return None

def handle_menu(args: argparse.Namespace) -> int:
    """
    Main interactive menu for common tasks.
    """
    print_splash() # Call splash here
    
    while True:
        try: # Added try block for robustness
            console.clear()
            
            # Header / Status
            notes_root = Path(getattr(args, "notes_root", DEFAULT_NOTES_ROOT))
            skills = load_skills(notes_root)
            xp = sum(skills.values())
            level_title, _ = get_level_info(xp)
            
            settings = load_settings(notes_root)
            user_name = settings.get("user_name", "Engineer")
            
            console.print(Panel(
                f"[bold white]NEXUS DOJO[/bold white] | [cyan]{user_name}[/cyan] | [yellow]{level_title} ({xp} XP)[/yellow]",
                border_style="blue",
            ))
            
            console.print()
            console.print("[bold]Available Actions:[/bold]")
            console.print(" [bold cyan]1[/bold cyan] ⚡ Quick Train (Start a new random drill)")
            console.print(" [bold cyan]2[/bold cyan] 🆕 Start New Session (Manual setup)")
            
            last_slug = get_last_session(Path(args.root)) # Using the new get_last_session
            resume_label = f"Resume '{last_slug}'" if last_slug else "Resume Last Kata"
            console.print(f" [bold cyan]3[/bold cyan] ▶️  {resume_label}")
            
            console.print(" [bold cyan]4[/bold cyan] 📂 Return to Any Kata (Pick from list)")
            console.print(" [bold cyan]5[/bold cyan] 📊 Profile & History")
            console.print(" [bold cyan]6[/bold cyan] ⚙️  Settings")
            console.print(" [bold cyan]7[/bold cyan] ❓ Help & Workflow")
            console.print(" [bold cyan]8[/bold cyan] 🚪 Exit")
            console.print()
            
            choice = Prompt.ask("[italic grey50]Select option [1-8]:[/italic grey50]", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="1", show_choices=False)
            
            if choice == "1":
                # Quick Train: Auto-pick based on weakest pillar
                # We call handle_start with no idea, forcing the picker
                return handle_start(argparse.Namespace(**vars(args), idea=None, guided=False, yes=False))
                
            elif choice == "2":
                # Manual Start
                return handle_start(argparse.Namespace(**vars(args), idea=None, guided=True))
                
            elif choice == "3":
                return handle_continue(args)
                
            elif choice == "4":
                # Pick from list
                kata_root = Path(args.root).expanduser()
                katas = [d for d in kata_root.iterdir() if d.is_dir() and not d.name.startswith(".")] # Fixed typo
                katas.sort(key=lambda d: d.stat().st_mtime, reverse=True)
                
                if not katas:
                    console.print("[yellow]No katas found.[/yellow]")
                    Prompt.ask("Press Enter")
                    continue
                    
                console.print("\n[bold]Select Kata:[/bold]")
                for idx, k in enumerate(katas[:9], 1):
                    console.print(f" [{idx}] {k.name}")
                
                sel = Prompt.ask("Select", choices=[str(i) for i in range(1, len(katas[:9])+1)])
                target = katas[int(sel)-1].name
                
                action = Prompt.ask("Action", choices=["watch", "check", "log"], default="watch")
                if action == "watch":
                    return handle_watch(argparse.Namespace(**vars(args), project=target))
                elif action == "check":
                    return handle_check(argparse.Namespace(**vars(args), project=target))
                elif action == "log":
                    note = Prompt.ask("Log Note")
                    return handle_log(argparse.Namespace(**vars(args), project=target, note=note))
                    
            elif choice == "5":
                handle_info(args) # Reusing info as profile for now
                Prompt.ask("Press Enter")
                
            elif choice == "6":
                handle_settings(args)
                
            elif choice == "7":
                handle_help(args)
                
            elif choice == "8":
                console.clear()
                console.print("[blue]Session terminated.[/blue]")
                return 0

        except Exception as e:
            console.print(f"[bold red]CRITICAL MENU ERROR: {e}[/bold red]")
            import traceback
            console.print(traceback.format_exc())
            Prompt.ask("Press Enter to retry...")
            continue
