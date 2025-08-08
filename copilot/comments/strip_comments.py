"""
TypeScript Comment Stripper

This module provides a function to strip comments from TypeScript source code
using regular expressions. It removes:
- Block comments (/* ... */)
- Line comments that don't begin with "// Hint: "

Note: This is a basic regex approach that doesn't handle string literals
containing comment-like patterns.
"""

import re


def strip_typescript_comments(source_text: str) -> str:
    """
    Strip comments from TypeScript source code.
    
    Removes:
    - All block comments (/* ... */)
    - Line comments that don't begin with "// Hint: "
    
    Args:
        source_text: The TypeScript source code as a string
        
    Returns:
        The source code with comments stripped
        
    Note:
        This function uses a basic regex approach that doesn't correctly
        handle string literals containing "//", "/*", and "*/".
    """
    # First, remove block comments (/* ... */)
    # This handles both single-line and multi-line block comments
    source_text = re.sub(r'/\*.*?\*/', '', source_text, flags=re.DOTALL)
    
    # Remove line comments that don't begin with "// Hint: "
    # This pattern matches // followed by anything that doesn't start with " Hint: "
    # We use a negative lookahead to preserve "// Hint: " comments
    source_text = re.sub(r'//(?! Hint: ).*$', '', source_text, flags=re.MULTILINE)
    
    return source_text


def strip_typescript_comments_alternative(source_text: str) -> str:
    """
    Alternative implementation that processes line by line.
    
    This approach might be clearer for understanding the logic,
    though less efficient for large files.
    """
    lines = source_text.split('\n')
    result_lines = []
    in_block_comment = False
    
    for line in lines:
        current_line = line
        
        # Handle block comments
        while True:
            if not in_block_comment:
                # Look for start of block comment
                start_pos = current_line.find('/*')
                if start_pos == -1:
                    break
                
                # Found start of block comment
                end_pos = current_line.find('*/', start_pos + 2)
                if end_pos != -1:
                    # Block comment ends on same line
                    current_line = current_line[:start_pos] + current_line[end_pos + 2:]
                else:
                    # Block comment continues to next line
                    current_line = current_line[:start_pos]
                    in_block_comment = True
                    break
            else:
                # We're inside a block comment, look for end
                end_pos = current_line.find('*/')
                if end_pos != -1:
                    # Block comment ends on this line
                    current_line = current_line[end_pos + 2:]
                    in_block_comment = False
                else:
                    # Entire line is inside block comment
                    current_line = ''
                    break
        
        # Handle line comments (if we're not inside a block comment)
        if not in_block_comment:
            comment_pos = current_line.find('//')
            if comment_pos != -1:
                # Check if it's a "// Hint: " comment
                remaining = current_line[comment_pos:]
                if not remaining.startswith('// Hint: '):
                    # Remove the line comment
                    current_line = current_line[:comment_pos].rstrip()
        
        result_lines.append(current_line)
    
    return '\n'.join(result_lines)


# Example usage and test cases
if __name__ == "__main__":
    test_code = '''
    // This comment should be removed
    // Hint: This comment should be preserved
    function example() {
        /* This block comment should be removed */
        const x = 5; // This line comment should be removed
        const y = "// This is not a comment"; // But this comment should be removed
        /* Multi-line
           block comment
           should be removed */
        return x + y; // Hint: This should stay
    }
    '''
    
    print("Original code:")
    print(test_code)
    print("\nAfter stripping comments:")
    print(strip_typescript_comments(test_code))
    print("\nAlternative implementation:")
    print(strip_typescript_comments_alternative(test_code))
