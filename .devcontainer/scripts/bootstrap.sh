#!/usr/bin/env bash
set -euo pipefail

VENV_TARGET="/opt/agentic-venv"
WORKSPACE_VENV=".venv"

if [ ! -d "$VENV_TARGET" ]; then
    echo "Prebuilt virtual environment not found at $VENV_TARGET" >&2
    exit 1
fi

if [ -L "$WORKSPACE_VENV" ]; then
    CURRENT_TARGET=$(readlink -f "$WORKSPACE_VENV")
    if [ "$CURRENT_TARGET" != "$VENV_TARGET" ]; then
        rm "$WORKSPACE_VENV"
        ln -s "$VENV_TARGET" "$WORKSPACE_VENV"
    fi
elif [ -e "$WORKSPACE_VENV" ]; then
    echo "⚠️  Existing $WORKSPACE_VENV detected; leaving it in place. Delete or rename it to use the prebuilt environment." >&2
else
    ln -s "$VENV_TARGET" "$WORKSPACE_VENV"
fi

PYTHON_BIN="$VENV_TARGET/bin/python"

if command -v uv >/dev/null 2>&1; then
    if ! uv pip sync --python "$PYTHON_BIN" requirements.txt; then
        echo "uv pip sync failed, falling back to install" >&2
        uv pip install --python "$PYTHON_BIN" --upgrade -r requirements.txt
    fi
else
    echo "uv not detected; installing to ensure reproducible environment." >&2
    curl -LsSf https://astral.sh/install.sh | sh -s -- --yes --bin-dir /usr/local/bin
    uv pip sync --python "$PYTHON_BIN" requirements.txt
fi

ACTIVATE_SNIPPET="source \"$PWD/.venv/bin/activate\""
for shell_rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$shell_rc" ] && ! grep -Fqx "$ACTIVATE_SNIPPET" "$shell_rc"; then
        printf '\n%s\n' "$ACTIVATE_SNIPPET" >> "$shell_rc"
    fi
done
