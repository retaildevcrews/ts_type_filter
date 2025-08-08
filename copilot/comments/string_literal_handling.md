# TypeScript Comment Stripping - String Literal Handling

## Current Limitations

The basic regex approach in `strip_comments.py` has a significant limitation: it doesn't correctly handle string literals that contain comment-like patterns. For example:

```typescript
const message = "This /* is not */ a comment";
const url = "https://example.com"; // This comment will be incorrectly removed
const regex = /\/\*/; // This will confuse the comment stripper
```

## Approaches to Handle String Literals

### 1. Simple Regex Pre-processing (Quick Fix)
Before applying comment removal, temporarily replace string contents:

```python
def strip_comments_with_string_protection(source_text: str) -> str:
    # Step 1: Find and temporarily replace string literals
    strings = []
    placeholder_pattern = "___STRING_PLACEHOLDER_{}___"
    
    # Match double-quoted strings (with escape handling)
    def replace_string(match):
        strings.append(match.group(0))
        return placeholder_pattern.format(len(strings) - 1)
    
    # Replace string literals with placeholders
    protected_text = re.sub(r'"(?:[^"\\]|\\.)*"', replace_string, source_text)
    protected_text = re.sub(r"'(?:[^'\\]|\\.)*'", replace_string, protected_text)
    protected_text = re.sub(r'`(?:[^`\\]|\\.)*`', replace_string, protected_text)
    
    # Step 2: Remove comments from protected text
    cleaned_text = strip_typescript_comments(protected_text)
    
    # Step 3: Restore original strings
    for i, original_string in enumerate(strings):
        cleaned_text = cleaned_text.replace(placeholder_pattern.format(i), original_string)
    
    return cleaned_text
```

### 2. State Machine Approach (More Robust)
Track whether we're inside a string literal while parsing:

```python
def strip_comments_state_machine(source_text: str) -> str:
    result = []
    i = 0
    in_string = False
    string_char = None
    in_block_comment = False
    
    while i < len(source_text):
        char = source_text[i]
        
        if not in_string and not in_block_comment:
            if char in ['"', "'", '`']:
                in_string = True
                string_char = char
                result.append(char)
            elif char == '/' and i + 1 < len(source_text):
                next_char = source_text[i + 1]
                if next_char == '*':
                    # Start of block comment
                    in_block_comment = True
                    i += 1  # Skip the '*'
                elif next_char == '/':
                    # Check for "// Hint: "
                    line_end = source_text.find('\n', i)
                    if line_end == -1:
                        line_end = len(source_text)
                    line_comment = source_text[i:line_end]
                    if line_comment.startswith('// Hint: '):
                        result.append(line_comment)
                    i = line_end - 1  # Will be incremented at end of loop
                else:
                    result.append(char)
            else:
                result.append(char)
        elif in_string:
            result.append(char)
            if char == string_char and (i == 0 or source_text[i-1] != '\\'):
                in_string = False
                string_char = None
        elif in_block_comment:
            if char == '*' and i + 1 < len(source_text) and source_text[i + 1] == '/':
                in_block_comment = False
                i += 1  # Skip the '/'
        
        i += 1
    
    return ''.join(result)
```

### 3. Lexer-based Approach (Most Robust)
Use a proper lexer that understands TypeScript syntax:

```python
# Using a library like pygments or esprima-python
from pygments.lexers import TypeScriptLexer
from pygments.token import Token

def strip_comments_lexer_based(source_text: str) -> str:
    lexer = TypeScriptLexer()
    tokens = list(lexer.get_tokens(source_text))
    
    result = []
    for token_type, value in tokens:
        if token_type in [Token.Comment.Single, Token.Comment.Multiline]:
            # Check if it's a "// Hint: " comment
            if token_type == Token.Comment.Single and value.startswith('// Hint: '):
                result.append(value)
            # Otherwise, skip the comment
        else:
            result.append(value)
    
    return ''.join(result)
```

## Recommendations

1. **For Quick Prototyping**: Use the basic regex approach provided in `strip_comments.py`
2. **For Better Accuracy**: Implement the string protection approach (#1)
3. **For Production Use**: Consider the state machine approach (#2) or lexer-based approach (#3)
4. **For Maximum Robustness**: Use a proper TypeScript parser like the TypeScript compiler API or a Python binding

## Trade-offs

- **Regex**: Fast, simple, but inaccurate with string literals
- **String Protection**: Moderate complexity, handles most cases
- **State Machine**: More complex, very accurate, handles edge cases
- **Lexer**: Most accurate, requires external dependencies

Choose the approach that best fits your accuracy requirements and complexity tolerance.
