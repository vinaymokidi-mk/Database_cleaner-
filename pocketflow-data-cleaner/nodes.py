"""
Node definitions for data cleaning pipeline
"""
import pandas as pd
import numpy as np
import yaml
from pocketflow import Node, BatchNode
from utils import load_csv, save_csv


class LoadDataNode(Node):
    """Load CSV/Excel file into pandas DataFrame"""
    
    def prep(self, shared):
        return shared["input_file"]
    
    def exec(self, filepath):
        # Support both CSV and Excel
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
    """Analyze dataset structure using pandas (NO LLM)"""
    
    def prep(self, shared):
        return shared["df_original"]
    
    def exec(self, df):
        profile = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": {}
        }
        
        for col in df.columns:
            col_profile = {
                "dtype": str(df[col].dtype),
                "missing_count": int(df[col].isnull().sum()),
                "missing_percent": round((df[col].isnull().sum() / len(df)) * 100, 2)
            }
            
            # Numeric columns
            if df[col].dtype in ['int64', 'int32', 'float64', 'float32']:
                col_profile["type"] = "numeric"
                clean_data = df[col].dropna()
                if len(clean_data) > 0:
                    col_profile["stats"] = {
                        "mean": float(clean_data.mean()),
                        "median": float(clean_data.median()),
                        "std": float(clean_data.std()),
                        "min": float(clean_data.min()),
                        "max": float(clean_data.max())
                    }
                    # IQR outlier thresholds
                    Q1 = clean_data.quantile(0.25)
                    Q3 = clean_data.quantile(0.75)
                    IQR = Q3 - Q1
                    col_profile["outlier_threshold"] = {
                        "lower": float(Q1 - 1.5 * IQR),
                        "upper": float(Q3 + 1.5 * IQR)
                    }
            else:
                # Categorical columns
                col_profile["type"] = "categorical"
                col_profile["unique_count"] = int(df[col].nunique())
                if len(df[col].dropna()) > 0:
                    col_profile["most_common"] = str(df[col].mode()[0]) if len(df[col].mode()) > 0 else "Unknown"
                else:
                    col_profile["most_common"] = "Unknown"
            
            profile["columns"][col] = col_profile
        
        return profile
    
    def post(self, shared, prep_res, exec_res):
        shared["profile"] = exec_res
        print(f"📊 Profiled {exec_res['total_columns']} columns")
        return "default"


class DetectAnomaliesBatchNode(BatchNode):
    """Detect anomalies using rule-based logic (NO LLM)"""
    
    def prep(self, shared):
        df = shared["df_original"]
        profile = shared["profile"]
        
        items = []
        for col in df.columns:
            if col in profile["columns"]:
                items.append((col, df[col], profile["columns"][col]))
        return items
    
    def exec(self, item):
        col_name, col_data, col_profile = item
        anomalies = []
        
        # 1. Missing values
        missing_indices = col_data[col_data.isnull()].index.tolist()
        for idx in missing_indices:
            anomalies.append({
                "row_idx": int(idx),
                "issue_type": "missing",
                "current_value": None,
                "severity": "high",
                "description": f"Missing value in {col_name}"
            })
        
        # 2. Numeric outliers
        if col_profile["type"] == "numeric" and "outlier_threshold" in col_profile:
            lower = col_profile["outlier_threshold"]["lower"]
            upper = col_profile["outlier_threshold"]["upper"]
            
            outlier_mask = ((col_data < lower) | (col_data > upper)) & col_data.notna()
            outlier_indices = col_data[outlier_mask].index.tolist()
            
            for idx in outlier_indices:
                anomalies.append({
                    "row_idx": int(idx),
                    "issue_type": "outlier",
                    "current_value": float(col_data[idx]),
                    "severity": "medium",
                    "description": f"Outlier in {col_name}: {col_data[idx]}"
                })
        
        # 3. Categorical issues - ONLY detect ACTUAL data quality problems
        if col_profile["type"] == "categorical":
            for idx, val in col_data.items():
                if pd.isna(val):
                    continue  # Already handled in missing values
                
                val_str = str(val).strip()
                val_lower = val_str.lower()
                
                # Detect string "NULL", "null", "None" as missing value indicators
                if val_lower in ['null', 'none', 'n/a', 'na', 'nan', '']:
                    anomalies.append({
                        "row_idx": int(idx),
                        "issue_type": "string_null",
                        "current_value": val_str,
                        "severity": "medium",
                        "description": f"String '{val_str}' should be NULL in {col_name}"
                    })
        
        return {"anomalies": anomalies}
    
    def post(self, shared, prep_res, exec_res_list):
        all_anomalies = []
        for i, (col_name, _, _) in enumerate(prep_res):
            for anomaly in exec_res_list[i]["anomalies"]:
                anomaly["column"] = col_name
                all_anomalies.append(anomaly)
        
        shared["anomalies"] = all_anomalies
        print(f"🔍 Detected {len(all_anomalies)} anomalies")
        return "default"


