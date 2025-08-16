#!/usr/bin/env python3
"""
PDF Automation Tool - Flask Backend
A comprehensive web-based PDF manipulation tool for resumes and documents
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import io
from pathlib import Path
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime
import logging

# PDF Libraries
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import black, gray, blue
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(base_name, extension='.pdf'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}{extension}"

class PDFProcessor:
    """Main class for PDF operations"""
    
    def __init__(self):
        self.upload_folder = UPLOAD_FOLDER
        self.output_folder = OUTPUT_FOLDER
    
    def merge_pdfs(self, file_paths, output_filename):
        """Merge multiple PDF files"""
        try:
            merger = PdfMerger()
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    merger.append(file_path)
            
            output_path = os.path.join(self.output_folder, output_filename)
            merger.write(output_path)
            merger.close()
            
            # Cleanup uploaded files
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            return output_path
        except Exception as e:
            logger.error(f"Error merging PDFs: {str(e)}")
            raise
    
    def add_watermark(self, pdf_path, watermark_text, output_filename):
        try:
           reader = PdfReader(pdf_path)
           writer = PdfWriter()
        
           # Create watermark
           watermark_buffer = io.BytesIO()
           c = canvas.Canvas(watermark_buffer, pagesize=letter)
        
           # Set watermark properties
           c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)  # Gray with transparency
           c.setFont("Helvetica", 40)
        
           # Get page dimensions
           page_width, page_height = letter
        
           # Save graphics state
           c.saveState()
        
        # Rotate and position the watermark
           c.translate(page_width/2, page_height/2)  # Move to center
           c.rotate(45)  # Rotate 45 degrees
        
        # Draw text centered at origin (which is now center of page)
           text_width = c.stringWidth(watermark_text.upper(), "Helvetica", 40)
           c.drawString(-text_width/2, 0, watermark_text.upper())
        
        # Restore graphics state
           c.restoreState()
           c.save()
           watermark_buffer.seek(0)
        
           watermark_reader = PdfReader(watermark_buffer)
           watermark_page = watermark_reader.pages[0]
        
        # Apply watermark to each page
           for page in reader.pages:
               page.merge_page(watermark_page)
               writer.add_page(page)
        
           output_path = os.path.join(self.output_folder, output_filename)
           with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Cleanup
           os.remove(pdf_path)
           return output_path
        
        except Exception as e:
          logger.error(f"Error adding watermark: {str(e)}")
          raise

    def extract_text(self, pdf_path):
        """Extract text from PDF"""
        try:
            reader = PdfReader(pdf_path)
            text_content = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                text_content.append(f"--- Page {page_num} ---\n{page_text}\n")
            
            full_text = "\n".join(text_content)
            
            # Save as text file
            output_filename = generate_filename("extracted_text", ".txt")
            output_path = os.path.join(self.output_folder, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            # Cleanup
            os.remove(pdf_path)
            return output_path, full_text[:1000] + "..." if len(full_text) > 1000 else full_text
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise
    
    def split_pdf(self, pdf_path, pages_per_file):
        """Split PDF into multiple files"""
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            output_files = []
            
            for start_page in range(0, total_pages, pages_per_file):
                writer = PdfWriter()
                end_page = min(start_page + pages_per_file, total_pages)
                
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                output_filename = generate_filename(f"split_pages_{start_page+1}-{end_page}")
                output_path = os.path.join(self.output_folder, output_filename)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
            
            # Cleanup
            os.remove(pdf_path)
            return output_files
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {str(e)}")
            raise
    
    def rotate_pdf(self, pdf_path, angle, output_filename):
        """Rotate all pages in PDF"""
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                # PyPDF2 expects 90, 180, or 270 degrees for clockwise rotation
                rotated_page = page.rotate(angle)
                writer.add_page(rotated_page)
            
            output_path = os.path.join(self.output_folder, output_filename)
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Cleanup
            os.remove(pdf_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error rotating PDF: {str(e)}")
            raise
    
    def create_cover_letter(self, name, position, company, email="", phone="", output_filename="cover_letter.pdf"):
        """Create a professional cover letter template"""
        try:
            output_path = os.path.join(self.output_folder, output_filename)
            doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=1*inch)
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=blue,
                alignment=TA_CENTER
            )
            
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20,
                alignment=TA_LEFT
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                alignment=TA_LEFT
            )
            
            # Content
            story = []
            
            # Header
            story.append(Paragraph(f"<b>{name}</b>", title_style))
            if email or phone:
                contact_info = []
                if email:
                    contact_info.append(f"Email: {email}")
                if phone:
                    contact_info.append(f"Phone: {phone}")
                story.append(Paragraph(" | ".join(contact_info), header_style))
            
            story.append(Spacer(1, 20))
            
            # Date
            current_date = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(current_date, body_style))
            story.append(Spacer(1, 20))
            
            # Company info
            story.append(Paragraph(f"<b>{company}</b><br/>Hiring Manager", body_style))
            story.append(Spacer(1, 20))
            
            # Salutation
            story.append(Paragraph("Dear Hiring Manager,", body_style))
            story.append(Spacer(1, 12))
            
            # Body paragraphs (template)
            body_content = [
                f"I am writing to express my strong interest in the {position} position at {company}. With my background and passion for this field, I am confident that I would be a valuable addition to your team.",
                
                "In my previous experience, I have developed strong technical skills and a deep understanding of industry best practices. I am particularly drawn to this opportunity because of your company's reputation for innovation and excellence.",
                
                f"I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to {company}'s continued success. Thank you for considering my application. I look forward to hearing from you soon."
            ]
            
            for paragraph in body_content:
                story.append(Paragraph(paragraph, body_style))
                story.append(Spacer(1, 12))
            
            # Closing
            story.append(Spacer(1, 20))
            story.append(Paragraph("Sincerely,<br/><br/><br/>", body_style))
            story.append(Paragraph(f"<b>{name}</b>", body_style))
            
            # Build PDF
            doc.build(story)
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating cover letter: {str(e)}")
            raise

# Initialize processor
pdf_processor = PDFProcessor()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/merge', methods=['POST'])
def merge_pdfs():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        output_name = request.form.get('output_name', 'merged.pdf')
        
        if len(files) < 2:
            return jsonify({'error': 'At least 2 files required for merging'}), 400
        
        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths.append(file_path)
        
        if len(file_paths) < 2:
            return jsonify({'error': 'Valid PDF files required'}), 400
        
        output_path = pdf_processor.merge_pdfs(file_paths, output_name)
        
        return jsonify({
            'success': True,
            'message': f'Successfully merged {len(file_paths)} PDF files',
            'filename': os.path.basename(output_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watermark', methods=['POST'])
def add_watermark():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        watermark_text = request.form.get('watermark_text', 'CONFIDENTIAL')
        output_name = request.form.get('output_name', 'watermarked.pdf')
        
        if not (file and allowed_file(file.filename)):
            return jsonify({'error': 'Valid PDF file required'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        output_path = pdf_processor.add_watermark(file_path, watermark_text, output_name)
        
        return jsonify({
            'success': True,
            'message': f'Watermark "{watermark_text}" added successfully',
            'filename': os.path.basename(output_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not (file and allowed_file(file.filename)):
            return jsonify({'error': 'Valid PDF file required'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        output_path, preview_text = pdf_processor.extract_text(file_path)
        
        return jsonify({
            'success': True,
            'message': 'Text extracted successfully',
            'filename': os.path.basename(output_path),
            'preview': preview_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/split', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        pages_per_file = int(request.form.get('pages_per_file', 1))
        
        if not (file and allowed_file(file.filename)):
            return jsonify({'error': 'Valid PDF file required'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        output_files = pdf_processor.split_pdf(file_path, pages_per_file)
        
        return jsonify({
            'success': True,
            'message': f'PDF split into {len(output_files)} files',
            'files': [os.path.basename(f) for f in output_files]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rotate', methods=['POST'])
def rotate_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        angle = int(request.form.get('angle', 90))
        output_name = request.form.get('output_name', 'rotated.pdf')
        
        if not (file and allowed_file(file.filename)):
            return jsonify({'error': 'Valid PDF file required'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        output_path = pdf_processor.rotate_pdf(file_path, angle, output_name)
        
        return jsonify({
            'success': True,
            'message': f'PDF rotated by {angle} degrees',
            'filename': os.path.basename(output_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cover-letter', methods=['POST'])
def create_cover_letter():
    try:
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name', '').strip()
        position = data.get('position', '').strip()
        company = data.get('company', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        output_name = data.get('output_name', 'cover_letter.pdf')
        
        if not all([name, position, company]):
            return jsonify({'error': 'Name, position, and company are required'}), 400
        
        output_path = pdf_processor.create_cover_letter(
            name, position, company, email, phone, output_name
        )
        
        return jsonify({
            'success': True,
            'message': 'Cover letter created successfully',
            'filename': os.path.basename(output_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB'}), 413

if __name__ == '__main__':
    print("PDF Automation Tool Backend Starting...")
    print("Available endpoints:")
    print("- POST /api/merge - Merge PDFs")
    print("- POST /api/watermark - Add watermark")
    print("- POST /api/extract - Extract text")
    print("- POST /api/split - Split PDF")
    print("- POST /api/rotate - Rotate pages")
    print("- POST /api/cover-letter - Create cover letter")
    print("- GET /api/download/<filename> - Download file")
    
    # Production ready configuration
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'production') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)