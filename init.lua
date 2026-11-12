-- Standalone config / validation entrypoint for this checkout.
local addon = "/Users/mika/Developer/RexAddons/rex-worktree-action"
package.path = addon .. "/?.lua;" .. package.path
require("create_worktree")(addon)
