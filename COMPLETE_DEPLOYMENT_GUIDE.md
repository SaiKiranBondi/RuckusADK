# 🚀 TestMozart Complete Deployment & Usage Guide

This guide will walk you through **exactly** how to deploy TestMozart and use it with file uploads, including all permissions, URLs, and step-by-step instructions.

## 📋 **Prerequisites Checklist**

Before starting, ensure you have:
- [ ] Google Cloud Project: `ruckusdevtools`
- [ ] Google Cloud SDK installed
- [ ] ADK (Agent Development Kit) installed
- [ ] Python 3.8+ installed
- [ ] Access to Google Cloud Console

---

## 🔐 **Step 1: Set Up Google Cloud Permissions**

### **1.1 Enable Required APIs**
```bash
# Enable all required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### **1.2 Set Up Authentication**
```bash
# Login to Google Cloud
gcloud auth login

# Set up application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project ruckusdevtools

# Set quota project for Vertex AI
gcloud auth application-default set-quota-project ruckusdevtools
```

### **1.3 Required IAM Roles**
Your user account needs these roles:
- **Vertex AI User** (`roles/aiplatform.user`)
- **Cloud Run Admin** (`roles/run.admin`)
- **Storage Admin** (`roles/storage.admin`)
- **Cloud Build Editor** (`roles/cloudbuild.builds.editor`)

**To add these roles:**
1. Go to [Google Cloud Console IAM](https://console.cloud.google.com/iam-admin/iam)
2. Find your user account
3. Click "Edit" (pencil icon)
4. Add the roles listed above
5. Click "Save"

### **1.4 Create GCS Bucket**
```bash
# Create the bucket for file storage
gsutil mb gs://saikiranruckusdevtools-bucket

# Make bucket publicly readable (for downloads)
gsutil iam ch allUsers:objectViewer gs://saikiranruckusdevtools-bucket
```

---

## 🛠️ **Step 2: Deploy the Agent**

### **2.1 Set Up Environment**
```bash
# Navigate to your testmozart directory
cd /path/to/your/testmozart

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### **2.2 Deploy Agent to Agent Engine**
```bash
# Deploy the agent
adk deploy agent_engine RuckusADK \
  --display_name "TestMozart AI Test Generator" \
  --staging_bucket gs://saikiranruckusdevtools-bucket
```

**Expected Output:**
```
✅ Agent deployed successfully!
🎉 Your TestMozart agent is now available at: testmozart
```

### **2.3 Deploy Web Interface**
```bash
# Deploy web interface to Cloud Run
gcloud run deploy testmozart-web \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=ruckusdevtools \
  --memory 2Gi \
  --timeout 3600
```

**Expected Output:**
```
✅ Service [testmozart-web] revision [testmozart-web-00001-abc] has been deployed
🌐 Service URL: https://testmozart-web-xxxxx-uc.a.run.app
```

---

## 🌐 **Step 3: Access Your Deployed System**

### **3.1 Get Your URLs**

After deployment, you'll have:

1. **Agent Engine URL**: `https://agentengine.googleapis.com/v1/projects/ruckusdevtools/agents/testmozart`
2. **Web Interface URL**: `https://testmozart-web-xxxxx-uc.a.run.app`

**To find your exact URLs:**
```bash
# Get Agent Engine URL
echo "Agent Engine: https://agentengine.googleapis.com/v1/projects/ruckusdevtools/agents/testmozart"

# Get Web Interface URL
gcloud run services describe testmozart-web --region=us-central1 --format="value(status.url)"
```

### **3.2 Test Your Deployment**
```bash
# Test if web interface is running
curl https://your-web-interface-url/health

# Expected response: {"status": "healthy", "service": "TestMozart Web Interface"}
```

---

## 📁 **Step 4: How to Use the System**

### **4.1 Method 1: Web Interface (Recommended)**

1. **Open your web interface URL** in a browser:
   ```
   https://testmozart-web-xxxxx-uc.a.run.app
   ```

