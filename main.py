from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Union
import os
import shutil
from pathlib import Path

# Initialize the MCP server
mcp = FastMCP("FileManager", dependencies=["pydantic"])

# Resource: File organization rules and supported text extensions
@mcp.resource("prompts://file-rules")
def get_file_rules() -> Dict[str, Dict[str, str]]:
    """Provide rules for organizing files and supported text extensions."""
    return {
        "organize": {
            ".pdf": "Documents",
            ".docx": "Documents",
            ".jpg": "Images",
            ".png": "Images",
            ".mp3": "Music",
            ".mp4": "Videos"
        },
        "text_extensions": [".txt", ".md", ".py", ".json", ".csv"]  # New: Supported text file types
    }

# Tool: List files in a directory
@mcp.tool()
def list_files(directory: str) -> List[Dict[str, str]]:
    """List files in the specified directory."""
    try:
        directory = Path(directory).resolve()
        if not directory.exists():
            return [{"error": f"Directory {directory} does not exist"}]
        files = []
        for item in directory.iterdir():
            if item.is_file():
                files.append({
                    "name": item.name,
                    "extension": item.suffix.lower(),
                    "size": str(item.stat().st_size),
                    "modified": str(item.stat().st_mtime)
                })
        return files
    except Exception as e:
        return [{"error": f"Failed to list files: {str(e)}"}]

# Tool: Search files by name or extension
@mcp.tool()
def search_files(directory: str, query: str) -> List[Dict[str, str]]:
    """Search files by name or extension in the directory."""
    try:
        directory = Path(directory).resolve()
        if not directory.exists():
            return [{"error": f"Directory {directory} does not exist"}]
        files = []
        query = query.lower()
        for item in directory.rglob("*"):
            if item.is_file() and (query in item.name.lower() or query == item.suffix.lower()):
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "extension": item.suffix.lower()
                })
        return files if files else [{"message": "No files found"}]
    except Exception as e:
        return [{"error": f"Failed to search files: {str(e)}"}]

# Tool: Organize files into folders
@mcp.tool()
def organize_files(directory: str) -> Dict[str, str]:
    """Move files to folders based on extension rules."""
    try:
        directory = Path(directory).resolve()
        if not directory.exists():
            return {"error": f"Directory {directory} does not exist"}
        rules = get_file_rules()["organize"]
        moved = 0
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in rules:
                target_folder = directory / rules[item.suffix.lower()]
                target_folder.mkdir(exist_ok=True)
                shutil.move(str(item), str(target_folder / item.name))
                moved += 1
        return {"status": "success", "message": f"Moved {moved} files"}
    except Exception as e:
        return {"error": f"Failed to organize files: {str(e)}"}

# New Tool: Read file content
@mcp.tool()
def read_file(file_path: str) -> Dict[str, str]:
    """Read the content of a specified file if it's a text file."""
    try:
        file = Path(file_path).resolve()
        if not file.exists():
            return {"error": f"File {file} does not exist"}
        if not file.is_file():
            return {"error": f"{file} is not a file"}
        
        rules = get_file_rules()
        text_extensions = rules["text_extensions"]
        if file.suffix.lower() not in text_extensions:
            return {"error": f"File type {file.suffix} not supported for reading. Supported types: {', '.join(text_extensions)}"}
        
        # Try reading with UTF-8, fall back to latin1 if needed (based on your CSV encoding issue)
        try:
            with file.open("r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with file.open("r", encoding="latin1") as f:
                content = f.read()
        
        # Limit content to 1000 characters to avoid overwhelming the LLM
        if len(content) > 1000:
            content = content[:1000] + "... (truncated)"
        return {"status": "success", "file": file.name, "content": content}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

# Updated Prompt: Handle file lists and content
@mcp.prompt()
def format_file_summary(data: Union[List[Dict[str, str]], Dict[str, str]]) -> List[Dict[str, str]]:
    """Instruct the LLM to summarize files or display file content."""
    if isinstance(data, list):
        # Handle file list (from list_files or search_files)
        summary = "\n".join([f"- {f.get('name', 'Unknown')} ({f.get('extension', '')})" for f in data if "error" not in f])
        return [
            {"role": "user", "content": f"Summarize these files and suggest organization:\n{summary}"},
            {"role": "assistant", "content": "I'll provide a clear summary and suggest how to organize these files."}
        ]
    else:
        # Handle file content (from read_file)
        if "error" in data:
            return [
                {"role": "user", "content": f"Report this error: {data['error']}"},
                {"role": "assistant", "content": "I'll explain the error clearly."}
            ]
        content = data.get("content", "")
        file_name = data.get("file", "Unknown")
        return [
            {"role": "user", "content": f"Display the content of {file_name} clearly, summarizing if too long:\n{content}"},
            {"role": "assistant", "content": f"I'll present the content of {file_name} in a readable format, with a summary if needed."}
        ]

if __name__ == "__main__":
    mcp.run()


