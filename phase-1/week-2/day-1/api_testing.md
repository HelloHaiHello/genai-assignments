# User Registration API Test Cases

## Context & Business Rules
- **Endpoint**: `POST /api/v1/users/register`
- **Request Payload**: `username`, `email`, `password`, `confirm_password`
- **Success Response**: `{"message": "string", "user_id": "string"}`
- **Error Response**: `{"error_code": "string", "message": "string"}`
- **Business Rules**: 
  1. Email must be unique and in a valid format.
  2. Password requires 8+ characters, 1 uppercase letter, 1 number, and 1 special character.
  3. `password` and `confirm_password` must match exactly.

---

## Comprehensive Test Cases

| Test Case ID | Scenario | Method | Endpoint | Request Payload (JSON) | Expected Status | Expected Response (JSON) |
|---|---|---|---|---|---|---|
| TC_REG_01 | Successful registration | POST | `/api/v1/users/register` | `{"username":"johndoe", "email":"john@test.com", "password":"Secure1!", "confirm_password":"Secure1!"}` | 201 | `{"message": "Success", "user_id": "usr_123"}` |
| TC_REG_02 | Invalid email format | POST | `/api/v1/users/register` | `{"username":"johndoe", "email":"invalid-email", "password":"Secure1!", "confirm_password":"Secure1!"}` | 400 | `{"error_code": "VAL_001", "message": "Invalid email format"}` |
| TC_REG_03 | Password mismatch | POST | `/api/v1/users/register` | `{"username":"johndoe", "email":"john@test.com", "password":"Secure1!", "confirm_password":"Secure2!"}` | 400 | `{"error_code": "VAL_002", "message": "Passwords do not match"}` |
| TC_REG_04 | Weak password (missing special char) | POST | `/api/v1/users/register` | `{"username":"johndoe", "email":"john@test.com", "password":"Secure123", "confirm_password":"Secure123"}` | 400 | `{"error_code": "VAL_003", "message": "Password lacks complexity"}` |
| TC_REG_05 | Email already exists (Conflict) | POST | `/api/v1/users/register` | `{"username":"janedoe", "email":"existing@test.com", "password":"Secure1!", "confirm_password":"Secure1!"}` | 409 | `{"error_code": "BIZ_001", "message": "Email already registered"}` |
| TC_REG_06 | Security: SQL Injection in email | POST | `/api/v1/users/register` | `{"username":"hacker", "email":"admin' OR '1'='1", "password":"Secure1!", "confirm_password":"Secure1!"}` | 400 | `{"error_code": "VAL_001", "message": "Invalid email format"}` |
| TC_REG_07 | Security: Excessively long payload | POST | `/api/v1/users/register` | `{"username":"[500 chars]", "email":"[500 chars]@test.com", "password":"[500 chars]", "confirm_password":"[500 chars]"}` | 422 | `{"error_code": "SEC_001", "message": "Payload too large or malformed"}` |

---

## Critical Test Cases (Postman v2.1 Format)

```json
[
  {
    "name": "TC_REG_01_Successful_Registration",
    "request": {
      "method": "POST",
      "header": [
        {
          "key": "Content-Type",
          "value": "application/json"
        }
      ],
      "body": {
        "mode": "raw",
        "raw": "{\n  \"username\": \"johndoe\",\n  \"email\": \"john@test.com\",\n  \"password\": \"Secure1!\",\n  \"confirm_password\": \"Secure1!\"\n}"
      },
      "url": {
        "raw": "{{base_url}}/api/v1/users/register",
        "host": ["{{base_url}}"],
        "path": ["api", "v1", "users", "register"]
      }
    },
    "response": []
  },
  {
    "name": "TC_REG_05_Email_Already_Exists",
    "request": {
      "method": "POST",
      "header": [
        {
          "key": "Content-Type",
          "value": "application/json"
        }
      ],
      "body": {
        "mode": "raw",
        "raw": "{\n  \"username\": \"janedoe\",\n  \"email\": \"existing@test.com\",\n  \"password\": \"Secure1!\",\n  \"confirm_password\": \"Secure1!\"\n}"
      },
      "url": {
        "raw": "{{base_url}}/api/v1/users/register",
        "host": ["{{base_url}}"],
        "path": ["api", "v1", "users", "register"]
      }
    },
    "response": []
  },
  {
    "name": "TC_REG_06_SQL_Injection_Attempt",
    "request": {
      "method": "POST",
      "header": [
        {
          "key": "Content-Type",
          "value": "application/json"
        }
      ],
      "body": {
        "mode": "raw",
        "raw": "{\n  \"username\": \"hacker\",\n  \"email\": \"admin' OR '1'='1\",\n  \"password\": \"Secure1!\",\n  \"confirm_password\": \"Secure1!\"\n}"
      },
      "url": {
        "raw": "{{base_url}}/api/v1/users/register",
        "host": ["{{base