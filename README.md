# 🔧 PDF Automation Tool

A comprehensive web-based PDF manipulation tool built with Flask and JavaScript. Perform various PDF operations with an intuitive drag-and-drop interface.

## 🌐 Live Demo

**[Try it live on Render](https://pdf-automation-tool-q8sc.onrender.com)**

## ✨ Features

### 📄 PDF Operations
- **Merge PDFs** - Combine multiple PDF files into one
- **Add Watermarks** - Add custom text watermarks to PDFs
- **Extract Text** - Extract all text content from PDFs
- **Split PDFs** - Split large PDFs into smaller files
- **Rotate Pages** - Rotate PDF pages by 90°, 180°, or 270°
- **Create Cover Letters** - Generate professional cover letter templates

### 🎯 User Experience
- **Drag & Drop Interface** - Easy file uploads
- **Auto-Download** - Files download automatically after processing
- **Progress Indicators** - Real-time processing feedback
- **Responsive Design** - Works on desktop and mobile
- **File Size Validation** - Handles files up to 50MB
- **Error Handling** - Clear error messages and fallbacks

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip package manager

## 🔧 Tech Stack

### Backend
- **Flask** - Python web framework
- **PyPDF2** - PDF manipulation library
- **ReportLab** - PDF generation and watermarking
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5** - Structure and semantic markup
- **CSS3** - Styling and responsive design
- **JavaScript (ES6+)** - Dynamic functionality and API calls
- **Drag & Drop API** - File upload interface

### Deployment
- **Render** - Cloud hosting platform
- **Gunicorn** - WSGI HTTP server

## 📁 Project Structure

```
pdf-automation-tool/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── README.md             # This file
│
├── templates/
│   └── index.html        # Main HTML template
│
├── static/
│   ├── script.js         # Frontend JavaScript
│   └── style.css         # CSS styling
│
├── uploads/              # Temporary file uploads (auto-created)
├── outputs/              # Processed files (auto-created)
└── venv/                 # Virtual environment (optional)
```

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/api/merge` | POST | Merge multiple PDF files |
| `/api/watermark` | POST | Add watermark to PDF |
| `/api/extract` | POST | Extract text from PDF |
| `/api/split` | POST | Split PDF into multiple files |
| `/api/rotate` | POST | Rotate PDF pages |
| `/api/cover-letter` | POST | Create cover letter template |
| `/api/download/<filename>` | GET | Download processed files |

## 📋 Dependencies

```txt
Flask==2.3.3
Flask-CORS==4.0.0
PyPDF2==3.0.1
reportlab==4.0.4
Werkzeug==2.3.7
gunicorn==21.2.0
```

## 🔒 Security Features

- **File Type Validation** - Only accepts PDF files
- **File Size Limits** - Maximum 50MB per file
- **Secure Filename Handling** - Prevents directory traversal
- **Temporary File Cleanup** - Auto-removes processed files
- **CORS Protection** - Controlled cross-origin requests

## 🎨 Usage Examples

### Adding a Watermark
1. Select a PDF file
2. Enter watermark text (e.g., "CONFIDENTIAL")
3. Specify output filename
4. Click "Add Watermark"
5. File downloads automatically

### Merging PDFs
1. Select multiple PDF files (Ctrl/Cmd + click)
2. Set output filename
3. Click "Merge PDFs"
4. Combined file downloads automatically

### Extracting Text
1. Upload a PDF file
2. Click "Extract Text"
3. View text preview
4. Download .txt file with full content


## 📝 License

This project is licensed under the MIT License

**⭐ Star this repository if you found it helpful!**

Made with ❤️ by [Your Name]
