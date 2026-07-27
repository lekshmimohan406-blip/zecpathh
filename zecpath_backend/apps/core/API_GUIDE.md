# ZecPath API Guide

## Base URL

http://127.0.0.1:8000/api/

---

## Authentication

### Login

**Method:** POST  
**URL:** `/login/`

**Request Body:**

```json
{
  "email": "mohan2003@gmail.com",
  "password": "mohan2003"
}