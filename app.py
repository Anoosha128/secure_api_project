
import os
import logging

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ==================================================
# 1. Load environment variables from .env
# ==================================================

load_dotenv()


# ==================================================
# 2. Create Flask application
# ==================================================

app = Flask(__name__)


# ==================================================
# 3. Get secrets from .env
# ==================================================

SECRET_KEY = os.getenv("SECRET_KEY")
API_KEY = os.getenv("API_KEY")

# Set Flask secret key
app.config["SECRET_KEY"] = SECRET_KEY


# ==================================================
# 4. Logging Configuration
# ==================================================

# Logs will:
# 1. Be saved in app.log
# 2. Also appear in the terminal

logging.basicConfig(
    level=logging.INFO,

    # Log format:
    # Date/Time - Level - Message
    format="%(asctime)s - %(levelname)s - %(message)s",

    handlers=[
        # Save logs to app.log
        logging.FileHandler("app.log"),

        # Show logs in terminal
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger(__name__)


# ==================================================
# 5. Create Rate Limiter
# ==================================================

# get_remote_address identifies the client by IP address.
#
# Example:
# 5 requests per minute are allowed.

limiter = Limiter(
    key_func=get_remote_address,
    app=app
)


# ==================================================
# 6. Home Route
# ==================================================

@app.route("/")
def home():

    # Record that the home page was accessed
    logger.info("Home page accessed")

    return jsonify({
        "message": "Secure API is running!"
    })


# ==================================================
# 7. Protected API
# ==================================================

@app.route("/api/hello", methods=["POST"])
@limiter.limit("5 per minute")
def hello():

    try:

        # --------------------------------------------------
        # Step 1: Log incoming request
        # --------------------------------------------------

        logger.info("POST request received on /api/hello")


        # --------------------------------------------------
        # Step 2: Get JSON data
        # --------------------------------------------------

        data = request.get_json(silent=True)


        # --------------------------------------------------
        # Step 3: Make sure valid JSON was provided
        # --------------------------------------------------

        if not isinstance(data, dict):

            logger.warning(
                "Request did not contain valid JSON data"
            )

            return jsonify({
                "error": "Request must contain JSON data"
            }), 400


        # --------------------------------------------------
        # Step 4: Get name from JSON
        # --------------------------------------------------

        name = data.get("name")


        # --------------------------------------------------
        # Step 5: Check if name exists
        # --------------------------------------------------

        if name is None:

            logger.warning(
                "Name field is missing from request"
            )

            return jsonify({
                "error": "Name is required"
            }), 400


        # --------------------------------------------------
        # Step 6: Check name data type
        # --------------------------------------------------

        if not isinstance(name, str):

            logger.warning(
                "Name field is not a string"
            )

            return jsonify({
                "error": "Name must be a string"
            }), 400


        # --------------------------------------------------
        # Step 7: Remove extra spaces
        # --------------------------------------------------

        name = name.strip()


        # --------------------------------------------------
        # Step 8: Check if name is empty
        # --------------------------------------------------

        if not name:

            logger.warning(
                "Empty name received"
            )

            return jsonify({
                "error": "Name cannot be empty"
            }), 400


        # --------------------------------------------------
        # Step 9: Check maximum name length
        # --------------------------------------------------

        if len(name) > 50:

            logger.warning(
                "Name exceeded 50 characters"
            )

            return jsonify({
                "error": "Name must not exceed 50 characters"
            }), 400


        # --------------------------------------------------
        # Step 10: Get API key from request header
        # --------------------------------------------------

        user_api_key = request.headers.get("X-API-Key")


        # --------------------------------------------------
        # Step 11: Validate API key
        # --------------------------------------------------

        if user_api_key != API_KEY:

            # IMPORTANT:
            # Never log the actual API key.
            logger.warning(
                "Invalid or missing API key"
            )

            return jsonify({
                "error": "Invalid or missing API key"
            }), 401


        # --------------------------------------------------
        # Step 12: Successful request
        # --------------------------------------------------

        logger.info(
            "Request successfully validated and processed"
        )

        return jsonify({
            "message": f"Hello, {name}!"
        })


    # ==================================================
    # Exception Handling
    # ==================================================

    except Exception as e:

        # logger.exception() records the error
        # and its traceback in the log.
        #
        # We DON'T send the actual error to the user.
        logger.exception(
            "Unexpected error occurred"
        )

        # Safe generic response
        return jsonify({
            "error": "Internal server error"
        }), 500


# ==================================================
# 8. Run Flask Application
# ==================================================

if __name__ == "__main__":

    logger.info(
        "Starting Secure API application"
    )

    app.run(debug=True)





# def hello():

#     # get api key from request header
#     user_api_key = request.headers.get("x-api-key")

#     # check weather api key is correct
#     if user_api_key != API_KEY:
#         return jsonify({
#             "error": "Invalid or missing API Key"
#         }), 401

#     # API KEY is correct
#     return jsonify ({
#         "message": "Welcome to the protected API route! You have access to this resource."

#     })






















