"""Search functionality for First1KGreek Browser."""

import os
import re
from html import escape


def search_corpus(search_term):
    """Search for the given term in all XML files."""
    results = []

    # Normalize search term
    search_term = search_term.strip().lower()
    if not search_term:
        return results

    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith(".xml") and not file == "__cts__.xml":
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Find all occurrences (case-insensitive)
                    positions = []
                    lower_content = content.lower()
                    pos = lower_content.find(search_term)

                    while pos >= 0:
                        positions.append(pos)
                        pos = lower_content.find(search_term, pos + 1)

                    if positions:
                        # Extract author information
                        author_name = "Unknown"
                        author_matches = re.findall(r"<author.*?>(.*?)</author>", content)
                        if author_matches and len(author_matches[0].strip()) > 0:
                            author_name = author_matches[0]

                        # Extract title information
                        work_title = "Unknown"
                        title_matches = re.findall(r"<title.*?>(.*?)</title>", content)
                        if title_matches:
                            work_title = title_matches[0]
                        else:
                            # Try to find a title in TEI header
                            title_start = content.find("<title")
                            if title_start > 0:
                                title_end = content.find("</title>", title_start)
                                if title_end > 0:
                                    tag_end = content.find(">", title_start)
                                    work_title = content[tag_end + 1 : title_end].strip()

                        # Extract editor information
                        editor_name = "Unknown"
                        editor_matches = re.findall(r"<editor>(.*?)</editor>", content)
                        if editor_matches and len(editor_matches[0].strip()) > 0:
                            editor_name = editor_matches[0]

                        # Get context for the first occurrence
                        pos = positions[0]
                        start_context = max(0, pos - 100)
                        end_context = min(len(content), pos + len(search_term) + 100)
                        context = content[start_context:end_context]

                        # Highlight search term in context
                        search_pattern = re.compile(re.escape(search_term), re.IGNORECASE)
                        context = search_pattern.sub(f'<span class="highlight">{search_term}</span>', context)

                        # Clean up context by removing partial tags at edges
                        if start_context > 0:
                            tag_start = context.find("<", 0, 50)
                            if tag_start > 0:
                                context = context[tag_start:]

                        if end_context < len(content):
                            last_close_tag = context.rfind(">", len(context) - 50)
                            if last_close_tag > 0:
                                context = context[: last_close_tag + 1]

                        # Add to results
                        results.append(
                            {
                                "file_path": file_path,
                                "author": author_name,
                                "title": work_title,
                                "editor": editor_name,
                                "context": escape(context),
                                "occurrence_count": len(positions),
                            }
                        )
                except Exception as e:
                    print(f"Error searching {file_path}: {str(e)}")

    # Sort results by number of occurrences
    results.sort(key=lambda x: x["occurrence_count"], reverse=True)

    return results
