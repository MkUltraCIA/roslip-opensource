https://www.roblox.com/games/5068979318/City-Explorer-OPEN-SOURCE

RoSlip - City Explorer Demo
===========================

This project uses [Slippy Map technology](https://developers.planet.com/tutorials/slippy-maps-101/) to provide a view of any city or town
in the world through Roblox. Here you'll find a tutorial on how to get this project
up and running on your local machine!

<p>
    <img src="https://jpatrickdill.github.io/images/sanfran.png" width="59%">
    <img src="https://i.imgur.com/q0d3yh4.png" width="40%">
</p>


Project Structure
-----------------
This project has 3 main components:
- Roblox Game
- Web Server
- Data Processing Server

1 - The Roblox game has two main responsibilities:
- render the location entered while effectively managing memory usage.
- allow players to create servers based on location and travel between servers

2 - The Web Server acts is a communication channel between the Roblox game and Data Processing Server
via a Redis Database.

Note that this is NOT the best way to do this in production - this just allowed
me to host the web server for free on Heroku while doing the data processing and caching from my old PC.

3 - The Data Processing Server downloads and caches data from multiple sources, filters out necessary
road/building data, and calculates land shape geometry before uploading the data to Redis.

Prerequisites
-------------

To run this project, you'll need to:
- Have a copy of this repository
- Have Python 3.7 or later installed - https://www.python.org/
- Install the Python requirements for this project - `$ pip install -r requirements.txt`
- Set up a RedisLabs free database (recommended) or install Redis locally
    - RedisLabs - https://redislabs.com/try-free/
    - Install locally - https://redis.io/topics/quickstart
- A free NextZen API key - https://developers.nextzen.org/

If you want to run the game outside of Studio, you'll need to:
- Make an account on https://heroku.com/ and create a Free Dyno
  - This repository comes with a Procfile included :)

Part 1 - Config File
------

The first step in getting this project up and running is creating our configuration file.

The web server and data processor will both use the `config.json` file to get the database information,
as well as the API key for the main map tile source.

Example `config.json` using RedisLabs:
```json
{
  "REDIS_URI": "redis-XXXXX.cXX.us-east-1-3.ec2.cloud.redislabs.com",
  "REDIS_PORT": 14785,
  "REDIS_PW": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "NEXTZEN": "xxxxxxxxxxxxxxxxxxxxxx"
}
```

To find your RedisLabs database information, first find the database you created after signup:
![](https://i.imgur.com/kAqoCYQ.png)

Clicking your database should reveal the necessary information:
![](https://i.imgur.com/lTRveIG.png)

Copy the URL portion of the endpoint (before :) to the `REDIS_URI` value in your config file.
Copy the port (after :) to the `REDIS_PORT` value.
Click the eye to reveal your database password, and copy this to the `REDIS_PW` value.

A NextZen API key can be created at https://developers.nextzen.org/. Copy the key 
and paste it in the `NEXTZEN` value of the config file.

![](https://i.imgur.com/PLXpRQF.png)

**Warning: NEVER publish this file! If you're using GitHub to host your files, make the repository private!**

Part 2 - Running the Data Processing Server
------

The data processing server can be run locally or on a hosted service such as Heroku for a monthly cost.
Running the server locally is simple:

1. Navigate to the top level directory of the project in a command prompt
2. Ensure all requirements are installed using `$ pip install -r requirements.txt`
3. Start the server using this command: `$ python ./roslip/data/__init__.py`

After starting the data server, your prompt should look something like this:
![](https://i.imgur.com/wnYEbXF.png)

As the program detects requests in the Redis database, it will spawn a new process for each requested tile
that will download and process the tile data before pushing it to the database. Half of the download
requests get sent through a proxy if it's online.

You can press CTRL+C to stop the data processor while we set up the web server.

Part 3 - Running the Web Server Locally
------

RoSlip uses Flask as its web server. A `runlocal.py` file is included in the project that will run
the Flask debug web server, which can be used to run your project locally.

To run the debug server, open a terminal in the project folder and run `$ python runlocal.py`

Your terminal should look like this:
![](https://i.imgur.com/c4cmAPx.png)

If this is successful, the web server will be running locally at `localhost:3000`

Part 4 - Configuring the Game
------

To get your copy of the game, visit https://www.roblox.com/games/5068979318/OPEN-SOURCE and click
the three dots in the top right, then click Edit. This should open the place in Studio.

Only one value needs to be configured in the game for it to work - the Web Server URL. To do this,
navigate to the Tiles.api module found under `game.ReplicatedStorage.Tiles.api`.
In this ModuleScript, find this line: `local server = "server URL here"`

To make the game connect to our local server, change this value to `"http://localhost:3000"`

Part 5 - Testing Locally
------

To run the game properly, we'll need to get the two servers running first. You'll need two separate
terminals open, one for the web server, and one for the data processor.
We'll start these scripts the same as before in each terminal:

`$ python roslip/data/__init__.py`

`$ python runlocal.py`

Finally, click Run in Studio. By default, the game will begin loading in Atlanta, Georgia. To change
the location that loads in Studio, you can edit the values of `workspace.Lat` and `workspace.Lon` with
coordinates. The server list will not work, as TeleportService cannot be used in Studio.
