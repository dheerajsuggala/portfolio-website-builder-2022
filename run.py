from portfolio_builder.app import app
import portfolio_builder.routes

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0')
