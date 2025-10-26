# 🧹 Data Cleaning Assistant

A simple, local data cleaning application with a web interface. Upload your messy Excel/CSV files and get them cleaned automatically!

## ✨ Features

- 📁 **File Upload** - Support for Excel (.xlsx, .xls) and CSV files
- 🧹 **Automatic Cleaning** - Detects and fixes:
  - Missing values (imputed with median/mode)
  - Outliers (replaced with median)
  - Invalid/rare values (corrected to most common)
- 📊 **Health Report** - Quality scores and cleaning summary
- ⬇️ **Downloads** - Get cleaned Excel file and YAML report
- 💬 **Chat Interface** - Ask questions about your data

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the App
```bash
python app.py
```

or double-click: `START_APP.bat`

### 3. Open in Browser
```
http://127.0.0.1:7860
```

## 📖 How to Use

### Clean Data Tab
1. Click "📁 Upload Excel File"
2. Select your file (Excel or CSV)
3. Click "🧹 Clean Data"
4. View the health report
5. Download cleaned data and report

### Ask Questions Tab
1. Upload and clean a file first
2. Go to "💬 Ask Questions" tab
3. Type questions like:
   - "How many rows?"
   - "Show missing values"
   - "What's the data quality?"
   - "Describe the data"

## 📊 What Gets Cleaned

| Issue Type | Detection Method | Fix Strategy |
|------------|------------------|--------------|
| Missing Values | Pandas `.isnull()` | Impute with median (numeric) or mode (categorical) |
| Outliers | IQR method (Q1-1.5×IQR, Q3+1.5×IQR) | Replace with median |
| Invalid Values | Rare values (appears once) | Replace with most common value |

## 📁 Project Structure

```
pocketflow-data-cleaner/
├── app.py              # Gradio UI
├── flow.py             # Pipeline orchestration
├── nodes.py            # 7 cleaning nodes
├── utils/              # Helper functions
│   ├── load_csv.py
│   └── save_csv.py
├── data/               # Output directory
├── requirements.txt    # Dependencies
└── START_APP.bat       # Quick launcher
```

## 🔧 Requirements

- Python 3.7+
- pocketflow
- pandas
- numpy
- pyyaml
- openpyxl (for Excel support)
- gradio (for UI)
- tabulate (for chat)

## 💡 Tips

- **Large files?** The app can handle thousands of rows
- **No internet needed** - Everything runs locally
- **Privacy** - Your data never leaves your computer
- **No API keys** - No external services required

## 🛠️ Customization

Edit `nodes.py` to customize cleaning rules:
- Change imputation strategies
- Adjust outlier thresholds
- Add custom validation logic

## 🆘 Troubleshooting

**App won't start?**
```bash
pip install -r requirements.txt
python app.py
```

**Port already in use?**
```bash
# Check what's using port 7860
netstat -ano | findstr :7860
```

**Can't upload file?**
- Check file format (must be .xlsx, .xls, or .csv)
- Ensure file isn't corrupted

## 📄 License

This project is built using PocketFlow framework.

## 🎉 Enjoy!

Your data cleaning assistant is ready to use. No setup, no API keys, no complexity!

**Open:** http://127.0.0.1:7860
