# Clothes bot
## Краткое вступление
Clothes bot предназначен для облегчения процесса выбора одежды перед выходом на улицу. Вы можете добавить несколько предметов одежды с помощью команды  ```/add_clothes```.
В данный момент этот бот запущен на сервере Heroku, а любой желающий может [воспользоваться](https://t.me/lit_clothes_bot) им в Telegram.
## Инструкция
Вот основные команды для бота:
* ```/start``` - приветственное сообщение с инструкцией
* ```/instruction``` - инструкция по использованию бота
* ```/add_clothes``` - добавить одежду
* ```/delete_clothes``` - удалить одежду
* ```/what_to_wear``` - что мне надеть
* ```/my_clothes``` - список добавленной одежды
* ```/commands``` - список доступных команд

### Start
Когда вы вводите ```/start```, бот отправляет вам приветсвенное сообщение и предлагает ввести команду ```/instruction```, чтобы узнать больше о боте.
![Instruction](https://github.com/Gregory-coder/Clothes_Bot/blob/main/start.jpg)
### Instruction
Когда вы вводите ```/instruction```, бот отправляет вам сообщение с кратким описанем и инструкцией.
![Instruction](https://github.com/Gregory-coder/Clothes_Bot/blob/main/instruction.jpg)

## How it works?
When the user enters ```/what_to_wear```, the bot asks him/her to share his/her location. And then the bot asks OpenWeatherMap about the current weather and the forecast in the place where the user is. The bot looks for the clothes, which are good for such weather.

