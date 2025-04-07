"""Network utility functions for First1KGreek Browser."""

import socket


def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return start_port  # Fallback to the original port if none found


def add_shutdown_button(html):
    """Add a shutdown button to the HTML pages."""
    shutdown_button = """
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
        <a href="/shutdown" style="display: inline-block; padding: 10px 15px; background-color: #f44336; color: white; text-decoration: none; border-radius: 4px; font-family: Arial, sans-serif; font-size: 14px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            Shutdown Server
        </a>
    </div>
    """
    # Insert before the closing body tag
    if "</body>" in html:
        return html.replace("</body>", f"{shutdown_button}</body>")
    else:
        return html + shutdown_button
