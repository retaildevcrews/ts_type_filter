# TypeScript Comment Stripper

This directory contains Python functions for stripping comments from TypeScript source code.

## Files

### `strip_comments.py`
The main module containing the basic regex-based comment stripping function:
- `strip_typescript_comments()` - Basic regex approach
- `strip_typescript_comments_alternative()` - Line-by-line processing approach

### `enhanced_strip_comments.py`
Enhanced version with string literal protection:
- `strip_typescript_comments_protected()` - Handles string literals containing comment-like patterns
- `analyze_comment_patterns()` - Analyzes source code for potential issues

### `test_strip_comments.py`
Comprehensive test suite demonstrating:
- Basic functionality
- String literal handling differences
- Edge cases and complex scenarios

### `string_literal_handling.md`
Documentation explaining:
- Current limitations of the basic approach
- Various strategies for handling string literals
- Trade-offs between different approaches

## Quick Start

```python
from strip_comments import strip_typescript_comments
from enhanced_strip_comments import strip_typescript_comments_protected

# Basic approach (fast, but may have issues with strings)
cleaned_code = strip_typescript_comments(typescript_source)

# Protected approach (safer with string literals)
cleaned_code = strip_typescript_comments_protected(typescript_source)
```

## Comment Stripping Rules

The functions remove:
1. **Block comments**: `/* ... */` (including multi-line)
2. **Line comments**: `// ...` EXCEPT those starting with `// Hint: `

### Preserved Comments
- `// Hint: This will be kept`
- `// Hint: Any text after this prefix is preserved`

### Removed Comments
- `// Regular line comments`
- `/* Block comments */`
- `/* Multi-line
     block comments */`

## Limitations

### Basic Approach (`strip_comments.py`)
- Does not handle string literals containing `//`, `/*`, or `*/`
- May incorrectly process comment-like patterns inside strings

### Protected Approach (`enhanced_strip_comments.py`)
- Handles most string literal cases correctly
- Slightly more complex and slower
- Better for production use

## Example

```typescript
// Input
const message = "This /* is not */ a comment";
const url = "https://example.com"; // This comment should be removed
// Hint: This comment will be preserved
/* This block comment will be removed */

// Basic approach output (INCORRECT)
const message = "This  a comment";
const url = "https:
// Hint: This comment will be preserved

// Protected approach output (CORRECT)
const message = "This /* is not */ a comment";
const url = "https://example.com";
// Hint: This comment will be preserved
```

## Running Tests

```bash
cd copilot/comments
python test_strip_comments.py
```

This will run comprehensive tests showing the differences between approaches and demonstrating various edge cases.