2. **Upload a file**:
   - Drag and drop your `.py` or `.c` file onto the upload area
   - OR click to select a file from your computer
   - Supported formats: `.py` (Python), `.c` (C)

3. **Generate tests**:
   - Click "🚀 Generate Tests"
   - Wait 1-3 minutes for processing
   - Download the generated test file

4. **Example workflow**:
   ```
   Upload: sample_code.py
   ↓
   Processing: AI analyzes code and generates tests
   ↓
   Download: final_test_suite.py
   ```

### **4.2 Method 2: Direct API Calls**

You can also call the agent directly via API:

```python
import requests
import json

# Your web interface URL
WEB_URL = "https://testmozart-web-xxxxx-uc.a.run.app"

# Upload a file
def upload_and_generate_tests(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{WEB_URL}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Generated tests: {result['test_code']}")
        print(f"Download URL: {result['download_url']}")
    else:
        print(f"❌ Error: {response.text}")

# Usage
upload_and_generate_tests("sample_code.py")
```

### **4.3 Method 3: Agent Engine Direct API**

For advanced users, you can call the agent directly:

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

# Initialize runner
runner = Runner(
    app_name="testmozart_agent",
    agent=your_deployed_agent,
    session_service=InMemorySessionService()
)

# Create session
session = await runner.session_service.create_session(
    app_name="testmozart_agent",
    user_id="api_user"
)

# Prepare request with file URL
request_data = {
    "file_url": "gs://saikiranruckusdevtools-bucket/uploads/20241201_143022_sample_code.py",
    "filename": "sample_code.py",
    "language": "python"
}

user_message = types.Content(
    role="user",
    parts=[types.Part(text=json.dumps(request_data))]
)

# Run the agent
async for event in runner.run_async(
    user_id=session.user_id,
    session_id=session.id,
    new_message=user_message
):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

---

## 🧪 **Step 5: Testing Your Deployment**

### **5.1 Test with Sample Files**

1. **Create test files**:
   ```bash
   # Create a simple Python test file
   echo 'def add(a, b): return a + b' > test_sample.py
   
   # Create a simple C test file
   echo 'int add(int a, int b) { return a + b; }' > test_sample.c
   ```

2. **Upload via web interface**:
   - Go to your web interface URL
   - Upload `test_sample.py`
   - Wait for test generation
   - Download the generated test file

3. **Verify results**:
   ```bash
   # Run the generated Python tests
   pytest final_test_suite.py -v
   
   # Compile and run C tests
   gcc -o test_runner final_test_suite.c -std=c99
   ./test_runner
   ```

### **5.2 Expected Results**

**For Python files**:
- Input: `test_sample.py`
- Output: `final_test_suite.py` with pytest tests
- Command: `pytest final_test_suite.py -v`

**For C files**:
- Input: `test_sample.c`
- Output: `final_test_suite.c` with simple C assertions
- Command: `gcc -o test_runner final_test_suite.c -std=c99 && ./test_runner`

---

## 🔍 **Step 6: Monitoring and Troubleshooting**

### **6.1 Check Deployment Status**

```bash
# Check if agent is deployed
adk list agents

# Check if web interface is running
gcloud run services list --filter="metadata.name:testmozart-web"

# Check GCS bucket
gsutil ls gs://saikiranruckusdevtools-bucket/
```

### **6.2 View Logs**

```bash
# View agent logs
gcloud logging read "resource.type=agent_engine" --limit=50

# View web interface logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# View GCS access logs
gcloud logging read "resource.type=gcs_bucket" --limit=50
```

### **6.3 Common Issues & Solutions**

#### **Issue: "Permission denied" errors**
```bash
# Solution: Re-authenticate and set permissions
gcloud auth application-default login
gcloud auth application-default set-quota-project ruckusdevtools
```

#### **Issue: "Agent not found"**
```bash
# Solution: Check if agent is deployed
adk list agents
# If not listed, redeploy:
adk deploy agent_engine testmozart --display_name "TestMozart AI Test Generator" --staging_bucket gs://saikiranruckusdevtools-bucket
```

