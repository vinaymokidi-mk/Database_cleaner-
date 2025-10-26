"""
LLM-Powered Node definitions for intelligent data cleaning
"""
import pandas as pd
import numpy as np
import yaml
from pocketflow import Node, BatchNode
from utils.load_csv import load_csv
from utils.save_csv import save_csv
from utils.call_llm import call_llm
from utils.parse_yaml import parse_yaml


class LoadDataNode(Node):
    """Load CSV/Excel file into pandas DataFrame"""
    
    def prep(self, shared):
        return shared["input_file"]
    
    def exec(self, filepath):
        if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
            df = pd.read_excel(filepath)
        else:
            df = load_csv(filepath)
        print(f"📂 Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def post(self, shared, prep_res, exec_res):
        shared["df_original"] = exec_res
        return "default"


class ProfileDataNode(Node):
    """LLM analyzes dataset and provides insights"""
    
    def prep(self, shared):
        df = shared["df_original"]
        # Create a summary of the data
        summary = {
            "shape": f"{len(df)} rows × {len(df.columns)} columns",
            "columns": list(df.columns),
            "sample_rows": df.head(3).to_dict('records'),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing": {col: int(df[col].isnull().sum()) for col in df.columns}
        }
        return summary
    
    def exec(self, summary):
        prompt = f"""Analyze this dataset and provide a profile.

Dataset Summary:
- Shape: {summary['shape']}
- Columns: {', '.join(summary['columns'])}
- Missing values: {summary['missing']}
- Sample data (first 3 rows):
{yaml.dump(summary['sample_rows'], default_flow_style=False)}

Provide a profile in YAML format:

```yaml
data_type: <e.g., "customer data", "sales data", "employee records">
column_analysis:
  <column_name>:
    type: <numeric|categorical|date|email|phone|text>
    description: <what this column represents>
    quality_issues: <any obvious issues>
insights:
  - <key insight 1>
  - <key insight 2>
```

Return ONLY valid YAML in code fences."""
        
        response = call_llm(prompt)
        profile = parse_yaml(response)
        return profile
    
    def post(self, shared, prep_res, exec_res):
        shared["profile"] = exec_res
        print(f"📊 LLM analyzed {len(shared['df_original'].columns)} columns")
        return "default"


class DetectAnomaliesBatchNode(BatchNode):
    """LLM detects anomalies in each column"""
    
    def prep(self, shared):
        df = shared["df_original"]
        profile = shared["profile"]
        
        items = []
        for col in df.columns:
            col_info = profile.get("column_analysis", {}).get(col, {})
            items.append((col, df[col].tolist(), col_info))
        return items
    
    def exec(self, item):
        col_name, col_data, col_info = item
        
        # Sample data (max 20 values)
        sample_data = col_data[:20] if len(col_data) > 20 else col_data
        
        prompt = f"""Detect data quality issues in this column.

Column: {col_name}
Type: {col_info.get('type', 'unknown')}
Description: {col_info.get('description', 'N/A')}
Sample data: {sample_data}

Detect these issues:
1. Missing values (NULL, NaN, empty, "null" as string)
2. Outliers (unusually high/low numbers)
3. Invalid formats (bad emails, wrong dates, etc.)
4. Inconsistent formatting (case issues, spacing)

Return in YAML:

```yaml
anomalies:
  - row_idx: <index number>
    issue_type: <missing|outlier|invalid|inconsistent>
    current_value: <current value>
    severity: <high|medium|low>
    reason: <why this is an issue>
```

Return ONLY valid YAML. If no issues, return empty anomalies list."""
        
        response = call_llm(prompt)
        result = parse_yaml(response)
        return result
    
    def post(self, shared, prep_res, exec_res_list):
        all_anomalies = []
        for i, (col_name, _, _) in enumerate(prep_res):
            for anomaly in exec_res_list[i].get("anomalies", []):
                anomaly["column"] = col_name
                all_anomalies.append(anomaly)
        
        shared["anomalies"] = all_anomalies
        print(f"🔍 LLM detected {len(all_anomalies)} anomalies")
        return "default"


class ProposeFixesNode(Node):
    """LLM proposes fixes for detected anomalies"""
    
    def prep(self, shared):
        df = shared["df_original"]
        anomalies = shared["anomalies"]
        profile = shared["profile"]
        
        # Group anomalies by column for context
        by_column = {}
        for anom in anomalies:
            col = anom["column"]
            if col not in by_column:
                by_column[col] = []
            by_column[col].append(anom)
        
        return df, by_column, profile
    
    def exec(self, prep_res):
        df, anomalies_by_col, profile = prep_res
        
        all_fixes = []
        for col_name, anomalies in anomalies_by_col.items():
            # Get column context
            col_data = df[col_name].tolist()
            col_info = profile.get("column_analysis", {}).get(col_name, {})
            
            prompt = f"""Propose fixes for data quality issues.

Column: {col_name}
Type: {col_info.get('type', 'unknown')}
Column data sample: {col_data[:15]}

Issues detected:
{yaml.dump(anomalies, default_flow_style=False)}

For each issue, propose a fix in YAML:

```yaml
fixes:
  - row_idx: <same as anomaly>
    column: "{col_name}"
    issue_type: <same as anomaly>
    current_value: <current value>
    proposed_value: <your proposed fix>
    strategy: <explain strategy>
    justification: <why this fix>
```

Rules:
- Keep original data when possible
- For missing: impute with median/mode/average
- For outliers: cap at reasonable bounds or use median
- For format issues: standardize format
- For typos: correct obvious mistakes

Return ONLY valid YAML."""
            
            response = call_llm(prompt)
            result = parse_yaml(response)
            all_fixes.extend(result.get("fixes", []))
        
        return {"fixes": all_fixes}
    
    def post(self, shared, prep_res, exec_res):
        shared["fixes"] = exec_res["fixes"]
        print(f"💡 LLM proposed {len(exec_res['fixes'])} fixes")
        return "default"


class ApplyFixesNode(Node):
    """Apply LLM-proposed fixes to create cleaned DataFrame"""
    
    def prep(self, shared):
        df = shared["df_original"].copy()
        fixes = shared["fixes"]
        return df, fixes
    
    def exec(self, prep_res):
        df, fixes = prep_res
        
        applied_count = 0
        for fix in fixes:
            row_idx = fix.get("row_idx")
            column = fix.get("column")
            proposed_value = fix.get("proposed_value")
            
            if row_idx is None or column is None:
                continue
            
            if column not in df.columns or row_idx < 0 or row_idx >= len(df):
                continue
            
            # Apply fix
            if proposed_value is None or str(proposed_value).lower() in ['null', 'none', 'nan']:
                df.loc[row_idx, column] = np.nan
            else:
                if df[column].dtype in ['int64', 'int32', 'float64', 'float32']:
                    try:
                        df.loc[row_idx, column] = float(proposed_value)
                    except:
                        df.loc[row_idx, column] = proposed_value
                else:
                    df.loc[row_idx, column] = str(proposed_value)
            
            applied_count += 1
        
        print(f"🧹 Applied {applied_count}/{len(fixes)} fixes")
        return df
    
    def post(self, shared, prep_res, exec_res):
        shared["df_cleaned"] = exec_res
        return "default"


class GenerateReportNode(Node):
    """LLM generates comprehensive health report"""
    
    def prep(self, shared):
        df_original = shared["df_original"]
        df_cleaned = shared["df_cleaned"]
        profile = shared["profile"]
        anomalies = shared["anomalies"]
        fixes = shared["fixes"]
        
        # Calculate quality scores
        original_total = df_original.shape[0] * df_original.shape[1]
        original_clean = original_total - df_original.isnull().sum().sum()
        original_quality = round((original_clean / original_total) * 100, 2)
        
        cleaned_total = df_cleaned.shape[0] * df_cleaned.shape[1]
        cleaned_clean = cleaned_total - df_cleaned.isnull().sum().sum()
        cleaned_quality = round((cleaned_clean / cleaned_total) * 100, 2)
        
        return {
            "original_quality": original_quality,
            "cleaned_quality": cleaned_quality,
            "total_rows": len(df_original),
            "total_columns": len(df_original.columns),
            "data_type": profile.get("data_type", "unknown"),
            "anomalies_count": len(anomalies),
            "fixes_count": len(fixes)
        }
    
    def exec(self, context):
        prompt = f"""Generate a data health report.

Dataset Info:
- Type: {context['data_type']}
- Rows: {context['total_rows']}
- Columns: {context['total_columns']}
- Original Quality: {context['original_quality']}%
- Issues Found: {context['anomalies_count']}
- Fixes Applied: {context['fixes_count']}
- Final Quality: {context['cleaned_quality']}%

Create a professional health report in YAML:

```yaml
dataset_info:
  total_rows: {context['total_rows']}
  total_columns: {context['total_columns']}
  data_type: "{context['data_type']}"
  original_quality_score: {context['original_quality']}
quality_assessment:
  overall_grade: <A|B|C|D|F>
  strengths:
    - <strength 1>
    - <strength 2>
  weaknesses:
    - <weakness 1>
    - <weakness 2>
issues_found:
  total_anomalies: {context['anomalies_count']}
  severity_breakdown: <describe severity distribution>
fixes_applied: {context['fixes_count']}
final_quality_score: {context['cleaned_quality']}
improvement: <calculate improvement>
summary: <2-3 sentence executive summary>
recommendations:
  - <recommendation 1>
  - <recommendation 2>
  - <recommendation 3>
```

Return ONLY valid YAML."""
        
        response = call_llm(prompt)
        report = parse_yaml(response)
        return report
    
    def post(self, shared, prep_res, exec_res):
        shared["health_report"] = exec_res
        print(f"📄 LLM generated health report")
        print(f"   Quality: {exec_res['dataset_info']['original_quality_score']}% → {exec_res['final_quality_score']}%")
        return "default"


class SaveOutputsNode(Node):
    """Save cleaned data and health report"""
    
    def prep(self, shared):
        df_cleaned = shared["df_cleaned"]
        health_report = shared["health_report"]
        output_csv = shared.get("output_csv", "data/cleaned_data.csv")
        output_excel = shared.get("output_excel", "data/cleaned_data.xlsx")
        output_report = shared.get("output_report", "data/health_report.yaml")
        
        return df_cleaned, health_report, output_csv, output_excel, output_report
    
    def exec(self, prep_res):
        df_cleaned, health_report, output_csv, output_excel, output_report = prep_res
        
        # Save CSV
        save_csv(df_cleaned, output_csv)
        
        # Save Excel
        df_cleaned.to_excel(output_excel, index=False)
        print(f"✅ Saved Excel to {output_excel}")
        
        # Save health report
        with open(output_report, 'w') as f:
            yaml.dump(health_report, f, default_flow_style=False, sort_keys=False)
        print(f"✅ Saved health report to {output_report}")
        
        return True
    
    def post(self, shared, prep_res, exec_res):
        print("\n🎉 Data cleaning complete!")
        return "default"

