from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config.get('PORT', 8888), debug=app.config.get('DEBUG', False))
