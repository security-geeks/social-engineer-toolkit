# Lessons

## 2026-06-04 - Apply patches in the intended worktree

- What went wrong: I added `tests/test_packaging.py` in the original checkout after creating the feature worktree.
- Fix: Removed the misplaced file and re-applied the patch with an absolute path inside the worktree.
- Prevention: After creating or switching worktrees, run `pwd` and `git status --short --branch` before every file edit, and use absolute paths for patches when multiple checkouts are open.
