from .media_handler import media_handler

def setup_handlers(app):
    app.add_handler(media_handler)
