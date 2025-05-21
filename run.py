from app import create_app
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

app = create_app()

app.secret_key = 'secret-key-2025'


if __name__ == '__main__':
    app.run(debug=True)
