_____________________________
_____________________________
Where the Data Collection Happens
_____________________________________
_____________________________
All scripts responsible for retrieving environmental data are located in:
BackEnd → SourceFiles
Each file in this folder connects to one specific environmental data provider. These scripts pull environmental measurements like rainfall, temperature, river levels, or soil data, and store them in the project database.


____________________________
____________________________
General Workflow of a Source File
____________________________________
____________________________
Each source file follows the same three-step workflow:
_pull → _process → _push
_pull() – downloads raw data from the external provider (e.g., API, CSV file, or website).


_process() – converts the raw data into a consistent table format and stores it temporarily in temp_staging.


_push() – moves the processed data from temp_staging into the final database table, updating existing records or adding new ones.


This pattern ensures all data sources end up in a consistent format, making the website easier to maintain.


___________________________________
___________________________________
Summary of Source Files and Data Sources
_____________________________________________
___________________________________
Here’s what each script is responsible for:
DANR.py – Data from the North Dakota Department of Agriculture and Natural Resources. Includes environmental and water monitoring measurements.


USACE.py – Water resource data from the U.S. Army Corps of Engineers, including reservoir levels and river monitoring.


Cocorahs.py – Precipitation and snowfall data from the CoCoRaHS network.





__________________________
__________________________
Key Notes for Maintainers
__________________________
__________________________
All source files follow the same pull → process → push framework.


Each script is specific to one provider, so if the provider changes their system, only that file needs updating.


The database (mydatabase.db) is where all processed data is stored, ready for the website to display.


Temporary staging tables (temp_staging) prevent partial or broken data from being added to the main tables.


This design makes the backend modular and easy to maintain, allowing new data sources to be added simply by creating a new source file following the same pattern.



________________________________
________________________________
config.py – The Master Settings File
________________________________________
________________________________
config.py is a very important file that manages how all the data-collecting scripts work. You can think of it as the “control center” for the backend. It tells the other scripts where to get data, which stations to use, and how to organize the data in the database.
What It Does
Database Location


Sets the path to the main database (Measurements.db).


Ensures all scripts save their data in the same place.


Field Name Mappings


Different sources might call the same measurement by different names (like “Air Temperature” vs. “Average Temperature”).


SQL_CONVERSION maps all of these to consistent names so the database stays organized.


Source Settings


Provides URLs, station IDs, dataset codes, and date formats for each data source.


Makes it easy to add or change stations without editing the individual source scripts.


Why It Matters
Keeps all scripts coordinated and consistent.


Lets you update stations or datasets in one place.


Makes sure the data in the database is organized the same way for every source.

Backend source files (like DANR.py, USACE.py, etc.) start running.


Each script looks at config.py to find:


The database path
Which stations or datasets to pull
How to name the columns in the database


The source script pulls data from the external site.


It processes the data into a standard format.


It pushes the processed data into the database using the names and table info from config.py.


Key idea: config.py is like a roadmap — the source scripts follow it to know where to go, what to collect, and how to store it.



________________________________
________________________________
Updates.py – The Daily Update Script
________________________________
________________________________
This is the main script you run to refresh all data in the system. Think of it as the “master switch” that tells every data source to pull and update.
What It Does
Sets up the project environment


Make sure Python can find all the backend files and modules.



Lists all the data sources


Each source has a name (like "DANR") and the path to its Python script (New_DANR).


Runs each source’s update function


For every source in the list:


Imports the module dynamically


Calls its update() function, which:


Pulls data from the source


Processes it


Pushes it into Measurements.db


Why It’s Important
This is the script that keeps the entire database up to date.


Instead of running each source manually, you just run this once a day (or on a schedule), and all sources refresh automatically.


If anything goes wrong with a source, the script catches the error and continues updating the others — so one failure doesn’t stop everything.


Bottom line: If you want the website to show the latest environmental data, this is the script you run. It’s the central point for updating the entire system.



_______________________
_______________________
commands.py (Backend API)
_______________________
_______________________
This file provides functions that the website or front end can use to interact with the backend.


listAllSources() goes through the SourceFiles folder and lists all the scripts that pull data.


listStations(source) is meant to list all stations for a specific data source (not fully implemented yet).


Essentially, it acts as a gateway, letting the website see what data is available and connect to the scripts that update or retrieve it.


Bottom line: The website doesn’t access the source files directly — it uses this file to know what data exists and to trigger updates safely.



________________________________
________________________________
Measurements.db – The Main Database
________________________________
________________________________
Measurements.db is where all the data from every source comes together. Every script that pulls environmental data stores it here, and the website reads from it to show users the latest information.
It's like a central hub for the system, it keeps everything organized and in one place. Without it, the data would be scattered across scripts, and the website wouldn’t have a reliable source to display.
Basically, it’s the backbone that makes the whole system work smoothly.

Accessing Measurements.db
Since Measurements.db is a SQLite database, you can access it in a few ways:
Using Python – The backend scripts do this all the time. For example:
import sqlite3
conn = sqlite3.connect("Measurements.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM USGS LIMIT 5")
print(cursor.fetchall())
conn.close()
This lets you read or query any table in the database.
Using a Database Browser – You can open it with a tool like “DB Browser for SQLite.” This gives you a visual interface to look at tables, see the data, and even run queries without writing code.
Through the Backend API – Some functions in commands.py are designed to expose data to the front end, so the website itself reads from this database automatically.
Key point: Don’t move or rename the database file, because the scripts expect it in the location defined in config.py.



________________________________________
________________________________________
mydatabase.db – The Temporary Staging Database
________________________________________
________________________________________
mydatabase.db is used by the backend as a temporary workspace while new data is being pulled and processed.
When a source script pulls data from a website, it first stores it here in a temporary table (temp_staging).


Once the data is cleaned and formatted, it’s pushed into the main database (Measurements.db).


This approach keeps the main database safe — if something goes wrong while processing, the main data isn’t affected.


Key point: Think of mydatabase.db as a holding area or scratchpad for new data before it’s officially saved in Measurements.db.
You usually don’t need to access it directly unless you’re troubleshooting a pull or processing issue.
