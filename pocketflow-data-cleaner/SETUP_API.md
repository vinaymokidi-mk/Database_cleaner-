# 🤖 LLM API Setup Guide

The app automatically detects and uses LLM APIs for intelligent data cleaning!

## ✨ How It Works

When you run `python app.py`, the app:
1. **Checks for API keys** (Gemini, OpenAI, or Anthropic)
2. **Auto-configures** the right API
3. **Uses AI** for smart cleaning if found
4. **Falls back** to rule-based if no API

**No manual configuration needed!** Just set an API key and run.

---

## 🚀 Quick Setup (3 Minutes)

### **Option 1: Google Gemini (RECOMMENDED - FREE)**

#### 1. Get API Key:
- Go to: https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Copy the key

#### 2. Install Library:
```bash
pip install google-genai
```

#### 3. Set Environment Variable:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_key_here
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY=your_key_here
```

#### 4. Run the App:
```bash
python app.py
```

You'll see: `✅ LLM API available: Gemini`

---

### **Option 2: OpenAI GPT**

#### 1. Get API Key:
- Go to: https://platform.openai.com/api-keys
- Create an API key

#### 2. Install & Set:
```bash
pip install openai
```

**Windows:**
```powershell
$env:OPENAI_API_KEY="your_key_here"
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY=your_key_here
```

---

### **Option 3: Anthropic Claude**

#### 1. Get API Key:
- Go to: https://console.anthropic.com/
- Create an API key

#### 2. Install & Set:
```bash
pip install anthropic
```

**Windows:**
```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=your_key_here
```

---

## 💡 Making API Keys Permanent

### **Windows (Permanent):**

1. Search "Environment Variables" in Start Menu
2. Click "Edit system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `GEMINI_API_KEY`
6. Variable value: `your_api_key_here`
7. Click OK

**OR** use PowerShell:
```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_key_here', 'User')
```

### **Mac/Linux (Permanent):**

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export GEMINI_API_KEY="your_key_here"
```

Then reload:
```bash
source ~/.bashrc
```

---

## 🔍 Verify Setup

### **Test Your API:**

```bash
python utils/call_llm.py
```

**Expected Output:**
```
✅ LLM API available: Gemini
Response: Hello! API working!
```

---

## 🎯 App Modes

### **AI Mode (With API):**
```
✅ Using LLM-powered cleaning (AI mode)
```

**Features:**
- ✅ Intelligent anomaly detection
- ✅ Context-aware data cleaning
- ✅ Smart fix proposals with reasoning
- ✅ Natural language chat with your data
- ✅ Comprehensive health reports

### **Rule-Based Mode (No API):**
```
⚠️ Using rule-based cleaning (no API configured)
```

**Features:**
- ✅ Basic anomaly detection (missing, outliers)
- ✅ Statistical imputation
- ✅ Simple cleaning rules
- ❌ No chat functionality
- ❌ Basic reports

---

## 📊 Comparison

| Feature | AI Mode | Rule-Based |
|---------|---------|------------|
| Detect missing values | ✅ | ✅ |
| Detect outliers | ✅ | ✅ |
| Understand context | ✅ | ❌ |
| Smart formatting fixes | ✅ | ❌ |
| Typo correction | ✅ | ❌ |
| Chat with data | ✅ | Limited |
| Detailed reports | ✅ | Basic |
| Speed | Slower | Fast |
| Cost | API usage | Free |

---

## 🔧 Troubleshooting

### **"No LLM API configured!"**

**Solution:** Set an environment variable:
```powershell
$env:GEMINI_API_KEY="your_key_here"
```

### **"google-genai not installed"**

**Solution:**
```bash
pip install google-genai
```

### **API Key Not Working**

1. Check the key is correct (no extra spaces)
2. Verify it's set:
   ```powershell
   echo $env:GEMINI_API_KEY
   ```
3. Restart terminal/PowerShell
4. Try running app again

### **Rate Limit Errors**

The app has built-in retry logic with 10-second waits. If you hit rate limits:
- **Gemini Free:** 15 requests/minute
- **OpenAI:** Depends on your plan
- **Solution:** Wait a minute, try again

---

## 🎓 Example Usage

### **1. Start with API:**
```powershell
$env:GEMINI_API_KEY="AIzaSyBfGENEwl3RI9kccCLredeR5bTL8_Q97kU"
python app.py
```

**Output:**
```
✅ LLM API available: Gemini
✅ Using LLM-powered cleaning (AI mode)
* Running on local URL:  http://127.0.0.1:7860
```

### **2. Upload & Clean:**
- Upload your messy Excel/CSV
- Click "🧹 Clean Data"
- Watch AI analyze and fix issues!

### **3. Chat with Your Data:**
```
You: "What patterns do you see in the data?"
AI: "I notice several interesting patterns:
1. Most customers are from urban areas (68%)
2. Purchase amounts cluster around $500-1000
3. Weekend sales are 30% higher than weekdays..."
```

---

## 🌟 Recommended: Gemini

**Why Gemini?**
- ✅ FREE tier (15 RPM)
- ✅ Fast responses
- ✅ Good at data analysis
- ✅ Easy setup
- ✅ Generous quotas

**Get Started:**
1. https://aistudio.google.com/app/apikey
2. `pip install google-genai`
3. Set `GEMINI_API_KEY`
4. Done! 🎉

---

## 🚀 Ready to Go!

```bash
# Install LLM library (choose one)
pip install google-genai

# Set your API key
$env:GEMINI_API_KEY="your_key_here"

# Run the app
python app.py
```

**That's it!** The app handles everything else automatically! 🎉



