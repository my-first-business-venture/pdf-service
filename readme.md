# PDF-Service

## Description

The PDF-Service is the backend for the Chatbot-UI. Follow the steps below to use the application.

## Requirements

1. Built with Python 3.10.11 and React 19.1.0

## Backend Service

### Setup

1. Create a virtual environment

`python -m venv venv`

2. Activate the virtual environment

`./venv/Scripts/activate`

3. Install dependencies

`pip install -r .\requirements.txt`

### Initiating Service

`uvicorn main_service:app --reload`

### Local testing

1. Use postman:

Post method => `http://127.0.0.1:8000/chat`

Payload => 
`{`
`  "message": "What is the main topic of the document?",`
`  "conversation_id": "test-session-001"`
`}`

Use the attached postman collection.

[View PDFReader.postman_collection](./documentation/PDFReader.postman_collection.json)

## Frontend

### Setup

1. Install dependencies

`npm install`

### Initiating Service

`npm run dev`

### Local testing

`http://localhost:5173/`