from appz import db, create_app, cli
from appz.models import User, Post, Notification, Message, Task, followers


app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post, 'Message': Message, 'Notification': Notification, 'Task': Task}

if __name__ == '__main__':
    app.run(debug=False)
