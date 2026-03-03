"""
Bear Notes Client Module

Provides functionality to interact with Bear notes via its SQLite database
and URL scheme for updates.
"""

import sqlite3
import subprocess
import urllib.parse
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import time


class BearNotesClient:
    """Interface to Bear notes using URL scheme for updates and SQLite for reads."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize Bear notes interface.

        Args:
            db_path: Path to Bear database. Defaults to standard Bear location.
                    Can be overridden with BEAR_DB_PATH environment variable.
        """
        if db_path is None:
            # Check for environment variable first (for Docker)
            env_path = os.environ.get('BEAR_DB_PATH')
            if env_path:
                db_path = Path(env_path)
            else:
                # Default to standard macOS Bear location
                db_path = Path.home() / "Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"

        self.db_path = db_path

        if not self.db_path.exists():
            raise FileNotFoundError(f"Bear database not found at {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection for reading."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _open_bear_url(self, url: str) -> bool:
        """
        Open a Bear URL scheme.

        Args:
            url: Bear URL scheme (e.g., bear://x-callback-url/create?...)

        Returns:
            True if successful

        Raises:
            Exception: If the URL scheme fails to execute
        """
        try:
            subprocess.run(['open', url], check=True, capture_output=True)
            # Give Bear a moment to process
            time.sleep(0.2)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error opening Bear URL: {e}")

    def search_notes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for notes by title or content.

        Args:
            query: Search string
            limit: Maximum number of results

        Returns:
            List of matching notes with id, title, text, creation/modification dates
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT ZUNIQUEIDENTIFIER, ZTITLE, ZTEXT,
                       datetime(ZCREATIONDATE + 978307200, 'unixepoch', 'localtime') as creation_date,
                       datetime(ZMODIFICATIONDATE + 978307200, 'unixepoch', 'localtime') as modification_date
                FROM ZSFNOTE
                WHERE (ZTITLE LIKE ? OR ZTEXT LIKE ?)
                  AND ZTRASHED = 0
                  AND ZARCHIVED = 0
                ORDER BY ZMODIFICATIONDATE DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit)
            )

            results = []
            for row in cursor:
                results.append({
                    'id': row['ZUNIQUEIDENTIFIER'],
                    'title': row['ZTITLE'],
                    'text': row['ZTEXT'],
                    'creation_date': row['creation_date'],
                    'modification_date': row['modification_date']
                })

            return results
        finally:
            conn.close()

    def get_note_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Get a note by exact title match.

        Args:
            title: Note title to search for

        Returns:
            Note dict if found, None otherwise
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT ZUNIQUEIDENTIFIER, ZTITLE, ZTEXT,
                       datetime(ZCREATIONDATE + 978307200, 'unixepoch', 'localtime') as creation_date,
                       datetime(ZMODIFICATIONDATE + 978307200, 'unixepoch', 'localtime') as modification_date
                FROM ZSFNOTE
                WHERE ZTITLE = ?
                  AND ZTRASHED = 0
                  AND ZARCHIVED = 0
                ORDER BY ZMODIFICATIONDATE DESC
                LIMIT 1
                """,
                (title,)
            )

            row = cursor.fetchone()
            if row:
                return {
                    'id': row['ZUNIQUEIDENTIFIER'],
                    'title': row['ZTITLE'],
                    'text': row['ZTEXT'],
                    'creation_date': row['creation_date'],
                    'modification_date': row['modification_date']
                }
            return None
        finally:
            conn.close()

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a note by its unique identifier.

        Args:
            note_id: Note UUID

        Returns:
            Note dict if found, None otherwise
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT ZUNIQUEIDENTIFIER, ZTITLE, ZTEXT,
                       datetime(ZCREATIONDATE + 978307200, 'unixepoch', 'localtime') as creation_date,
                       datetime(ZMODIFICATIONDATE + 978307200, 'unixepoch', 'localtime') as modification_date
                FROM ZSFNOTE
                WHERE ZUNIQUEIDENTIFIER = ?
                  AND ZTRASHED = 0
                  AND ZARCHIVED = 0
                LIMIT 1
                """,
                (note_id,)
            )

            row = cursor.fetchone()
            if row:
                return {
                    'id': row['ZUNIQUEIDENTIFIER'],
                    'title': row['ZTITLE'],
                    'text': row['ZTEXT'],
                    'creation_date': row['creation_date'],
                    'modification_date': row['modification_date']
                }
            return None
        finally:
            conn.close()

    def create_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> str:
        """
        Create a new Bear note using URL scheme.

        Args:
            title: Note title
            content: Note content (markdown)
            tags: Optional list of tags to add

        Returns:
            Note title (URL scheme doesn't return ID immediately)
        """
        # Bear adds the title automatically, just use content
        full_content = content

        if tags:
            tag_string = " ".join(f"#{tag.strip('#')}" for tag in tags)
            full_content += f"\n\n{tag_string}"

        # Encode for URL
        encoded_title = urllib.parse.quote(title)
        encoded_content = urllib.parse.quote(full_content)

        # Use Bear's URL scheme
        url = f"bear://x-callback-url/create?title={encoded_title}&text={encoded_content}&open_note=no"

        if self._open_bear_url(url):
            return title
        else:
            raise Exception("Failed to create note in Bear")

    def update_note(self, note_id: str, content: str, title: Optional[str] = None) -> bool:
        """
        Update an existing note's content using URL scheme.

        Args:
            note_id: Note UUID or title
            content: New content (markdown)
            title: Optional new title (must match existing title to update)

        Returns:
            True if successful
        """
        # Get the actual note to find its UUID
        note = self.get_note_by_title(title if title else note_id)

        if not note:
            # Note doesn't exist, create it
            note_title = title if title else note_id
            encoded_title = urllib.parse.quote(note_title)
            encoded_content = urllib.parse.quote(content)
            url = f"bear://x-callback-url/create?title={encoded_title}&text={encoded_content}&open_note=no"
            return self._open_bear_url(url)

        # Note exists, update by ID
        encoded_id = urllib.parse.quote(note['id'])
        encoded_content = urllib.parse.quote(content)

        # Use Bear's add-text with mode=replace to update the entire note
        url = f"bear://x-callback-url/add-text?id={encoded_id}&text={encoded_content}&mode=replace&open_note=no"

        return self._open_bear_url(url)

    def update_or_create_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> tuple[str, bool]:
        """
        Update a note if it exists (by title), or create it if it doesn't.

        Args:
            title: Note title
            content: Note content (markdown)
            tags: Optional list of tags to add

        Returns:
            Tuple of (note_title, was_created)
        """
        # Check if note exists
        existing = self.get_note_by_title(title)

        # Prepare full content - Bear adds title automatically
        full_content = content
        if tags:
            tag_string = " ".join(f"#{tag.strip('#')}" for tag in tags)
            full_content += f"\n\n{tag_string}"

        if existing:
            # Update existing note by ID
            encoded_id = urllib.parse.quote(existing['id'])
            encoded_content = urllib.parse.quote(full_content)
            url = f"bear://x-callback-url/add-text?id={encoded_id}&text={encoded_content}&mode=replace&open_note=no"

            if self._open_bear_url(url):
                return title, False
            else:
                raise Exception("Failed to update note in Bear")
        else:
            # Create new note
            encoded_title = urllib.parse.quote(title)
            encoded_content = urllib.parse.quote(full_content)
            url = f"bear://x-callback-url/create?title={encoded_title}&text={encoded_content}&open_note=no"

            if self._open_bear_url(url):
                return title, True
            else:
                raise Exception("Failed to create note in Bear")

    def delete_note(self, title: str) -> bool:
        """
        Delete (trash) a note by title using URL scheme.

        Args:
            title: Note title to delete

        Returns:
            True if successful, False if note not found
        """
        # Get the note to find its UUID
        note = self.get_note_by_title(title)

        if not note:
            return False

        # Use Bear's trash URL scheme
        encoded_id = urllib.parse.quote(note['id'])
        url = f"bear://x-callback-url/trash?id={encoded_id}"

        return self._open_bear_url(url)

    def delete_note_by_id(self, note_id: str) -> bool:
        """
        Delete (trash) a note by ID using URL scheme.

        Args:
            note_id: Note UUID to delete

        Returns:
            True if successful
        """
        # Use Bear's trash URL scheme
        encoded_id = urllib.parse.quote(note_id)
        url = f"bear://x-callback-url/trash?id={encoded_id}"

        return self._open_bear_url(url)

    def list_recent_notes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List recently modified notes.

        Args:
            limit: Maximum number of notes to return

        Returns:
            List of notes sorted by modification date (newest first)
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT ZUNIQUEIDENTIFIER, ZTITLE,
                       datetime(ZCREATIONDATE + 978307200, 'unixepoch', 'localtime') as creation_date,
                       datetime(ZMODIFICATIONDATE + 978307200, 'unixepoch', 'localtime') as modification_date
                FROM ZSFNOTE
                WHERE ZTRASHED = 0
                  AND ZARCHIVED = 0
                ORDER BY ZMODIFICATIONDATE DESC
                LIMIT ?
                """,
                (limit,)
            )

            results = []
            for row in cursor:
                results.append({
                    'id': row['ZUNIQUEIDENTIFIER'],
                    'title': row['ZTITLE'],
                    'creation_date': row['creation_date'],
                    'modification_date': row['modification_date']
                })

            return results
        finally:
            conn.close()

    def open_note(self, title: str) -> bool:
        """
        Open a note in the Bear app.

        Args:
            title: Note title to open

        Returns:
            True if successful, False if note not found
        """
        note = self.get_note_by_title(title)
        if not note:
            return False

        encoded_id = urllib.parse.quote(note['id'])
        url = f"bear://x-callback-url/open-note?id={encoded_id}"

        return self._open_bear_url(url)

    def add_tags_to_note(self, title: str, tags: List[str]) -> bool:
        """
        Add tags to an existing note.

        Args:
            title: Note title
            tags: List of tags to add

        Returns:
            True if successful, False if note not found
        """
        note = self.get_note_by_title(title)
        if not note:
            return False

        # Add tags to the end of the note content
        tag_string = " ".join(f"#{tag.strip('#')}" for tag in tags)
        new_content = f"{note['text']}\n\n{tag_string}"

        return self.update_note(note['id'], new_content, title)

# Made with Bob
