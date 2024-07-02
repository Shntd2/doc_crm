from flask import Flask, send_from_directory
from reg_login_and_logout import registration_app
import os
from werkzeug.utils import safe_join


def create_app():

    app = Flask(__name__, static_folder='../doc_crm_frontend/build', static_url_path='')

    # Register the blueprint with the URL prefix for API routes
    app.register_blueprint(registration_app, url_prefix='/registration')

    # Serve static files for the React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
        # Safely join the path to the static folder
        file_path = safe_join(app.static_folder, path)
        if path != '' and os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app


if __name__ == '__main__':
    # Get the debug mode and port from environment variables or set defaults
    debug_mode = os.getenv('FLASK_DEBUG', 'True') == 'True'
    port = int(os.getenv('PORT', 5000))

    app = create_app()
    app.run(debug=debug_mode, port=port)
    