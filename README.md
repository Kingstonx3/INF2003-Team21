# INF2003-Team21

Kobee, One Stop Home Theater

Team number: 21

Team Task Allocation:

Tan Wen Zheng, Ashley: Full Stack Development, Database Design, Bug testing, Report Writing

Tan Le Min Sheryl: Database Design, Report Writing, Bug testing

Tan Jing Yuan: Full Stack Development, Bug testing, Report Writing, Presentation Slides

Chun Jia Jun Louis: Bug testing, Report Writing, Presentation Slides

Dave Bryan Tan: Bug testing, ER Diagram

Marcus Ong: Bug testing, ER Diagram



Code Instructions:

Step 0: Run "Create Env.bat"

Step 1: Get Mongo and Run Launch Env.bat
cd to mongod.exe folder, below is the default location for MongoDB

cd 'C:\Program Files\MongoDB\Server\7.0\bin'

.\mongod.exe --port 27017 --dbpath 'PATH\project\mongoDB' 
Change PATH, where PATH is the folder that leads to the mongoDB folder in the project, the directory where you extracted the files from the zip to.

** Make sure MongoDB\Server\7.0\data does not exist, if it does, delete it**

Step 2: Start the server
Run "Launch Env.bat" again (While having the first Launch Env.Bat for MongoDB still active)
Run these commands:

$env:FLASK_APP = ".\run.py"; $env:FLASK_ENV = "development"

flask run

Step 3:
Login using:

Admin: admin
Password: asd
Pin: None

Note: If you can't delete the data folder try
Close everything
Open CMD as admin
taskkill /F /IM mongod.exe
Try to delete again
