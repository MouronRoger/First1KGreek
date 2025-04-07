"""UI handlers for First1KGreek Browser."""

from ..config import MAIN_STYLESHEET


def render_main_page():
    """Render the main page HTML."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>First1KGreek Browser</title>
    <style>
        {MAIN_STYLESHEET}
        .nav-links {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .search-box {{
            width: 100%;
            padding: 10px;
            margin: 20px 0;
            border: none;
            border-radius: 4px;
            background: #444;
            color: #fff;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background: #4299e1;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            transition: background 0.2s;
        }}
        .button:hover {{
            background: #3182ce;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>First1KGreek Browser</h1>

        <div class="nav-links">
            <a href="/browse/authors" class="button">Browse by Author</a>
            <a href="/browse/editors" class="button">Browse by Editor</a>
            <a href="/search" class="button">Search Texts</a>
            <a href="/import" class="button">Import from Scaife</a>
        </div>

        <div class="card">
            <h2>Quick Search</h2>
            <form action="/search" method="get">
                <input type="text" name="q" class="search-box" placeholder="Search the corpus...">
            </form>
        </div>

        <div class="card">
            <h2>About</h2>
            <p>Browse and search through Greek texts from the First Thousand Years Project.
            Features include browsing by author or editor, full-text search, and importing texts from Scaife/Perseus.</p>
        </div>
    </div>
</body>
</html>"""
