from flask import Flask, send_from_directory, request


app = Flask(__name__, static_folder='./')


@app.route('/model', defaults={'filename': 'index.html'})
@app.route('/model/<path:filename>')
def static_model(filename):
    return send_from_directory(app.static_folder + '/model/', filename)


@app.route('/', defaults={'filename': 'index.html'})
@app.route('/<path:filename>')
def static_jupyterbook(filename):
    print(request.endpoint)
    try:
        return send_from_directory(app.static_folder + '/_build/html/', filename)
    except:
        return send_from_directory(app.static_folder + '/model/', filename)


if __name__ == '__main__':
    app.run()
