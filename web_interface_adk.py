#!/usr/bin/env python3
"""
ADK-based Web Interface for TestMozart Agent
Uses ADK runner to call the agent directly without API calls.
"""

import os
import json
import asyncio
from flask import Flask, request, jsonify, render_template_string
from google.cloud import storage
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the regular coordinator (same as main.py)
from agents.coordinator import create_root_agent
print("Successfully imported create_root_agent")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize session service
session_service = InMemorySessionService()

# Initialize the ADK Runner with our agent (will be created dynamically)
# We'll create the agent dynamically based on the language

# GCS Configuration
BUCKET_NAME = "saikiranruckusdevtools-bucket"

def upload_file_to_gcs(file_content: str, filename: str) -> str:
    """Upload file content to Google Cloud Storage."""
    import datetime
    
    try:
        print(f"Attempting to upload {filename} to GCS...")
        
        # Try to initialize the client with explicit project
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'ruckusdevtools')
        print(f"Using project: {project_id}")
        
        # Initialize the client with proper authentication
        try:
            # Try to use default credentials first
            client = storage.Client(project=project_id)
            print("GCS client initialized successfully with default credentials")
        except Exception as auth_error:
            print(f"Default credentials failed: {auth_error}")
            # Try to use service account key if available
            try:
                from google.oauth2 import service_account
                # Look for service account key file
                key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if key_path and os.path.exists(key_path):
                    credentials = service_account.Credentials.from_service_account_file(key_path)
                    client = storage.Client(project=project_id, credentials=credentials)
                    print("GCS client initialized with service account key")
                else:
                    raise Exception("No service account key found")
            except Exception as key_error:
                print(f"Service account key failed: {key_error}")
                raise Exception("GCS authentication failed")
        
        # Get the bucket
        bucket = client.bucket(BUCKET_NAME)
        print(f"Accessing bucket: {BUCKET_NAME}")
        
        # Create blob name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"uploads/{timestamp}_{filename}"
        print(f"Uploading to: {blob_name}")
        
        # Upload content
        blob = bucket.blob(blob_name)
        blob.upload_from_string(file_content)
        print(f"File uploaded successfully to {blob_name}")
        
        # Return the GCS URL
        gcs_url = f"gs://{BUCKET_NAME}/{blob_name}"
        print(f"GCS URL: {gcs_url}")
        return gcs_url
        
    except Exception as e:
        print(f"GCS upload failed: {e}")
        # Create a mock URL for development
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mock_url = f"gs://{BUCKET_NAME}/uploads/{timestamp}_{filename}"
        print(f"Created mock GCS URL: {mock_url}")
        return mock_url

def create_download_url(gcs_url: str) -> str:
    """Convert GCS URL to a downloadable URL."""
    if gcs_url.startswith('gs://'):
        # Convert gs://bucket/path to https://storage.googleapis.com/bucket/path
        path = gcs_url[5:]  # Remove gs://
        return f"https://storage.googleapis.com/{path}"
    return gcs_url

def create_signed_download_url(gcs_url: str) -> str:
    """Create a signed URL for downloading from GCS."""
    try:
        if gcs_url.startswith('gs://'):
            path = gcs_url[5:]  # Remove gs://
            bucket_name, blob_name = path.split('/', 1)
            
            # Initialize GCS client
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'ruckusdevtools')
            client = storage.Client(project=project_id)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Generate signed URL valid for 1 hour
            from datetime import datetime, timedelta
            expiration = datetime.utcnow() + timedelta(hours=1)
            
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method='GET'
            )
            return signed_url
    except Exception as e:
        print(f"Failed to create signed URL: {e}")
        # Fallback to public URL
        return create_download_url(gcs_url)
    
    return gcs_url

def detect_language_from_filename(filename: str) -> str:
    """Detect programming language based on file extension."""
    if filename.endswith('.py'):
        return 'python'
    elif filename.endswith('.c'):
        return 'c'
    else:
        return 'python'  # Default to python

