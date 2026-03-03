#!/bin/bash
# Setup script for MCP Bear Notes Server
# Uses pyenv for Python version management and uv for package management

set -e  # Exit on error

echo "🐻 Setting up MCP Bear Notes Server..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo -e "${YELLOW}⚠️  pyenv not found. Installing pyenv...${NC}"
    curl https://pyenv.run | bash
    echo ""
    echo -e "${YELLOW}Please add pyenv to your shell configuration and restart your terminal:${NC}"
    echo 'export PYENV_ROOT="$HOME/.pyenv"'
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"'
    echo 'eval "$(pyenv init -)"'
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
fi

# Install Python 3.11.14 if not already installed
echo -e "${BLUE}📦 Checking Python 3.11.14...${NC}"
if ! pyenv versions | grep -q "3.11.14"; then
    echo -e "${BLUE}Installing Python 3.11.14 with pyenv...${NC}"
    pyenv install 3.11.14
else
    echo -e "${GREEN}✓ Python 3.11.14 already installed${NC}"
fi

# Set local Python version
echo -e "${BLUE}🔧 Setting local Python version to 3.11.14...${NC}"
pyenv local 3.11.14

# Create virtual environment with uv
echo -e "${BLUE}🌍 Creating virtual environment with uv...${NC}"
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Removing...${NC}"
    rm -rf .venv
fi

uv venv --python 3.11.14

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies with uv
echo -e "${BLUE}📚 Installing dependencies with uv...${NC}"
uv pip install -e .

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}To activate the virtual environment, run:${NC}"
echo "  source .venv/bin/activate"
echo ""
echo -e "${BLUE}To test the server, run:${NC}"
echo "  python -m mcp_bear_notes.server"
echo ""
echo -e "${BLUE}To deactivate the virtual environment, run:${NC}"
echo "  deactivate"
echo ""
echo -e "${GREEN}🐻 Happy note-taking!${NC}"

# Setup script for MCP Bear Notes Server
