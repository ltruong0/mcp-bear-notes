# Testing Guide - MCP Bear Notes Server

This guide shows you how to test your MCP server using various methods.

## Method 1: MCP Inspector (Recommended - Has UI)

The **MCP Inspector** is the official testing tool from Anthropic that provides a web-based UI similar to FastMCP.

### Quick Start

1. **Activate your virtual environment:**
   ```bash
   cd /path/to/mcp-bear-notes
   source .venv/bin/activate
   ```

2. **Run the MCP Inspector:**
   ```bash
   npx @modelcontextprotocol/inspector python -m mcp_bear_notes.server
   ```

3. **Open your browser:**
   The inspector will automatically open at `http://localhost:5173` (or similar)

### What You'll See in the UI

The MCP Inspector provides:

- **📋 Tools Tab**: List of all 9 tools with their schemas
- **🧪 Test Tools**: Interactive forms to test each tool
- **📚 Resources Tab**: View available resources
- **📊 Logs**: Real-time server logs and responses
- **🔍 Inspector**: JSON request/response viewer

### Testing Your Tools

#### 1. List Recent Notes
```
Tool: list_recent_notes
Parameters: { "limit": 5 }
```

#### 2. Search Notes
```
Tool: search_notes
Parameters: { "query": "test", "limit": 10 }
```

#### 3. Create a Note
```
Tool: create_note
Parameters: {
  "title": "Test Note from MCP Inspector",
  "content": "This is a test note created via the MCP Inspector!",
  "tags": ["test", "mcp"]
}
```

#### 4. Get a Note
```
Tool: get_note
Parameters: { "title": "Test Note from MCP Inspector" }
```

#### 5. Update a Note
```
Tool: update_note
Parameters: {
  "title": "Test Note from MCP Inspector",
  "content": "Updated content via MCP Inspector"
}
```

#### 6. Delete a Note
```
Tool: delete_note
Parameters: { "title": "Test Note from MCP Inspector" }
```

## Method 2: Direct Python Testing

Create a test script to verify functionality:

```python
# test_bear_mcp.py
import asyncio
from mcp_bear_notes.bear_client import BearNotesClient

async def test_bear_client():
    """Test Bear Notes client directly."""
    bear = BearNotesClient()
    
    # Test 1: List recent notes
    print("📋 Recent notes:")
    notes = bear.list_recent_notes(limit=5)
    for note in notes:
        print(f"  - {note['title']}")
    
    # Test 2: Search notes
    print("\n🔍 Searching for 'test':")
    results = bear.search_notes("test", limit=3)
    for note in results:
        print(f"  - {note['title']}")
    
    # Test 3: Create a note
    print("\n✏️  Creating test note...")
    title, created = bear.update_or_create_note(
        title="MCP Test Note",
        content="This is a test note from the MCP server.",
        tags=["mcp", "test"]
    )
    print(f"  {'Created' if created else 'Updated'}: {title}")
    
    # Test 4: Get the note
    print("\n📖 Getting test note...")
    note = bear.get_note_by_title("MCP Test Note")
    if note:
        print(f"  Found: {note['title']}")
        print(f"  Content preview: {note['text'][:50]}...")
    
    # Test 5: Delete the note
    print("\n🗑️  Deleting test note...")
    success = bear.delete_note("MCP Test Note")
    print(f"  {'Success' if success else 'Failed'}")

if __name__ == "__main__":
    asyncio.run(test_bear_client())
```

Run it:
```bash
python test_bear_mcp.py
```

## Method 3: Using Claude Desktop or Bob

Once configured in your MCP client, you can test interactively:

### In Claude Desktop:
```
"List my recent Bear notes"
"Search my Bear notes for 'project'"
"Create a Bear note titled 'Test' with content 'Hello World'"
```

### In Bob:
Same natural language commands work through the MCP protocol.

## Method 4: Manual stdio Testing

For advanced debugging, you can test the stdio interface directly:

```bash
# Start the server
python -m mcp_bear_notes.server

# It will wait for JSON-RPC messages on stdin
# Press Ctrl+C to exit
```

Send a test message (JSON-RPC format):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

## Troubleshooting

### Inspector Won't Start

**Issue**: `npx @modelcontextprotocol/inspector` fails

**Solution**: Ensure Node.js is installed:
```bash
node --version  # Should be v18 or higher
npm --version
```

Install Node.js if needed:
```bash
brew install node
```

### Bear Database Not Found

**Issue**: `Bear database not found`

**Solution**: 
1. Ensure Bear is installed
2. Open Bear at least once to create the database
3. Verify the path:
   ```bash
   ls -la "$HOME/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
   ```

### Virtual Environment Not Activated

**Issue**: `ModuleNotFoundError: No module named 'mcp_bear_notes'`

**Solution**:
```bash
source .venv/bin/activate
```

### Notes Not Appearing in Bear

**Issue**: Created notes don't show up in Bear

**Solution**:
- Ensure Bear is running (URL scheme requires Bear to be open)
- Wait a moment for Bear to process the update
- Try refreshing Bear's note list

## Testing Checklist

Use this checklist to verify all functionality:

- [ ] MCP Inspector opens successfully
- [ ] All 9 tools are listed in the inspector
- [ ] `list_recent_notes` returns notes
- [ ] `search_notes` finds relevant notes
- [ ] `create_note` creates a new note in Bear
- [ ] `get_note` retrieves the created note
- [ ] `update_note` modifies the note content
- [ ] `upsert_note` works for both create and update
- [ ] `delete_note` moves note to trash
- [ ] `open_note` opens Bear app to the note
- [ ] `add_tags` adds tags to existing note
- [ ] Resource `bear://notes/recent` returns JSON

## Performance Testing

Test with larger datasets:

```python
# Create multiple notes
for i in range(10):
    bear.create_note(
        title=f"Performance Test {i}",
        content=f"Test note number {i}",
        tags=["performance", "test"]
    )

# Search performance
import time
start = time.time()
results = bear.search_notes("performance", limit=50)
print(f"Search took {time.time() - start:.3f}s")

# Cleanup
for i in range(10):
    bear.delete_note(f"Performance Test {i}")
```

## Next Steps

After testing:

1. **Configure in Bob/Claude**: Add to MCP settings
2. **Test integration**: Use natural language commands
3. **Monitor logs**: Check for any errors
4. **Optimize**: Adjust based on usage patterns

## Additional Resources

- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Bear URL Scheme Docs](https://bear.app/faq/x-callback-url-scheme-documentation/)

Happy testing! 🐻📝