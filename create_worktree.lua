-- Load with: require("create_worktree")("/absolute/path/to/rex-worktree")
return function(addon_dir)
  rex.action{
    name = "create_worktree",
    title = "Create Worktree",
    description = "Create a Git branch and worktree in a new terminal tab",
    category = "Git",
    keywords = "create worktree branch git",
    run = function(ctx, args)
      if not ctx.session_id or not ctx.block_id then
        error("Create Worktree must run from a terminal pane.", 0)
      end
      -- Process cwd works while Codex or another foreground program is running,
      -- even when the shell has never emitted an OSC 7 directory report.
      local process = rex.block.call("com.superlogical.terminal", "process", {})
      local cwd = process and process.foreground and process.foreground.cwd
      if not cwd or cwd == "" then
        local info = rex.block.call("com.superlogical.terminal", "pwd", {})
        cwd = info and info.pwd
      end
      if not cwd or cwd == "" then
        error("Cannot determine this pane's directory from its process or shell integration.", 0)
      end
      if cwd:match("^file://") then
        cwd = cwd:match("^file://[^/]*(/.*)$")
        if not cwd then error("Cannot read this pane's directory URL.", 0) end
        cwd = cwd:gsub("%%(%x%x)", function(hex) return string.char(tonumber(hex, 16)) end)
      end
      local result, git_err = rex.exec({"git", "-C", cwd, "rev-parse", "--show-toplevel"})
      if not result or not result.ok then
        error("Create Worktree requires a Git working directory. " .. (git_err or ""), 0)
      end
      local root = result.stdout:gsub("[\r\n]+$", "")
      local w, window_err = rex.session.new_window{
        window_label = "Create Worktree",
        focus = true,
        layout = rex.layout.block{
          flavor = "com.superlogical.terminal.shell",
          options = {
            cwd = root,
            command = {"python3", addon_dir .. "/worktree.py", root},
            exit = {on_completion = false},
          },
        },
      }
      if not w then error(window_err, 0) end
      return w
    end,
  }
end
