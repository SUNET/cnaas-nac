import os

from cnaas_nac.api import app


os.environ['PYTHONPATH'] = os.getcwd()


def get_app():
    return app.app

if __name__ == '__main__':
    get_app().run(debug=True, host='0.0.0.0', port=5001)
else:
    cnaas_app = get_app()
