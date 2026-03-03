#!/usr/bin/env python3
"""
Bear Notes MCP Server

Provides Model Context Protocol tools and resources for Bear Notes integration.
"""

import asyncio
import logging
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl
import mcp.server.stdio

from .bear_client import BearNotesClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-bear-notes")

# Initialize Bear client
try:
    bear = BearNotesClient()
    logger.info("Bear Notes client initialized successfully")
except FileNotFoundError as e:
    logger.error(f"Failed to initialize Bear client: {e}")
    bear = None

# Create server instance
app = Server("mcp-bear-notes")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_notes",
            description="Search Bear notes by title or content. Returns matching notes with their metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string to match against note titles and content"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10, max: 50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_note",
            description="Get a specific Bear note by its exact title. Returns the full note content and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Exact title of the note to retrieve"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="create_note",
            description="Create a new Bear note with the specified title, content, and optional tags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title for the new note"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content of the note in Markdown format"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags to add to the note (without # prefix)"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="update_note",
            description="Update an existing Bear note's content. The note is identified by its title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note to update"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content for the note in Markdown format"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="upsert_note",
            description="Create a new note or update an existing one (upsert operation). If a note with the title exists, it will be updated; otherwise, a new note will be created.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content of the note in Markdown format"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags to add to the note (without # prefix)"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="delete_note",
            description="Delete (trash) a Bear note by its title. The note will be moved to Bear's trash.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note to delete"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_recent_notes",
            description="List recently modified Bear notes, sorted by modification date (newest first).",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of notes to return (default: 20, max: 100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    }
                }
            }
        ),
        Tool(
            name="open_note",
            description="Open a Bear note in the Bear application by its title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note to open in Bear"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="add_tags",
            description="Add tags to an existing Bear note. Tags will be appended to the note content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note to add tags to"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tags to add (without # prefix)"
                    }
                },
                "required": ["title", "tags"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    if bear is None:
        return [TextContent(
            type="text",
            text="Error: Bear Notes client not initialized. Please ensure Bear is installed and the database is accessible."
        )]

    try:
        if name == "search_notes":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            results = bear.search_notes(query=query, limit=limit)
            
            if not results:
                return [TextContent(
                    type="text",
                    text=f"No notes found matching '{query}'"
                )]
            
            response = f"Found {len(results)} note(s) matching '{query}':\n\n"
            for i, note in enumerate(results, 1):
                response += f"{i}. **{note['title']}**\n"
                response += f"   - Modified: {note['modification_date']}\n"
                response += f"   - ID: {note['id']}\n"
                # Show first 100 chars of content
                preview = note['text'][:100].replace('\n', ' ')
                if len(note['text']) > 100:
                    preview += "..."
                response += f"   - Preview: {preview}\n\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "get_note":
            title = arguments["title"]
            note = bear.get_note_by_title(title)
            
            if not note:
                return [TextContent(
                    type="text",
                    text=f"Note '{title}' not found"
                )]
            
            response = f"# {note['title']}\n\n"
            response += f"**ID:** {note['id']}\n"
            response += f"**Created:** {note['creation_date']}\n"
            response += f"**Modified:** {note['modification_date']}\n\n"
            response += "---\n\n"
            response += note['text']
            
            return [TextContent(type="text", text=response)]
        
        elif name == "create_note":
            title = arguments["title"]
            content = arguments["content"]
            tags = arguments.get("tags")
            
            result_title = bear.create_note(
                title=title,
                content=content,
                tags=tags
            )
            
            tag_info = f" with tags: {', '.join(tags)}" if tags else ""
            return [TextContent(
                type="text",
                text=f"✅ Created note: '{result_title}'{tag_info}"
            )]
        
        elif name == "update_note":
            title = arguments["title"]
            content = arguments["content"]
            
            success = bear.update_note(
                note_id=title,
                content=content,
                title=title
            )
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"✅ Updated note: '{title}'"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to update note: '{title}'"
                )]
        
        elif name == "upsert_note":
            title = arguments["title"]
            content = arguments["content"]
            tags = arguments.get("tags")
            
            result_title, created = bear.update_or_create_note(
                title=title,
                content=content,
                tags=tags
            )
            
            action = "Created" if created else "Updated"
            tag_info = f" with tags: {', '.join(tags)}" if tags else ""
            return [TextContent(
                type="text",
                text=f"✅ {action} note: '{result_title}'{tag_info}"
            )]
        
        elif name == "delete_note":
            title = arguments["title"]
            success = bear.delete_note(title)
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"✅ Deleted note: '{title}' (moved to trash)"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Note '{title}' not found"
                )]
        
        elif name == "list_recent_notes":
            limit = arguments.get("limit", 20)
            notes = bear.list_recent_notes(limit=limit)
            
            if not notes:
                return [TextContent(
                    type="text",
                    text="No notes found"
                )]
            
            response = f"Recent notes ({len(notes)}):\n\n"
            for i, note in enumerate(notes, 1):
                response += f"{i}. **{note['title']}**\n"
                response += f"   - Modified: {note['modification_date']}\n"
                response += f"   - Created: {note['creation_date']}\n\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "open_note":
            title = arguments["title"]
            success = bear.open_note(title)
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"✅ Opened note: '{title}' in Bear"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Note '{title}' not found"
                )]
        
        elif name == "add_tags":
            title = arguments["title"]
            tags = arguments["tags"]
            
            success = bear.add_tags_to_note(title, tags)
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"✅ Added tags to note '{title}': {', '.join(tags)}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Note '{title}' not found"
                )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Error in {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri=AnyUrl("bear://notes/recent"),
            name="Recent Bear Notes",
            mimeType="application/json",
            description="List of recently modified Bear notes (last 20)"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read a resource."""
    if bear is None:
        return json.dumps({"error": "Bear Notes client not initialized"})
    
    try:
        if str(uri) == "bear://notes/recent":
            notes = bear.list_recent_notes(limit=20)
            return json.dumps(notes, indent=2)
        
        raise ValueError(f"Unknown resource: {uri}")
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def main():
    """Run the MCP server."""
    logger.info("Starting Bear Notes MCP server...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()

# Made with Bob
