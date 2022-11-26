import os

from cnaas_nac.api.internal import app

os.environ['PYTHONPATH'] = os.getcwd()


def run_app():
    return app.app


if __name__ == '__main__':
    run_app().run(debug=True, host='0.0.0.0', port=5002)

else:
    cnaas_app = run_app()
