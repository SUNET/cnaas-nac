import os

from cnaas_nac.api import app


__import__('pkg_resources').declare_namespace(__name__)
os.environ['PYTHONPATH'] = os.getcwd()


def main():
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()
