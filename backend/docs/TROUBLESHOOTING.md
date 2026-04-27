# Troubleshooting Guide

Panduan lengkap untuk mengatasi masalah umum yang mungkin terjadi.

---

## Quick Diagnostics

Jalankan script diagnostik untuk cek semua komponen:

```bash
python run_tests.py
```

---

## Common Issues

### 1. ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Penyebab:**
- Dependencies belum terinstall
- Virtual environment tidak aktif
- Python version tidak sesuai

**Solusi:**
```bash
# Install dependencies
pip install -r requirements.txt

# Atau install ulang
pip install --upgrade -r requirements.txt

# Cek installed packages
pip list | grep fastapi
```

---

### 2. AWS Credentials Error

**Error:**
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

atau

```
botocore.exceptions.ClientError: An error occurred (UnrecognizedClientException)
```

**Penyebab:**
- File `.env` tidak ada atau salah
- AWS credentials tidak valid
- Region tidak sesuai

**Solusi:**

1. **Cek file .env:**
```bash
# Windows
type .env

# Linux/Mac
cat .env
```

2. **Verify credentials:**
```python
python test_aws.py
```

3. **Test AWS CLI:**
```bash
aws bedrock list-foundation-models --region us-east-1
```

4. **Cek environment variables:**
```python
from config import get_settings
settings = get_settings()
print(f"AWS Key: {settings.aws_access_key_id[:5]}***")
print(f"Region: {settings.aws_region}")
```

5. **Regenerate credentials:**
- Login ke AWS Console
- IAM → Users → Security Credentials
- Create new access key
- Update `.env` file

---

### 3. Qdrant Connection Error

**Error:**
```
qdrant_client.http.exceptions.UnexpectedResponse: Unexpected Response: 401 (Unauthorized)
```

atau

```
requests.exceptions.ConnectionError: Failed to establish a new connection
```

**Penyebab:**
- Qdrant URL atau API key salah
- Qdrant cluster tidak aktif
- Network issue

**Solusi:**

1. **Test connection:**
```python
python test_qdrant.py
```

2. **Verify credentials:**
```python
from config import get_settings
settings = get_settings()
print(f"URL: {settings.qdrant_url}")
print(f"Key: {settings.qdrant_api_key[:10]}***")
```

3. **Test dengan curl:**
```bash
curl https://your-cluster.aws.cloud.qdrant.io/collections \
  -H "api-key: your-api-key"
```

4. **Cek Qdrant Console:**
- Login ke Qdrant Cloud
- Verify cluster is running
- Check API key is valid

---

### 4. Model Not Found Error

**Error:**
```
botocore.errorfactory.ResourceNotFoundException: Could not resolve the foundation model
```

**Penyebab:**
- Model belum enabled di AWS Bedrock
- Model ID salah
- Region tidak support model

**Solusi:**

1. **Enable model di AWS Console:**
   - Go to AWS Bedrock Console
   - Model access → Manage model access
   - Enable:
     - Claude 3.5 Sonnet v2
     - Titan Embeddings V2

2. **Verify model ID:**
```python
# In config.py
embedding_model: str = "amazon.titan-embed-text-v2:0"
llm_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
```

3. **Check available models:**
```bash
aws bedrock list-foundation-models --region us-east-1
```

---

### 5. Port Already in Use

**Error:**
```
ERROR: [Errno 48] Address already in use
ERROR: [Errno 98] Address already in use (Linux)
```

**Penyebab:**
- Port 8000 sudah digunakan
- Server masih running di background

**Solusi:**

**Windows:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

---

### 6. Slow Response Time

**Symptoms:**
- API response takes > 10 seconds
- Timeout errors
- High latency

**Penyebab:**
- First request (cold start)
- AWS Bedrock throttling
- Network latency
- Large conversation history

**Solusi:**

1. **First request is always slower:**
   - Wait for initialization
   - Subsequent requests will be faster

