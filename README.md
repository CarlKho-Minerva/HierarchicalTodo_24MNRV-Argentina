# Medieval Todo List Application

A hierarchical todo list application with an immersive medieval theme that allows users to manage quests (todos) with up to 3 levels of nested sub-quests.

## Demo Video
<div>
    <a href="https://www.loom.com/share/da2a485c02b14377ae5e01d53ba56695">
      <p>Medieval Task List App Demo 🏰 - Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/da2a485c02b14377ae5e01d53ba56695">
      <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/da2a485c02b14377ae5e01d53ba56695-da8fa7d1abdd6bbb-full-play.gif">
    </a>
  </div>

## Features

- 🏰 Medieval-themed UI with smooth animations and visual effects
- 👤 User authentication system
- 📜 Multiple todo lists (quest journals)
- ⚔️ Hierarchical tasks up to 3 levels deep
- 🔄 AJAX-powered interactions for smooth UX
- 📱 Responsive design with elegant scrolling behavior

## Project Structure
The project uses Flask for the backend, SQLAlchemy for the database, and vanilla JavaScript with AJAX for frontend interactions. The medieval theme is implemented through CSS variables, gradients, and animations.
```
medieval-todos/
├── app/
│   ├── models/
│   │   ├── todo.py         # TodoList and TodoItem models
│   │   └── user.py         # User authentication model
│   ├── routes/
│   │   ├── auth.py         # Authentication routes
│   │   └── todos.py        # Todo management routes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Medieval-themed styling
│   │   └── js/
│   │       └── main.js     # AJAX handlers and UI interactions
│   └── templates/
│       ├── _list_card.html # List component template
│       ├── _macros.html    # Reusable template components
│       └── todos.html      # Main todo interface
└── tests/
    ├── test_auth.py        # Authentication tests
    └── test_todos.py       # Todo functionality tests
```

## Key Components

### Frontend

`(app/static/js/main.js)`

- Smooth scroll position management with
storeScrollPosition() / restoreScrollPosition()

- AJAX form submissions via handleAjaxSubmission()

- Dynamic list updates using updateListItems() and updateListsContainer()

### Styling

(`app/static/css/style.css`)

- Medieval color scheme with variables
- Smooth animations and transitions
- Hierarchical indentation for nested items
- Responsive layout with mobile support

### Backend Models

`(app/models/todo.py)`

- TodoList for managing collections of items
- TodoItem with self-referential relationship for hierarchy

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Run development server
flask run
```

## Usage

1. Register/Login to access your todo lists
2. Create new lists using the "Create New List" form
3. Add items to lists with the "Add new quest..." form
4. Create sub-items up to 3 levels deep
5. Toggle item completion with checkboxes
6. Expand/collapse sub-items using arrow buttons
7. Move items between lists using the move button

## Testing

Run the test suite:

```bash
pytest -v
```

Generate coverage report:

```bash
pytest --cov=app --cov-report=term-missing
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Made with ❤️ by Carl Kho.
