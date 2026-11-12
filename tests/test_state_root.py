from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import support
import state_root


def setUpModule() -> None:
    support.never_run("git")


class SlugTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()

    def repo(self, *parts: str) -> Path:
        return support.temp_git_repo(self.root.joinpath(*parts))

    def test_same_named_checkouts_in_different_places_get_different_slugs(self) -> None:
        work, clients = self.repo("Work", "App"), self.repo("Clients", "App")
        slugs = {state_root.slug_for(work), state_root.slug_for(clients)}
        self.assertEqual(len(slugs), 2)
        self.assertTrue(all(slug.startswith("app-") for slug in slugs))
        self.assertTrue(all(state_root.SLUG_RE.fullmatch(slug) for slug in slugs))

    def test_a_worktree_and_a_subdirectory_share_the_main_checkouts_slug(self) -> None:
        main = self.repo("app")
        support.git(main, "commit", "-q", "--allow-empty", "-m", "base")
        worktree = self.root / "elsewhere" / "feature-tree"
        support.git(main, "worktree", "add", "-q", str(worktree), "-b", "feature")
        (main / "sub").mkdir()
        slug = state_root.slug_for(main)
        self.assertTrue(slug.startswith("app-"))
        self.assertEqual(state_root.slug_for(worktree), slug)
        self.assertEqual(state_root.slug_for(main / "sub"), slug)

    def test_a_symlink_to_a_checkout_gets_its_slug(self) -> None:
        main = self.repo("app")
        link = self.root / "link"
        link.symlink_to(main)
        self.assertEqual(state_root.slug_for(link), state_root.slug_for(main))

    def test_a_path_with_no_git_checkout_has_no_slug(self) -> None:
        plain = self.root / "plain"
        plain.mkdir()
        with self.assertRaisesRegex(ValueError, "no project slug"):
            state_root.slug_for(plain)

    def test_a_bare_repository_has_no_slug(self) -> None:
        bare = support.temp_git_repo(self.root / "app.git", bare=True)
        with self.assertRaisesRegex(ValueError, "no project slug"):
            state_root.slug_for(bare)


class CliTest(unittest.TestCase):
    def test_prints_the_slug_or_refuses_with_one_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = support.temp_git_repo(Path(tmp).resolve() / "app")
            plain = Path(tmp).resolve() / "plain"
            plain.mkdir()
            code, out, err = support.run_main(state_root.main, [str(repo)])
            self.assertEqual((code, out, err), (0, state_root.slug_for(repo) + "\n", ""))
            code, out, err = support.run_main(state_root.main, [str(plain)])
            self.assertEqual((code, out), (1, ""))
            self.assertIn("no project slug", err)
            self.assertEqual(len(err.splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
