"""
Parse YAML from LLM responses
"""
import yaml
import re

def parse_yaml(text: str) -> dict:
    """
    Extract and parse YAML from LLM response.
    Handles code fences and plain YAML.
    """
    # Try to extract YAML from code fences
    yaml_pattern = r'```(?:yaml)?\s*\n(.*?)\n```'
    matches = re.findall(yaml_pattern, text, re.DOTALL)
    
    if matches:
        yaml_str = matches[0]
    else:
        # No code fence, assume entire text is YAML
        yaml_str = text.strip()
    
    # Parse YAML
    try:
        result = yaml.safe_load(yaml_str)
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict, got {type(result)}")
        return result
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML: {e}\n\nText was:\n{yaml_str}")


if __name__ == "__main__":
    # Test
    test_text = """
```yaml
summary:
  - Point 1
  - Point 2
status: ok
```
    """
    result = parse_yaml(test_text)
    print(result)



