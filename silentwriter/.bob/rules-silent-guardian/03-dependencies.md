# SILENT-003 : Allowed Dependencies Only

## Rule
Only approved libraries can be added to the project.

## Approved
gradio, next, react, prisma, fastapi, pydantic, ibm-watsonx-ai, ibm-granite

## Blocked (auto-reject)
mongoose, sequelize, typeorm, left-pad, colors

## Warned (requires justification)
moment → use date-fns instead
lodash → use native methods instead
axios → use fetch instead

## Why This Matters
Dependency standardization reduces tech debt,
security vulnerabilities, and maintenance overhead.

## Block Message Template
"📦 Unauthorized dependency detected: {{package}}.
Use {{alternative}} instead, or justify in PR comments."
