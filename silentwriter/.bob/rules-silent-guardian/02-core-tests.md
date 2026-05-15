# SILENT-002 : Tests Required on Core

## Rule
Any change in `src/core/` MUST include unit tests.

## Requirements
- At least 1 new test per modified function
- Coverage ≥ 80% on modified file
- Coverage must NOT decrease

## Why This Matters
The `src/core/` directory contains fundamental business logic.
A bug here can break the entire application.

## Suggested Test Template
\`\`\`typescript
describe('{{functionName}}', () => {
  it('should {{expectedBehavior}}', () => {
    // Arrange
    // Act
    // Assert
  });
});
\`\`\`

## Block Message Template
"🧪 Missing tests in core layer.
Coverage must be ≥ 80%.
A test template has been generated below."