2. **Check AWS quotas:**
   - AWS Console → Service Quotas
   - Check Bedrock limits

3. **Reduce conversation history:**
```python
# Keep only last 4 messages
conversation_history = conversation_history[-4:]
```

4. **Optimize prompt:**
   - Reduce context length
   - Simplify prompt

5. **Add timeout:**
```python
# In rag_service.py
self.llm = ChatBedrock(
    ...,
    request_timeout=30  # 30 seconds
)
```

---

### 7. Empty Restaurant Results

**Symptoms:**
- API returns empty restaurants array
- No recommendations

**Penyebab:**
- Qdrant collection empty
- Data not ingested
- Search query too specific

**Solusi:**

1. **Check collection:**
```python
python test_qdrant.py
```

2. **Verify data count:**
```python
from qdrant_client import QdrantClient
from config import get_settings

settings = get_settings()
client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
info = client.get_collection(settings.qdrant_collection_name)
print(f"Points: {info.points_count}")  # Should be 3900
```

3. **Re-ingest data:**
```bash
python ingest_data.py
```

---

### 8. Encoding Errors

**Error:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Penyebab:**
- CSV file encoding issue
- Special characters

**Solusi:**

1. **Specify encoding:**
```python
# In ingest_data.py
df = pd.read_csv('cleaned_enhanced_data_2.csv', encoding='utf-8')
```

2. **Try different encodings:**
```python
# Try latin-1
df = pd.read_csv('cleaned_enhanced_data_2.csv', encoding='latin-1')

# Or cp1252
df = pd.read_csv('cleaned_enhanced_data_2.csv', encoding='cp1252')
```

---

### 9. Memory Error

**Error:**
```
MemoryError: Unable to allocate array
```

**Penyebab:**
- Processing too much data at once
- Insufficient RAM

**Solusi:**

1. **Process in smaller batches:**
```python
# In ingest_data.py
batch_size = 5  # Reduce from 10
```

2. **Use chunking:**
```python
# Process CSV in chunks
for chunk in pd.read_csv('file.csv', chunksize=100):
    process_chunk(chunk)
```

3. **Increase system memory:**
- Close other applications
- Use machine with more RAM

---

### 10. JSON Decode Error

**Error:**
```
json.decoder.JSONDecodeError: Expecting value
```

**Penyebab:**
- Invalid JSON in request
- Response not JSON
- API error

**Solusi:**

1. **Validate request JSON:**
```python
import json

# Test your JSON
json_str = '{"message": "test"}'
json.loads(json_str)  # Should not error
```

2. **Check API response:**
```bash
curl -v http://localhost:8000/health
```

3. **Add error handling:**
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()
except json.JSONDecodeError:
    print("Invalid JSON response")
    print(response.text)
```

---

## Installation Issues

### Python Version Mismatch

**Error:**
```
ERROR: Package requires Python >=3.9
```

**Solusi:**
```bash
# Check Python version
python --version

# Use Python 3.9+
python3.9 -m venv venv
```

### Pip Install Fails

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solusi:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with --user
pip install --user -r requirements.txt

# Or use sudo (Linux/Mac)
sudo pip install -r requirements.txt
```

---

## Runtime Issues

### Import Error After Install

**Error:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Solusi:**
```bash
# Reinstall package
pip uninstall package-name
pip install package-name

# Clear cache
pip cache purge

# Restart Python interpreter
```

### Environment Variables Not Loading

**Error:**
```
ValidationError: field required
```

**Solusi:**

1. **Check .env file exists:**
```bash
ls -la .env
```

2. **Verify .env format:**
```
KEY=value
# No spaces around =
# No quotes needed
```

3. **Restart application:**
```bash
# Kill and restart
python main.py
```

4. **Load manually:**
```python
from dotenv import load_dotenv
load_dotenv(override=True)
```

---

## Data Issues

### CSV File Not Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'cleaned_enhanced_data_2.csv'
```

**Solusi:**
```bash
# Check file exists
ls -la cleaned_enhanced_data_2.csv

