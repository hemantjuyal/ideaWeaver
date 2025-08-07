# utils/save_to_markdown.py
# This module saves the generated story content to a markdown file.

import os

def save_to_markdown(title: str, content: str, output_dir: str = "outputs"):
    """Saves the generated story content to a markdown file.

    The filename is derived from the story title, with special characters sanitized.

    Args:
        title (str): The title of the story, used to create the filename.
        content (str): The markdown content of the story to be saved.
        output_dir (str, optional): The directory where the markdown file will be saved. Defaults to "outputs".
    """
    os.makedirs(output_dir, exist_ok=True)

    # Sanitize title to use as filename
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in title)
    safe_title = safe_title.strip().replace(" ", "_")

    filename = os.path.join(output_dir, f"{safe_title}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n Saved output to: {filename}")
