from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from app import models  # noqa - ensure models are registered with SQLAlchemy

    from app.routes import auth, invitations, academics, users, exams, marks, reports, dashboard, school_settings

    app.register_blueprint(auth.bp)
    app.register_blueprint(invitations.bp)
    app.register_blueprint(academics.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(exams.bp)
    app.register_blueprint(marks.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(school_settings.bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
