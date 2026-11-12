import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from worktree import create_worktree, run


class WorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rex worktree ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        home_patch = patch("worktree.Path.home", return_value=self.home)
        home_patch.start()
        self.addCleanup(home_patch.stop)
        self.base = self.home / ".worktrees" / self.root.name
        run("git", "init", "-q", str(self.root))
        run("git", "-C", str(self.root), "-c", "user.name=Test", "-c",
            "user.email=test@example.com", "commit", "--allow-empty", "-m", "Initial")

    def test_create_in_home_and_from_linked_worktree(self):
        path = create_worktree(self.root, "feature/login")
        self.assertEqual(path, self.base / "feature/login")
        self.assertEqual(run("git", "-C", str(path), "branch", "--show-current"), "feature/login")
        self.assertFalse((self.root / ".worktrees").exists())
        self.assertNotIn("/.worktrees/", (self.root / ".git/info/exclude").read_text())
        second = create_worktree(path, "second")
        self.assertEqual(second, self.base / "second")

    def test_invalid_and_existing_branches(self):
        for name in ("", "../escape", "-bad", "HEAD", "a b", "a" * 129):
            with self.subTest(name=name), self.assertRaises((ValueError, subprocess.CalledProcessError)):
                create_worktree(self.root, name)
        create_worktree(self.root, "existing")
        with self.assertRaises(ValueError):
            create_worktree(self.root, "existing")
        run("git", "-C", str(self.root), "branch", "taken")
        with self.assertRaises(subprocess.CalledProcessError):
            create_worktree(self.root, "taken")

    def test_symlink_and_non_repository(self):
        self.base.parent.mkdir(parents=True)
        self.base.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            create_worktree(self.root, "escape")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(subprocess.CalledProcessError):
                create_worktree(directory, "test")
