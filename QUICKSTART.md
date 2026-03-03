# Quick Start Guide - MCP Bear Notes Server

This guide will help you get the MCP Bear Notes server up and running quickly.

## Prerequisites

- macOS (Bear Notes is macOS/iOS only)
- Bear Notes installed and running
- Python 3.11.14 (managed via pyenv)
- uv (Python package manager)
- Docker (optional, for containerized deployment)

## Installation Methods

### Method 1: Automated Setup with pyenv and uv (Recommended)

This project uses **pyenv** for Python version management and **uv** for fast package installation.

1. **Run the setup script:**
   ```bash
   cd /path/to/mcp-bear-notes
   ./setup.sh
   ```

   The script will:
   - Install pyenv (if not present)
   - Install uv (if not present)
   - Install Python 3.11.14
   - Create a virtual environment with uv
   - Install all dependencies

2. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Test the installation:**
   ```bash
   python -m mcp_bear_notes.server
   ```
   
   The server should start and wait for input. Press `Ctrl+C` to stop.

4. **Deactivate when done:**
   ```bash
   deactivate
   ```

### Method 2: Manual Installation with pyenv and uv

If you prefer manual setup:

1. **Install pyenv (if not installed):**
   ```bash
   curl https://pyenv.run | bash
   ```

2. **Install uv (if not installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Navigate to the project directory:**
   ```bash
   cd /path/to/mcp-bear-notes
   ```

4. **Install Python 3.11.14:**
   ```bash
   pyenv install 3.11.14
   pyenv local 3.11.14
   ```

5. **Create virtual environment with uv:**
   ```bash
   uv venv --python 3.11.14
   source .venv/bin/activate
   ```

6. **Install dependencies with uv:**
   ```bash
   uv pip install -e .
   ```

7. **Test the installation:**
   ```bash
   python -m mcp_bear_notes.server
   ```

### Method 3: Docker Installation

1. **Build the Docker image:**
   ```bash
   cd /path/to/mcp-bear-notes
   docker build -t mcp-bear-notes .
   ```

2. **Or use Docker Compose:**
   ```bash
   docker-compose build
   ```

## Configuration

### For Bob MCP Client

1. **Open your MCP settings file:**
   ```bash
   code ~/.bob/settings/mcp_settings.json
   ```

2. **Add the Bear Notes server configuration:**
   ```json
   {
     "mcpServers": {
       "bear-notes": {
         "command": "python",
         "args": ["-m", "mcp_bear_notes.server"]
       }
     }
   }
   ```

3. **Save and restart Bob** to load the new server.

### For Claude Desktop

1. **Open Claude's config file:**
   ```bash
   code ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Add the same configuration as above.**

3. **Restart Claude Desktop.**

## Testing the Server

### Using MCP Inspector

The MCP Inspector is a great tool for testing your server:

```bash
npx @modelcontextprotocol/inspector python -m mcp_bear_notes.server
```

This will open a web interface where you can:
- View available tools
- Test tool calls
- Inspect resources
- Debug server responses

### Manual Testing

Once configured in Bob or Claude, try these commands:

1. **List recent notes:**
   ```
   "Show me my recent Bear notes"
   ```

2. **Search notes:**
   ```
   "Search my Bear notes for 'project'"
   ```

3. **Create a note:**
   ```
   "Create a Bear note titled 'Test Note' with content 'This is a test'"
   ```

4. **Get a specific note:**
   ```
   "Get my Bear note titled 'Test Note'"
   ```

5. **Delete a note:**
   ```
   "Delete my Bear note titled 'Test Note'"
   ```

## Docker Usage

### Running with Docker

```bash
docker run --rm -i \
  -v "$HOME/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear:/bear-data:ro" \
  mcp-bear-notes
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Docker Configuration in MCP Settings

```json
{
  "mcpServers": {
    "bear-notes": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/Users/YOUR_USERNAME/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear:/bear-data:ro",
        "mcp-bear-notes"
      ]
    }
  }
}
```

## Troubleshooting

### Server Won't Start

**Issue:** `Bear database not found`

**Solution:** 
- Ensure Bear is installed
- Open Bear at least once to create the database
- Verify the database path exists:
  ```bash
  ls -la "$HOME/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
  ```

### Notes Not Updating

**Issue:** Changes don't appear in Bear

**Solution:**
- Ensure Bear is running
- The server uses Bear's URL scheme which requires Bear to be open
- Try restarting Bear if issues persist

### Docker Permission Issues

**Issue:** Docker can't access the Bear database

**Solution:**
- Verify the volume mount path in docker-compose.yml
- Ensure Docker has permission to access the directory
- Check Docker Desktop settings for file sharing permissions

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
pip install mcp
```

## Available Tools

Once running, the server provides these tools:

- `search_notes` - Search notes by content
- `get_note` - Get a specific note
- `create_note` - Create a new note
- `update_note` - Update existing note
- `upsert_note` - Create or update
- `delete_note` - Delete a note
- `list_recent_notes` - List recent notes
- `open_note` - Open in Bear app
- `add_tags` - Add tags to a note

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [Bear URL Scheme documentation](https://bear.app/faq/x-callback-url-scheme-documentation/)
- Check out the source code in `src/mcp_bear_notes/`

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the Bear Notes database location
- Ensure all dependencies are installed
- Test with the MCP Inspector

Happy note-taking! 🐻📝