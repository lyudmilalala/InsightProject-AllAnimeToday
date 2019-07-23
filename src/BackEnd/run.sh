# This script should run on your EC2 server
# Prerequisite
# AWS_LINUX EC2 server with Python3.6 with Pip3
# at least two private subnets and one public subnets in your VPC
# a security group for your private subnets
# a lambda IAM account

# for testing and running on local, need the following Python3 libraries
# boto3
# botocore
# lxml
# selenium
# psycopg2 (not the same as the lambda one)
# flask


# Set up selenium
cd BackEnd
wget https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
curl https://intoli.com/install-google-chrome.sh

# Place functions on Lambda
mkdir LambdaBuilder
cd LambdaBuilder

mkdir lambdaL
cp -r psycopg2/ lambdaL
pip3 install --target ./lambdaL lxml
cd lambdaL
zip -r9 ../loadtoDB.zip .
cd ../
zip -g loadtoDB.zip loadtoDB.py
aws lambda create-function  --function-name loadtoDB --zip-file fileb://loadtoDB.zip --role <your-lambda-user-arn> --handler loadtoDB.lambda_handler --runtime python3.6 --timeout 900 --vpc-config {
    "SubnetIds": [<your-private-subnet1>, <your-private-subnet2>,...], "SecurityGroupIds": [<your-security-group>] }

mkdir lambdaU
cp -r psycopg2/ lambdaU
cd lambdaU
zip -r9 ../userUpdate.zip .
cd ../
zip -g userUpdate.zip userUpdate.py
aws lambda create-function  --function-name userUpdate --zip-file fileb://userUpdate.zip --role <your-lambda-user-arn> --handler userUpdate.lambda_handler --runtime python3.6 --timeout 600 --vpc-config {
    "SubnetIds": [<your-private-subnet1>, <your-private-subnet2>,...], "SecurityGroupIds": [<your-security-group>] }

# Create SNS topic that lambda functions listen to
aws sns create-topic --name ExtractTrigger
aws sns create-topic --name UpdateTrigger
aws sns create-topic --name MessageSenderTrigger

# Start the FrontEnd website
pip3 install flask
cd ../../
export FLASK_APP= ./WebContent/frontEnd.py
sudo python3 WebContent/frontEnd.py
# to keep the FrontEnd website running at backstage, replace the above command with
# nohup sudo python3 WebContent/frontEnd.py & [1] 24823

# Initialize
python3 init.py
