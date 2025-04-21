import os
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from tax_agents.document_agent import DocumentAgent
from tax_agents.extraction_agent import ExtractionAgent
from tax_agents.tax_calc_agent import TaxCalcAgent

from tax_agents.report_agent import ReportAgent
from dotenv import load_dotenv
import ollama

# Load environment variables
load_dotenv()

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

# Initialize the Ollama LLM client and agents
llm_client = ollama.Client()

document_agent = DocumentAgent()
extraction_agent = ExtractionAgent()
tax_calc_agent = TaxCalcAgent(llm_client)  # ✅ Correctly passed
report_agent = ReportAgent()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        dob = request.form.get('dob', '')
        income_source = request.form.get('income_source', '')
        
        pan_file = request.files.get('pan_card')
        aadhaar_file = request.files.get('aadhaar_card')
        financial_files = request.files.getlist('financial_docs')
        
        # Validate required files
        if not (pan_file and allowed_file(pan_file.filename)):
            flash('Valid PAN card file is required')
            return redirect(request.url)
        
        if not (aadhaar_file and allowed_file(aadhaar_file.filename)):
            flash('Valid Aadhaar card file is required')
            return redirect(request.url)
        
        # Save and process all files
        doc_ids = document_agent.save_documents(name, email, pan_file, aadhaar_file, financial_files)
        extracted_data = extraction_agent.extract_all(doc_ids)
        
        # Add user details to extracted data
        user_details = {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'dob': dob,
            'income_source': income_source
        }
        extracted_data.update({'user_details': user_details})
        
        # Calculate tax
        tax_result = tax_calc_agent.calculate_tax(extracted_data)
        
        # Generate and send report
        pdf_report = report_agent.generate_pdf_report(name, tax_result)
        report_agent.send_report(email, pdf_report)
        
        return render_template(
            'success.html', 
            name=name,
            result=tax_result,
            pan_number=extracted_data.get('pan_number', 'N/A'),
            aadhaar_number=extracted_data.get('aadhaar_number', 'N/A'),
            user_details=user_details
        )
    
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_support():
    """Endpoint for chat support functionality"""
    message = request.json.get('message', '')
    response = {
        'reply': f"Thank you for your message: '{message}'. Our support team will get back to you shortly."
    }
    return jsonify(response)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
