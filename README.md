# Bridge Buff API

 This is the implementation of a server and a client with a ***Web Interface*** to export statistics on Bridge Defense games played in the servers in our class.

## Prerequisites

* Python 3.6 or higher
* Flask
* Flasgger (for Swagger UI)
* Streamlit library

## Install the required packages:

```bash
pip install Flask Flasgger streamlit
```

## Installation
```bash
git clone https://github.com/HenriqueDSousa/BridgeBuffAPI.git
cd BridgeBuffAPI
```

### REST API Server

The server is responsible for loading information from the games and responding to client requests arriving at URL endpoints.

It can be initialized by running

```bash
./server.py
```
The server will start on http://0.0.0.0:8000 by default, being it hosted in the address of IP ***127.0.0.1*** and port ***8000***, so make sure they are not being already used. 


### API Endpoints
* Get Game by ID : ```/api/game/<int:id>```

* Rank Games by Sunk Ships: ```/api/rank/sunk```

* Rank Games by Escaped Ships: ```/api/rank/escaped```

### Swagger UI
Swagger UI is available at http://localhost:8000/swagger/ and provides a visual interface to interact with the API and documents the endpoints.

## Client

This Python client is designed to interact with a game statistics API. It retrieves and analyzes game data to provide insights into game performance and cannon placements.

### Overview
The client connects to a remote server via HTTP, retrieves game data, and performs two types of analyses:

* Best Performance Analysis: Identifies the best performances based on the number of sunk ships.
* Cannon Placements Analysis: Analyzes cannon placements and their effectiveness in preventing ship escapes.


### Usage

To run the client, use the following command:

```bash
./client.py <IP> <port> <analysis> <output>
```
Parameters

```js
* IP: The IP address of the server hosting the API.
* port: The port number on which the server is listening.
* analysis: The type of analysis to perform (1 for best performance analysis, 2 for cannon placements analysis).
* output: The path to the output file where results will be saved.
```

## Web Interface

This application provides a user interface for analyzing game data using a Streamlit web app. It can perform the following analyses:

* Best Performance: Analyzes the best performance based on game statistics.
* Cannon Placements: Analyzes cannon placements and their effectiveness.
* Select Game by ID: Retrieves and displays details of a specific game by its ID.

### Run the Application

To start the Streamlit application, use the following command:

```bash
python3 -m streamlit run client_ui.py
```

Open your web browser and navigate to http://localhost:8501 to access the Game Analysis Web Interface.

### Using the Application
1. Enter Host Details
Host (IP
): Input the address of the server providing the game data in the format IP:Port. For example, ```localhost:8000```.
2. Select Analysis Type
Choose one of the following analysis types from the dropdown menu:

* Best Performance: Analyzes and displays game performance statistics based on gas and sunk ships.
* Cannon Placements: Analyzes cannon placements and their correlation with escaped ships.
* Select Game by ID: Allows you to retrieve and view details of a specific game by entering its ID.

3. Start Analysis
Click the "Start Analysis" button to execute the selected analysis. Results will be displayed below the button based on your choice.

