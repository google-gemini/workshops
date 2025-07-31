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

"""Add screenplay to existing film context document

Takes a screenplay PDF and appends it to an existing comprehensive film context document,
then optionally recreates embeddings with the expanded content.
"""

import sys
import traceback
from pathlib import Path
from typing import Optional

try:
    import pdfplumber
except ImportError:
    print("❌ pdfplumber not installed. Install with: pip install pdfplumber")
    sys.exit(1)


def extract_screenplay_text(pdf_path: str) -> Optional[str]:
    """Extract text from screenplay PDF using pdfplumber

    Args:
        pdf_path: Path to the screenplay PDF file

    Returns:
        Extracted text or None if extraction failed
    """
    try:
        print(f"📄 Extracting text from: {pdf_path}")

        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"❌ PDF file not found: {pdf_path}")
            return None

        text_parts = []
        page_count = 0

        with pdfplumber.open(pdf_path) as pdf:
            print(f"📊 PDF has {len(pdf.pages)} pages")

            for i, page in enumerate(pdf.pages, 1):
                print(f"📄 Processing page {i}/{len(pdf.pages)}...")

                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text.strip())
                    page_count += 1
                else:
                    print(f"⚠️  Page {i} contained no readable text")

        if not text_parts:
            print("❌ No readable text found in PDF")
            return None

        screenplay_text = "\n\n".join(text_parts)
        print(f"✅ Successfully extracted {len(screenplay_text):,} characters from {page_count} pages")

        return screenplay_text

    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        traceback.print_exc()
        return None


def append_screenplay_to_document(context_file: str, screenplay_text: str) -> str:
    """Append screenplay to existing context document

    Args:
        context_file: Path to existing film context document
        screenplay_text: Extracted screenplay text

    Returns:
        Path to the new extended document
    """
    try:
        print(f"📝 Reading existing context document: {context_file}")

        context_path = Path(context_file)
        if not context_path.exists():
            raise FileNotFoundError(f"Context file not found: {context_file}")

        # Read existing document
        with open(context_file, "r", encoding="utf-8") as f:
            existing_content = f.read()

        print(f"📊 Existing document: {len(existing_content):,} characters")

        # Create screenplay section
        screenplay_section = f"""

=== SCREENPLAY ===

{screenplay_text}
"""

        # Combine content
        extended_content = existing_content + screenplay_section

        # Generate new filename
        extended_filename = str(context_path).replace(".txt", "_with_screenplay.txt")

        # Save extended document
        with open(extended_filename, "w", encoding="utf-8") as f:
            f.write(extended_content)

        print(f"💾 Extended document saved to: {extended_filename}")
        print(f"📊 New document size: {len(extended_content):,} characters")
        print(f"📊 Screenplay added: {len(screenplay_text):,} characters")

        return extended_filename

    except Exception as e:
        print(f"❌ Document extension failed: {e}")
        traceback.print_exc()
        raise


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 3:
        print("Usage: python add_screenplay.py <screenplay.pdf> <context_file.txt>")
        print("Example: python add_screenplay.py Big_Sleep.pdf The_Big_Sleep_1946_context.txt")
        print()
        print("This will:")
        print("1. Extract text from the screenplay PDF")
        print("2. Append it to the existing film context document")
        print("3. Create a new '_with_screenplay.txt' file")
        print()
        print("Next steps:")
        print("- Run create_embeddings.py on the new extended document")
        print("- Update your TV companion to use the new embeddings file")
        sys.exit(1)

    pdf_path = sys.argv[1]
    context_file = sys.argv[2]

    print("🎬 Adding screenplay to film context document")
    print("=" * 50)

    try:
        # Extract screenplay text
        screenplay_text = extract_screenplay_text(pdf_path)
        if not screenplay_text:
            print("❌ Failed to extract screenplay text")
            sys.exit(1)

        # Append to context document
        extended_file = append_screenplay_to_document(context_file, screenplay_text)

        print(f"\n🎉 Success! Screenplay added to film context.")
        print(f"📄 Extended document: {extended_file}")
        print()
        print("Next steps:")
        print(f"1. Create new embeddings:")
        print(f"   poetry run python -m film_context.create_embeddings '{extended_file}'")
        print()
        print("2. Update TV companion to use new embeddings file:")
        print(f"   Update the filename in search_film_context() method")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
