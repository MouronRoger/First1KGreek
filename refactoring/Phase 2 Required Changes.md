# ## Required Changes:
### 1. For each handler file (browse.py, view.py, works.py, search.py, ui.py):
### 1 Remove the import statement: python 







Apply 

   

  

*from* ..config *import* MAIN_STYLESHEET   

 ### 1 Add time import for cache busting: python 







Apply 

   

  

*import* time   

 ### 1 Import CSS path constants from config: python 







Apply 

   

  

*from* ..config *import* CSS_DIR   

 ### 1 Replace inline style sections that use MAIN_STYLESHEET with external CSS links:

⠀Replace:

html




Apply














<style>
    {MAIN_STYLESHEET}
    */* Other styles... */*
</style>



### With:
html




Apply










<link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
*<!-- Add other specific CSS files as needed -->*





### 2. Specific CSS files to include based on page type:
* For browse.py, ui.py: html 







Apply 

   

  

  <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">   

 

* For view.py (text viewing pages): html 







Apply 

    

   

  <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">    <link rel="stylesheet" href="/static/css/reader.css?v={int(time.time())}">   

 

* For search.py: html 







Apply 

    

   

  <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">    <link rel="stylesheet" href="/static/css/styles.css?v={int(time.time())}">   

 

* For works.py (author tables): html 







Apply 

    

   

  <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">    <link rel="stylesheet" href="/static/css/authors-table.css?v={int(time.time())}">   

 


⠀3. Example for browse.py:


python




Apply




































































*# Remove: from ..config import MAIN_STYLESHEET*
*import* time
*from* ..config *import* CSS_DIR

def render_authors_page():
    """Generate the authors listing page."""
    *# ... existing code ...*
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>First1K Greek - Authors</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/css/main.css?v={int(time.time())}">
    <style>
        .author-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            grid-gap: 20px;
            margin-top: 20px;
        }}
        .author-card {{
            background-color: #333;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s;
            cursor: pointer;
        }}
        /* ... other page-specific styles ... */
    </style>
</head>





### 4. Verify server.py can handle static file serving:
### Ensure the server has a route handler for/static/ paths that serves files from the static directory:

python




Apply














*# Example route handling in server.py*
*if* self.path.startswith('/static/'):
    self.serve_static_file(self.path[1:])  *# Remove leading slash*
    *return*



### This approach keeps the refactoring aligned with the original plan of extracting CSS to external files while maintaining functionality throughout the transition.
