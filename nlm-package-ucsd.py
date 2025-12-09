yaml_block = """
---
title: "Packaging and Transferring Obsidian Vault to NotebookLM"
tags: [tbd]
author: "Matthew C. Vanderbilt"
note: "Coding supported with GitHub Copilot"
date: 2024-06-10
---
"""

# ------------------------------------------------------
# load libraries

import os                   # interaction with operating system
import re                   # regular expressions for pattern matching
import yaml                 # Parsing YAML files into Python dictionaries
from datetime import datetime               # handling date and time
from collections import defaultdict, deque  # specialized data structures

# ------------------------------------------------------
# set global variables

PATH_VAULT = r"O:\OneDrive\Documents\GitHub\UCSD-DOM-Business-Office"
PATH_NLM = r"N:\My Drive\NotebookLM\UCSD-DOM-Business-Office"
FILE_TAGS = os.path.join(VAULT_PATH, "tags.md")
FILE_INDEX = os.path.join(EXPORT_PATH, "tags_index.md")
FILE_LOG = os.path.join(VAULT_PATH, "pipeline_log.md")

MAX_RUNS = 7  # keep last 7 runs in summary
COPYRIGHT_HEADER = f"© {datetime.now().year} Matthew C. Vanderbilt. All Rights Reserved.\n\n"

# ------------------------------------------------------
# define functions

# function to remove Obsidian-specific syntax (wikilinks, embeds)
def clean_content(content):
    content = re.sub(r"\[\[(.*?)\]\]", r"\1", content)  # wikilinks
    content = re.sub(r"!\[\[(.*?)\]\]", r"\1", content) # embeds
    return content

# function to read YAML frontmatter and extract any tags
def extract_tags_from_file(filepath):
    tags = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"---(.*?)---", content, re.DOTALL) # uses REGEX to identify YAML frontmatter
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1)) # parses YAML frontmatter
            if frontmatter and "tags" in frontmatter:
                tags = frontmatter["tags"]
                if isinstance(tags, str):
                    tags = [tags]
        except Exception:
            pass
    return tags

# function to load tags from manual tag governance file
def load_existing_tags():
    existing_tags = set() # empty set object, which automatically avoids duplicates
    if os.path.exists(FILE_TAGS): # looks for existing tags file
        with open(FILE_TAGS, "r", encoding="utf-8") as f: # opens the existing file read-only
            for line in f:
                match = re.match(r"-\s*(\w+)", line.strip()) # uses REGEX to identify bulleted tags
                if match:
                    existing_tags.add(match.group(1)) # adds tags to variable set
    return existing_tags












# ------------------------------------------------------
# ------------------------------------------------------
# ------------------------------------------------------


import os
import re
import yaml
from datetime import datetime
from collections import defaultdict, deque

# Paths
PATH_VAULT = r"O:\OneDrive\Documents\GitHub\UCSD-DOM-Business-Office"   # your Obsidian vault
PATH_NLM   = r"N:\My Drive\NotebookLM\UCSD-DOM-Business-Office"         # staging folder inside Google Drive
FILE_TAGS  = os.path.join(PATH_VAULT, "tags.md")                        # curated tags file
FILE_INDEX = os.path.join(PATH_NLM, "tags_index.md")                    # auto-generated taxonomy index
FILE_LOG   = os.path.join(PATH_VAULT, "pipeline_log.md")                # nightly log inside Obsidian vault

COPYRIGHT_HEADER = f"© {datetime.now().year} Matthew C. Vanderbilt. All Rights Reserved.\n\n"
MAX_RUNS = 7  # keep last 7 runs in summary

def clean_content(content):
    content = re.sub(r"

\[

\[(.*?)\]

\]

", r"\1", content)  # wikilinks
    content = re.sub(r"!

\[

\[(.*?)\]

\]

", r"\1", content) # embeds
    return content

def extract_tags_from_file(filepath):
    tags = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"---(.*?)---", content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            if frontmatter and "tags" in frontmatter:
                tags = frontmatter["tags"]
                if isinstance(tags, str):
                    tags = [tags]
        except Exception:
            pass
    return tags

def load_existing_tags():
    existing_tags = set()
    if os.path.exists(FILE_TAGS):
        with open(FILE_TAGS, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(r"-\s*(\w+)", line.strip())
                if match:
                    existing_tags.add(match.group(1))
    return existing_tags

def export_and_index():
    if not os.path.exists(PATH_NLM):
        os.makedirs(PATH_NLM)

    tag_map = defaultdict(list)
    existing_tags = load_existing_tags()
    exported_files = []

    for root, _, files in os.walk(PATH_VAULT):
        for file in files:
            if file.endswith(".md") and file not in ["tags.md", "pipeline_log.md"]:
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                cleaned = clean_content(content)
                final_text = COPYRIGHT_HEADER + cleaned

                export_file = os.path.join(PATH_NLM, file)
                with open(export_file, "w", encoding="utf-8") as f:
                    f.write(final_text)

                exported_files.append(file)

                # Collect tags from YAML
                tags = extract_tags_from_file(filepath)
                for tag in tags:
                    tag_map[tag].append(file)

    # Merge with curated tags
    for tag in existing_tags:
        if tag not in tag_map:
            tag_map[tag] = []

    # Write taxonomy index
    with open(FILE_INDEX, "w", encoding="utf-8") as f:
        f.write(COPYRIGHT_HEADER)
        f.write("# Tag Index\n\n")
        for tag, files in sorted(tag_map.items()):
            f.write(f"## {tag}\n")
            for file in sorted(files):
                f.write(f"- {file}\n")
            f.write("\n")

    # Load previous runs (if any)
    runs = deque(maxlen=MAX_RUNS)
    if os.path.exists(FILE_LOG):
        with open(FILE_LOG, "r", encoding="utf-8") as f:
            content = f.read()
        past_runs = re.findall(r"(## Run.*?)(?=\n## Run|\Z)", content, re.DOTALL)
        for run in past_runs:
            runs.append(run.strip())

    # Add current run
    run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_run = f"## Run {run_time}\n\n**Exported files:** {len(exported_files)}\n" \
                  + "".join([f"- {file}\n" for file in exported_files]) \
                  + f"\n**Tags indexed:** {len(tag_map)}\n"
    runs.append(current_run)

    # Write new log file (overwrite)
    with open(FILE_LOG, "w", encoding="utf-8") as log:
        log.write(COPYRIGHT_HEADER)
        log.write("# Pipeline Log\n\n")
        log.write("## Summary (Last 7 Runs)\n\n")
        for run in runs:
            header = run.split("\n")[0]
            log.write(f"- {header}\n")
        log.write("\n---\n\n")
        log.write("\n\n".join(runs))

    print("Export + merged taxonomy index complete. Markdown log updated with 7-run summary.")

if __name__ == "__main__":
    export_and_index()
