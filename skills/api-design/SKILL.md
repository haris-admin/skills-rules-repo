---
name: api-design
description: >-
  Design RESTful APIs, OpenAPI/Swagger specifications, GraphQL schemas, and RPC interfaces following modern API design standards. Use when creating, refactoring, or documenting APIs.
---

# API Design & Contract Standards Skill

Guides the agent in crafting clean, intuitive, backward-compatible, and well-documented APIs.

## Workflow

1. **Step 1: Resource Modeling & Endpoints**
   - Identify core domain resources and relationships.
   - Use plural nouns for resource endpoints (`/users`, `/orders/{id}/items`).
   - Use standard HTTP methods:
     - `GET`: Retrieve resource(s) (safe & idempotent).
     - `POST`: Create a new resource (non-idempotent).
     - `PUT`: Replace an existing resource completely (idempotent).
     - `PATCH`: Partially update a resource (idempotent/non-idempotent).
     - `DELETE`: Remove a resource (idempotent).

2. **Step 2: Request & Response Schema Design**
   - Use predictable, camelCase or snake_case conventions consistently across JSON payloads.
   - Design consistent envelope structures for error responses:
     ```json
     {
       "error": {
         "code": "RESOURCE_NOT_FOUND",
         "message": "User with ID 123 does not exist",
         "details": []
       }
     }
     ```
   - Implement cursor-based or limit-offset pagination for collection responses.

3. **Step 3: Idempotency & Versioning**
   - Include `Idempotency-Key` headers for mutating financial or critical operations.
   - Use URI path versioning (`/api/v1/...`) or header-based versioning for evolving API contracts.

4. **Step 4: Contract Specification**
   - Generate or update OpenAPI 3.0+ (Swagger) specifications or GraphQL schemas.

## Reference

- [RESTful Best Practices & Status Code Guide](./references/rest-guidelines.md)
