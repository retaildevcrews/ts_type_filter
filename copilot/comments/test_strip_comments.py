"""
Test script for TypeScript comment stripping functions.
"""

from strip_comments import strip_typescript_comments, strip_typescript_comments_alternative
from enhanced_strip_comments import (
    strip_typescript_comments_protected, 
    strip_typescript_comments_preserve_hint_blocks,
    analyze_comment_patterns
)


def test_basic_functionality():
    """Test basic comment stripping functionality."""
    print("=" * 60)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 60)
    
    test_cases = [
        # Simple line comments
        '''
        const x = 5; // Remove this
        const y = 10; // Hint: Keep this
        ''',
        
        # Block comments
        '''
        /* Remove this block comment */
        function test() {
            /* Also remove
               this multi-line
               block comment */
            return 42;
        }
        ''',
        
        # Mixed comments
        '''
        // Remove this line comment
        /* Remove this block */ const x = 5; // Remove this too
        // Hint: But keep this one
        '''
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("Input:", repr(test_case))
        result = strip_typescript_comments(test_case)
        print("Output:", repr(result))


def test_hint_block_preservation():
    """Test the difference between preserving line hints only vs line and block hints."""
    print("=" * 60)
    print("TESTING HINT BLOCK PRESERVATION")
    print("=" * 60)
    
    test_code = '''
    // Regular line comment - should be removed
    // Hint: Line hint comment - should be preserved
    function example() {
        /* Regular block comment - should be removed */
        /* Hint: Block hint comment - should be preserved */
        const x = 5; // Another line comment - should be removed
        /* Hint: Multi-line block hint
           with multiple lines
           should be preserved */
        return x; // Hint: Another line hint - should be preserved
    }
    '''
    
    print("Original code:")
    print(test_code)
    
    print("\n--- ORIGINAL PROTECTED (line hints only) ---")
    result1 = strip_typescript_comments_protected(test_code)
    print(result1)
    
    print("\n--- NEW PRESERVE HINT BLOCKS (line and block hints) ---")
    result2 = strip_typescript_comments_preserve_hint_blocks(test_code)
    print(result2)
    
    print("\n--- COMPARISON ---")
    print(f"Results are identical: {result1 == result2}")
    if result1 != result2:
        print("Differences found - the new function preserves block hints!")


def test_string_literal_handling():
    """Test how different approaches handle string literals."""
    print("=" * 60)
    print("TESTING STRING LITERAL HANDLING")
    print("=" * 60)
    
    problematic_code = '''
    const message = "This /* is not */ a comment";
    const url = "https://example.com"; // This comment should be removed
    const regex = /\\/\\*/; // This pattern looks like a comment start
    const template = `Contains // comment markers`;
    // Hint: This should be preserved
    /* This block comment should be removed */
    '''
    
    print("Original code:")
    print(problematic_code)
    
    print("\n--- ANALYSIS ---")
    analysis = analyze_comment_patterns(problematic_code)
    for key, value in analysis.items():
        if key != 'strings_with_comment_patterns':
            print(f"{key}: {value}")
        else:
            print(f"Problematic strings: {[s['content'] for s in value]}")
    
    print("\n--- BASIC REGEX APPROACH ---")
    basic_result = strip_typescript_comments(problematic_code)
    print(basic_result)
    
    print("\n--- PROTECTED APPROACH ---")
    protected_result = strip_typescript_comments_protected(problematic_code)
    print(protected_result)
    
    print("\n--- PRESERVE HINT BLOCKS APPROACH ---")
    preserve_blocks_result = strip_typescript_comments_preserve_hint_blocks(problematic_code)
    print(preserve_blocks_result)
    
    print("\n--- ALTERNATIVE APPROACH ---")
    alternative_result = strip_typescript_comments_alternative(problematic_code)
    print(alternative_result)


def test_edge_cases():
    """Test edge cases and complex scenarios."""
    print("=" * 60)
    print("TESTING EDGE CASES")
    print("=" * 60)
    
    edge_cases = [
        # Nested quotes
        '''const nested = "He said 'Hello /* world */' to me"; // Comment''',
        
        # Escaped quotes in strings
        '''const escaped = "String with \\"quotes\\" and /* comment markers */";''',
        
        # Comments at end of file without newline
        '''const x = 5; // No newline after this comment''',
        
        # Empty comments
        '''
        //
        /**/
        // Hint: 
        ''',
        
        # Comments with special characters
        '''
        // Comment with Unicode: café 🚀
        /* Block with symbols: @#$%^&*() */
        // Hint: Special chars: <>&"'
        '''
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}:")
        print("Input:", repr(test_case))
        basic_result = strip_typescript_comments(test_case)
        protected_result = strip_typescript_comments_protected(test_case)
        preserve_blocks_result = strip_typescript_comments_preserve_hint_blocks(test_case)
        print("Basic result:", repr(basic_result))
        print("Protected result:", repr(protected_result))
        print("Preserve blocks result:", repr(preserve_blocks_result))
        print("Protected vs Preserve blocks same:", protected_result == preserve_blocks_result)


if __name__ == "__main__":
    test_basic_functionality()
    test_hint_block_preservation()
    test_string_literal_handling()
    test_edge_cases()
