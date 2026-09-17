# from flask import Flask
# from flask_cors import CORS

# from routes.analyzer import analyzer_bp
# from routes.comparison import comparison_bp

# app = Flask(__name__)

# CORS(app)

# app.register_blueprint(analyzer_bp)
# app.register_blueprint(comparison_bp)


# @app.route("/")
# def home():
#     return {
#         "success": True,
#         "message": "RouteSense API is running.",
#     }


# if __name__ == "__main__":
#     app.run(
#         host="127.0.0.1",
#         port=5000,
#         debug=True,
#     )

import os
from flask import Flask
from flask_cors import CORS

from routes.analyzer import analyzer_bp
from routes.comparison import comparison_bp

app = Flask(__name__)

# Enterprise CORS configuration allowing modern React frontend access
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(analyzer_bp)
app.register_blueprint(comparison_bp)

@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health_check():
    return {
        "status": "healthy",
        "engine": "RouteSense Real-Time Telemetry Engine",
        "version": "1.0.0",
    }, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Production deployment friendly execution configuration
    app.run(host="0.0.0.0", port=port, debug=True)