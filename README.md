# Trading-Bot


This trading bot is based on sentiment. The trading bot goes through the News related to the Ticker(GOOG,MSFT,RELIANCE.NS, etc.). Based on the current and past news and the sentiment of the market it potrays its decicion wheter to Hold/Buy/Sell the stock.

TO RUN THE PROGRAM:
1. Simply download all the files.
2. The project folder contains all the neccessarty file required. It also contains the dockerfile alongwith the .yaml file, to deploy it on Huggingface, Render, etc.
3. The main program is the app.py. Before running make sure that all the libraries are download. They can be downloaded through requirements.txt.
4. First run the app.py using:- python app.py
5. After it has succesfully ran, use fastapi.
6. uvicorn app:app --host(enter the host here) --port(specify the port) --reload.
7. For example: uvicorn app:app --host 00.00.00.00 --port 0000 --reload
8. After the application has succesfully started, using postman or any other alternative using GET, it can be tested.
9. For Global Stocks like Google, Microsoft, etc. there original stock name can be used like GOOG, MSFT, etc.
10. For stocks listed in the NSE, make sure to add .NS after the stock name. For example, RELIANCE.NS.
