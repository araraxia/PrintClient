#!/usr/bin/env python3

from flask import Flask, request, jsonify
from waitress import serve
from print import printerHandler
import uuid, os


class PrintClient:
    def __init__(self):
        self.app = Flask(__name__)
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(self.root_dir, "tmp")
        print(f"Temporary directory for print jobs: {self.temp_dir}")
        if not os.path.exists(self.temp_dir):
            print(f"Creating temporary directory: {self.temp_dir}")
            os.makedirs(self.temp_dir)

        @self.app.route("/print", methods=["POST"])
        def print_message():        # Expand to support printing any file type eventually!!
            print("Received print request")
            if 'pdf' not in request.files:
                return jsonify({"error": "No PDF file provided"}), 400
            pdf_file = request.files['pdf']

            print_handler = printerHandler(
                printer_name="Westinghouse_WHTP203e",
            )
            
            '''
            with BytesIO(pdf_file.read()) as pdf_file_io:
                print_handler.print_pdf_io(
                    pdf_file_io=pdf_file_io,
                    page_width=2,  # Default width in inches
                    page_height=3,  # Default height in inches
                    raster_dpi=202,  # Default DPI
                    doc_name=pdf_file.filename or "PDF Document",
                    rotate=True,  # Rotate pages if needed
                )
            '''
            tmp_file_name = f"{uuid.uuid4().hex}.pdf"
            pdf_file_path = os.path.join(self.temp_dir, tmp_file_name)
            print(f"Saving PDF file to temporary path: {pdf_file_path}")
            pdf_file.save(dst=pdf_file_path)
            print(f"PDF file saved successfully: {pdf_file_path}")
            
            try:
                print(f"Printing PDF file: {pdf_file_path}")
                print_handler.print_file(
                    pdf_file_path=pdf_file_path,
                    page_width=2,  # Media width in inches
                    page_height=3,  # Media height in inches
                    raster_dpi=202,  # Default DPI
                    rotate_pages=True,  # Rotate the content of the PDF
                )
            except Exception as e:
                print(f"Error printing PDF: {e}")
                return jsonify({"error": str(e), "traceback": e.__traceback__}), 500
            finally:
                if os.path.exists(pdf_file_path):
                    os.remove(pdf_file_path)
                    
            return jsonify({"message": "Print job submitted successfully"}), 200




if __name__ == "__main__":
    print("Starting Print Client Service...")
    client = PrintClient()
    serve(client.app, host="0.0.0.0", port=5571)
