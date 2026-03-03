# MCP Bear Notes Server

A Model Context Protocol (MCP) server for seamless Bear Notes integration. This server provides tools and resources to interact with Bear Notes through the MCP protocol, enabling AI assistants to create, read, update, and manage your Bear notes.

## Features

### 🔧 Tools

- **search_notes** - Search notes by title or content with customizable result limits
- **get_note** - Retrieve a specific note by its exact title
- **create_note** - Create new notes with markdown content and optional tags
- **update_note** - Update existing note content
- **upsert_note** - Create or update notes (intelligent merge operation)
- **delete_note** - Move notes to trash
- **list_recent_notes** - List recently modified notes
- **open_note** - Open notes directly in the Bear app
- **add_tags** - Add tags to existing notes

### 📚 Resources

- **bear://notes/recent** - JSON resource providing the 20 most recently modified notes

## Architecture

This MCP server uses a **hybrid approach** for optimal performance:

- **Reads**: Direct SQLite database queries for fast, non-intrusive access
- **Writes**: Bear's official URL scheme for instant updates that appear immediately in the app

This design ensures:
- ✅ Instant visual feedback in Bear
- ✅ Fast read operations
- ✅ Officially supported integration
- ✅ No database corruption risks

## Requirements

- **macOS** (Bear is macOS/iOS only)
- **Bear Notes** installed and running
- **Python 3.11.14** (managed via pyenv)
- **pyenv** for Python version management
- **uv** for fast package installation
- **Bear database** accessible at standard location

## Installation

### Quick Start (Recommended)

Run the automated setup script:

```bash
cd /path/to/mcp-bear-notes
./setup.sh
```

This will:
- Install pyenv and uv (if needed)
- Install Python 3.11.14
- Create a virtual environment
- Install all dependencies

Then activate the environment:
```bash
source .venv/bin/activate
```

### Manual Installation

1. Install pyenv and uv:
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Navigate to the project:
```bash
cd /path/to/mcp-bear-notes
```

3. Install Python 3.11.14 and create virtual environment:
```bash
pyenv install 3.11.14
pyenv local 3.11.14
uv venv --python 3.11.14
source .venv/bin/activate
```

4. Install the package with uv:
```bash
uv pip install -e .
```

### Docker Installation

Build the Docker image:
```bash
docker build -t mcp-bear-notes .
```

Or use docker-compose:
```bash
docker-compose build
```

## Configuration

### For Bob (MCP Client)

Add to your MCP settings file (`~/.bob/settings/mcp_settings.json`):

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

### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Docker Configuration

For Docker deployment, mount the Bear database directory:

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

Or use docker-compose:

```bash
docker-compose up -d
```

## Usage Examples

Once configured, you can use the MCP server through your AI assistant:

### Search for Notes
```
"Search my Bear notes for 'project ideas'"
```

### Create a Note
```
"Create a Bear note titled 'Meeting Notes' with the following content: ..."
```

### Update a Note
```
"Update my 'TODO List' note in Bear with these new items: ..."
```

### List Recent Notes
```
"Show me my 20 most recent Bear notes"
```

### Delete a Note
```
"Delete the Bear note titled 'Old Draft'"
```

### Add Tags
```
"Add tags 'work' and 'urgent' to my 'Project Plan' note"
```

## Development

### Project Structure

```
mcp-bear-notes/
├── src/
│   └── mcp_bear_notes/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # MCP server implementation
│       └── bear_client.py       # Bear Notes client library
├── pyproject.toml               # Python project configuration
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
├── .dockerignore               # Docker build exclusions
└── README.md                    # This file
```

### Running Locally

For development and testing:

```bash
# Install in development mode
pip install -e .

# Run the server directly
python -m mcp_bear_notes.server
```

### Testing with MCP Inspector

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python -m mcp_bear_notes.server
```

## Docker Details

### Building the Image

```bash
docker build -t mcp-bear-notes .
```

### Running with Docker

```bash
docker run --rm -i \
  -v "/Users/YOUR_USERNAME/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear:/bear-data:ro" \
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

## Bear URL Scheme Reference

This server uses Bear's official URL scheme for write operations:

- **Create/Update**: `bear://x-callback-url/create?title=...&text=...`
- **Add Text**: `bear://x-callback-url/add-text?id=...&text=...&mode=replace`
- **Trash**: `bear://x-callback-url/trash?id=...`
- **Open Note**: `bear://x-callback-url/open-note?id=...`

For more information: [Bear URL Scheme Documentation](https://bear.app/faq/x-callback-url-scheme-documentation/)

## Database Schema

The server reads from Bear's SQLite database (`database.sqlite`) with the following key fields:

- `ZUNIQUEIDENTIFIER` - Note UUID
- `ZTITLE` - Note title
- `ZTEXT` - Note content (markdown)
- `ZCREATIONDATE` - Creation timestamp (Apple Core Data format)
- `ZMODIFICATIONDATE` - Modification timestamp
- `ZTRASHED` - Trash status (0 = active, 1 = trashed)
- `ZARCHIVED` - Archive status

## Troubleshooting

### Bear Database Not Found

**Error**: `Bear database not found at ...`

**Solution**: Ensure Bear is installed and has been opened at least once. The database is created on first launch.

### Permission Denied

**Error**: Permission errors when accessing the database

**Solution**: Ensure your user has read access to the Bear database directory. For Docker, verify volume mount permissions.

### Notes Not Updating in Bear

**Issue**: Changes don't appear immediately in Bear

**Solution**: This server uses Bear's URL scheme for writes, which should update instantly. Ensure Bear is running. If issues persist, try restarting Bear.

### Docker Container Can't Access Database

**Issue**: Docker container reports database not found

**Solution**: Verify the volume mount path matches your Bear database location. The path may vary based on your macOS version and Bear installation.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this in your own projects.

## Acknowledgments

- Built with the [Model Context Protocol SDK](https://github.com/modelcontextprotocol)
- Inspired by the [public mcp-bear server](https://github.com/jkawamoto/mcp-bear)
- Uses [Bear Notes](https://bear.app) official URL scheme

## Author

YOUR_NAME

## Version

0.1.0 - Initial release