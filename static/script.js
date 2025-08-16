// File handling for all file inputs
document.addEventListener('DOMContentLoaded', function() {
    // Handle merge files (multiple selection)
    document.getElementById('merge-files').addEventListener('change', function(e) {
        const fileList = document.getElementById('merge-file-list');
        const files = Array.from(e.target.files);
        
        if (files.length > 0) {
            fileList.style.display = 'block';
            fileList.innerHTML = files.map((file, index) => `
                <div class="file-item">
                    <span>📄 ${file.name} (${formatFileSize(file.size)})</span>
                    <span class="remove-file" onclick="removeFile('merge-files', ${index})">✕</span>
                </div>
            `).join('');
        } else {
            fileList.style.display = 'none';
        }
    });

    // Handle single file inputs
    const singleFileInputs = ['watermark-file', 'extract-file', 'split-file', 'rotate-file'];
    singleFileInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        const container = input.closest('.form-group');
        
        input.addEventListener('change', function(e) {
            showSelectedFile(inputId, e.target.files[0]);
        });
    });

    // Drag and drop functionality
    document.querySelectorAll('.file-input-label').forEach(label => {
        label.addEventListener('dragover', (e) => {
            e.preventDefault();
            label.style.borderColor = '#5a67d8';
            label.style.backgroundColor = '#edf2f7';
        });

        label.addEventListener('dragleave', (e) => {
            e.preventDefault();
            label.style.borderColor = '#cbd5e0';
            label.style.backgroundColor = '#f7fafc';
        });

        label.addEventListener('drop', (e) => {
            e.preventDefault();
            label.style.borderColor = '#cbd5e0';
            label.style.backgroundColor = '#f7fafc';
            
            const input = label.previousElementSibling;
            const files = e.dataTransfer.files;
            
            if (input.multiple) {
                input.files = files;
            } else if (files.length > 0) {
                // For single file inputs, create a new FileList with just the first file
                const dt = new DataTransfer();
                dt.items.add(files[0]);
                input.files = dt.files;
            }
            
            input.dispatchEvent(new Event('change'));
        });
    });
});

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showSelectedFile(inputId, file) {
    const container = document.getElementById(inputId).closest('.form-group');
    let fileDisplay = container.querySelector('.selected-file-display');
    
    if (file) {
        if (!fileDisplay) {
            fileDisplay = document.createElement('div');
            fileDisplay.className = 'selected-file-display';
            container.appendChild(fileDisplay);
        }
        
        fileDisplay.innerHTML = `
            <div class="file-item" style="background: #e6fffa; border: 1px solid #38d9a9; margin-top: 10px;">
                <span>📄 ${file.name} (${formatFileSize(file.size)})</span>
                <span class="remove-file" onclick="clearFile('${inputId}')" style="color: #c53030;">✕</span>
            </div>
        `;
        fileDisplay.style.display = 'block';
    } else {
        if (fileDisplay) {
            fileDisplay.style.display = 'none';
        }
    }
}

function clearFile(inputId) {
    const input = document.getElementById(inputId);
    input.value = '';
    showSelectedFile(inputId, null);
}

function removeFile(inputId, index) {
    const input = document.getElementById(inputId);
    const dt = new DataTransfer();
    const files = Array.from(input.files);
    
    files.splice(index, 1);
    files.forEach(file => dt.items.add(file));
    input.files = dt.files;
    
    // Trigger change event to update display
    input.dispatchEvent(new Event('change'));
}

function showResult(content, isSuccess = true) {
    const resultArea = document.getElementById('result-area');
    const resultContent = document.getElementById('result-content');
    
    resultArea.classList.add('show');
    resultContent.innerHTML = `
        <div class="alert ${isSuccess ? 'alert-success' : 'alert-error'}">
            ${content}
        </div>
    `;
}

function showProgress() {
    document.getElementById('progress-container').style.display = 'block';
    const progressFill = document.getElementById('progress-fill');
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += 10;
            progressFill.style.width = width + '%';
        }
    }, 100);
}

function hideProgress() {
    setTimeout(() => {
        document.getElementById('progress-container').style.display = 'none';
        document.getElementById('progress-fill').style.width = '0%';
    }, 500);
}

