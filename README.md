# tunain-django-backend

## Application Description

Tunain application allows users to co-write a book with an AI, generating both text and illustrations. Users provide prompts for extracts, and the AI completes paragraphs and generates illustrative images.

## Backend Overview

The backend repository provides API endpoints and manages business logic for the application. It coordinates interactions between the frontend, image worker, and text worker.

## Features

- RESTful API for user operations and content management.
- Integration with image and text generation services.
- User authentication and session management.

## Technology Stack

- Framework: Django
- Database: PostgreSQL

## Configuration

`example.env` file contains a set of environment variable values suitable for local configuration

```
cp example.env .env
```
