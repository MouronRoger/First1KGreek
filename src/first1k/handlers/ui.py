"""UI handlers for First1KGreek Browser."""

from ..config import MAIN_STYLESHEET


def render_main_page():
    """Return HTML for the main page."""
    return f"""
<html>
<head>
    <title>First1KGreek Browser</title>
</head>
<body>
    <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>First1KGreek Browser</h1>
        <div style="margin-bottom: 30px;">
            <h2>Quick Search</h2>
            <form action="/search" method="get">
                <label for="search_term">Search term:</label>
                <input type="text" id="search_term" name="search_term" style="padding: 5px; margin-right: 10px;">
                <button type="submit" style="padding: 5px 15px;">Search</button>
            </form>
        </div>
        <div style="margin-bottom: 30px;">
            <h2>Browse</h2>
            <a href="/browse/authors" class="button" style="display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; background-color: #4CAF50; color: white; border-radius: 4px;">Browse by Author</a>
            <a href="/browse/editors" class="button" style="display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; background-color: #4CAF50; color: white; border-radius: 4px;">Browse by Editor</a>
        </div>
        <div style="margin-bottom: 30px;">
            <h2>Import</h2>
            <a href="/import" style="color: #0066cc;">Import new text</a>
        </div>
        <div>
            <h2>About</h2>
            <p>This browser allows you to explore and search through the First1KGreek corpus. You can browse texts by author or editor, perform full-text searches, and import new texts.</p>
        </div>
    </div>
</body>
</html>
"""
