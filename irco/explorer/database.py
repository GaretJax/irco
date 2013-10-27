from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


_session_maker = None


def Session(*args, **kwargs):
    return _session_maker(*args, **kwargs)


def init_app(app):
    engine = create_engine(app.config['DATABASE'])
    global _session_maker
    _session_maker = scoped_session(sessionmaker(bind=engine))

    @app.teardown_request
    def shutdown_session(exc):
        if exc is None:
            _session_maker().commit()
        _session_maker.remove()
        return exc
