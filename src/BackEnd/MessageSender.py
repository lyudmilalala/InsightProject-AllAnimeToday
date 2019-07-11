import json
import boto3
from botocore.exceptions import ClientError

def make_it_text(username, updates):
    content = 'Hi '+ username +'! You have new episode(s)\r\n\r\n'
    for anime in updates:
        content = content + anime + '\r\n'
        for episode in updates[anime]:
            content = content + 'Episode ' + episode + '\r\n'
            for link in updates[anime][episode]:
                content = content + link + '\r\n'
        content = content + '\r\n'
    # print(content)
    return content

def make_it_html(username, updates):
    content = '<!DOCTYPE html><html lang = "en"><head></head><body>'
    content = content + '<h4>Hi '+ username +'! You have new episode(s)</h4><br>'
    for anime in updates:
        content = content + "<span style='font-weight: bold;'>"+anime+"</span><br>";
        content = content + '<ul>'
        for episode in updates[anime]:
            content = content + "<li><span>Episode "+episode+"</span><br>";
            for link in updates[anime][episode]:
                content = content + "<a href='" + link + "'>" + link + "</a><br>"
        content = content + '</ul><br>'
    content = content + '</body></html>'
    # with open('email_test.html', 'w') as f:
    #     f.write(content)
    return content

def sent_one_email(body_text, body_html, emailaddress):
    client = boto3.client("ses")
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "AnimeToday <sunyuchen2014@gmail.com>"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = emailaddress
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"
    # The subject line for the email.
    SUBJECT = "Your New Episodes Today!"
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = body_text
    BODY_HTML = body_html
    # The character encoding for the email.
    CHARSET = "UTF-8"
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID: %s" % response['MessageId'])

def sent_one_sms(content, number):
    client = boto3.client("sns")
    try:
        response = client.publish(Message=content, PhoneNumber=number)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Text message sent! Message ID:%s" % response['MessageId'])

def sendUpdates(username, email, number, data):
    body_html = make_it_html(username, data)
    body_text = make_it_text(username, data)
    sent_one_sms(body_text, number)
    sent_one_email(body_text, body_html, email)

def sendWarning(username, number):
    client = boto3.client("sns")
    content = 'Hi '+ username +'\r\n'
    content = content+'WARNING: The function for extracting HTML information is not efficiently working now! Please check and modify.\r\n'
    try:
        response = client.publish(Message=content, PhoneNumber=number)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Warning sent! Message ID:%s" % response['MessageId'])

def lambda_handler(event, context):
    msg = json.loads(event['Records'][0]['Sns']['Message'])
    # print(msg)
    username = msg['username']
    number = msg['number']
    if msg['type'] == 'user':
        email = msg['email']
        data = msg['payload']
        sendUpdates(username, email, number, data)
    else:
        sendWarning(username, number)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
