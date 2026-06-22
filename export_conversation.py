#!/usr/bin/env python3
"""
Export a Claude Code conversation from its JSONL transcript to a readable
markdown file.

Usage:
    python3 export_conversation.py <session-id> [output.md]

The JSONL file is read from:
    ~/.claude/projects/<project-slug>/<session-id>.jsonl

The project slug is derived from the current working directory. You can also
pass a full path to the JSONL file directly as the session-id argument.

Example:
    python3 export_conversation.py 6ce33bc7-4ea8-4c90-88a2-0e0c644df43d
    python3 export_conversation.py 6ce33bc7-... conversation.md
"""
import json
import os
import re
import sys
from pathlib import Path


# Only the first 5 characters of each secret are stored here.
# The pattern matches the prefix followed by any word characters,
# so the full token is redacted without the full secret being in this file.
SECRET_PREFIXES = [
    'SLP6Y',  # Visual Crossing API key
    'b7b91',  # Strava client secret
    '3ff8b',  # Strava refresh token
]


def redact(text: str) -> str:
    for prefix in SECRET_PREFIXES:
        text = re.sub(re.escape(prefix) + r'\w*', '******', text, flags=re.IGNORECASE)
    return text


def extract_text(content) -> str:
    """Return human-readable text from a message content block."""
    if isinstance(content, str):
        return redact(content)
    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get('type')
        if btype == 'text':
            parts.append(block.get('text', ''))
        elif btype == 'tool_use':
            name = block.get('name', 'tool')
            inp = block.get('input', {})
            if name in ('Bash', 'bash'):
                cmd = inp.get('command', '')[:120]
                parts.append(f'  ● Bash({cmd})')
            elif name in ('Write', 'Edit'):
                path = inp.get('file_path', inp.get('path', ''))
                parts.append(f'  ● {name}({path})')
            elif name == 'Read':
                path = inp.get('file_path', inp.get('path', ''))
                parts.append(f'  ● Read({path})')
            else:
                parts.append(f'  ● {name}(...)')
        # skip: thinking, tool_result, system_reminder, etc.
    return redact('\n'.join(parts))


def has_text_block(content) -> bool:
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        return any(
            isinstance(b, dict) and b.get('type') == 'text'
            for b in content
        )
    return False


def resolve_jsonl(session_id: str) -> Path:
    """Find the JSONL file for the given session id."""
    p = Path(session_id)
    if p.exists():
        return p

    # Derive project slug from cwd
    cwd = Path.cwd()
    slug = str(cwd).replace('/', '-').lstrip('-')
    candidate = Path.home() / '.claude' / 'projects' / slug / f'{session_id}.jsonl'
    if candidate.exists():
        return candidate

    # Fall back: search all project dirs
    projects = Path.home() / '.claude' / 'projects'
    if projects.exists():
        matches = list(projects.glob(f'*/{session_id}.jsonl'))
        if matches:
            return matches[0]

    raise FileNotFoundError(
        f'Cannot find JSONL for session {session_id!r}.\n'
        f'Tried: {candidate}'
    )


def export(jsonl_path: Path, out_path: Path) -> None:
    with open(jsonl_path) as f:
        records = [json.loads(line) for line in f]

    seen = set()
    prev_role = None
    lines = []

    lines.append('# CBN App — Conversation Export\n')
    lines.append(f'*Source: {jsonl_path}*\n')
    lines.append('---\n')

    for obj in records:
        if obj.get('type') not in ('user', 'assistant'):
            continue
        uuid = obj.get('uuid')
        if uuid:
            if uuid in seen:
                continue
            seen.add(uuid)

        msg = obj.get('message', {})
        role = msg.get('role')
        content = msg.get('content', '')
        text = extract_text(content).strip()

        if not text:
            continue

        if role == 'user':
            if not has_text_block(content):
                continue
            lines.append(f'> **You:** {text}\n')
        elif role == 'assistant':
            lines.append(f'{text}\n')

        prev_role = role

    out_path.write_text('\n'.join(lines))
    print(f'Wrote {len(lines)} blocks to {out_path}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    session_id = sys.argv[1]
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('conversation.md')

    jsonl = resolve_jsonl(session_id)
    print(f'Reading: {jsonl}')
    export(jsonl, output)
