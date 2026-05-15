# SILENT-001 : Protect API Contracts

## Rule
Public function signatures in `src/api/` MUST NOT be changed.

## Forbidden Changes
- Changing an exported function signature
- Removing an exported function
- Changing the return type
- Removing a parameter
- Renaming an exported function

## Allowed Changes
- Adding an optional parameter
- Creating an overload
- Deprecating a function with `@deprecated` tag

## Why This Matters
These functions are called by external services.
A breaking change would cause production incidents.

## What To Do Instead
1. Create a new function (e.g., `getUserV2`)
2. Keep the old one with `@deprecated`
3. Coordinate migration with consumer teams

## Block Message Template
"🛡️ Breaking change detected in API layer.
This function is called by {{caller_count}} services.
Create a V2 endpoint instead."
