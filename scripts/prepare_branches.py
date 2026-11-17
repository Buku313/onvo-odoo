#!/usr/bin/env python3
"""Prepare local marketplace branches from a clean source checkout. Does not push."""
import argparse
import subprocess
from pathlib import Path
import shutil
from build_version import build, SUPPORTED


def git(*args, cwd):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if git('status', '--porcelain', cwd=root):
        raise SystemExit('Commit source changes before preparing version branches.')
    source_commit = git('rev-parse', 'HEAD', cwd=root)
    source_branch = git('branch', '--show-current', cwd=root)
    for version in SUPPORTED:
        branch = f'{version}.0'
        if branch == source_branch:
            continue
        worktree = (args.output / branch).resolve()
        if worktree.exists():
            raise SystemExit(f'Refusing to overwrite {worktree}')
        # New branches only. Existing releases must be updated explicitly and reviewed.
        git('worktree', 'add', '-b', branch, str(worktree), source_commit, cwd=root)
        generated, _ = build(version, args.output.resolve() / f'package-{version}')
        shutil.rmtree(worktree / 'payment_onvo')  # Newly created worktree, never the source.
        shutil.copytree(generated, worktree / 'payment_onvo')
        git('add', 'payment_onvo', cwd=worktree)
        git('commit', '-m', f'Package ONVO Checkout for Odoo {version}', cwd=worktree)
        print(branch, git('rev-parse', 'HEAD', cwd=worktree))


if __name__ == '__main__':
    main()
