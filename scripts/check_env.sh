#!/usr/bin/env bash
# Checks that the tools needed for this project are installed.
# Prints each tool's version and exits non-zero if any are missing or too old.
#
# Usage (from the repository root): bash scripts/check_env.sh

set -u

MISSING=0

ok()   { printf '  [OK]      %-10s %s\n' "$1" "$2"; }
fail() { printf '  [MISSING] %-10s %s\n' "$1" "$2"; MISSING=$((MISSING + 1)); }

# version_at_least "3.13.9" "3.11" -> true if the first is >= the second
version_at_least() {
  [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

echo "Checking development environment..."
echo

# Git
if command -v git >/dev/null 2>&1; then
  ok "Git" "$(git --version | awk '{print $3}')"
else
  fail "Git" "not found - install from https://git-scm.com"
fi

# VS Code
if command -v code >/dev/null 2>&1; then
  ok "VS Code" "$(code --version 2>/dev/null | head -n1)"
else
  fail "VS Code" "'code' command not found - install VS Code and add it to PATH"
fi

# Python 3.11+ (Windows often has only 'python', macOS/Linux often only 'python3')
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 \
    && "$candidate" -c 'import sys' >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
if [ -n "$PYTHON" ]; then
  py_version="$("$PYTHON" -c 'import platform; print(platform.python_version())')"
  if version_at_least "$py_version" "3.11"; then
    ok "Python" "$py_version"
  else
    fail "Python" "$py_version found, but 3.11+ is required"
  fi
else
  fail "Python" "not found - install Python 3.11+"
fi

# Node 20+
if command -v node >/dev/null 2>&1; then
  node_version="$(node --version | sed 's/^v//')"
  if version_at_least "$node_version" "20"; then
    ok "Node" "$node_version"
  else
    fail "Node" "$node_version found, but 20+ is required"
  fi
else
  fail "Node" "not found - install Node.js 20+"
fi

# npm (comes with Node)
if command -v npm >/dev/null 2>&1; then
  ok "npm" "$(npm --version)"
else
  fail "npm" "not found - reinstall Node.js"
fi

# GitHub SSH key: GitHub replies "successfully authenticated" when the key works
if command -v ssh >/dev/null 2>&1; then
  ssh_reply="$(ssh -T -o BatchMode=yes -o ConnectTimeout=10 git@github.com 2>&1)"
  if printf '%s' "$ssh_reply" | grep -q "successfully authenticated"; then
    gh_user="$(printf '%s' "$ssh_reply" | sed -n 's/^Hi \([^!]*\)!.*/\1/p')"
    ok "GitHub SSH" "authenticated as ${gh_user:-unknown}"
  else
    fail "GitHub SSH" "key not set up - see https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
  fi
else
  fail "GitHub SSH" "ssh not found"
fi

echo
if [ "$MISSING" -eq 0 ]; then
  echo "All tools found. Environment is ready."
  exit 0
else
  echo "$MISSING problem(s) found. Install the missing tools and run this again."
  exit 1
fi
