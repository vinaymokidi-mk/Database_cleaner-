"""
Gradio UI for Data Cleaning Pipeline
Auto-detects LLM API and uses intelligent cleaning
"""
import gradio as gr
import pandas as pd
import yaml
import os
from utils.call_llm import check_api_available, call_llm

# Auto-detect which flow to use
use_llm = False
try:
    if check_api_available():
        from flow_llm import create_llm_cleaning_flow
        use_llm = True
        print("✅ Using LLM-powered cleaning (AI mode)")
    else:
        from flow import create_local_cleaning_flow
        print("⚠️ Using rule-based cleaning (no API configured)")
except Exception as e:
    from flow import create_local_cleaning_flow
    print(f"⚠️ Falling back to rule-based cleaning: {e}")


# Global state
current_data = {"original": None, "cleaned": None, "report": None}


def clean_data(file):
    """Clean uploaded file and return health report"""
    if file is None:
        return "❌ Please upload a file first", None, None
    
    try:
        # Create shared store
        shared = {
            "input_file": file.name,
            "output_csv": "data/cleaned_data.csv",
            "output_excel": "data/cleaned_data.xlsx",
            "output_report": "data/health_report.yaml"
        }
        
        # Run cleaning flow (LLM or rule-based)
        if use_llm:
            flow = create_llm_cleaning_flow()
        else:
            flow = create_local_cleaning_flow()
        
        flow.run(shared)
        
        # Store in global state
        current_data["original"] = shared["df_original"]
        current_data["cleaned"] = shared["df_cleaned"]
        current_data["report"] = shared["health_report"]
        
        # Format health report for display
        report = shared["health_report"]
        report_text = f"""# 📊 Data Health Report

## Dataset Info
- **Rows:** {report['dataset_info']['total_rows']}
- **Columns:** {report['dataset_info']['total_columns']}
- **Original Quality:** {report['dataset_info']['original_quality_score']}%

## Issues Found
- **Total Anomalies:** {report['issues_found']['total_anomalies']}
- **By Severity:** {report['issues_found']['by_severity']}
- **By Type:** {report['issues_found']['by_type']}

## Fixes Applied
- **Total Fixes:** {report['fixes_applied']}
- **Final Quality:** {report['final_quality_score']}%

## Summary
{report['summary']}

## Recommendations
{report['recommendations']}
"""
        
        return report_text, "data/cleaned_data.xlsx", "data/health_report.yaml"
    
    except Exception as e:
        return f"❌ Error: {str(e)}", None, None


def chat_with_data(message, history):
    """Answer questions about the data using LLM if available"""
    if current_data["original"] is None:
        response = "⚠️ Please upload and clean a file first before asking questions."
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]
    
    df = current_data["cleaned"] if current_data["cleaned"] is not None else current_data["original"]
    
    # If LLM available, use it for intelligent responses
    if use_llm:
        try:
            data_summary = f"""Dataset Info:
- Rows: {len(df)}
- Columns: {', '.join(df.columns)}
- Sample (first 3 rows):
{df.head(3).to_string()}

Statistics:
{df.describe().to_string()}"""
            
            prompt = f"""You are a data analyst. Answer this question about the dataset.

{data_summary}

Question: {message}

Provide a clear, helpful answer using markdown formatting."""
            
            response = call_llm(prompt)
            return history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]
        
        except Exception as e:
            response = f"⚠️ LLM error: {str(e)[:100]}... Using rule-based response."
            # Continue to rule-based fallback
    
    # Rule-based responses (fallback or no LLM)
    message_lower = message.lower()
    
    # Generate response based on query
    response = ""
    
    # Basic statistics queries
    if "how many" in message_lower and ("row" in message_lower or "record" in message_lower):
        response = f"The dataset has **{len(df)} rows**."
    
    elif "how many" in message_lower and "column" in message_lower:
        response = f"The dataset has **{len(df.columns)} columns**: {', '.join(df.columns)}"
    
    elif "column" in message_lower and "name" in message_lower:
        response = f"**Columns:** {', '.join(df.columns)}"
    
    elif "describe" in message_lower or "summary" in message_lower:
        stats = df.describe().to_string()
        response = f"**Statistical Summary:**\n```\n{stats}\n```"
    
    elif "missing" in message_lower or "null" in message_lower:
        missing = df.isnull().sum()
        missing_info = "\n".join([f"- **{col}:** {count} missing" for col, count in missing.items() if count > 0])
        if missing_info:
            response = f"**Missing Values:**\n{missing_info}"
        else:
            response = "✅ No missing values found in the dataset."
    
    elif "quality" in message_lower or "health" in message_lower:
        if current_data["report"]:
            report = current_data["report"]
            response = f"""**Data Quality:**
- Original: {report['dataset_info']['original_quality_score']}%
- After Cleaning: {report['final_quality_score']}%
- Anomalies Found: {report['issues_found']['total_anomalies']}
- Fixes Applied: {report['fixes_applied']}"""
        else:
            response = "⚠️ Clean the data first to see quality metrics."
    
    # Show first few rows
    elif "show" in message_lower or "preview" in message_lower or "head" in message_lower:
        preview = df.head(5).to_markdown()
        response = f"**First 5 rows:**\n{preview}"
    
    else:
        # Column-specific queries
        found_column = False
        for col in df.columns:
            if col.lower() in message_lower:
                found_column = True
                if df[col].dtype in ['int64', 'float64']:
                    response = f"""**{col} Statistics:**
- Mean: {df[col].mean():.2f}
- Median: {df[col].median():.2f}
- Min: {df[col].min():.2f}
- Max: {df[col].max():.2f}
- Std Dev: {df[col].std():.2f}"""
                else:
                    unique = df[col].nunique()
                    most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
                    response = f"""**{col} Info:**
- Unique Values: {unique}
- Most Common: {most_common}
- Type: {df[col].dtype}"""
                break
        
        # Default response if no pattern matched
        if not found_column:
            response = """I can help you with:
- 📊 **Dataset info:** "How many rows?", "How many columns?"
- 📈 **Statistics:** "Describe the data", "Show summary"
- ❓ **Missing data:** "Show missing values"
- 🔍 **Preview:** "Show the data", "Preview dataset"
- 💊 **Quality:** "What's the data quality?"
- 📋 **Columns:** Ask about specific columns like "age" or "income"

Try asking one of these questions!"""
    
    # Return updated history in messages format
    return history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]


