# AllAnimeToday

Though Internet is pretty powerful nowadays, it is still hard for people to find the resource they want sometimes. To decrease the effort needs by anime fans to find the newly released episode of the animations they love, Saina Shawulieti designed a project that could send the users the links of anime episodes once they were released. This project aims at improving Saina's project by increasing the number of resource websites and implementing the whole process with AWS Lambda serverless functions. As a result, users get more available information, and can choose to watch anime on the website they like the most. Developers would also be glad to save the cost of maintaining EC2 servers. Such multi-resource subscribe system can be applied to all kinds of merchant goods, notifying buyers about the newly available items they want.

# Methodology

There are five main steps in our approach.

Collecting requests -- Create a front-end website by Flask to display all available anime and let users subscribe them. 

Pooling data -- We use Selenium to crawl HTML webpages and store them in S3 bucket. 

Extract and clean information -- We use xpath to collect useful information, such as episode names and links, in each HTML webpage. In later improvement, we record the regular paths to each kind of information in the database, and go through these data to find the information for all three websites in a general method. We then use regular expression and the tags offered by the websites to modify the informations to ensure that the same anime episode from different websites can be matched with each other and merged together. After cleaning, data are stored into PostgreSQL database in AWS RDS. 

Notify users -- Once data have been insert into AWS RDS, a function would be triggered to check whether the animations that a user follows has been updated. If new episodes have been inserted to the database, an email and a text message will be sent by AWS SNS and AWS SES to the user. 

All functions are implemented as AWS Lambda functions. The crawling function is scheduled by the AWS CloudWatch to run periodically, and the later functions are triggered by a AWS SNS notification from its previous function.

# Structure of Repo


The directory structure for your repo should look like this:

    ├── README.md 
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
    
    
                    
# Set Up
