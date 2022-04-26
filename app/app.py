from inits import create_app

app = create_app()

if __name__ == "__main__":
    for _ in app.router.routes_all:
        print(_)

    app.run(port=8000, debug=True, auto_reload=True)