# Create Gradio Interface
with gr.Blocks(title="Data Cleaning Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🧹 Data Cleaning Assistant
    Upload your Excel file, clean it, and ask questions about your data!
    """)
    
    with gr.Tab("Clean Data"):
        with gr.Row():
            with gr.Column():
                file_upload = gr.File(
                    label="📁 Upload Excel File",
                    file_types=[".xlsx", ".xls", ".csv"]
                )
                clean_btn = gr.Button("🧹 Clean Data", variant="primary", size="lg")
            
            with gr.Column():
                health_report = gr.Markdown(label="📊 Health Report")
        
        with gr.Row():
            download_cleaned = gr.File(label="⬇️ Download Cleaned Data (Excel)")
            download_report = gr.File(label="⬇️ Download Health Report (YAML)")
        
        clean_btn.click(
            fn=clean_data,
            inputs=[file_upload],
            outputs=[health_report, download_cleaned, download_report]
        )
    
    with gr.Tab("💬 Ask Questions"):
        gr.Markdown("""
        ### 💬 Chat with Your Data
        Ask questions about your dataset after uploading and cleaning it.
        """)
        
        # Question input at TOP
        with gr.Row():
            with gr.Column(scale=9):
                msg = gr.Textbox(
                    placeholder="Type your question here... (e.g., 'How many rows?', 'Show missing values', 'Describe the data')",
                    label="📝 Your Question",
                    lines=2,
                    show_label=True
                )
            with gr.Column(scale=1, min_width=100):
                send_btn = gr.Button("▶️ Send", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Clear")
        
        gr.Markdown("""
        **💡 Example Questions:**
        - "How many rows and columns?"
        - "Show me missing values"
        - "What's the data quality score?"
        - "Describe the dataset"
        - "Show sample data"
        - "What are the column names?"
        """)
        
        # Results at BOTTOM
        chatbot = gr.Chatbot(
            height=500,
            type="messages",
            label="💬 Conversation History",
            show_label=True
        )
        
        # Button actions
        send_btn.click(chat_with_data, [msg, chatbot], [chatbot])
        send_btn.click(lambda: "", None, msg)  # Clear input after send
        
        msg.submit(chat_with_data, [msg, chatbot], [chatbot])
        msg.submit(lambda: "", None, msg)  # Clear input after Enter
        
        clear_btn.click(lambda: [], None, chatbot)  # Clear chat history
    
    gr.Markdown("""
    ---
    ### 📝 Tips:
    - Upload Excel (.xlsx, .xls) or CSV files
    - Click "Clean Data" to process and see the health report
    - Download both cleaned data and report
    - Ask questions in the chat tab about your data
    """)


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Launch the app
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)

