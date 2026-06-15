from src.app.run import create_app

app = create_app()

# functions-framework --target=entry_point --debug
def entry_point(request):
    """Entry point for Google Cloud Function"""
    return app



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)