# 🚀 Quick Start Guide

## ✅ API Key is Now Set Permanently!

Your Gemini API key has been saved to your Windows environment.

---

## 🎯 How to Run the App

### **Option 1: Double-Click (Easiest)**

1. Find `START_APP_SIMPLE.bat` in this folder
2. Double-click it
3. Browser opens automatically at http://127.0.0.1:7860

### **Option 2: Command Line**

**IMPORTANT:** Close and reopen PowerShell first!

```powershell
cd "C:\Users\Dcruise\git\Database cleaner\PocketFlow\pocketflow-data-cleaner"
python app.py
```

Then open: http://127.0.0.1:7860

---

## ⚠️ First Time After Setting API Key

**You MUST restart your terminal/PowerShell!**

Why? Windows needs to reload environment variables.

**Steps:**
1. Close this PowerShell window
2. Open a NEW PowerShell window
3. Run: `python app.py`

---

## ✅ Verify API Key is Working

In your NEW PowerShell window:

```powershell
# Check if key is set
echo $env:GEMINI_API_KEY
```

**Expected:** Shows your API key

If it shows nothing, restart PowerShell again.

---

## 🎉 What You'll See

When you run `python app.py`:

```
✅ LLM API available: Gemini
✅ Using LLM-powered cleaning (AI mode)
* Running on local URL:  http://127.0.0.1:7860
```

---

## 🛠️ Troubleshooting

### **"No LLM API configured"**

**Cause:** API key not loaded yet

**Fix:**
1. Close PowerShell
2. Open NEW PowerShell
3. Try again

### **Port 7860 already in use**

**Fix:**
```powershell
Get-Process python | Stop-Process -Force
python app.py
```

### **Module not found**

**Fix:**
```powershell
pip install -r requirements.txt
pip install google-genai
```

---

## 🎯 Using the App

### **1. Clean Data Tab**
- Upload Excel/CSV file
- Click "🧹 Clean Data"
- Download results

### **2. Ask Questions Tab**
- Type your question at the TOP
- Click "▶️ Send" button
- See AI response at the BOTTOM

---

## 📋 Quick Commands

```powershell
# Start app
python app.py

# Stop app (if running)
Get-Process python | Stop-Process -Force

# Check API key
echo $env:GEMINI_API_KEY

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🎉 You're Ready!

The API key is permanent - you only need to set it once!

From now on, just:
1. Open PowerShell
2. `cd pocketflow-data-cleaner`
3. `python app.py`

**Or just double-click `START_APP_SIMPLE.bat`!** 🚀



