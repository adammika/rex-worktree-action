"""Interactive helper for the Rex Create Worktree action (Python 3.9+)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def run(*args):
    return subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True).stdout.strip()


def create_worktree(directory, branch):
    root = Path(run("git", "-C", str(directory), "rev-parse", "--show-toplevel"))
    # Resolve to the main checkout even when invoked from a linked worktree.
    common = Path(run("git", "-C", str(root), "rev-parse", "--path-format=absolute",
                      "--git-common-dir"))
    main_root = common.parent
    if common.name != ".git":
        raise ValueError("Repositories with a separate Git directory are not supported.")
    if not branch or branch == "HEAD" or branch.startswith("-") or len(branch) > 128:
        raise ValueError("Enter a new branch name of 1–128 characters (not HEAD or an option).")
    validated = run("git", "-C", str(root), "check-ref-format", "--branch", branch)
    if validated != branch:
        raise ValueError("Enter a literal branch name, not a previous-branch expression.")
    run("git", "-C", str(root), "rev-parse", "--verify", "HEAD")
    base = main_root / ".worktrees"
    target = base / branch
    # Do not let symlinks redirect creation outside the main checkout.
    if base.is_symlink() or target.resolve() != target.absolute():
        raise ValueError("The worktree path must not traverse a symbolic link.")
    if target.exists():
        raise ValueError("The worktree directory already exists: " + str(target))
    # Keep generated checkouts out of git status without changing tracked files.
    exclude = common / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_text() if exclude.exists() else ""
    if "/.worktrees/" not in existing.splitlines():
        with exclude.open("a") as file:
            file.write(("\n" if existing and not existing.endswith("\n") else "")
                       + "/.worktrees/\n")
    run("git", "-C", str(root), "worktree", "add", "-b", branch, str(target))
    return target


def main():
    directory = sys.argv[1]
    print("Create Worktree — leave the branch name empty to cancel.")
    try:
        branch = input("New branch name: ").strip()
        if not branch:
            return
        target = create_worktree(directory, branch)
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("Error: " + (getattr(error, "stderr", None) or str(error)), file=sys.stderr)
        return 1

    rex = shutil.which("rex") or "/Applications/Rex Beta.app/Contents/Helpers/Rex Server.rex/Contents/MacOS/rex"
    try:
        session, block = os.environ["REX_SESSION"], os.environ["REX_BLOCK"]
        info = json.loads(run(rex, "block", "inspect", "-s", session, block, "--json"))
        run(rex, "window", "rename", "-s", session, info["block"]["window_id"], branch)
        run(rex, "focus", "-s", session, block)
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as error:
        print("Worktree created, but Rex could not rename/focus the tab: " + str(error), file=sys.stderr)
    os.chdir(target)
    shell = os.environ.get("SHELL", "/bin/zsh")
    print("Worktree ready: " + str(target))
    os.execv(shell, [shell, "-l"])


if __name__ == "__main__":
    sys.exit(main())
