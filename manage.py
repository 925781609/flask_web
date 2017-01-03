from app import create_app, db
from app.models import User, Role, Post, Permission, Follow, Comment
from flask_script import Manager, Shell
import os
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,Permission=Permission, Post=Post, Follow=Follow, Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
    """ run deployment tasks """
    from flask_migrate import upgrade
    from app.models import User, Role

    #Migrate datebase to latest version
    upgrade()

    #Create user Roles
    Role.insert_roles()

    User.add_self_follows()



print('start to run main')

if __name__ == '__main__':
    print('app.run called')
    #app.run()
    manager.run()