#### **Issue: "Web interface not accessible"**
```bash
# Solution: Check Cloud Run status
gcloud run services describe testmozart-web --region=us-central1
# If not running, redeploy:
gcloud run deploy testmozart-web --source . --platform managed --region us-central1
```

#### **Issue: "File upload fails"**
```bash
# Solution: Check GCS bucket permissions
gsutil iam get gs://saikiranruckusdevtools-bucket
# Ensure bucket exists and is accessible
```

---

## 📊 **Step 7: Usage Examples**

### **7.1 Example 1: Python Calculator**

1. **Create test file** (`calculator.py`):
   ```python
   class Calculator:
       def add(self, a, b):
           return a + b
       
       def multiply(self, a, b):
           return a * b
   ```

2. **Upload via web interface**
3. **Download generated tests** (`final_test_suite.py`)
4. **Run tests**: `pytest final_test_suite.py -v`

### **7.2 Example 2: C Math Functions**

1. **Create test file** (`math.c`):
   ```c
   int add(int a, int b) {
       return a + b;
   }
   
   int multiply(int a, int b) {
       return a * b;
   }
   ```

2. **Upload via web interface**
3. **Download generated tests** (`final_test_suite.c`)
4. **Run tests**: `gcc -o test_runner final_test_suite.c -std=c99 && ./test_runner`

---

## 🎯 **Step 8: Success Verification**

Your deployment is successful when:

- [ ] ✅ Agent deploys without errors
- [ ] ✅ Web interface is accessible at the provided URL
- [ ] ✅ File upload works (drag & drop or click to select)
- [ ] ✅ Test generation completes successfully
- [ ] ✅ Generated test files are downloadable
- [ ] ✅ Both Python (.py) and C (.c) files are supported
- [ ] ✅ Generated tests run successfully

---

## 🔄 **Step 9: Updates and Maintenance**

### **9.1 Update Agent**
```bash
# Make changes to your code
# Then redeploy
adk deploy agent_engine testmozart --display_name "TestMozart AI Test Generator" --staging_bucket gs://saikiranruckusdevtools-bucket
```

### **9.2 Update Web Interface**
```bash
# Make changes to web_interface.py
# Then redeploy
gcloud run deploy testmozart-web --source . --platform managed --region us-central1
```

### **9.3 Monitor Costs**
```bash
# Check Vertex AI usage
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" --limit=10

# Check Cloud Run usage
gcloud logging read "resource.type=cloud_run_revision" --limit=10
```

---

## 📞 **Support and Help**

### **Quick Commands Reference**
```bash
# Deploy agent
adk deploy agent_engine testmozart --display_name "TestMozart AI Test Generator" --staging_bucket gs://saikiranruckusdevtools-bucket

# Deploy web interface
gcloud run deploy testmozart-web --source . --platform managed --region us-central1 --allow-unauthenticated

# Check status
adk list agents
gcloud run services list

# View logs
gcloud logging read "resource.type=agent_engine" --limit=20
```

### **Important URLs**
- **Web Interface**: `https://testmozart-web-xxxxx-uc.a.run.app`
- **Agent Engine**: `https://agentengine.googleapis.com/v1/projects/ruckusdevtools/agents/testmozart`
- **GCS Bucket**: `gs://saikiranruckusdevtools-bucket`

### **File Upload Process**
1. **Go to web interface URL**
2. **Drag & drop your .py or .c file**
3. **Click "Generate Tests"**
4. **Wait 1-3 minutes**
5. **Download the generated test file**

---

## 🎉 **You're All Set!**

Your TestMozart system is now deployed and ready to use! You can:

- ✅ **Upload files** via the web interface
- ✅ **Generate tests** automatically with AI
- ✅ **Download results** as ready-to-run test files
- ✅ **Support both Python and C** code
- ✅ **Scale automatically** with Google Cloud

**Next Steps:**
1. Test with your own code files
2. Integrate into your development workflow
3. Share the web interface URL with your team
4. Monitor usage and costs in Google Cloud Console

---

*Happy testing with TestMozart! 🚀*
