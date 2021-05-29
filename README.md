<h1 align="center">
  iGo
  <br>
</h1>

<h4 align="center">Drive in no time through the city.</h4>

<p align="center">
  <a href="#description">Description</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#download">Download</a> •
  <a href="#credits">Credits</a> •
  <a href="#related">Related</a>
</p>

## Description
iGo is designed to calculate time-saving car routes through the streets of a city. It can calculate these routes by using only the length and maximum speed of a street, but you will make the most of it if the city in question has an open data policy about street congestion state.

This project was originally designed and intended to work with data from Barcelona, Catalonia.

## How to use
You can use iGo either through the `igo.py` module or through the Telegram bot implemented in `bot.py`, in the [following link](https://t.me/AlexPereSuperbot/) (if the bot is running).


### iGo

iGo is the heart of the interface, every function has been thoroughly documented in the `igo.py` file plus we consider our code to be very understandable for every user.

### Bot
At first, the Bot downloads all the information needed which may take a few seconds. If two `go` or `map` type commands are executed within a time gap greater than five minutes a new download of the traffic data will be performed.
`bot.py` has the following functions:
- `start`: start the conversation with the bot.
- `help` : returns a help message containing the utility of all commands.
- `go` : + Location. Returns the shortest path from your current position to the location specified. In the generated image, the red dot represents the destination and the green dot represents the origin.
- `map`: returns a map that resumes the current traffic information of the city.
- `pos`: + Location. secret command to fake your position.
- `pos`: + “reset” erases the fake position.
- `where` : returns the users current location.
- `author`: returns information of the authors.

### Download
Make sure you can run python commands, copy the following lines in your terminal and execute. 
```bash
git clone https://www.github.com/Atellas23/igo-ap2
cd igo-ap2
pip install -r requirements.txt
```

###  Credits
This interface is created by Àlex Batlle and Pere Cornellà.

### Related
Jordi Cortadella and Jordi Petit: https://github.com/jordi-petit/ap2-igo-2021