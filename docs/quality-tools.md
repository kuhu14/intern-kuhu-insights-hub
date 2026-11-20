# Quality tools and pre-commit hook

| Tool     | Checks            | Config                       |
| -------- | ----------------- | ---------------------------- |
| ruff     | Python lint       | `backend/pyproject.toml`     |
| black    | Python formatting | `backend/pyproject.toml`     |
| prettier | TS/JS formatting  | `frontend/.prettierrc.json`  |
| eslint   | TS/JS lint        | `frontend/eslint.config.mjs` |

All four run through [pre-commit](https://pre-commit.com) on every `git commit`
(see `.pre-commit-config.yaml`). If a hook fails or changes a file, the commit is
stopped. Review the changes, `git add` them, and commit again.

Note: the Python hooks run as `python -m <tool>` because Windows Smart App
Control blocks the unsigned `.exe` launchers that pre-commit creates by default.

## Demo: the hook blocks badly formatted files

Two badly formatted files were staged:

```python
# backend/warmup/bad_format.py
import os
def add( a,b ):
    return a+b
```

```ts
// frontend/warmup/badFormat.ts
export function add( a:number,b:number ) {
  let unused = 1
  return a+b
}
```

Output of `git commit -m "test: try to commit badly formatted files"`:

```text
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...........................................(no files to check)Skipped
check for merge conflicts................................................Passed
check for added large files..............................................Passed
ruff check...............................................................Failed
- hook id: ruff-check
- files were modified by this hook

Found 1 error (1 fixed, 0 remaining).

black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted backend\warmup\bad_format.py

All done! ✨ 🍰 ✨
1 file reformatted.

prettier.................................................................Failed
- hook id: prettier
- files were modified by this hook

warmup/badFormat.ts 92ms

eslint...................................................................Failed
- hook id: eslint
- exit code: 1
- files were modified by this hook

C:\dev\intern-kuhu-insights-hub\frontend\warmup\badFormat.ts
  2:9  error  'unused' is assigned a value but never used  @typescript-eslint/no-unused-vars

✖ 1 problem (1 error, 0 warnings)
```

The commit exited with code 1 and nothing was committed: ruff removed the unused
`import os`, black and prettier reformatted the code, and eslint rejected the
unused variable.
