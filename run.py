import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.exceptions import NoCredentialsError
import requests

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Configure Flask-SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    db = SQLAlchemy(app)

    # AWS SNS configuration
    SNS_TOPIC_ARN = 'arn:aws:sns:eu-west-1:250738637992:ecofarmforest'
    sns = boto3.client('sns', region_name='eu-west-1', aws_access_key_id='ASIATUYJP7SUPN6OOR6T',
                      aws_secret_access_key='sdxAdNkpf0+qHES0RyVEUncBsPOnbxOGMBxY4Dm3',
                      aws_session_token='IQoJb3JpZ2luX2VjEGQaCXVzLWVhc3QtMSJHMEUCIBDKS7sm9Vt4CzcTZzFj2lDYl7aJbOqfetXLP9bRs6vrAiEA8o5iI7+g1Ts/9R5A52rHvU76xsiUqPLa6kvcOC90Rg8qhAQIvf//////////ARADGgwyNTA3Mzg2Mzc5OTIiDGzIdnl21Jtzb4vknSrYA27GMmnHLARCv1I4ik/GqM9PdVdtQKzxk5fzMWIhyaOrXTRVmZ27T+2r4hW2GHPShWTPLEoqdGi0Fv3+AvC42ZsPQ2GOCp1qlDEJDR7/iT8e8jevVfECoX6rXAcPQTw7Vwd0h2304y+KXrjCPgQ0rB1AOYFiTJ09nynpIQqFycRLbsEf3O0pMNTa6CcbmehD+/QU8RiuiMeWmYqSxXw2YUHgL+2GurtpCODxSsg7G1s51xxgT/l7qchwn/J6lGZ6TxD3k17ADsxkZFah36mZl7dpIfIV01K1K+YkOjFh4OM8s336WQ+wjtD5KsmQEFkOSP4C3jgIMLN5QZdFKv3Re9IUSQN3O6179okAcr/TFtBE9Ld4Z+NxfaJUNGNiZ8oKhDSCXkDJFxmZuTPqUGPkNcgwXCNQ3aNpYt9aONZwp2jzTf5l1BO4wgeQYXn7DZXiGuy6iPttmHfgVtUVjw+CLO6A+S4VASza7QHubXXRzLlF6MavSr+DsVvzeOWNDc6gbiX6nvY3d/NVtpoCf/yN97ZYVEc6cuS87oRwVr3jprU72M+4aAuu0Tb3UdY0yKA9LoivDdYN28f+anW8OINCFAzRD5tSROAIy125VhqteXh/CkmzTKLn4ukwxqyXqwY6pgHnh5lpf0T2JnK38bHs2XBmspFUpCLyFrgPJHXMnE/mA2hrYKKhDL76k5BTJfRvUQZLALakBgx41Bg/l5IZ1UR9xTkE90f6GrsmCqgtM7dDjo/2X/mtXThIVJln36H3l8O3ffQBAnBhPW+fyRuY1gtktzWojPFdLO8iYMTbZHs1/2cmfRmK2oMuU6Ur+D8zn2oV22aGa/ym/+7mvoKcpAqvodJ2vT9B')

    # API Gateway endpoint
    apigateway_url = 'https://c4qcwigljg.execute-api.eu-west-1.amazonaws.com/beta'

    class Contact(db.Model):
        id = db.Column(db.Integer, primary_key=True)  # Primary key column
        name = db.Column(db.String(100))
        email = db.Column(db.String(100)) 


        message = db.Column(db.Text)

    @app.route('/')
    def landing_page():
        return render_template('index.html')

    @app.route('/contact', methods=['POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

            # Send the data to API Gateway
            data = {'httpMethod': 'POST', 'name': name, 'email': email, 'message': message}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(apigateway_url, data=json.dumps(data), headers=headers)

            # Publish message to SNS
            sns.publish(
                TopicArn='arn:aws:sns:eu-west-1:250738637992:ecofarmforest',
                Message=f"New contact: {name}, Email: {email}, Message: {message}",
            )

            # Print the API Gateway response for debugging
            print(response.text)

        return redirect(url_for('thank_you'))

    @app.route('/invoke-lambda', methods=['GET'])
    def invoke_lambda():
        return jsonify({'message': 'This endpoint is for Lambda invocation'})

    @app.route('/thank-you')
    def thank_you():
        return render_template('thank_you.html')

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