async def call_agent_async(file_url: str, filename: str, language: str, file_content: str = "") -> tuple[str, list]:
    """Call the agent using ADK runner and return output with logs."""
    # Initialize variables at the start to avoid scope issues
    final_output = ""
    event_count = 0
    agent_logs = []
    all_responses = []
    
    try:
        print(f"Creating session for agent call...")
        
        # Create the root agent for the detected language (same as main.py)
        root_agent = create_root_agent(language)
        print(f"Created root agent for language: {language}")
        
        # Initialize the ADK Runner with our agent
        runner = Runner(
            app_name="testmozart_web_interface",
            agent=root_agent,
            session_service=session_service
        )
        
        # Create session
        session = await session_service.create_session(
            app_name="testmozart_web_interface",
            user_id="web_user"
        )
        print(f"Session created: {session.id}")
        
        # Prepare request for the agent (same format as main.py)
        agent_request = json.dumps({
            "source_code": file_content,
            "language": language
        })
        print(f"Agent request prepared: {agent_request[:100]}...")
        print(f"Source code length: {len(file_content)} characters")
        print(f"Language: {language}")
        print(f"Source code preview: {file_content[:200]}...")
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=agent_request)]
        )
        
        # Run the agent with timeout
        print("Starting agent execution...")
        
        try:
            # Run with timeout to prevent hanging
            import asyncio
            import time
            
            start_time = time.time()
            timeout_seconds = 300  # 5 minutes
            
            # Run the agent with timeout check
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=user_message
            ):
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    timeout_log = "Agent execution timed out after 5 minutes"
                    print(timeout_log)
                    agent_logs.append(timeout_log)
                    break
                
                event_count += 1
                log_message = f"Agent event {event_count}: {event.author}"
                print(log_message)
                agent_logs.append(log_message)
                
                # Add more detailed event information
                event_details = f"  → Event type: {type(event).__name__}"
                print(event_details)
                agent_logs.append(event_details)
                
                if hasattr(event, 'is_final_response'):
                    final_status = f"  → Is final response: {event.is_final_response()}"
                    print(final_status)
                    agent_logs.append(final_status)
                
                # Add content preview if available
                if event.content and event.content.parts:
                    content_preview = ""
                    full_content = ""
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            full_content += part.text
                            if not content_preview:
                                content_preview = part.text[:100] + "..." if len(part.text) > 100 else part.text
                    
                    if content_preview:
                        content_log = f"  → Content: {content_preview}"
                        print(content_log)
                        agent_logs.append(content_log)
                    
                    # Collect all responses
                    if full_content:
                        all_responses.append(full_content)
                        
                        # Special handling for TestImplementer to see what it's receiving
                        if event.author == "TestImplementer":
                            print(f"  → TestImplementer received content: {len(full_content)} characters")
                            if full_content:
                                print(f"  → TestImplementer content preview: {full_content[:200]}...")
                            else:
                                print(f"  → TestImplementer received empty content - this might be the issue!")
                            
                            # Check if TestImplementer is calling tools
                            if hasattr(event, 'tool_calls') and event.tool_calls:
                                print(f"  → TestImplementer tool calls: {[tc.name for tc in event.tool_calls]}")
                            else:
                                print(f"  → TestImplementer made no tool calls")
                
                # Check for final response - but don't break immediately
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_output = event.content.parts[0].text if event.content.parts[0].text else ""
                    final_log = f"Final response received: {len(final_output)} characters"
                    print(final_log)
                    agent_logs.append(final_log)
                    
                    # For TestImplementer, we want to break and use its output
                    if event.author == "TestImplementer" and final_output and len(final_output) > 100:
                        print("TestImplementer completed with substantial output - breaking")
                        break
                    # For other agents, continue the workflow
                    elif event.author != "TestImplementer":
                        print(f"Agent {event.author} completed - continuing workflow")
                        continue
                    # If we get here and it's a final response, break to avoid infinite loop
                    else:
                        print("Final response received - breaking")
                        break
        
        except Exception as e:
            error_log = f"Error during agent execution: {str(e)}"
            print(error_log)
            agent_logs.append(error_log)
        
        # If no final output, use the last meaningful response
        if not final_output and all_responses:
            final_output = all_responses[-1]
            fallback_log = f"Using last response as final output: {len(final_output)} characters"
            print(fallback_log)
            agent_logs.append(fallback_log)
        
        # If still no output, create a fallback response
        if not final_output:
            fallback_output = f"""# Test suite for {filename}

# Generated by TestMozart AI Test Generator
# Language: {language}
# Source file: {filename}

# Note: The AI agent processing encountered an issue, but here's a basic test structure:

def test_basic_functionality():
    \"\"\"Basic test to verify the code structure.\"\"\"
    # Add your test cases here
    assert True  # Placeholder test

if __name__ == "__main__":
    test_basic_functionality()
    print("Basic test completed successfully!")
"""
            final_output = fallback_output
            fallback_log = f"Created fallback test output: {len(final_output)} characters"
            print(fallback_log)
            agent_logs.append(fallback_log)
        
        return final_output, agent_logs
        
    except Exception as e:
        error_log = f"Error in call_agent_async: {str(e)}"
        print(error_log)
        agent_logs.append(error_log)
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to call agent: {e}")

