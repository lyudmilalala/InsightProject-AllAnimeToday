# AllAnimeToday

Though Internet is pretty powerful nowadays, it is still hard for people to find the resource they want sometimes. To decrease the effort needs by anime fans to find the newly released episode of the animations they love, Saina Shawulieti designed a project that could send the users the links of anime episodes once they were released. This project aims at improving Saina's project by increasing the number of resource websites and implementing the whole process with AWS Lambda serverless functions. As a result, users get more available information, and can choose to watch anime on the website they like the most. Developers would also be glad to save the cost of maintaining EC2 servers. Such multi-resource subscribe system can be applied to all kinds of merchant goods, notifying buyers about the newly available items they want.

# Methodology

There are four main steps in our approach.

1. Collecting requests -- Create a front-end website by Flask to display all available anime and let users subscribe them. 

2. Pooling data -- We use Selenium to crawl HTML webpages by Selenium and store them in S3 bucket. 

3. Extract and clean information -- We use xpath to collect useful information, such as episode names and links, in each HTML webpage. In later improvement, we record the regular paths to each kind of information in the database, and go through these data to find the information for all three websites in a general method. We then use regular expression and the tags offered by the websites to modify the informations to ensure that the same anime episode from different websites can be matched with each other and merged together. After cleaning, data are stored into PostgreSQL database in AWS RDS. 

4. Notify users -- Once data have been insert into AWS RDS, a function would be triggered to check whether the animations that a user follows has been updated. If new episodes have been inserted to the database, an email and a text message will be sent by AWS SNS and AWS SES to the user. 

Here is a pipeline of the application.

![Image description](https://github.com/lyudmilalala/InsightProject-AllAnimeToday/blob/master/img/pipeline.png)

All functions are implemented as AWS Lambda functions. The crawling function is scheduled by the AWS CloudWatch to run periodically, and the later functions are triggered by a AWS SNS notification from its previous function.

![Image description](https://github.com/lyudmilalala/InsightProject-AllAnimeToday/blob/master/img/CloudWatch.png)
![Image description](https://github.com/lyudmilalala/InsightProject-AllAnimeToday/blob/master/img/SNS.png)

# Structure of Repo

The directory structure for your repo should look like this:

    ├── README.md 
    ├── img
    ├── src
    │   └── BackEnd
    │       └── run.sh
    │       └── init.py
    │       └── crawling.py
    │       └── loadtoDB.py
    │       └── userUpdate.py
    │       └── MessageSender.py   
    │       └── chromedriver
    │       └── psycopg2
    ├────── WebContent
            └── frontEnd.py
            └── static
            │   └── jquery-3.4.0.js 
            │   └── jquery-3.4.0.min.js 
            ├── templates
                └──login.html
                └── main.html
                └── info.html
    
    
The `src` folder holds function scripts. Scripts in `BackEnd` are used for server-only functions, which includes:

* `crawling.py`: the function for crawling HTML webpages from websites
    
* `loadtoDB.py`: the function for extracting information from HTML webpages, cleaning, merging, and finally storing them into the database
    
* `userUpdate.py`: the function for checking whether new episodes of the animations that users follow have been inserted into the database
    
* `MessageSender.py`: the function sending users the resource links of newly released episodes
    `
There are two complements for the scripts, which are:

* `chromedriver`:  A separate executable that Selenium uses to control Chrome on an EC2 server
    
* `psycopg2`: The external Python library that enable a AWS Lambda function to work with PostgresSQL databases
     
Scripts in `WebContent` build up the frontEnd website where users can view existing episodes resources and choose animations to subscribe. `frontEnd.py` is the backEnd script, HTML files in `templates` are frontend views, and files in `static` are the library required by running Javascript on the frontend.

# Set Up

## Configuration of the VPC

As most of our functions are running as AWS Lambda functions, it is important to understand in what the environments they can run properly and how should we set up the environments. Our database should always be put in a private subnet of a VPC. As our lambda functions input data into and output data from the database, they should also be put in the private subnet and access. On the other hand, these lambda functions also need to connect to the outside Internet in order to get HTML webpages from AWS S3 and send messages to users. Indeed, we need a public subnet that connect to the Internet gateway that allows its traffic to get into the public Internet, and a Network Address Translation (NAT) gateway that conducts the traffic from the private subnet to the public subnet. As we also need to access the services hold by the AWS cloud, such as S3 and SNS, we need to add Endpoints for our VPC to access those services. A structure of our application on cloud looks like this:

![Image description](https://github.com/lyudmilalala/InsightProject-AllAnimeToday/blob/master/img/structure.png)

To build up such structure:

1. Following this link https://gist.github.com/reggi/dc5f2620b7b4f515e68e46255ac042a7 to create a VPC with subnet and NAT.

   For more information, look into:
   
   https://docs.aws.amazon.com/lambda/latest/dg/vpc.html
   
   https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Scenario2.html

2. Following this link https://aws.amazon.com/blogs/aws/new-vpc-endpoint-for-amazon-s3/ to add a S3 EndPoint to your VPC.

2. Following the same steps in step2 to add a SNS EndPoint to your VPC, just choose `com.amazonaws.<your-region>.sns` instead of `com.amazonaws.<your-region>.s3`.

## Create an AWS Lambda Execution Role

To run lambda functions, you need grant an AWS Lambda Execution Role. Following the instruction below to create a AWS Lambda Execution Role in IAM, and then replace the  `<your-lambda-user-arn>` in `src/BackEnd/run.sh` the arn of your role.

https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html

## Start the application

Get into the root folder of the repository and run `./src/BackEnd/run.sh`. You will get all VPC, S3 bucket, Postgres database, Lambda functions, CloudWatch events, and SNS topics set up. 

Get into your AWS console, go Lambda -> Functions, and in the designer part, add the correpsonding trigger to each function.

* SNS Topic `ExtractTrigger` to `loadtoDB`

* SNS Topic `UpdateTrigger` to `userUpdate`

* SNS Topic `MessageTrigger` to `MessageSender`

Now you are all set. Please get onto the website http://datawonderland.club/, choose the animations that you want to subscribe, and expect for automatic updates! Have Fun!!!

![Image description](https://github.com/lyudmilalala/InsightProject-AllAnimeToday/blob/master/img/Website1.png)

![Image description](https://github.com/lyudmilalala/InsightProject-AllAnimeToday/blob/master/img/Website2.png)

![Image description](https://github.com/lyudmilalala/InsightProject-AllAnimeToday/blob/master/img/Website3.png)
