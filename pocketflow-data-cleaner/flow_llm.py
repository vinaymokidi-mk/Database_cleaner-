"""
LLM-Powered Flow orchestration for intelligent data cleaning
"""
from pocketflow import Flow
from nodes_llm import (
    LoadDataNode,
    ProfileDataNode,
    DetectAnomaliesBatchNode,
    ProposeFixesNode,
    ApplyFixesNode,
    GenerateReportNode,
    SaveOutputsNode
)


def create_llm_cleaning_flow():
    """
    Create LLM-powered data cleaning flow.
    Uses AI for intelligent analysis and decision-making.
    
    Returns:
        Flow: The configured LLM-powered cleaning flow
    """
    # Instantiate all LLM-powered nodes
    load_node = LoadDataNode()
    profile_node = ProfileDataNode(max_retries=3, wait=10)
    detect_node = DetectAnomaliesBatchNode(max_retries=3, wait=10)
    propose_node = ProposeFixesNode(max_retries=3, wait=10)
    apply_node = ApplyFixesNode()
    report_node = GenerateReportNode(max_retries=3, wait=10)
    save_node = SaveOutputsNode()
    
    # Wire them in sequence
    load_node >> profile_node >> detect_node >> propose_node >> apply_node >> report_node >> save_node
    
    # Create and return flow
    return Flow(start=load_node)


if __name__ == "__main__":
    flow = create_llm_cleaning_flow()
    print("✅ LLM-powered data cleaning flow created")
    print("\nFlow sequence:")
    print("  1. LoadDataNode - Load CSV/Excel")
    print("  2. ProfileDataNode - LLM analyzes data structure")
    print("  3. DetectAnomaliesBatchNode - LLM detects issues")
    print("  4. ProposeFixesNode - LLM proposes fixes")
    print("  5. ApplyFixesNode - Apply fixes")
    print("  6. GenerateReportNode - LLM generates report")
    print("  7. SaveOutputsNode - Save outputs")



