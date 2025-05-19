# MCP FileManager Server

This project provides a file management server using the **MCP (Modular Command Platform)** framework. It exposes tools for listing, searching, organizing, and reading files in a directory, with built-in rules for file organization and text file support.

## Features

- **List Files**  
  List all files in a specified directory, including metadata:
  - Name
  - Extension
  - Size
  - Modified time

- **Search Files**  
  Search for files by name or extension (recursively).

- **Organize Files**  
  Automatically move files into categorized folders based on their extension:
  - Documents
  - Images
  - Music
  - Videos

- **Read File Content**  
  Read and return the content of supported text files:
  - `.txt`, `.md`, `.py`, `.json`, `.csv`  
  Includes:
  - Encoding fallback
  - Content length limit

- **Prompt Formatting**  
  Summarize file lists or display file content in a user-friendly format, including robust error handling.
