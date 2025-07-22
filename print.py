
import os
import platform
import subprocess
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image, ImageWin

class printerHandler:
    def __init__(
        self,
        printer_name: str="Westinghouse_WHTP203e",
        poppler_path: str=r"C:\Code\Poppler\Library\bin"
        ):
        self.printer_name = printer_name
        self.poppler_path = poppler_path
        
    def print_windows_images(
        self,
        images: list[Image.Image],
        page_width: float,
        page_height: float,
        doc_name: str = "PDF Document",
        ):
        import win32ui
        if not images:
            raise ValueError("Could not rasterize PDF file into images.")

        hdc = win32ui.CreateDC("WINSPOOL", self.printer_name, None)
        hdc.CreatePrinterDC(self.printer_name)
        
        # Get the device capabilities for DPI
        dpi_x = hdc.GetDeviceCaps(88)
        dpi_y = hdc.GetDeviceCaps(90)
        
        pixel_width = int(page_width * dpi_x)
        pixel_height = int(page_height * dpi_y)
        
        hdc.StartDoc(doc_name)
        for i, image in enumerate(images):
            hdc.StartPage()
            
            # Resize the image to fit the page dimensions
            image = image.resize((pixel_width, pixel_height), Image.LANCZOS)
            
            dib = ImageWin.Dib(image)
            dib.draw(hdc.GetHandleOutput(), (0, 0, pixel_width, pixel_height))
            hdc.EndPage()
            
        # Execute the document and delete the DC    
        hdc.EndDoc()
        hdc.DeleteDC()


    def print_file(
        self,
        pdf_file_path: str,
        page_width: float,
        page_height: float,
        raster_dpi: int = 202,
        rotate_pages: bool = False,
        ):
        """
        Print a PDF file from a given path.
        Args:
            pdf_file_path (str): The path to the PDF file.
            page_width (float): The width of the page in inches.
            page_height (float): The height of the page in inches.
            raster_dpi (int): The DPI for rasterizing the PDF pages. Default is 202.
            rotate_pages (bool): Whether to rotate the pages before printing. Default is False.
        """
        platform_name = platform.system()
        
        if platform_name == "Windows":
            images = convert_from_path(
                pdf_file_path,
                poppler_path=self.poppler_path,
                dpi=raster_dpi,
                )
            
            self.print_windows_images(
                images=images,
                page_width=page_width,
                page_height=page_height,
                doc_name=os.path.basename(pdf_file_path),
            )
        elif platform_name == "Linux":
            # For Linux, you can use the `lp` command to print PDF files directly
            if rotate_pages:
                reader = PdfReader(pdf_file_path)
                writer = PdfWriter()
                
                for page in reader.pages:
                    page.rotate(90)
                    writer.add_page(page)
                
                with open(pdf_file_path, "wb") as f:
                    writer.write(f)
                
            subprocess.run(
                ["lp", "-d", self.printer_name, "-o", f"media={page_width}x{page_height}in", pdf_file_path],
                check=True,
            )
        else:
            raise NotImplementedError(f"Printing not implemented for {platform_name}.")
        
        
    def print_pdf_io(
        self,
        pdf_file_io: bytes,
        page_width: float,
        page_height: float,
        raster_dpi: int = 202,
        doc_name: str = "PDF Document",
        rotate_pages: bool = False,
        ):
        """
        Print a PDF file from a BytesIO object.
        Args:
            pdf_file_io (bytes): The PDF file as a BytesIO object.
            page_width (float): The width of the page in inches.
            page_height (float): The height of the page in inches.
            raster_dpi (int): The DPI for rasterizing the PDF pages. Default is 202.
            doc_name (str): The name of the document to print.
            rotate_pages (bool): Whether to rotate the pages before printing. Default is False.
        """
        
        
        images = convert_from_bytes(
            pdf_file_io,
            poppler_path=self.poppler_path,
            dpi=raster_dpi,
        )
        
        if rotate_pages:
            images = [image.rotate(90, expand=True) for image in images]
        
        self.print_windows_images(
            images=images,
            page_width=page_width,
            page_height=page_height,
            doc_name=doc_name,
        )