from scripts import app_runner

app = app_runner.app
server = app_runner.server

if __name__ == "__main__":
    app.run_server(debug=True)
