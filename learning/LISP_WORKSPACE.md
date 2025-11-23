# Lisp Workspace Implementation

This document describes the implementation of Lisp workspaces using JSCL (JavaScript Common Lisp) alongside the existing Python workspace functionality.

## Overview

The learning application now supports both **Python** and **Common Lisp** workspaces, allowing users to work with either language depending on the library they're studying:

- **PAIP Chapter 1 (Introduction to Lisp)**: Uses Lisp workspace
- **Traveling Salesperson Problem**: Uses Python workspace

## Implementation Details

### 1. JSCL Integration

We use [JSCL](https://github.com/jscl-project/jscl) (version 0.9.0) for running Common Lisp in the browser:
- Loaded via CDN: `https://cdn.jsdelivr.net/npm/jscl@0.9.0/jscl.js`
- Compiles Common Lisp to JavaScript and executes it directly in the browser
- No backend required - runs entirely client-side

### 2. New Components

#### LispScratchpad.tsx
A new component parallel to `PythonScratchpad.tsx` that provides:
- Common Lisp code editor with syntax highlighting
- Execute button (Ctrl+Enter shortcut)
- Output/error display
- Reset functionality
- Purple-themed UI to distinguish from Python (green)

Key features:
```typescript
- Loads JSCL from window.jscl
- Uses jscl.evaluateString() to execute code
- Displays results or errors
- Matches PythonScratchpad API for consistency
```

### 3. Modified Components

#### layout.tsx
Added JSCL script loading alongside Pyodide:
```html
<script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jscl@0.9.0/jscl.js"></script>
```

#### SocraticDialogue.tsx
Enhanced to support both workspace types:
- Added `workspaceType` prop ('python' | 'lisp')
- Added `sourceFile` prop for library-specific source material
- Changed tab from "Python" to dynamic "Workspace" (shows Python or Lisp icon)
- Conditionally renders `LispScratchpad` or `PythonScratchpad`
- Updates code block language in messages (```python vs ```lisp)

#### page.tsx
Updated Library type to include:
```typescript
type Library = {
  // ... existing fields
  workspaceType?: 'python' | 'lisp';
  sourceFile?: string;
}
```

### 4. Configuration Changes

#### public/data/libraries.json
Added workspace configuration for each library:

```json
{
  "id": "paip-ch1",
  "workspaceType": "lisp",
  "sourceFile": "data/paip-ch1/text.md"
}

{
  "id": "pytudes-tsp",
  "workspaceType": "python",
  "sourceFile": "data/pytudes/tsp.md"
}
```

### 5. Type Definitions

#### types/browser-globals.d.ts
New type definitions for browser globals:
```typescript
interface Window {
  loadPyodide: (config?: { indexURL: string }) => Promise<unknown>;
  jscl?: {
    evaluateString: (code: string) => unknown;
  };
}
```

### 6. Data Files

Copied PAIP Chapter 1 text to public directory:
- `learning/public/data/paip-ch1/text.md` (67KB)

## Usage

### For Library Maintainers

To add a new library with Lisp support:

1. Add library entry to `public/data/libraries.json`:
```json
{
  "id": "your-library-id",
  "workspaceType": "lisp",
  "sourceFile": "data/your-library/source.md",
  // ... other required fields
}
```

2. Place source material in `public/data/your-library/`

### For Users

When learning with a Lisp library:
1. The workspace tab shows "🎨 Lisp" instead of "🐍 Python"
2. Write Common Lisp code in the workspace
3. Click "Run" or press Ctrl+Enter to execute
4. View results in the output panel below

Example Lisp code:
```lisp
;;; Basic arithmetic
(+ 2 2)

;;; Function definition
(defun double (x) (* x 2))
(double 21)

;;; List operations
(list 1 2 3)
```

## Design Decisions

1. **JSCL over WECL**: JSCL is more mature with better browser support and npm package availability
2. **Parallel Implementation**: Created separate component rather than modifying PythonScratchpad for clarity
3. **Color Coding**: Purple theme for Lisp to distinguish from Python's green theme
4. **Minimal Changes**: Only modified necessary components to maintain backward compatibility

## Testing

Due to environment limitations, manual testing should verify:

1. **Python Workspace** (TSP library):
   - Still loads correctly
   - Can execute Python code
   - Pyodide loads without issues

2. **Lisp Workspace** (PAIP library):
   - JSCL loads from CDN
   - Can execute Common Lisp code
   - Error handling works
   - Results display correctly

3. **Source Viewer**:
   - Python library shows pytudes/tsp.md
   - Lisp library shows paip-ch1/text.md

## Troubleshooting

### JSCL not loading
- Check browser console for CDN errors
- Verify network access to cdn.jsdelivr.net
- Check that jscl.js loaded successfully

### Type errors
- Ensure types/browser-globals.d.ts is included in tsconfig

### Workspace not appearing
- Check library configuration has correct workspaceType
- Verify conceptData.hide_editor is not set to true

## Future Enhancements

- Add more Lisp-specific features (REPL history, better error messages)
- Support for loading Lisp libraries/packages
- Syntax highlighting for Lisp code blocks
- Better output formatting for Lisp data structures
- Consider adding WECL as an alternative backend

## References

- JSCL Project: https://github.com/jscl-project/jscl
- JSCL CDN: https://www.jsdelivr.com/package/npm/jscl
- Original Issue: https://github.com/google-gemini/workshops/issues/156
