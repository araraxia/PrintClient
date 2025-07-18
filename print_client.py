from flask import Flask, request, jsonifty
from waitress import serve
from print import printerHandler
from io import BytesIO


class PrintClient:
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route("/print", methods=["POST"])
        def print_message():
            if 'pdf' not in request.files:
                return jsonifty({"error": "No PDF file provided"}), 400
            pdf_file = request.files['pdf']

            print_handler = printerHandler(
                printer_name="Westinghouse WHTP203e",
                poppler_path="/usr/bin/poppler"  # Adjust the path as needed
            )
            
            with BytesIO(pdf_file.read()) as pdf_file_io:
                print_handler.print_pdf_io(
                    pdf_file_io=pdf_file_io,
                    page_width=2,  # Default width in inches
                    page_height=3,  # Default height in inches
                    raster_dpi=202,  # Default DPI
                    doc_name=pdf_file.filename or "PDF Document",
                )
            
            data = request.get_json()
            if not data or "message" not in data:
                return jsonifty({"error": "No message provided"}), 400

            message = data["message"]
            print(message)
            return jsonifty({"status": "Message printed successfully"}), 200


if __name__ == "__main__":
    client = PrintClient()
    serve(client.app, host="0.0.0.0", port=5571)
