from flask_migrate import Migrate
from app import create_app, db
from app.models import TodoList, TodoItem, User

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'TodoList': TodoList,
        'TodoItem': TodoItem,
        'User': User
    }

if __name__ == '__main__':
    app.run()
