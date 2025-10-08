#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Documentation generator for Gemini meetup workshop subprojects.

Analyzes git commit history using LLMs to generate comprehensive NOTES.md files
and user-facing README.md files for each subproject.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Import from parent directory's utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.model import make_gemini


def run_git_command(cmd: List[str], cwd: str = ".") -> str:
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        return ""


def get_commit_history(subdir: str) -> List[Dict[str, str]]:
    """Get chronological commit history for a subdirectory."""
    # Get commit hashes in reverse chronological order (oldest first)
    log_output = run_git_command([
        "git", "log", "--reverse", "--oneline", "--", subdir
    ])
    
    if not log_output:
        print(f"No commit history found for {subdir}")
        return []
    
    commits = []
    for line in log_output.split('\n'):
        if line.strip():
            parts = line.split(' ', 1)
            if len(parts) >= 2:
                commit_hash = parts[0]
                commit_title = parts[1]
                
                # Get full commit details
                full_commit = run_git_command([
                    "git", "show", commit_hash, "--", subdir
                ])
                
                commits.append({
                    "hash": commit_hash,
                    "title": commit_title,
                    "full_diff": full_commit
                })
    
    return commits


def analyze_commit_with_llm(commit: Dict[str, str], existing_docs: str = "") -> str:
    """Analyze a commit using LLM to generate a NOTES.md entry."""
    llm = make_gemini()
    
    prompt = f"""You are analyzing git commits to create development documentation. 

Your task: Write a detailed NOTES.md entry for this commit that captures the development story.

Focus on:
- What problem was being solved
- The technical approach taken
- Key architectural decisions made
- Challenges that were overcome
- Implementation details that matter

Write in the style of technical development notes - detailed but engaging, like you're explaining to a fellow developer what happened.

Existing project context:
{existing_docs[:1000] if existing_docs else "No existing documentation provided."}

Commit to analyze:
Hash: {commit['hash']}
Title: {commit['title']}

Full commit diff:
{commit['full_diff']}

Write a comprehensive but focused NOTES.md entry (2-4 paragraphs) for this commit:"""

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"LLM analysis failed for commit {commit['hash']}: {e}")
        return f"## {commit['title']}\n\nCommit {commit['hash']} - Analysis failed: {e}\n"


def load_existing_docs(subdir: str) -> str:
    """Load existing documentation files for context."""
    docs_content = []
    
    # Common documentation files to check
    doc_files = [
        "README.md", "NOTES.md", "FRICTION-LOG.md", 
        "TODO.md", "CHANGELOG.md"
    ]
    
    # Check main directory
    for doc_file in doc_files:
        doc_path = Path(subdir) / doc_file
        if doc_path.exists():
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    docs_content.append(f"=== {doc_file} ===\n{content}\n")
            except Exception as e:
                print(f"Could not read {doc_path}: {e}")
    
    # Also check notes/ subdirectory for additional NOTES files
    notes_dir = Path(subdir) / "notes"
    if notes_dir.exists() and notes_dir.is_dir():
        for notes_file in notes_dir.glob("NOTES*.md"):
            try:
                with open(notes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    docs_content.append(f"=== notes/{notes_file.name} ===\n{content}\n")
            except Exception as e:
                print(f"Could not read {notes_file}: {e}")
    
    return "\n".join(docs_content)


def generate_notes_file(subdir: str, commits: List[Dict[str, str]], existing_docs: str) -> str:
    """Generate comprehensive NOTES.md content from commit analysis."""
    notes_content = [
        f"# {subdir.title()} Development Notes\n",
        f"Generated from git commit history on {datetime.now().strftime('%Y-%m-%d')}\n",
        "## Development Timeline\n"
    ]
    
    print(f"Analyzing {len(commits)} commits for {subdir}...")
    
    for i, commit in enumerate(commits, 1):
        print(f"  [{i}/{len(commits)}] Analyzing {commit['hash']}: {commit['title']}")
        
        # Get LLM analysis of this commit
        analysis = analyze_commit_with_llm(commit, existing_docs)
        
        # Add to notes with proper formatting
        notes_content.append(f"### Commit {i}: {commit['title']} ({commit['hash']})\n")
        notes_content.append(f"{analysis}\n")
    
    return "\n".join(notes_content)


def generate_readme_from_notes(subdir: str, notes_content: str, existing_docs: str) -> str:
    """Generate user-facing README.md from comprehensive NOTES.md."""
    llm = make_gemini()
    
    prompt = f"""You are creating a user-facing README.md file for a workshop project.

Your task: Distill the comprehensive development notes into a clean, professional README.md that explains:

1. **What this project does** (2-3 sentences)
2. **Key features/capabilities** (bullet points)
3. **Quick start/usage** (if applicable)
4. **Technical highlights** (what makes it interesting)
5. **Links to detailed documentation** (NOTES.md, slides if mentioned)

Make it engaging for workshop attendees - they want to understand what this project demonstrates and how to explore it further.

Existing project documentation:
{existing_docs[:1500] if existing_docs else ""}

Development notes to distill:
{notes_content}

Generate a professional README.md:"""

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"README generation failed: {e}")
        return f"# {subdir.title()}\n\nGeneration failed: {e}\n\nSee NOTES.md for detailed development history."


