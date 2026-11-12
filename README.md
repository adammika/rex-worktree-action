# Rex Create Worktree

Search **Create Worktree** in Rex's command palette. From a terminal in a Git
checkout, it opens a new tab and prompts for a new branch name. After submission
it creates `<main-checkout>/.worktrees/<branch>`, renames and focuses the tab,
and starts your login shell there. Empty input cancels; errors stay visible.

Requires Rex custom actions, Git, and Python 3.9+. Uses the foreground process's
working directory, with shell integration as a fallback. Python and Git must be
on Rex's shell PATH.

## Load the action

Add these lines to your Rex `init.lua` (normally `~/.config/rex/init.lua`):

```lua
local addon = "/Users/mika/Developer/RexAddons/rex-worktree"
package.path = addon .. "/?.lua;" .. package.path
require("create_worktree")(addon)
```

Then run `rex config check` and `rex config reload`. If `rex` is not on PATH,
use `/Applications/Rex Beta.app/Contents/Helpers/Rex Server.rex/Contents/MacOS/rex`.
All action files remain in this repository; moving it requires updating `addon`.

## Behavior and limitations

- The prompt runs in the new terminal tab. Rex's documented Lua API has no
  general text-input dialog, and action callbacks have a 30-second deadline.
  Moving interactive input into a helper avoids that deadline.
- Git uses `git worktree add -b <branch> <path>` to create both at once.
- The new branch starts at the invoking checkout's HEAD. Uncommitted changes
  stay in the original checkout; a repository needs an initial commit.
- Existing branches or directories are rejected; nothing is overwritten.
- Slash names such as `feature/login` produce `.worktrees/feature/login`.
- Invoking from a linked worktree still uses the main checkout's `.worktrees`.
- Adds `/.worktrees/` to Git's local `info/exclude`, shared by all worktrees.
- Bare repos and repos using a separate Git directory are unsupported.
- If tab naming fails after Git succeeds, the helper reports it and still opens
  the shell in the new worktree. Close cancelled/error tabs manually.

Run tests with `python3 -m unittest discover -s tests -v`.

References: [Rex custom actions](https://www.superlogical.com/rex/docs/customize/actions)
and [Rex configuration](https://www.superlogical.com/rex/docs/customize/config).
