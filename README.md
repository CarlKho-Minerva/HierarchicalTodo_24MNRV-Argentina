# Medieval Todo List Application

## Description

A hierarchical todo list application with a medieval theme. Users can create multiple todo lists with nested items up to three levels deep. Each user has their own private lists and items.

## Features

- User authentication system
- Hierarchical todos (up to 3 levels deep)
- Collapsible todo items
- Task completion tracking
- Drag-and-drop task movement between lists
- Medieval-themed UI (coming soon)

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd medieval-todos
```

2. Create and activate virtual environment:

```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python3 -m venv venv
venv\Scripts\activate.bat
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python run.py
```

5. Access the application at: `http://localhost:5000`

## Project Structure

```
medieval-todos/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Route handlers
│   ├── static/          # Static files (CSS, JS)
│   ├── templates/       # HTML templates
│   └── __init__.py      # App initialization
├── tests/               # Test files
├── config.py           # Configuration files
├── requirements.txt    # Project dependencies
├── README.md          # This file
└── run.py             # Application entry point
```

## Testing

Run tests using:

```bash
python -m pytest
```

## Author

Carl Kho

## License

MIT License
