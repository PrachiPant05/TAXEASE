import os
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv


load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)


db = client.tax_assistant_db
collection = db.documents

class DocumentAgent:
    def save_documents(self, name, email, pan_file, aadhaar_file, financial_files):
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

       
        pan_filename = secure_filename(pan_file.filename)
        pan_path = os.path.join(upload_folder, pan_filename)
        pan_file.save(pan_path)

        aadhaar_filename = secure_filename(aadhaar_file.filename)
        aadhaar_path = os.path.join(upload_folder, aadhaar_filename)
        aadhaar_file.save(aadhaar_path)

        # Save financial documents
        financial_paths = []
        for file in financial_files:
            if file.filename:
                filename = secure_filename(file.filename)
                path = os.path.join(upload_folder, filename)
                file.save(path)
                financial_paths.append(path)

        # Insert metadata to MongoDB
        doc = {
            "name": name,
            "email": email,
            "pan_path": pan_path,
            "aadhaar_path": aadhaar_path,
            "financial_paths": financial_paths
        }

        result = collection.insert_one(doc)
        return str(result.inserted_id)
    
    def get_document_by_id(self, doc_id):
        return collection.find_one({"_id": ObjectId(doc_id)})
