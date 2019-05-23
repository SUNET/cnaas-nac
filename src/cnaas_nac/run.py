import os

from cnaas_nac.api import app


os.environ['PYTHONPATH'] = os.getcwd()

def main():
    app.app.run(debug=True, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()
