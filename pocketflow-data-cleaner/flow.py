"""
Flow orchestration for data cleaning pipeline
"""
from pocketflow import Flow
from nodes import (
    LoadDataNode,
    ProfileDataNode,
    DetectAnomaliesBatchNode,
    RuleBasedProposeFixesNode,
    ApplyFixesNode,
    GenerateReportNode,
    SaveOutputsNode
)


def create_local_cleaning_flow():
    """
    Create data cleaning flow that works WITHOUT API calls.
    Uses rule-based logic for all operations.
    
    Returns:
        Flow: The configured data cleaning flow
    """
    # Instantiate all nodes (NO LLM, NO API calls)
    load_node = LoadDataNode()
    profile_node = ProfileDataNode()
    detect_node = DetectAnomaliesBatchNode()
    propose_node = RuleBasedProposeFixesNode()
    apply_node = ApplyFixesNode()
    report_node = GenerateReportNode()
    save_node = SaveOutputsNode()
    
    # Wire nodes in sequence
    load_node >> profile_node
    profile_node >> detect_node
    detect_node >> propose_node
    propose_node >> apply_node
    apply_node >> report_node
    report_node >> save_node
    
    # Create flow
    flow = Flow(start=load_node)
    
    return flow


if __name__ == "__main__":
    flow = create_local_cleaning_flow()
    print("✅ Local data cleaning flow created (no API calls)")
    print("\nFlow sequence:")
    print("  1. LoadDataNode - Load CSV/Excel")
    print("  2. ProfileDataNode - Analyze with pandas")
    print("  3. DetectAnomaliesBatchNode - Rule-based detection")
    print("  4. RuleBasedProposeFixesNode - Simple fix strategies")
    print("  5. ApplyFixesNode - Apply transformations")
    print("  6. GenerateReportNode - Template-based report")
    print("  7. SaveOutputsNode - Save CSV/Excel + report")

