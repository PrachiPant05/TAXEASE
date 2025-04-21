import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import fitz  # PyMuPDF
import re
from tax_agents.document_agent import DocumentAgent

# Set path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class ExtractionAgent:
    def __init__(self):
        self.document_agent = DocumentAgent()

    # Function to enhance and preprocess the image
    def preprocess_image(self, path):
        image = Image.open(path)
        
        # Convert image to grayscale
        image = image.convert("L")
        
        # Sharpen the image
        image = image.filter(ImageFilter.SHARPEN)
        
        # Enhance the contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
        
        return image

    # Function to extract text from image (Aadhaar/PAN)
    def extract_text_from_image(self, path):
        image = self.preprocess_image(path)
        
        # Extract text using pytesseract
        text = pytesseract.image_to_string(image)
        return text

    # Function to extract text from PDF (for financial documents)
    def extract_text_from_pdf(self, path):
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    # Main extraction method
    def extract_all(self, doc_id):
        # Get document details (from MongoDB or wherever stored)
        doc = self.document_agent.get_document_by_id(doc_id)

        # Extract data for PAN, Aadhaar, and financial documents
        data = {
            "name": doc.get("name"),
            "email": doc.get("email"),
            "pan_text": self.extract_text_from_image(doc.get("pan_path")),
            "aadhaar_text": self.extract_text_from_image(doc.get("aadhaar_path")),
            "financial_text": ""
        }

        # Extract text from all financial documents
        for path in doc.get("financial_paths", []):
            data["financial_text"] += self.extract_text_from_pdf(path) + "\n"

        # Extract Aadhaar number using regex
        aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', data["aadhaar_text"])
        data["aadhaar_number"] = aadhaar_match.group() if aadhaar_match else "Not found"

        # Extract PAN number (if present)
        pan_match = re.search(r'\b[A-Z]{5}\d{4}[A-Z]{1}\b', data["pan_text"])
        data["pan_number"] = pan_match.group() if pan_match else "Not found"

        return data
