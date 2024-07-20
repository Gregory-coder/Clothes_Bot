# Clothes bot
## ⚠️ Attention
This bot is not supported since 2023. If you want to try it, please write me directly.
## Short introduction
This Telegram bot was created to help people to choose right clothes in different weather conditions. Unfortunately, the **bot speaks only Russian**. But I think, if you read the instruction carefully, you'll be able to use the bot even if you don't know Russian. Now it runs on Heroku, and if you want to use or test it, find it on Telegram (**@lit_clothes_bot**) or click [here](https://t.me/lit_clothes_bot).
## How it works?
The user can add his/her clothes via ```/add_clothes```. When the user enters ```/what_to_wear```, the bot asks him/her to share his/her location. And then the bot asks OpenWeatherMap about the current weather and the forecast in the place where the user is. The bot looks for the clothes, which are good for such weather and then sends the result.
## Instruction
Some basic commands are:
* ```/start``` - welcome message
* ```/instruction``` - instruction
* ```/add_clothes``` - add new clothes
* ```/delete_clothes``` - delete clothes
* ```/what_to_wear``` - shows what you can put on
* ```/my_clothes``` - shows the clothes you have already added
* ```/commands``` - a list of commands
### Start
When you enter ```/start```, the bot sends you a welcome message and offers to enter ```/instruction``` to learn more about this bot.
![Start](https://github.com/Gregory-coder/Clothes_Bot/blob/main/start.jpg)
### Instruction
When you enter ```/instruction```, the bot sends you a message with the short description of the bot and some advice how to use it.
![Instruction](https://github.com/Gregory-coder/Clothes_Bot/blob/main/instruction.jpg)
### Add clothes
When you enter ```/add_clothes```, the bot asks you the name of the clothes you are going to add and then asks you the type of it (hat/boots/coat...). After you enter these data, the bot asks you the temperature it suits for.
![Add_clothes](https://github.com/Gregory-coder/Clothes_Bot/blob/main/add_clothes.jpg) 
