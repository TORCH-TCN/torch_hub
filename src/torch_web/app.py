from multiprocessing.dummy import freeze_support
from flask_mail import Mail
from sassutils.wsgi import SassMiddleware
from torch_web import create_app

app = create_app()
mail = Mail(app)


if __name__ == "__main__":
    freeze_support()

    app.app_context().push()
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'torch_hub': ('static/styles', 'static/styles', '/static/styles')
    })
    socketio.run(app)
else:
    freeze_support()
    app.app_context().push()