// Auto download function
function autoDownloadFile(filename) {
    const link = document.createElement('a');
    link.href = `/api/download/${filename}`;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Auto download multiple files with delay
function autoDownloadMultiple(filenames) {
    filenames.forEach((filename, index) => {
        setTimeout(() => {
            autoDownloadFile(filename);
        }, index * 500); // 500ms delay between downloads
    });
}

// API Functions - Modified for auto download
async function mergePDFs() {
    const files = document.getElementById('merge-files').files;
    const outputName = document.getElementById('merge-output').value;
    
    if (files.length < 2) {
        showResult('Please select at least 2 PDF files to merge.', false);
        return;
    }
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    formData.append('output_name', outputName);
    
    showProgress();
    
    try {
        const response = await fetch('/api/merge', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        hideProgress();
        
        if (result.success) {
            // Auto download the file
            autoDownloadFile(result.filename);
            
            showResult(`✅ ${result.message}<br>📥 Download started automatically!`);
        } else {
            showResult(result.error || 'Error processing request', false);
        }
    } catch (error) {
        hideProgress();
        showResult('Error processing request: ' + error.message, false);
    }
}

async function addWatermark() {
    const file = document.getElementById('watermark-file').files[0];
    const watermarkText = document.getElementById('watermark-text').value;
    const outputName = document.getElementById('watermark-output').value;
    
    if (!file) {
        showResult('Please select a PDF file.', false);
        return;
    }
    
    if (!watermarkText.trim()) {
        showResult('Please enter watermark text.', false);
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('watermark_text', watermarkText);
    formData.append('output_name', outputName);
    
    showProgress();
    
    try {
        const response = await fetch('/api/watermark', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        hideProgress();
        
        if (result.success) {
            // Auto download the file
            autoDownloadFile(result.filename);
            
            showResult(`✅ ${result.message}<br>📥 Download started automatically!`);
        } else {
            showResult(result.error || 'Error processing request', false);
        }
    } catch (error) {
        hideProgress();
        showResult('Error processing request: ' + error.message, false);
    }
}

async function extractText() {
    const file = document.getElementById('extract-file').files[0];
    
    if (!file) {
        showResult('Please select a PDF file.', false);
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showProgress();
    
    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        hideProgress();
        
        if (result.success) {
            // Auto download the file
            autoDownloadFile(result.filename);
            
            showResult(`
                ✅ ${result.message}<br>📥 Download started automatically!<br><br>
                <div style="margin-top: 15px; padding: 15px; background: #f7fafc; border-radius: 8px; max-height: 200px; overflow-y: auto;">
                    <strong>Text Preview:</strong><br>
                    <pre style="white-space: pre-wrap; font-family: inherit; font-size: 13px;">${result.preview}</pre>
                </div>
            `);
        } else {
            showResult(result.error || 'Error processing request', false);
        }
    } catch (error) {
        hideProgress();
        showResult('Error processing request: ' + error.message, false);
    }
}

async function splitPDF() {
    const file = document.getElementById('split-file').files[0];
    const pagesPerFile = document.getElementById('pages-per-file').value;
    
    if (!file) {
        showResult('Please select a PDF file.', false);
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('pages_per_file', pagesPerFile);
    
    showProgress();
    
    try {
        const response = await fetch('/api/split', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        hideProgress();
        
        if (result.success) {
            // Auto download all split files
            autoDownloadMultiple(result.files);
            
            const fileList = result.files.map(filename => `📄 ${filename}`).join('<br>');
            showResult(`✅ ${result.message}<br>📥 Downloads started automatically!<br><br><div style="margin-top: 15px; padding: 15px; background: #f7fafc; border-radius: 8px;"><strong>Files:</strong><br>${fileList}</div>`);
        } else {
            showResult(result.error || 'Error processing request', false);
        }
    } catch (error) {
        hideProgress();
        showResult('Error processing request: ' + error.message, false);
    }
}

async function rotatePages() {
    const file = document.getElementById('rotate-file').files[0];
    const angle = document.getElementById('rotation-angle').value;
    const outputName = document.getElementById('rotate-output').value;
    
    if (!file) {
        showResult('Please select a PDF file.', false);
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('angle', angle);
    formData.append('output_name', outputName);
    
    showProgress();
    
    try {
        const response = await fetch('/api/rotate', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        hideProgress();
        
        if (result.success) {
            // Auto download the file
            autoDownloadFile(result.filename);
            
            showResult(`✅ ${result.message}<br>📥 Download started automatically!`);
        } else {
            showResult(result.error || 'Error processing request', false);
        }
    } catch (error) {
        hideProgress();
        showResult('Error processing request: ' + error.message, false);
    }
}

async function createCoverLetter() {
    const name = document.getElementById('cover-name').value;
    const position = document.getElementById('cover-position').value;
    const company = document.getElementById('cover-company').value;
    const outputName = document.getElementById('cover-output').value;
    
    if (!name.trim() || !position.trim() || !company.trim()) {
        showResult('Please fill in all required fields for the cover letter.', false);
        return;
    }
    
    const data = {
        name: name,
        position: position,
        company: company,
        output_name: outputName
    };
    
    showProgress();
    
    try {
        const response = await fetch('/api/cover-letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        hideProgress();
        
        if (result.success) {
            // Auto download the file
            autoDownloadFile(result.filename);
            
            showResult(`✅ ${result.message}<br>📥 Download started automatically!`);
        } else {
            showResult(result.error || 'Error processing request', false);
        }
    } catch (error) {
        hideProgress();
        showResult('Error processing request: ' + error.message, false);
    }
}

// Keep the manual download function for backward compatibility
function downloadFile(filename) {
    autoDownloadFile(filename);
}