#!/usr/bin/env python3
"""
Web Interface for TestMozart Agent
Provides a simple web interface for uploading files and interacting with the deployed agent.
"""

import os
import json
import tempfile
from flask import Flask, request, jsonify, render_template_string
from google.cloud import storage
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the deployed agent
from agents.coordinator_deployed import root_agent_deployed

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize session service
session_service = InMemorySessionService()

# Initialize the ADK Runner with our deployed agent
runner = Runner(
    app_name="testmozart_web_interface",
    agent=root_agent_deployed,
    session_service=session_service
)

# GCS Configuration
BUCKET_NAME = "saikiranruckusdevtools-bucket"

def upload_file_to_gcs(file_content: str, filename: str) -> str:
    """Upload file content to Google Cloud Storage."""
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        
        # Create blob name with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"uploads/{timestamp}_{filename}"
        
        # Upload content
        blob = bucket.blob(blob_name)
        blob.upload_from_string(file_content)
        
        # Return GCS URL
        return f"gs://{BUCKET_NAME}/{blob_name}"
    except Exception as e:
        raise Exception(f"Failed to upload to GCS: {e}")

def detect_language_from_filename(filename: str) -> str:
    """Detect programming language based on file extension."""
    if filename.endswith('.py'):
        return 'python'
    elif filename.endswith('.c'):
        return 'c'
    else:
        return 'python'  # Default to python

@app.route('/')
def index():
    """Main page with file upload form."""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TestMozart - AI Test Generator</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 2px dashed #ddd;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                transition: border-color 0.3s;
            }
            .upload-area:hover {
                border-color: #007bff;
            }
            .upload-area.dragover {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            input[type="file"] {
                margin: 20px 0;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 5px;
            }
            button:hover {
                background-color: #0056b3;
            }
            button:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #007bff;
            }
            .error {
                border-left-color: #dc3545;
                background-color: #f8d7da;
            }
            .success {
                border-left-color: #28a745;
                background-color: #d4edda;
            }
            .loading {
                text-align: center;
                color: #007bff;
            }
            .code-block {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
                overflow-x: auto;
            }
            pre {
                margin: 0;
                white-space: pre-wrap;
            }
            .download-link {
                display: inline-block;
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                text-decoration: none;
                border-radius: 4px;
                margin: 10px 0;
            }
            .download-link:hover {
                background-color: #218838;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 TestMozart - AI Test Generator</h1>
            <p style="text-align: center; color: #666;">
                Upload your Python or C code file and let AI generate comprehensive test suites for you!
            </p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="uploadArea">
                    <p>📁 Drag and drop your code file here, or click to select</p>
                    <input type="file" id="fileInput" name="file" accept=".py,.c" required>
                    <p style="color: #666; font-size: 14px;">
                        Supported formats: .py (Python), .c (C)
                    </p>
                </div>
                
                <div style="text-align: center;">
                    <button type="submit" id="submitBtn">🚀 Generate Tests</button>
                    <button type="button" id="clearBtn">🗑️ Clear</button>
                </div>
            </form>
            
            <div id="result" style="display: none;"></div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const uploadForm = document.getElementById('uploadForm');
            const submitBtn = document.getElementById('submitBtn');
            const clearBtn = document.getElementById('clearBtn');
            const resultDiv = document.getElementById('result');

            // Drag and drop functionality
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                }
            });

            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            // Form submission
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const file = fileInput.files[0];
                if (!file) {
                    showResult('Please select a file first.', 'error');
                    return;
                }

                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Generating Tests...';
                showResult('🔄 Processing your file and generating tests. This may take 1-3 minutes...', 'loading');

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        showResult(result.message, 'success', result.test_code, result.download_url);
                    } else {
                        showResult(result.error, 'error');
                    }
                } catch (error) {
                    showResult('Error: ' + error.message, 'error');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 Generate Tests';
                }
            });

            // Clear functionality
            clearBtn.addEventListener('click', () => {
                fileInput.value = '';
                resultDiv.style.display = 'none';
            });

            function showResult(message, type, testCode = null, downloadUrl = null) {
                resultDiv.className = `result ${type}`;
                resultDiv.style.display = 'block';
                
                let html = `<h3>${type === 'success' ? '✅ Success!' : type === 'error' ? '❌ Error' : '⏳ Processing'}</h3>`;
                html += `<p>${message}</p>`;
                
                if (testCode) {
                    html += '<h4>Generated Test Code:</h4>';
                    html += '<div class="code-block"><pre>' + escapeHtml(testCode) + '</pre></div>';
                }
                
                if (downloadUrl) {
                    html += `<a href="${downloadUrl}" class="download-link" target="_blank">📥 Download Test File</a>`;
                }
                
                resultDiv.innerHTML = html;
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        </script>
    </body>
    </html>
    """
    return html_template

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process with the agent."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Read file content
        file_content = file.read().decode('utf-8')
        filename = file.filename
        
        # Detect language
        language = detect_language_from_filename(filename)
        
        # Upload to GCS
        file_url = upload_file_to_gcs(file_content, filename)
        
        # Create session
        session = session_service.create_session(
            app_name="testmozart_web_interface",
            user_id="web_user"
        )
        
        # Prepare request for the agent
        agent_request = json.dumps({
            "file_url": file_url,
            "filename": filename,
            "language": language
        })
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=agent_request)]
        )
        
        # Run the agent
        final_output = ""
        async def run_agent():
            nonlocal final_output
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=user_message
            ):
                if event.is_final_response():
                    final_output = event.content.parts[0].text if event.content and event.content.parts else ""
        
        # Run the async function
        import asyncio
        asyncio.run(run_agent())
        
        # Extract test code from the output
        import re
        test_code = ""
        download_url = ""
        
        if language == 'python':
            python_match = re.search(r"```python\n([\s\S]+?)\n```", final_output, re.DOTALL)
            if python_match:
                test_code = python_match.group(1).strip()
                # Save to GCS and get download URL
                download_url = upload_file_to_gcs(test_code, f"test_{filename}")
        elif language == 'c':
            c_match = re.search(r"```c\n([\s\S]+?)\n```", final_output, re.DOTALL)
            if c_match:
                test_code = c_match.group(1).strip()
                # Save to GCS and get download URL
                download_url = upload_file_to_gcs(test_code, f"test_{filename}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully generated test suite for {filename} ({language})',
            'test_code': test_code,
            'download_url': download_url,
            'language': language
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'TestMozart Web Interface'})

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
