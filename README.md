# Medieval Todo List Application

A hierarchical todo list application with a medieval theme, supporting nested tasks up to 3 levels deep.

## Project Structure

```txt
HierarchicalTodo_24MNRV-Argentina/
├── app/
│   ├── __init__.py           # Application factory and extensions
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── todo.py          # TodoList and TodoItem models
│   │   └── user.py          # User model
│   ├── routes/              # Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication routes
│   │   └── todos.py        # Todo management routes
│   ├── static/             # Static assets
│   │   ├── css/
│   │   └── js/
│   └── templates/          # HTML templates
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_auth.py       # Authentication tests
│   └── test_todos.py      # Todo functionality tests
├── config.py              # Configuration settings
├── conftest.py           # Pytest configuration
└── requirements.txt      # Project dependencies
```

## Key Features

- User authentication (register/login)
- Hierarchical todo lists with up to 3 levels of nesting
- AJAX-powered interactions for smooth user experience
- Medieval-themed UI

## Testing

### Test Location

- Main test files are in the `tests/` directory:
  - `test_auth.py`: Tests for user registration and authentication
  - `test_todos.py`: Tests for todo list and item management

### Running Tests

1. Install test dependencies:

```bash
pip install pytest pytest-flask
```

2. Run the test suite:

```bash
pytest
```

### Test Coverage

The test suite covers:

- User registration and authentication
- Todo list creation and management
- Todo item creation and hierarchy
- Item completion and expansion states
- List and item deletion

## Core Functionality Locations

1. __Database Models__ (`app/models/`):
   - `user.py`: User authentication and management
   - `todo.py`: Todo list and item implementation with hierarchy

2. __Routes__ (`app/routes/`):
   - `auth.py`: Authentication endpoints
   - `todos.py`: Todo management endpoints

3. __Templates__ (`app/templates/`):
   - `base.html`: Base template with navigation
   - `login.html` & `register.html`: Authentication forms
   - `todos.html`: Main todo management interface

4. __Static Files__ (`app/static/`):
   - JavaScript for AJAX interactions
   - CSS for medieval-themed styling

## Running the Application

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Initialize the database:

```bash
flask db upgrade
```

3. Run the development server:

```bash
flask run
```

## Configuration

- Development configuration: `config.py`
- Test configuration: `config.TestConfig` in `config.py`

## Continuous Integration

- GitHub Actions workflow in `.github/workflows/test.yml`
- Automatically runs tests on push and pull requests

## Design Decisions

1. __Hierarchical Structure__:
   - Implemented using self-referential relationship in TodoItem model
   - Maximum nesting depth of 3 levels for clarity

2. __AJAX Interactions__:
   - Used for smooth updates without page reloads
   - Fallback to standard form submissions when JavaScript is disabled

3. __Medieval Theme__:
   - Consistent styling across all pages
   - Themed terminology (e.g., "quests" instead of "todos")