def generate_top_level_readme() -> str:
    """Generate top-level README.md from all subproject READMEs."""
    llm = make_gemini()
    
    # Find all README.md files in subdirectories
    readme_files = []
    for readme_path in Path("..").glob("*/README.md"):
        if readme_path.parent.name != "tools":  # Skip our tools directory
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    readme_files.append({
                        "project": readme_path.parent.name,
                        "content": content
                    })
            except Exception as e:
                print(f"Could not read {readme_path}: {e}")
    
    # Build context for LLM
    project_summaries = []
    for readme in readme_files:
        project_summaries.append(f"=== {readme['project']} ===\n{readme['content'][:800]}...\n")
    
    prompt = f"""You are creating a top-level README.md for the Gemini Meetup Workshops repository.

Your task: Create a comprehensive directory/index that explains what this repository contains and guides users to the right subprojects.

Structure should include:
1. **Repository Overview** - What this is (Gemini meetup workshop collection)
2. **Workshop Directory** - Organized list of all subprojects with brief descriptions
3. **Getting Started** - How to explore the workshops
4. **Categories** - Group similar projects together (AI/ML, Games, Tools, etc.)

Here are all the subproject README contents to summarize:

{chr(10).join(project_summaries)}

Create an engaging, well-organized top-level README.md that serves as the definitive guide to this workshop repository:"""

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"Top-level README generation failed: {e}")
        return "# Gemini Meetup Workshops\n\nFailed to generate overview. See individual project READMEs."


def main():
    parser = argparse.ArgumentParser(description="Generate documentation for workshop subprojects")
    parser.add_argument("subdir", nargs="?", help="Subdirectory to analyze (e.g., '../smash', '../waker')")
    parser.add_argument("--notes-only", action="store_true", help="Generate only NOTES.md, skip README.md")
    parser.add_argument("--readme-only", action="store_true", help="Generate README.md from existing NOTES.md")
    parser.add_argument("--top-level", action="store_true", help="Generate top-level README.md from all subproject READMEs")
    
    args = parser.parse_args()
    
    if args.top_level:
        print("Generating top-level README.md from all subproject READMEs...")
        readme_content = generate_top_level_readme()
        readme_path = Path("..") / "README.md"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ Generated {readme_path}")
        print("🎉 Top-level README.md generation complete!")
        return 0
    
    if not args.subdir:
        print("Error: subdir argument is required unless using --top-level")
        return 1
    
    if not os.path.isdir(args.subdir):
        print(f"Error: Directory '{args.subdir}' does not exist")
        return 1
    
    print(f"Generating documentation for {args.subdir}/")
    
    # Load existing documentation for context
    existing_docs = load_existing_docs(args.subdir)
    
    if args.readme_only:
        # Generate README from existing NOTES.md
        notes_path = Path(args.subdir) / "NOTES.md"
        if not notes_path.exists():
            print(f"Error: {notes_path} does not exist. Run without --readme-only first.")
            return 1
        
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes_content = f.read()
        
        readme_content = generate_readme_from_notes(args.subdir, notes_content, existing_docs)
        
        readme_path = Path(args.subdir) / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ Generated {readme_path}")
        return 0
    
    # Get commit history
    commits = get_commit_history(args.subdir)
    if not commits:
        print(f"No commits found for {args.subdir}")
        return 1
    
    # Generate NOTES.md
    notes_content = generate_notes_file(args.subdir, commits, existing_docs)
    notes_path = Path(args.subdir) / "NOTES.md"
    
    with open(notes_path, 'w', encoding='utf-8') as f:
        f.write(notes_content)
    
    print(f"✅ Generated {notes_path}")
    
    if not args.notes_only:
        # Generate README.md
        readme_content = generate_readme_from_notes(args.subdir, notes_content, existing_docs)
        readme_path = Path(args.subdir) / "README.md"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ Generated {readme_path}")
    
    print(f"\n🎉 Documentation generation complete for {args.subdir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