class RuleBasedProposeFixesNode(Node):
    """Propose fixes using simple rules (NO LLM)"""
    
    def prep(self, shared):
        profile = shared["profile"]
        anomalies = shared["anomalies"]
        return profile, anomalies
    
    def exec(self, prep_res):
        profile, anomalies = prep_res
        fixes = []
        
        for anomaly in anomalies:
            row_idx = anomaly["row_idx"]
            column = anomaly["column"]
            issue_type = anomaly["issue_type"]
            col_profile = profile["columns"][column]
            
            fix = {
                "row_idx": row_idx,
                "column": column,
                "issue_type": issue_type,
                "current_value": anomaly["current_value"]
            }
            
            # Rule-based fix strategies
            if issue_type == "missing":
                if col_profile["type"] == "numeric":
                    if "stats" in col_profile:
                        fix["proposed_value"] = col_profile["stats"]["median"]
                        fix["strategy"] = "impute_median"
                        fix["justification"] = f"Imputed with median ({fix['proposed_value']:.2f})"
                    else:
                        fix["proposed_value"] = 0
                        fix["strategy"] = "impute_zero"
                        fix["justification"] = "No statistics available, imputed with 0"
                else:
                    if col_profile["most_common"] != "Unknown":
                        fix["proposed_value"] = col_profile["most_common"]
                        fix["strategy"] = "impute_mode"
                        fix["justification"] = f"Imputed with mode ({fix['proposed_value']})"
                    else:
                        fix["proposed_value"] = "Unknown"
                        fix["strategy"] = "impute_unknown"
                        fix["justification"] = "No mode available, kept as Unknown"
            
            elif issue_type == "outlier":
                fix["proposed_value"] = col_profile["stats"]["median"]
                fix["strategy"] = "replace_with_median"
                fix["justification"] = f"Replaced outlier with median ({fix['proposed_value']:.2f})"
            
            elif issue_type == "string_null":
                # Convert string "NULL" to actual NULL
                fix["proposed_value"] = None
                fix["strategy"] = "convert_to_null"
                fix["justification"] = f"Converted string '{anomaly['current_value']}' to NULL"
            
            else:
                # Unknown issue type - skip
                continue
            
            fixes.append(fix)
        
        return {"fixes": fixes}
    
    def post(self, shared, prep_res, exec_res):
        shared["fixes"] = exec_res["fixes"]
        print(f"💡 Proposed {len(exec_res['fixes'])} fixes")
        return "default"


class ApplyFixesNode(Node):
    """Apply proposed fixes to create cleaned DataFrame"""
    
    def prep(self, shared):
        df = shared["df_original"].copy()
        fixes = shared["fixes"]
        return df, fixes
    
    def exec(self, prep_res):
        df, fixes = prep_res
        
        applied_count = 0
        for fix in fixes:
            row_idx = fix["row_idx"]
            column = fix["column"]
            proposed_value = fix["proposed_value"]
            
            if column not in df.columns or row_idx < 0 or row_idx >= len(df):
                continue
            
            # Apply fix
            if proposed_value is None or proposed_value == "null":
                df.loc[row_idx, column] = np.nan
            else:
                if df[column].dtype in ['int64', 'int32', 'float64', 'float32']:
                    df.loc[row_idx, column] = float(proposed_value)
                else:
                    df.loc[row_idx, column] = str(proposed_value)
            
            applied_count += 1
        
        print(f"🧹 Applied {applied_count}/{len(fixes)} fixes")
        return df
    
    def post(self, shared, prep_res, exec_res):
        shared["df_cleaned"] = exec_res
        return "default"


class GenerateReportNode(Node):
    """Generate health report using templates (NO LLM)"""
    
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
            "anomalies": anomalies,
            "fixes": fixes
        }
    
    def exec(self, context):
        # Group by severity and type
        by_severity = {}
        by_type = {}
        for anomaly in context["anomalies"]:
            sev = anomaly.get("severity", "unknown")
            typ = anomaly.get("issue_type", "unknown")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_type[typ] = by_type.get(typ, 0) + 1
        
        report = {
            "dataset_info": {
                "total_rows": context["total_rows"],
                "total_columns": context["total_columns"],
                "original_quality_score": context["original_quality"]
            },
            "issues_found": {
                "total_anomalies": len(context["anomalies"]),
                "by_severity": by_severity,
                "by_type": by_type
            },
            "fixes_applied": len(context["fixes"]),
            "final_quality_score": context["cleaned_quality"],
            "summary": f"Data cleaning completed. Detected {len(context['anomalies'])} anomalies and applied {len(context['fixes'])} fixes. Quality improved from {context['original_quality']}% to {context['cleaned_quality']}%.",
            "recommendations": "Review the cleaned data and verify the applied fixes are appropriate for your use case."
        }
        
        return report
    
    def post(self, shared, prep_res, exec_res):
        shared["health_report"] = exec_res
        print(f"📄 Generated health report")
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

