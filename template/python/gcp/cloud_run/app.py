import os
import sys
import logging
import base64
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        logging.info("start GET method")
        target = os.environ.get("TARGET", "World")
        return "Hello {}!".format(target)
    else:
        logging.info("start POST method")
        envelope = request.get_json()
        if not envelope:
            msg = "no Pub/Sub message received"
            print(msg)
            return "Bad Request: {}".format(msg), 400

        if not isinstance(envelope, dict) or "message" not in envelope:
            msg = "invalid Pub/Sub message format"
            print(msg)
            return "Bad Request: {}".format(msg), 400

        pubsub_message = envelope["message"]
        name = "World"
        if isinstance(pubsub_message, dict) and "data" in pubsub_message:
            name = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()

        # Flush the stdout to avoid log buffering.
        sys.stdout.flush()
        print("Hello {}!".format(name))
        return "OK", 200

@app.errorhandler(500)
def server_error(e):
    logging.exception("An error occurred during a request.")
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=int(os.environ.get("PORT", 8080)))
