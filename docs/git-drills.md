# Git Drills

All five drills were done in this repo on the local branches `drill/basics` and
`drill/conflict`, using a practice file `docs/drill-notes.md`. The terminal output
of each step is below.

---

## (a) Branch and commit

Create a branch, add a file and commit it.

```text
$ git switch -c drill/basics
Switched to a new branch 'drill/basics'

$ printf '# Drill notes\n\nLine 1: first drill commit.\n' > docs/drill-notes.md
$ git add docs/drill-notes.md
$ git commit -q -m 'docs: add drill notes file'

$ git branch --show-current
drill/basics

$ git log --oneline -2
5e5dcde docs: add drill notes file
b0c0b41 docs: document quality tools and pre-commit demo
```

---

## (b) Fix a wrong commit message with `git commit --amend`

The commit was made with a bad message (`updated stuff`, which is not a
Conventional Commit), then fixed with `--amend`.

```text
$ printf 'Line 2: added for the amend drill.\n' >> docs/drill-notes.md
$ git commit -q -am 'updated stuff'

$ git log --oneline -1
61f425d updated stuff

$ git commit -q --amend -m 'docs: add second line to drill notes'

$ git log --oneline -2
c8b7736 docs: add second line to drill notes
5e5dcde docs: add drill notes file
```

The hash changed from `61f425d` to `c8b7736`: amend replaces the last commit
with a new one. Only amend commits that have not been pushed yet.

---

## (c) Resolve a merge conflict

> Note: the mentor-seeded `drill/conflict` branch did not exist on the remote at
> the time of this drill, so the same kind of conflict was created locally:
> both branches changed the same line of the same file.

```text
$ git switch -c drill/conflict
$ sed -i 's/^Line 1: .*/Line 1: changed on drill\/conflict (version A)./' docs/drill-notes.md
$ git commit -q -am 'docs: change line 1 on drill/conflict'

$ git switch drill/basics
$ sed -i 's/^Line 1: .*/Line 1: changed on drill\/basics (version B)./' docs/drill-notes.md
$ git commit -q -am 'docs: change line 1 on drill/basics'

$ git merge drill/conflict
Auto-merging docs/drill-notes.md
CONFLICT (content): Merge conflict in docs/drill-notes.md
Automatic merge failed; fix conflicts and then commit the result.

$ git status --short
UU docs/drill-notes.md
```

The file with conflict markers (indented here so this document has no real
markers in it):

```text
  # Drill notes

  <<<<<<< HEAD
  Line 1: changed on drill/basics (version B).
  =======
  Line 1: changed on drill/conflict (version A).
  >>>>>>> drill/conflict
  Line 2: added for the amend drill.
```

Resolution: edit the file to keep the right content, delete all markers, then
`git add` and commit.

```text
$ cat docs/drill-notes.md
# Drill notes

Line 1: merged - kept both version A (drill/conflict) and version B (drill/basics).
Line 2: added for the amend drill.

$ grep -cE '^(<<<<<<<|=======|>>>>>>>)' docs/drill-notes.md
0

$ git add docs/drill-notes.md
$ git commit -q -m 'docs: merge drill/conflict and resolve conflict in drill notes'

$ git status --short
(clean)

$ git log --oneline --graph -6
*   21174f6 docs: merge drill/conflict and resolve conflict in drill notes
|\
| * f4cfced docs: change line 1 on drill/conflict
* | d2d58f6 docs: change line 1 on drill/basics
|/
* 2e747a0 revert: remove mistaken line from drill notes
* f4105de docs: add mistaken line to drill notes
* c8b7736 docs: add second line to drill notes
```

0 conflict markers are left.

---

## (d) Undo a commit with `git revert`

A commit added a wrong line. `git revert` makes a new commit that undoes it,
without rewriting history.

```text
$ printf 'Line 3: THIS LINE IS A MISTAKE.\n' >> docs/drill-notes.md
$ git commit -q -am 'docs: add mistaken line to drill notes'

$ git log --oneline -1
f4105de docs: add mistaken line to drill notes

$ git revert --no-commit HEAD
$ git commit -q -m 'revert: remove mistaken line from drill notes'

$ git log --oneline -3
2e747a0 revert: remove mistaken line from drill notes
f4105de docs: add mistaken line to drill notes
c8b7736 docs: add second line to drill notes

$ cat docs/drill-notes.md
# Drill notes

Line 1: first drill commit.
Line 2: added for the amend drill.
```

Both the mistake and its undo stay in the history, and the file is back to how
it was. That makes `revert` safe on branches that are already pushed.

---

## (e) Merge versus rebase

1. Merge joins two branches by adding a new merge commit, so the history shows exactly when the branches split and came back together.
2. Rebase moves my commits so they sit on top of the latest commits of the other branch, as if I had started my work from there.
3. Merge never changes existing commits, so it is safe on shared branches like `dev` and `main`.
4. Rebase rewrites commit hashes, so I should only rebase my own local branch before pushing, never a branch others are using.
5. I use rebase to keep my feature branch up to date with a clean, straight history, and merge (through a PR) to bring finished work into `dev`.