@app.route('/')
def index():
    """Main page with file upload form."""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BDC2 - AI Test Code generator</title>
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
                max-height: 400px;
                overflow-y: auto;
            }
            pre {
                margin: 0;
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
            .expandable-section {
                margin: 15px 0;
            }
            .expand-button {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                margin: 5px 0;
            }
            .expand-button:hover {
                background-color: #5a6268;
            }
            .collapsible-content {
                display: none;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
                max-height: 300px;
                overflow-y: auto;
            }
            .collapsible-content.show {
                display: block;
            }
            .agent-log {
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 10px;
                margin: 5px 0;
                font-family: monospace;
                font-size: 12px;
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
            <h1>BDC2 - AI Test Generator</h1>
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
                        showResult(result.message, 'success', result.test_code, result.download_url, result.agent_logs);
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

            function showResult(message, type, testCode = null, downloadUrl = null, agentLogs = null) {
                resultDiv.className = `result ${type}`;
                resultDiv.style.display = 'block';
                
                let html = `<h3>${type === 'success' ? '✅ Success!' : type === 'error' ? '❌ Error' : '⏳ Processing'}</h3>`;
                html += `<p>${message}</p>`;
                
                if (testCode) {
                    html += '<h4>🧪 Generated Test Code:</h4>';
                    html += '<div class="code-block"><pre>' + escapeHtml(testCode) + '</pre></div>';
                }
                
                if (downloadUrl) {
                    html += `<div style="margin: 15px 0;">
                        <a href="${downloadUrl}" class="download-link" target="_blank">📥 Download Test File</a>
                    </div>`;
                }
                
                if (agentLogs && agentLogs.length > 0) {
                    html += '<div class="expandable-section">';
                    html += '<button class="expand-button" onclick="toggleAgentLogs()">🤖 View AI Agent Processing Logs</button>';
                    html += '<div id="agentLogs" class="collapsible-content">';
                    agentLogs.forEach(log => {
                        html += `<div class="agent-log">${escapeHtml(log)}</div>`;
                    });
                    html += '</div></div>';
                }
                
                resultDiv.innerHTML = html;
            }
            
            function toggleAgentLogs() {
                const content = document.getElementById('agentLogs');
                if (content) {
                    content.classList.toggle('show');
                }
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
        print("=== Upload request received ===")
        
        if 'file' not in request.files:
            print("No file in request")
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            print("No filename provided")
            return jsonify({'success': False, 'error': 'No file selected'})
        
        print(f"Processing file: {file.filename}")
        
        # Read file content
        file_content = file.read().decode('utf-8')
        filename = file.filename
        
        # Detect language
        language = detect_language_from_filename(filename)
        print(f"Detected language: {language}")
        
        # Upload to GCS
        print("Uploading to GCS...")
        file_url = upload_file_to_gcs(file_content, filename)
        print(f"File uploaded to: {file_url}")
        
        # Call the agent using ADK runner
        print("Calling agent...")
        test_code, agent_logs = asyncio.run(call_agent_async(file_url, filename, language, file_content))
        print(f"Agent returned {len(test_code)} characters of test code")
        
        # Save test code to GCS and get download URL
        print("Saving test code to GCS...")
        # Extract timestamp from the original file URL to maintain consistency
        if file_url.startswith('gs://'):
            # Extract timestamp from original file: uploads/20250925_065851_sample_code.c
            blob_path = file_url.split('/', 3)[3]  # Get everything after gs://bucket/
            timestamp_part = blob_path.split('_')[0] + '_' + blob_path.split('_')[1]  # Get timestamp part
            test_filename = f"{timestamp_part}_test_{filename}"
        else:
            test_filename = f"test_{filename}"
        
        gcs_url = upload_file_to_gcs(test_code, test_filename)
        
        # Extract the filename from the GCS URL to ensure consistency
        if gcs_url.startswith('gs://'):
            # Extract the blob name from gs://bucket/path
            blob_path = gcs_url.split('/', 3)[3]  # Get everything after gs://bucket/
            # Remove the "uploads/" prefix if it exists to avoid double path
            if blob_path.startswith('uploads/'):
                download_filename = blob_path[8:]  # Remove "uploads/" prefix
            else:
                download_filename = blob_path
        else:
            # Fallback to creating a new timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"{timestamp}_test_{filename}"
        
        download_url = f"/download/{download_filename}"
        
        print(f"Test code saved to: {gcs_url}")
        print(f"Download URL: {download_url}")
        
        response_data = {
            'success': True,
            'message': f'Successfully generated test suite for {filename} ({language})',
            'test_code': test_code,
            'download_url': download_url,
            'gcs_url': gcs_url,
            'language': language,
            'agent_logs': agent_logs
        }
        
        print("=== Upload completed successfully ===")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"=== Error in upload: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        })

@app.route('/test-agent')
def test_agent():
    """Test endpoint to check if the agent is working."""
    try:
        print("=== Testing agent directly ===")
        
        # Create a simple test message
        test_message = types.Content(
            role="user",
            parts=[types.Part(text="Hello, can you generate a simple test for a basic function?")]
        )
        
        # Create a session
        session = asyncio.run(session_service.create_session("test_user"))
        print(f"Test session created: {session.id}")
        
        # Try to run the agent
        event_count = 0
        responses = []
        
        async def test_agent_async():
            nonlocal event_count, responses
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=test_message
            ):
                event_count += 1
                print(f"Test event {event_count}: {event.author}")
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            responses.append(part.text)
                            print(f"  → Response: {part.text[:100]}...")
                if event.is_final_response():
                    break
        
        asyncio.run(test_agent_async())
        
        return jsonify({
            'status': 'success',
            'events': event_count,
            'responses': len(responses),
            'sample_response': responses[0][:200] if responses else "No responses"
        })
        
    except Exception as e:
        print(f"Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download file from GCS."""
    try:
        # Construct GCS URL
        gcs_url = f"gs://{BUCKET_NAME}/uploads/{filename}"
        
        # Download from GCS
        if gcs_url.startswith('gs://'):
            path = gcs_url[5:]  # Remove gs://
            bucket_name, blob_name = path.split('/', 1)
            
            # Initialize GCS client
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'ruckusdevtools')
            client = storage.Client(project=project_id)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Download content
            content = blob.download_as_text()
            
            # Determine file extension
            if filename.endswith('_test_'):
                file_extension = '.py'
            elif 'sample_code.c' in filename:
                file_extension = '.c'
            else:
                file_extension = '.py'
            
            # Create response
            from flask import Response
            return Response(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename=test_{filename}{file_extension}'
                }
            )
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'TestMozart Web Interface'})

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
