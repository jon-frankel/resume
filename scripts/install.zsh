#!/usr/bin/env zsh
set -euo pipefail

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

function nvm_install() {
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash

  # in lieu of restarting the shell
  \. "$HOME/.nvm/nvm.sh"

  # Download and install Node.js:
  nvm install 24.15.0

  # Verify the Node.js version:
  node -v # Should print "v24.15.0".

  # Verify npm version:
  npm -v # Should print "11.12.1".
}

brew --version || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
docker compose version || brew install --cask orbstack
nvm --version || nvm_install
nvm install
nvm use
npm install -g pnpm
uv --version || brew install uv
uv python install
pulumi version || brew install pulumi/tap/pulumi
pnpm install
pnpm exec playwright install
uv sync --locked --all-extras --dev
