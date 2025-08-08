"""
Enhanced TypeScript Comment Stripper with String Literal Protection

This module provides an improved version of the comment stripper that
handles string literals containing comment-like patterns.
"""

import re
from typing import List, Tuple


def strip_typescript_comments_protected(source_text: str) -> str:
    """
    Strip comments from TypeScript source code with string literal protection.
    
    This version temporarily replaces string literals with placeholders
    to avoid incorrectly processing comment-like patterns within strings.
    
    Args:
        source_text: The TypeScript source code as a string
        
    Returns:
        The source code with comments stripped, preserving string literals
    """
    # Step 1: Find and temporarily replace string literals
    strings = []
    placeholder_pattern = "___STRING_PLACEHOLDER_{}___"
    
    def replace_string(match):
        strings.append(match.group(0))
        return placeholder_pattern.format(len(strings) - 1)
    
    # Replace string literals with placeholders
    # Handle double-quoted strings (with escape handling)
    protected_text = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string, source_text)
    # Handle single-quoted strings (with escape handling)
    protected_text = re.sub(r"'(?:[^'\\]|\\.)*'", replace_string, protected_text)
    # Handle template literals (with escape handling)
    protected_text = re.sub(r'`(?:[^`\\]|\\.)*`', replace_string, protected_text)
    
    # Step 2: Remove comments from protected text
    # Remove block comments
    protected_text = re.sub(r'/\*.*?\*/', '', protected_text, flags=re.DOTALL)
    
    # Remove line comments that don't begin with "// Hint: "
    protected_text = re.sub(r'//(?! Hint: ).*$', '', protected_text, flags=re.MULTILINE)
    
    # Step 3: Restore original strings
    for i, original_string in enumerate(strings):
        protected_text = protected_text.replace(placeholder_pattern.format(i), original_string)
    
    return protected_text


def strip_typescript_comments_preserve_hint_blocks(source_text: str) -> str:
    """
    Strip comments from TypeScript source code with string literal protection,
    preserving both line and block comments that start with "Hint: ".
    
    This version preserves:
    - Line comments starting with "// Hint: "
    - Block comments starting with "/* Hint: "
    
    Args:
        source_text: The TypeScript source code as a string
        
    Returns:
        The source code with comments stripped, preserving string literals
        and hint comments (both line and block)
    """
    # Step 1: Find and temporarily replace string literals
    strings = []
    placeholder_pattern = "___STRING_PLACEHOLDER_{}___"
    
    def replace_string(match):
        strings.append(match.group(0))
        return placeholder_pattern.format(len(strings) - 1)
    
    # Replace string literals with placeholders
    # Handle double-quoted strings (with escape handling)
    protected_text = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string, source_text)
    # Handle single-quoted strings (with escape handling)
    protected_text = re.sub(r"'(?:[^'\\]|\\.)*'", replace_string, protected_text)
    # Handle template literals (with escape handling)
    protected_text = re.sub(r'`(?:[^`\\]|\\.)*`', replace_string, protected_text)
    
    # Step 2: Remove comments from protected text, but preserve hint comments
    
    # First, find and temporarily protect hint block comments
    hint_blocks = []
    hint_block_pattern = "___HINT_BLOCK_PLACEHOLDER_{}___"
    
    def replace_hint_block(match):
        hint_blocks.append(match.group(0))
        return hint_block_pattern.format(len(hint_blocks) - 1)
    
    # Protect block comments that start with "/* Hint: "
    protected_text = re.sub(r'/\*\s*Hint:\s*.*?\*/', replace_hint_block, protected_text, flags=re.DOTALL)
    
    # Remove remaining block comments (non-hint ones)
    protected_text = re.sub(r'/\*.*?\*/', '', protected_text, flags=re.DOTALL)
    
    # Restore hint block comments
    for i, hint_block in enumerate(hint_blocks):
        protected_text = protected_text.replace(hint_block_pattern.format(i), hint_block)
    
    # Remove line comments that don't begin with "// Hint: "
    protected_text = re.sub(r'//(?! Hint: ).*$', '', protected_text, flags=re.MULTILINE)
    
    # Step 3: Restore original strings
    for i, original_string in enumerate(strings):
        protected_text = protected_text.replace(placeholder_pattern.format(i), original_string)
    
    return protected_text


def analyze_comment_patterns(source_text: str) -> dict:
    """
    Analyze the source text to identify potential issues with comment stripping.
    
    Returns a dictionary with statistics about comment-like patterns in strings.
    """
    # Find all string literals
    string_patterns = [
        r'"(?:[^"\\]|\\.)*"',  # Double-quoted strings
        r"'(?:[^'\\]|\\.)*'",  # Single-quoted strings
        r'`(?:[^`\\]|\\.)*`'   # Template literals
    ]
    
    strings_with_comment_patterns = []
    
    for pattern in string_patterns:
        for match in re.finditer(pattern, source_text):
            string_content = match.group(0)
            if '//' in string_content or '/*' in string_content or '*/' in string_content:
                strings_with_comment_patterns.append({
                    'content': string_content,
                    'start': match.start(),
                    'end': match.end()
                })
    
    # Count comment patterns
    block_comments = len(re.findall(r'/\*.*?\*/', source_text, flags=re.DOTALL))
    line_comments = len(re.findall(r'//.*$', source_text, flags=re.MULTILINE))
    hint_comments = len(re.findall(r'// Hint: .*$', source_text, flags=re.MULTILINE))
    
    return {
        'block_comments': block_comments,
        'line_comments': line_comments,
        'hint_comments': hint_comments,
        'strings_with_comment_patterns': strings_with_comment_patterns,
        'total_strings_with_issues': len(strings_with_comment_patterns)
    }


# Test the enhanced function
if __name__ == "__main__":
    test_code = '''
    // This comment should be removed
    // Hint: This line comment should be preserved
    function example() {
        /* This block comment should be removed */
        /* Hint: This block comment should be preserved */
        const x = 5; // This line comment should be removed
        const y = "This /* is not */ a comment"; // But this comment should be removed
        const url = "https://example.com"; // This comment should be removed
        const message = 'Contains // comment markers';
        const template = `Template with /* block comment markers */`;
        /* Multi-line
           block comment
           should be removed */
        /* Hint: Multi-line hint block
           should be preserved */
        return x + y; // Hint: This line hint should stay
    }
    '''
    
    print("=== ANALYSIS ===")
    analysis = analyze_comment_patterns(test_code)
    print(f"Block comments: {analysis['block_comments']}")
    print(f"Line comments: {analysis['line_comments']}")
    print(f"Hint comments: {analysis['hint_comments']}")
    print(f"Strings with comment patterns: {analysis['total_strings_with_issues']}")
    
    if analysis['strings_with_comment_patterns']:
        print("\nStrings containing comment-like patterns:")
        for string_info in analysis['strings_with_comment_patterns']:
            print(f"  {string_info['content']}")
    
    print("\n=== ORIGINAL CODE ===")
    print(test_code)
    
    print("\n=== BASIC REGEX APPROACH ===")
    from strip_comments import strip_typescript_comments
    basic_result = strip_typescript_comments(test_code)
    print(basic_result)
    
    print("\n=== PROTECTED APPROACH (Line hints only) ===")
    protected_result = strip_typescript_comments_protected(test_code)
    print(protected_result)
    
    print("\n=== PRESERVE HINT BLOCKS APPROACH (Line and block hints) ===")
    preserve_blocks_result = strip_typescript_comments_preserve_hint_blocks(test_code)
    print(preserve_blocks_result)
