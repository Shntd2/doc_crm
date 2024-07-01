from flask import Flask, send_from_directory
from reg_login_and_logout import registration_app
import os


def create_app():
    app = Flask(__name__, static_folder='../doc_crm_frontend/build', static_url_path='')

    # Register the blueprint
    app.register_blueprint(registration_app, url_prefix='/api')

    # Ensure the app serves static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
        if path != '' and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
