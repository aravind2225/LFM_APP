"""
import create_app method which is project's __init__
"""

from project import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
