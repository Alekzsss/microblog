from appz import app, db
from appz.models import User, Post
from appz import cli

@app.shell_context_processor
def make_shell_context():
    return {"db": db,"User": User, "Post": Post}

if __name__ == '__main__':
    app.run(debug=False)
