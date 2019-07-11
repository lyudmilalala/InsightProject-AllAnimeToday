# Prerequisite
# AWS_LINUX EC2 server with Python3.6 with Pip3

# Start from the project repo
cd src

# Set up selenium
cd BackEnd
wget https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
curl https://intoli.com/install-google-chrome.sh

# Place functions on Lambda
mkdir LambdaBuilder

mkdir LambdaBuilder/lambdaL
cp -r psycopg2/ lambdaL
pip3 install --target ./LambdaBuilder/lambdaL lxml
zip -r9 loadtoDB.zip lambdaL/
zip -g loadtoDB.zip loadtoDB.py
aws lambda create-function  --function-name loadtoDB --zip-file fileb://loadtoDB.zip --role <your-lambda-user-arn> --handler loadtoDB.lambda_handler --runtime python3.6 --timeout 900 --vpc-config SubnetIds= <comma-separated-your-vpc-subnet-ids>,SecurityGroupIds= <your-security-group-ids>

mkdir LambdaBuilder/lambdaU
cp -r psycopg2/ lambdaU
zip -r9 loadtoDB.zip lambdaL/
zip -g loadtoDB.zip loadtoDB.py
aws lambda create-function  --function-name userUpdate --zip-file fileb://userUpdate.zip --role <your-lambda-user-arn> --handler userUpdate.lambda_handler --runtime python3.6 --timeout 600 --vpc-config SubnetIds= <comma-separated-your-vpc-subnet-ids>,SecurityGroupIds= <your-security-group-ids>

# Create SNS topic that lambda functions listen to
aws sns create-topic --name ExtractTrigger
aws sns create-topic --name UpdateTrigger
aws sns create-topic --name MessageSenderTrigger

# Start the FrontEnd website
export FLASK_APP= WebContent/frontEnd.py
sudo python3 WebContent/frontEnd.py
# to keep the FrontEnd website running at backstage, replace the above command with
# nohup sudo python3 WebContent/frontEnd.py & [1] 24823

# Initialize
python3 init.py
