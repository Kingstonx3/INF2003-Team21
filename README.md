# INF2003-Team21

Kobee, One Stop Home Theater

Team number: 21

Team Task Allocation:

Tan Wen Zheng, Ashley: Full Stack Development, Database Design, Bug testing

Tan Le Min Sheryl: Database Design, Report Writing

Tan Jing Yuan: Full Stack Development, Bug testing, Report Writing

Chun Jia Jun Louis: Bug testing, Report Writing

Dave Bryan Tan: ER Diagram, Bug testing

Verano Marcus Ong: ER Diagram, Bug testing



Code Instructions:

Step 0: Run "Create Env.bat"

Step 1: Get Mongo and Run
cd to mongod.exe folder the below is the default
cd 'C:\Program Files\MongoDB\Server\7.0\bin'
.\mongod.exe --port 27017 --dbpath 'PATH\project\mongoDB' where PATH is the folder that leads to the mongoDB folder in the project

** Make sure MongoDB\Server\7.0\data does not exist**

Step 2: Start the server
Run "Launch Env.bat"
Run these commands 

$env:FLASK_APP = ".\run.py"; $env:FLASK_ENV = "development"
flask run

Step 3:
Test account: Test
Password: asd
Alice's Pin: 1111

Admin: admin
Password: asd
Pin: None

If you can't delete the data folder try
Close everything
Open CMD as admin
taskkill /F /IM mongod.exe
Try to delete again
