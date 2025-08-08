"""
Demonstration of placeholder pattern choices and their effects.
"""

import re


def demo_placeholder_formats():
    """Demonstrate different placeholder format approaches."""
    
    test_strings = [
        '"This is a string"',
        "'Another string'",
        '`Template literal`'
    ]
    
    print("=== ORIGINAL APPROACH (with {}) ===")
    strings = []
    placeholder_pattern = "___STRING_PLACEHOLDER_{}___"
    
    def replace_string_correct(match):
        strings.append(match.group(0))
        return placeholder_pattern.format(len(strings) - 1)
    
    test_text = 'const x = "hello"; const y = \'world\'; const z = `template`;'
    protected_text = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string_correct, test_text)
    protected_text = re.sub(r"'(?:[^'\\]|\\.)*'", replace_string_correct, protected_text)
    protected_text = re.sub(r'`(?:[^`\\]|\\.)*`', replace_string_correct, protected_text)
    
    print(f"Protected text: {protected_text}")
    print(f"Stored strings: {strings}")
    
    # Restore strings
    for i, original_string in enumerate(strings):
        protected_text = protected_text.replace(placeholder_pattern.format(i), original_string)
    print(f"Restored text: {protected_text}")
    
    print("\n=== WHAT HAPPENS WITHOUT {} ===")
    try:
        bad_pattern = "___STRING_PLACEHOLDER___"
        result = bad_pattern.format(0)  # This will fail!
    except Exception as e:
        print(f"Error: {e}")
        print("Without {}, .format() has no placeholder to substitute!")
    
    print("\n=== ALTERNATIVE: F-STRING APPROACH ===")
    strings2 = []
    def replace_string_fstring(match):
        strings2.append(match.group(0))
        index = len(strings2) - 1
        return f"___STRING_PLACEHOLDER_{index}___"
    
    test_text2 = 'const x = "hello"; const y = \'world\';'
    protected_text2 = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string_fstring, test_text2)
    protected_text2 = re.sub(r"'(?:[^'\\]|\\.)*'", replace_string_fstring, protected_text2)
    
    print(f"F-string approach: {protected_text2}")
    print(f"Stored strings: {strings2}")


def demo_collision_scenarios():
    """Show potential collision scenarios and how to avoid them."""
    print("\n=== COLLISION SCENARIOS ===")
    
    # Scenario 1: Malicious/coincidental collision
    malicious_code = '''
    const hack = "___STRING_PLACEHOLDER_0___";
    const real_string = "This should be protected";
    '''
    
    print("Problematic code with collision:")
    print(malicious_code)
    
    # This would cause issues with our current approach
    strings = []
    placeholder_pattern = "___STRING_PLACEHOLDER_{}___"
    
    def replace_string(match):
        strings.append(match.group(0))
        return placeholder_pattern.format(len(strings) - 1)
    
    protected = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string, malicious_code)
    print(f"Protected (problematic): {protected}")
    print(f"Stored strings: {strings}")
    
    # When restoring, it would restore the wrong string!
    for i, original_string in enumerate(strings):
        protected = protected.replace(placeholder_pattern.format(i), original_string)
    print(f"Restored (WRONG!): {protected}")
    
    print("\n=== SAFER APPROACH: UUID-BASED ===")
    import uuid
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4()).replace('-', '')
    safer_pattern = f"___STR_{session_id}_{{}}_STR___"
    
    print(f"Safer pattern: {safer_pattern}")
    print(f"Example: {safer_pattern.format(0)}")
    print("This is virtually impossible to collide with real code!")


if __name__ == "__main__":
    demo_placeholder_formats()
    demo_collision_scenarios()
