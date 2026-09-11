# Grocy Assistant

Grocy Assistant is a self-hosted conversational assistant for [Grocy](https://grocy.info/).

It provides a simple web-based chat interface that allows users to interact with their Grocy inventory using natural language and simple commands.

The current implementation runs as a Python/Flask application in Docker and communicates with a Grocy server through the Grocy REST API.

The project is designed to eventually support both:

* **Web:** the current Flask-based Grocy Assistant
* **Android:** a native Android application with its own assistant logic

The existing web application will remain available as a supported version even after the Android application becomes standalone.

---

## Features

The current web application provides:

* Conversational interaction with Grocy
* Product stock queries
* Product-group stock queries
* Low-stock queries
* Shopping-list management
* Adding stock
* Removing stock
* Product and product-group lookups
* Location-aware inventory information
* Unit-aware inventory operations
* Natural-language queries
* Conversational context
* ntfy integration for notifications
* Docker-based deployment
* Tailscale-friendly self-hosted deployment

The assistant is designed to make common Grocy operations easier without requiring the user to navigate through the Grocy web interface for every operation.

---

## Example Commands

The assistant supports both direct commands and conversational queries.

### Inventory

```text
stock
```

Shows current inventory.

```text
stock tomato
```

Shows the stock for Tomato.

```text
stock vegetables
```

Shows products belonging to the Vegetables group.

```text
stock rice
```

Shows products matching the Rice-related query.

### Low Stock

```text
low stock
```

or conversationally:

```text
What's running low?
```

The assistant identifies products that require attention based on Grocy's stock information and configured minimum-stock values.

### Shopping List

```text
shopping list
```

Displays the current Grocy shopping list.

Products can also be added or removed from the shopping list through the assistant.

### Adding Stock

Example:

```text
+ tomato 1 kg
```

### Removing Stock

Example:

```text
- tomato 0.5 kg
```

The assistant parses the product, quantity, and unit and performs the corresponding Grocy stock operation.

### Help

```text
help
```

Displays the currently supported commands and usage examples.

---

# Architecture

The current application follows a layered architecture.

```text
                    ┌─────────────────────┐
                    │      Web Browser     │
                    │      Chat UI         │
                    └──────────┬──────────┘
                               │
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │       Flask         │
                    │       app.py        │
                    │                     │
                    │     /api/chat       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Assistant Engine   │
                    │                     │
                    │ conversation.py     │
                    │ engine.py           │
                    │ parser.py           │
                    │ queries.py          │
                    │ inventory.py        │
                    │ masterdata.py       │
                    │ responses.py        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Grocy Modules    │
                    │                     │
                    │ api.py              │
                    │ products.py         │
                    │ groups.py           │
                    │ locations.py        │
                    │ units.py            │
                    │ stock.py            │
                    │ shopping.py         │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │        Grocy        │
                    └─────────────────────┘


                    ┌─────────────────────┐
                    │   Notifications     │
                    │       ntfy.py       │
                    └──────────┬──────────┘
                               │
                               ▼
                              ntfy
```

The application separates conversational processing from Grocy API operations.

This makes the assistant easier to maintain and provides a foundation for eventually implementing the same assistant functionality in another client, such as the planned Android application.

---

# Project Structure

The current web application has the following structure:

```text
.
│   .dockerignore
│   .env
│   .env.example
│   .gitignore
│   app.py
│   docker-compose.yaml
│   Dockerfile
│   requirements.txt
│
├───assistant
│   │   conversation.py
│   │   engine.py
│   │   inventory.py
│   │   masterdata.py
│   │   parser.py
│   │   queries.py
│   │   responses.py
│   │   __init__.py
│
├───config
│   │   config.py
│
├───grocy
│   │   api.py
│   │   groups.py
│   │   locations.py
│   │   products.py
│   │   shopping.py
│   │   stock.py
│   │   units.py
│   │   __init__.py
│
├───notifications
│   │   ntfy.py
│   │   __init__.py
│
└───templates
        index.html
```

---

# Application Entry Point

## `app.py`

`app.py` is the main Flask application.

It is responsible for:

* Starting the Flask web server
* Serving the web interface
* Handling `/api/chat`
* Receiving user messages
* Passing messages to the assistant engine
* Returning assistant responses to the browser

The previous application entry point was renamed to `app.py` to provide a clearer and more conventional Flask application structure.

---

# Assistant Layer

The `assistant/` directory contains the conversational logic.

## `assistant/engine.py`

The assistant engine is the central processing layer.

It coordinates:

```text
User message
     ↓
Conversation processing
     ↓
Intent/query parsing
     ↓
Assistant operation
     ↓
Grocy interaction
     ↓
Response generation
```

The engine determines what operation the user is requesting and calls the appropriate assistant and Grocy modules.

---

## `assistant/conversation.py`

Handles conversational behavior and context.

This module provides the foundation for moving beyond rigid command-based interaction toward a more natural conversational assistant.

For example, the assistant can distinguish between direct commands and conversational requests such as:

```text
What's running low?
```

rather than requiring the user to know an exact command.

---

## `assistant/parser.py`

Responsible for interpreting user input.

The parser identifies information such as:

* Requested operation
* Product name
* Product group
* Quantity
* Unit
* Shopping-list operation
* Inventory operation

Examples:

```text
+ tomato 1 kg
```

can be interpreted as:

```text
operation = add stock
product = tomato
amount = 1
unit = kg
```

---

## `assistant/queries.py`

Handles query-oriented assistant operations.

Examples include:

* Stock queries
* Product queries
* Group queries
* Low-stock queries
* Shopping-list queries

---

## `assistant/inventory.py`

Handles inventory-related assistant operations.

Examples include:

```text
+ tomato 1 kg
```

and:

```text
- tomato 0.5 kg
```

The module translates the assistant's interpreted request into the appropriate Grocy inventory operation.

---

## `assistant/masterdata.py`

Handles assistant operations involving Grocy master data.

This includes information such as:

* Products
* Product groups
* Locations
* Units

Keeping master-data functionality separate from inventory operations helps prevent the assistant logic from becoming tightly coupled to individual Grocy API endpoints.

---

## `assistant/responses.py`

Responsible for generating user-facing responses.

Keeping response formatting separate from the underlying Grocy operations makes it easier to improve the conversational experience without changing the Grocy API implementation.

---

# Grocy Integration

The `grocy/` directory contains the Grocy-specific integration layer.

The assistant does not need to know the details of every Grocy API endpoint.

Instead, the assistant calls functions in these modules, and the Grocy layer handles communication with the Grocy REST API.

---

## `grocy/api.py`

Provides the base Grocy API communication layer.

This module is responsible for tasks such as:

* Building API requests
* Authentication
* HTTP communication
* Processing Grocy API responses
* Handling API errors

Other Grocy modules use this layer instead of implementing their own HTTP communication.

---

## `grocy/products.py`

Handles Grocy product operations.

Examples include:

* Finding products
* Looking up product information
* Resolving product names
* Retrieving product-related data

Product name resolution is particularly important for conversational input because users may provide partial or natural-language product names.

---

## `grocy/groups.py`

Handles Grocy product groups.

For example:

```text
stock vegetables
```

can be resolved through the product-group layer.

---

## `grocy/locations.py`

Handles Grocy storage locations.

Examples may include:

* Fridge
* Shelf
* Frozen
* Bath

The location layer allows the assistant to work with Grocy's location data rather than hard-coding locations into the conversational logic.

---

## `grocy/units.py`

Handles Grocy quantity units.

Examples include:

```text
kg
gram
Pack
Piece
```

The unit layer is important when interpreting commands such as:

```text
+ tomato 1 kg
```

or:

```text
- tomato 500 gram
```

---

## `grocy/stock.py`

Handles inventory operations.

This includes operations such as:

* Reading stock
* Adding stock
* Removing stock
* Checking stock information
* Working with product quantities

---

## `grocy/shopping.py`

Handles Grocy shopping-list operations.

Examples include:

* Reading the shopping list
* Adding items
* Removing items
* Formatting shopping-list results

The assistant uses this layer instead of directly manipulating shopping-list API requests.

---

# Notifications

## `notifications/ntfy.py`

The `notifications` package provides ntfy integration.

The current implementation uses ntfy for notification-related functionality rather than requiring services such as WhatsApp or Telegram.

The ntfy server can be self-hosted and accessed through the user's own infrastructure.

Example architecture:

```text
Grocy Assistant
       │
       ▼
   ntfy.py
       │
       ▼
      ntfy
       │
       ▼
 User notification
```

The notification system is intentionally separated from the assistant and Grocy modules.

This allows notification functionality to evolve independently from conversational processing.

---

# Configuration

Configuration is handled through environment variables.

The repository contains:

```text
.env
.env.example
```

The `.env.example` file should contain placeholder values suitable for publishing in an open-source repository.

The actual `.env` file should **never be committed to Git**.

Example configuration:

```env
GROCY_URL=https://grocy.example.com
GROCY_API_KEY=your_grocy_api_key

NTFY_URL=https://ntfy.example.com
NTFY_TOPIC=your_topic
```

The exact environment variables used by the application should always be kept synchronized between:

```text
config/config.py
```

and:

```text
.env.example
```

---

# Security

Grocy Assistant is designed for self-hosting.

Because it communicates with Grocy using an API key, the API key must be protected.

## Never commit secrets

Do not commit:

```text
.env
```

or any file containing:

* Grocy API keys
* ntfy authentication credentials
* passwords
* access tokens
* private keys
* server credentials

The repository should contain only safe example values.

For example:

```env
GROCY_API_KEY=replace_with_your_key
```

not an actual API key.

---

# Docker Deployment

The application is designed to run as a Docker container.

The repository contains:

```text
Dockerfile
docker-compose.yaml
.dockerignore
requirements.txt
```

## Dockerfile

The Dockerfile defines the application image.

A typical build flow is:

```text
Dockerfile
     ↓
Python application image
     ↓
Grocy Assistant container
```

---

## Docker Compose

The Docker Compose configuration defines the application container and its runtime configuration.

Typical deployment:

```bash
docker compose up -d
```

Check the container:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop the application:

```bash
docker compose down
```

Rebuild after code changes:

```bash
docker compose up -d --build
```

---

# Requirements

Python dependencies are defined in:

```text
requirements.txt
```

The application is designed to run inside Docker, so installing Python dependencies directly on the host is generally not required for normal deployment.

For local development, a Python virtual environment can be used if desired.

---

# Web Interface

The web interface is located at:

```text
templates/index.html
```

The current interface provides a mobile-friendly chat experience.

The interface communicates with the Flask backend through:

```text
POST /api/chat
```

The web UI is intentionally lightweight.

The conversational logic remains on the server instead of being embedded in the browser.

---

# API

## `POST /api/chat`

The primary application API is:

```text
POST /api/chat
```

Example request:

```json
{
  "message": "What's running low?"
}
```

The server processes the message through the assistant engine and returns a response.

Example response structure:

```json
{
  "response": "..."
}
```

The exact response content depends on the requested operation and the current Grocy data.

---

# Request Flow

A typical request follows this path:

```text
Browser
  │
  │ POST /api/chat
  ▼
app.py
  │
  ▼
assistant.engine
  │
  ├── conversation.py
  ├── parser.py
  ├── queries.py
  ├── inventory.py
  ├── masterdata.py
  └── responses.py
  │
  ▼
grocy/
  │
  ├── api.py
  ├── products.py
  ├── groups.py
  ├── locations.py
  ├── units.py
  ├── stock.py
  └── shopping.py
  │
  ▼
Grocy REST API
  │
  ▼
Grocy
```

For notification-related operations:

```text
Assistant
   │
   ▼
notifications/ntfy.py
   │
   ▼
ntfy
```

---

# Development

The project is developed incrementally.

The recommended workflow is:

```text
Modify code
    ↓
Run tests
    ↓
Test assistant behavior
    ↓
Build Docker image
    ↓
Deploy
    ↓
Test through web interface
```

During development, assistant functionality should be tested without unnecessarily changing the user's real Grocy inventory.

For inventory-related tests, a useful pattern is:

```text
Add quantity
    ↓
Verify result
    ↓
Remove the exact same quantity
    ↓
Verify original state
```

For example:

```text
+ tomato 1 kg
```

followed by:

```text
- tomato 1 kg
```

This keeps test operations from permanently modifying inventory.

The same principle should be used when testing shopping-list operations:

```text
Add item
    ↓
Verify
    ↓
Remove the same item/quantity
    ↓
Verify original state
```

---

# Testing Philosophy

Grocy Assistant has several layers that can be tested independently.

### Parser

Test whether natural-language input is interpreted correctly.

### Queries

Test whether the correct query operation is selected.

### Engine

Test whether the assistant correctly coordinates parsing, Grocy operations, and responses.

### Grocy modules

Test product, group, location, unit, stock, and shopping-list operations against the Grocy API.

### Web API

Test:

```text
POST /api/chat
```

and verify the returned JSON.

### End-to-end

Finally, test through the actual web interface.

This layered approach makes it easier to identify whether a problem is caused by:

```text
UI
 ↓
Flask API
 ↓
Assistant
 ↓
Grocy integration
 ↓
Grocy
```

---

# Self-Hosting

Grocy Assistant is intended for personal/self-hosted environments.

A typical self-hosted setup can look like:

```text
                    Home Server
                         │
             ┌───────────┴───────────┐
             │                       │
          Grocy                Grocy Assistant
             │                       │
             └───────────┬───────────┘
                         │
                       ntfy
```

A reverse proxy or private network solution can then be used to expose the services securely.

For private deployments, technologies such as Tailscale can be used to provide access without exposing the application directly to the public Internet.

The project itself does not require Tailscale and can be deployed using other networking approaches.

---

# Open Source

Grocy Assistant is intended to be an open-source project.

When publishing the repository, make sure that the following are excluded:

```text
.env
```

along with any:

* API keys
* passwords
* tokens
* private certificates
* personal configuration
* server-specific secrets

The `.env.example` file should provide a safe starting point for new installations.

---

# Current Architecture

The current implementation is intentionally divided into three major areas:

```text
assistant/
    Conversational logic

grocy/
    Grocy API integration

notifications/
    Notification integrations
```

This separation is important for the future development of the project.

The assistant layer should remain as independent as possible from the Flask web application.

That allows the underlying assistant functionality to eventually be reused by other clients.

---

# Android Application Roadmap

A native Android application is planned as the next major stage of the project.

The Android application is **not currently part of this web application tree**.

The current development strategy is to keep the web application working while gradually rebuilding the assistant functionality for Android.

The long-term architecture is planned as:

```text
                    ┌──────────────────────┐
                    │   Grocy Assistant    │
                    │      Core Logic      │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │   Web Client    │        │ Android Client  │
        │                 │        │                 │
        │ Flask + HTML    │        │ Native Kotlin   │
        └────────┬────────┘        └────────┬────────┘
                 │                          │
                 ▼                          ▼
              Grocy                      Grocy
```

The final Android application is intended to become a **fully functional native Grocy Assistant**, rather than simply being a frontend for the existing Python server.

This means that the Android application will eventually contain its own implementation of the assistant functionality currently provided by the Python application.

---

# Python-to-Android Migration

The existing Python implementation serves as the reference implementation for the Android version.

The goal is not to mechanically translate every Python file into Kotlin.

Instead, the functionality will be recreated in a clean Android architecture.

Conceptually:

```text
Current Python

assistant/parser.py
assistant/queries.py
assistant/inventory.py
assistant/masterdata.py
assistant/responses.py
assistant/engine.py

             ↓

Future Android

Kotlin assistant/domain/data layers
```

The Python web application will remain available throughout this migration.

This provides:

* A working production implementation
* A reference for expected behavior
* A fallback while Android functionality is developed
* A way to compare Python and Kotlin implementations
* Continued access to the web interface

---

# Future Android Features

Planned Android functionality includes:

* Native Grocy Assistant interface
* Conversational interaction
* Grocy connection configuration
* Grocy API integration
* Product lookup
* Product-group lookup
* Inventory queries
* Stock updates
* Shopping-list management
* Low-stock queries
* Unit handling
* Location handling
* Conversation context
* Error handling
* Connection testing
* Local application settings
* Native Android notifications where appropriate

The Android application will be developed incrementally rather than replacing the working web application immediately.

---

# Design Goals

The project follows several design goals.

## Simple

Common Grocy operations should be possible without navigating through multiple screens.

## Conversational

Users should be able to ask for information naturally.

For example:

```text
What's running low?
```

instead of requiring knowledge of an exact API or command.

## Self-hosted

The project should work with infrastructure controlled by the user.

## Private

The assistant should not require third-party messaging services such as WhatsApp or Telegram.

## Modular

Assistant logic, Grocy integration, notifications, and UI should remain separated.

## Extensible

The architecture should allow additional clients and integrations to be added later.

---

# Roadmap

The project roadmap broadly follows these stages:

### Completed

* [x] Initial Grocy API integration
* [x] Flask web application
* [x] Web chat interface
* [x] Inventory queries
* [x] Product-group queries
* [x] Low-stock queries
* [x] Stock additions
* [x] Stock removals
* [x] Shopping-list integration
* [x] Product lookup
* [x] Group lookup
* [x] Location handling
* [x] Unit handling
* [x] Conversational query handling
* [x] ntfy integration
* [x] Docker deployment
* [x] Assistant code refactoring

### In Progress

* [ ] Improve conversational capabilities
* [ ] Expand assistant command coverage
* [ ] Improve error handling
* [ ] Expand automated testing
* [ ] Continue Android application development

### Planned

* [ ] Native Android Grocy integration
* [ ] Android-side assistant logic
* [ ] Android settings/configuration
* [ ] Native notification support
* [ ] Feature parity between web and Android
* [ ] Shared behavioral specification between clients
* [ ] Additional Grocy functionality

---

# Contributing

Contributions are welcome.

Before submitting changes:

1. Keep secrets out of the repository.
2. Keep Grocy API integration inside the `grocy/` package.
3. Keep conversational logic inside the `assistant/` package.
4. Keep notification integrations inside `notifications/`.
5. Avoid placing business logic directly inside Flask routes.
6. Add or update tests when changing assistant behavior.
7. Test inventory modifications carefully.
8. Prefer reversible tests that add and remove the same quantity.
9. Update `.env.example` when adding new configuration variables.
10. Update this README when the architecture changes significantly.

---

# License

This project is intended to be released as open-source.

The final license should be added to the repository before the first public release.

For example, the repository may eventually contain:

```text
LICENSE
README.md
```

The chosen license should reflect how the project is intended to be used, modified, and redistributed.

---

# Project Status

Grocy Assistant is an actively developed self-hosted project.

The **current stable development target is the Flask-based web chat application** documented in this README.

The native Android application is a separate development track and is intended to eventually provide a complete standalone Grocy Assistant experience while the existing web application remains supported.

```text
Current:

Browser
   ↓
Flask
   ↓
Python Assistant
   ↓
Grocy


Future:

Browser ──→ Web Assistant ──→ Grocy
                      

Android ──→ Native Assistant ──→ Grocy
```

The long-term goal is to provide the same Grocy Assistant experience across both platforms while keeping the project self-hosted, modular, private, and open source.