# Check current directory
pwd

# Run from correct directory
cd /path/to/project
python ingest_data.py
```

### Data Ingestion Fails

**Error:**
```
Error processing row X: ...
```

**Solusi:**

1. **Check data format:**
```python
import pandas as pd
df = pd.read_csv('cleaned_enhanced_data_2.csv')
print(df.head())
print(df.dtypes)
```

2. **Handle errors:**
```python
# In ingest_data.py
try:
    # process row
except Exception as e:
    print(f"Error at row {idx}: {e}")
    continue  # Skip problematic row
```

---

## Performance Issues

### High CPU Usage

**Symptoms:**
- CPU at 100%
- System slow

**Solusi:**

1. **Reduce concurrent requests:**
```python
# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

2. **Optimize code:**
- Use async operations
- Add caching
- Reduce batch size

### High Memory Usage

**Symptoms:**
- Memory constantly increasing
- Out of memory errors

**Solusi:**

1. **Check for memory leaks:**
```python
import tracemalloc
tracemalloc.start()
# ... run code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
```

2. **Clear cache:**
```python
import gc
gc.collect()
```

---

## Network Issues

### Connection Timeout

**Error:**
```
requests.exceptions.ConnectTimeout
```

**Solusi:**

1. **Increase timeout:**
```python
requests.post(url, json=data, timeout=30)
```

2. **Check network:**
```bash
ping aws.amazon.com
ping qdrant.tech
```

3. **Check firewall:**
- Allow outbound HTTPS (443)
- Check corporate proxy

### SSL Certificate Error

**Error:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solusi:**

1. **Update certificates:**
```bash
pip install --upgrade certifi
```

2. **Temporary workaround (not recommended for production):**
```python
import urllib3
urllib3.disable_warnings()
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Print Request/Response

```python
# In rag_service.py
print(f"Query: {user_query}")
print(f"Retrieved: {len(retrieved_restaurants)} restaurants")
print(f"Filtered: {len(filtered_restaurants)} restaurants")
print(f"Response length: {len(response.content)}")
```

### Use Python Debugger

```python
import pdb

# Add breakpoint
pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

### Check API Logs

```bash
# Run with verbose logging
uvicorn main:app --log-level debug

# Or redirect to file
uvicorn main:app > app.log 2>&1
```

---

## Getting Help

### Before Asking for Help

1. ✅ Run `python run_tests.py`
2. ✅ Check error message carefully
3. ✅ Search this troubleshooting guide
4. ✅ Check documentation
5. ✅ Try suggested solutions

### When Asking for Help

Include:
- Error message (full traceback)
- Python version: `python --version`
- OS: Windows/Linux/Mac
- What you tried
- Relevant code snippets
- Output of `python run_tests.py`

### Useful Commands for Diagnostics

```bash
# System info
python --version
pip --version
pip list

# Check services
python test_aws.py
python test_qdrant.py

# Check files
ls -la
cat .env

# Check processes
ps aux | grep python  # Linux/Mac
tasklist | findstr python  # Windows

# Check network
ping aws.amazon.com
curl http://localhost:8000/health
```

---

## Emergency Fixes

### Complete Reset

```bash
# 1. Stop all processes
pkill -f "python main.py"

# 2. Remove virtual environment
rm -rf venv

# 3. Recreate environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 4. Reinstall dependencies
pip install -r requirements.txt

# 5. Re-ingest data
python ingest_data.py

# 6. Restart server
python main.py
```

### Quick Health Check

```bash
# One-liner to check everything
python -c "from config import get_settings; s=get_settings(); print('Config OK')" && \
python test_aws.py && \
python test_qdrant.py && \
echo "All systems operational!"
```

---

## Still Having Issues?

1. Check GitHub Issues (if applicable)
2. Review documentation again
3. Contact support team
4. Provide full diagnostic output

Remember: Most issues are configuration-related. Double-check your `.env` file!
