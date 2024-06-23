import random
import requests
import time
from telebot import TeleBot, types
from config import token  
bot = TeleBot(token)
admin_ids = [1845730851] 

class Trainer:
    def __init__(self, username):
        self.username = username
        self.pokemons = []
        self.current_pokemon_index = 0
        self.experience = 0

    def add_pokemon(self, pokemon):
        self.pokemons.append(pokemon)

    def get_current_pokemon(self):
        if self.pokemons:
            return self.pokemons[self.current_pokemon_index]
        else:
            return None

    def switch_pokemon(self, index):
        if 0 <= index < len(self.pokemons):
            self.current_pokemon_index = index
            return True
        else:
            return False

    def gain_experience(self, amount):
        self.experience += amount
        for pokemon in self.pokemons:
            if self.experience >= pokemon.evolution_experience:
                pokemon.evolve()
                self.experience -= pokemon.evolution_experience
                bot.send_message(self.username, f"{pokemon.name} эволюционировал!")
                break


class Pokemon:
    def __init__(self, trainer, pokemon_type):
        self.trainer = trainer
        self.name = ""
        self.img = ""
        self.abilities = []
        self.level = 1
        self.height = 0
        self.health = 0
        self.max_health = 0
        self.slot = 0
        self.power = 0
        self.pokemon_type = pokemon_type
        self.shield = 0
        self.shield_cooldown = 5
        self.shield_used = 0
        self.last_heal_time = 0
        self.max_level = 5
        self.magic_ball_charge = 0
        self.crit_chance = 0
        self.stunned = False
        self.evolution_experience = 500
        self.name, self.img, self.abilities, self.level, self.height, self.health, self.max_health, self.slot, self.power, self.pokemon_type = self.get_pokemon_data()

    def get_pokemon_data(self):
        while True:
            pokemon_id = random.randint(1, 898)
            url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                name = data['forms'][0]['name']
                img = data['sprites']['front_default']
                abilities = [ability['ability']['name'] for ability in data['abilities']]
                level = data['base_experience']
                height = data["height"]
                slot = max([ability["slot"] for ability in data['abilities']])
                if self.pokemon_type == "Визерд":
                    health = random.randint(150, 800)
                    power = random.randint(20, 30)
                    abilities.append("Магический Щит")
                    self.shield = 200
                elif self.pokemon_type == "Боец":
                    health = random.randint(50, 500)
                    power = random.randint(30, 60)
                    abilities.append("Супер Удар")
                else:
                    health = random.randint(100, 700)
                    power = random.randint(5, 20)
                return name, img, abilities, level, height, health, health, slot, power, self.pokemon_type
            else:
                continue

    def info(self):
        return f"Имя: {self.name}, Тип: {self.pokemon_type}, Уровень: {self.level}, Здоровье: {self.health}/{self.max_health}, Сила: {self.power}, Способности: {', '.join(self.abilities)}, Опыт: {self.trainer.experience}/{self.evolution_experience}"

    def show_img(self):
        return self.img

    def attack(self, opponent):
        if "Супер Удар" in self.abilities and random.random() < 0.2:
            damage = max(1, self.power * 2 - opponent.power // 2)
            bot.send_message(opponent.trainer.username, f"Твой {opponent.name} получил супер удар! -{damage} ХП")
        elif "Магический Шар" in self.abilities and self.magic_ball_charge >= 2:
            damage = max(1, (self.power * 3) - opponent.power)
            self.magic_ball_charge = 0
            bot.send_message(opponent.trainer.username, f"Твой {opponent.name} получил Магический Шар! -{damage} ХП")
        else:
            damage = max(1, self.power - opponent.power // 2)
        if "Магический Щит" in self.abilities and self.shield_used < self.shield_cooldown:
            damage -= self.shield
            self.shield_used += 1
            bot.send_message(opponent.trainer.username, f"Твой {opponent.name} защищен Магическим Щитом! -{self.shield} урона")
        if random.random() < self.crit_chance:
            damage *= 2
            bot.send_message(opponent.trainer.username, f"Критический удар! +{damage} урона")
        opponent.health -= damage
        if opponent.health <= 0:
            opponent.stunned = True
            bot.send_message(opponent.trainer.username, f"{opponent.name} оглушен!")
        return damage

    def heal(self):
        cooldown_time = 1800
        if time.time() - self.last_heal_time >= cooldown_time:
            self.health = self.max_health
            self.last_heal_time = time.time()
            return True
        return False

    def evolve(self):
        if self.level < self.max_level:
            if self.pokemon_type == "Визерд":
                self.name = "магистр"
                self.img = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/133.png"
                self.abilities.append("Магический Шар")
                self.max_health = 1000
                self.power = 50
                self.evolution_experience = 2000
                self.max_level = 10
                self.shield = 300
                self.shield_cooldown = 5
            elif self.pokemon_type == "Боец":
                self.name = "гладиатор"
                self.img = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/150.png"
                self.abilities.append("Мощный Удар")
                self.max_health = 700
                self.power = 80
                self.evolution_experience = 2000
                self.max_level = 10
                self.crit_chance = 0.1
                self.health = self.max_health
                self.level = self.max_level
            return True
        return False

    def increase_stats(self):
        if self.level < self.max_level:
            self.max_health += 50
            self.power += 10
            self.health = self.max_health
            self.shield += 50
            self.shield_cooldown -= 1
            self.crit_chance += 0.05
            self.magic_ball_charge += 1
            self.level += 1

    def use_magic_ball(self):
        self.magic_ball_charge += 1
        if self.magic_ball_charge >= 2:
            bot.send_message(self.trainer.username, f"{self.name} готов к Магическому Шару! (Заряд: {self.magic_ball_charge}/2)")

    def stun_reset(self):
        self.stunned = False


class Wizerd(Pokemon):
    def __init__(self, trainer):
        super().__init__(trainer, "Визерд")


class Boez(Pokemon):
    def __init__(self, trainer):
        super().__init__(trainer, "Боец")


trainers = {}
START = 0
FIGHT_MENU = 1
COOLDOWN_TIME = 1800
FIGHT_DATA = {}
current_turn = None


@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    if username in trainers:
        bot.send_message(message.chat.id, f"Привет, {username}! Ты уже в игре!")
    else:
        trainers[username] = Trainer(username)
        bot.send_message(message.chat.id, f"Привет, {username}! Добро пожаловать в мир покемонов!")
        bot.send_message(message.chat.id, "Чтобы создать своего первого покемона, используй команду /go")


@bot.message_handler(commands=['go'])
def go(message):
    username = message.from_user.username
    if username in trainers:
        trainer = trainers[username]
        if len(trainer.pokemons) < 4:
            pokemon_type = random.randint(0, 1)
            if pokemon_type == 0:
                pokemon = Wizerd(trainer)
            else:
                pokemon = Boez(trainer)
            trainer.add_pokemon(pokemon)
            bot.send_message(message.chat.id, pokemon.info())
            bot.send_photo(message.chat.id, pokemon.show_img())
            bot.reply_to(message, f"Поздравляю, ты поймал {pokemon.name}!")
        else:
            bot.reply_to(message, "У тебя уже 4 покемона. Сначала поменяй их или выйди из игры.")
    else:
        bot.reply_to(message, "Сначала начни игру, используя /start")


@bot.message_handler(commands=['switch'])
def switch_pokemon(message):
    username = message.from_user.username
    trainer = trainers[username]
    if len(trainer.pokemons) > 1:
        try:
            index = int(message.text.split()[1]) - 1
            if trainer.switch_pokemon(index):
                bot.send_message(message.chat.id, f"Теперь твой атакующий покемон: {trainer.get_current_pokemon().name}")
            else:
                bot.send_message(message.chat.id, "Некорректный номер покемона.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Необходимо указать номер покемона.")
    else:
        bot.send_message(message.chat.id, "У тебя только один покемон.")


@bot.message_handler(commands=['show'])
def show_pokemons(message):
    username = message.from_user.username
    trainer = trainers[username]
    if trainer.pokemons:
        pokemon_list = "\n".join(f"{i+1}. {pokemon.name} - {pokemon.info()}" for i, pokemon in enumerate(trainer.pokemons))
        bot.send_message(message.chat.id, f"Твои покемоны:\n{pokemon_list}")
    else:
        bot.send_message(message.chat.id, "У тебя ещё нет покемонов.")


@bot.message_handler(commands=['heal'])
def heal_pokemon(message):
    username = message.from_user.username
    trainer = trainers[username]
    if time.time() - trainer.get_current_pokemon().last_heal_time < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (time.time() - trainer.get_current_pokemon().last_heal_time)
        minutes, seconds = divmod(int(remaining_time), 60)
        bot.send_message(message.chat.id, f"Подожди {minutes} минут {seconds} секунд, чтобы излечить покемона снова.")
        return
    if trainer.pokemons:
        for pokemon in trainer.pokemons:
            if pokemon.heal():
                bot.send_message(message.chat.id, f"{pokemon.name} излечен!")
    else:
        bot.send_message(message.chat.id, "У тебя ещё нет покемонов.")


@bot.message_handler(commands=['fight'])
def fight(message):
    username = message.from_user.username
    trainer = trainers[username]
    if username in trainers:
        if '@' in message.text:
            opponent_username = message.text.split('@')[1].strip()
            if opponent_username in trainers:
                opponent_trainer = trainers[opponent_username]
                if trainer.pokemons and opponent_trainer.pokemons:
                    my_pokemon = trainer.get_current_pokemon()
                    opponent_pokemon = opponent_trainer.get_current_pokemon()
                    bot.send_message(message.chat.id, f"{my_pokemon.name} против {opponent_pokemon.name}! Начинается бой!")
                    FIGHT_DATA[username] = {
                        'opponent_username': opponent_username,
                        'my_pokemon': my_pokemon,
                        'opponent_pokemon': opponent_pokemon,
                        'round': 1
                    }
                    FIGHT_DATA[opponent_username] = {
                        'opponent_username': username,
                        'my_pokemon': opponent_pokemon,
                        'opponent_pokemon': my_pokemon,
                        'round': 1
                    }
                    global current_turn
                    current_turn = username
                    send_fight_menu(username, FIGHT_DATA[username], 1)
                    bot.set_state(message.chat.id, FIGHT_MENU, message.chat.id)
                    bot.set_state(opponent_trainer.username, FIGHT_MENU, opponent_trainer.username)
                else:
                    bot.send_message(message.chat.id, "У одного из вас нет покемона!")
            else:
                bot.send_message(message.chat.id, "У этого пользователя нет покемона.")
        else:
            bot.send_message(message.chat.id, "Неверный формат команды. Используйте /fight @[username].")
    else:
        bot.send_message(message.chat.id, "Сначала создай покемона!")


def send_fight_menu(username, data, round_number):
    """Отправляет меню боя в чат игрока."""
    my_pokemon = data['my_pokemon']
    bot.send_message(username, f"{round_number} раунд.\n\n"
                          f"Ход {my_pokemon.name}. Выберите действие:\n"
                          f"1. Атака 1\n"
                          f"2. Атака 2\n"
                          f"3. Замена (сменить покемона)\n"
                          f"4. Убежать (шанс сбежать 1/3)\n"
                          f"5. Излечить (доступно раз в 3 минуты)")


@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == FIGHT_MENU, state=FIGHT_MENU)
def handle_fight_action(message):
    username = message.from_user.username
    data = FIGHT_DATA[username]
    opponent_username = data['opponent_username']
    my_pokemon = data['my_pokemon']
    opponent_pokemon = data['opponent_pokemon']
    round_number = data['round']
    try:
        action = int(message.text)
        if action == 1:
            damage = my_pokemon.attack(opponent_pokemon)
            bot.send_message(username, f"{round_number} раунд.\n\n"
                              f"{my_pokemon.name} атаковал {opponent_pokemon.name} атакой 1 и нанес {damage} урона.\n"
                              f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.\n\n"
                              f"Ход {opponent_pokemon.name}.")
            bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                              f"{my_pokemon.name} атаковал {opponent_pokemon.name} атакой 1 и нанес {damage} урона.\n"
                              f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.")
        elif action == 2:
            if my_pokemon.pokemon_type == "Визерд":
                my_pokemon.use_magic_ball()
                damage = my_pokemon.attack(opponent_pokemon)
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} атаковал {opponent_pokemon.name} атакой 2 и нанес {damage} урона.\n"
                                  f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.\n\n"
                                  f"Ход {opponent_pokemon.name}.")
                bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} атаковал {opponent_pokemon.name} атакой 2 и нанес {damage} урона.\n"
                                  f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.")
            elif my_pokemon.pokemon_type == "Боец":
                if "Мощный Удар" in my_pokemon.abilities:
                    my_pokemon.power *= 2
                    damage = my_pokemon.attack(opponent_pokemon)
                    my_pokemon.power //= 2
                    bot.send_message(username, f"{round_number} раунд.\n\n"
                                      f"{my_pokemon.name} использовал Мощный Удар! Атака 2 нанесла {damage} урона.\n"
                                      f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.\n\n"
                                      f"Ход {opponent_pokemon.name}.")
                    bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                      f"{my_pokemon.name} использовал Мощный Удар! Атака 2 нанесла {damage} урона.\n"
                                      f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.")
                else:
                    damage = my_pokemon.attack(opponent_pokemon)
                    bot.send_message(username, f"{round_number} раунд.\n\n"
                                      f"{my_pokemon.name} атаковал {opponent_pokemon.name} атакой 2 и нанес {damage} урона.\n"
                                      f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.\n\n"
                                      f"Ход {opponent_pokemon.name}.")
                    bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                      f"{my_pokemon.name} атаковал {opponent_pokemon.name} атакой 2 и нанес {damage} урона.\n"
                                      f"У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.")
        elif action == 3:
            trainer = trainers[username]
            if len(trainer.pokemons) > 1:
                bot.send_message(username, "Выберите покемона, которого хотите использовать:")
                pokemon_list = "\n".join(f"{i+1}. {pokemon.name} - {pokemon.info()}" for i, pokemon in enumerate(trainer.pokemons))
                bot.send_message(username, f"Твои покемоны:\n{pokemon_list}")
                bot.set_state(username, FIGHT_MENU, username)
            else:
                bot.send_message(username, "У вас только один покемон.")
        elif action == 4:
            if random.randint(1, 3) == 1:
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} успешно сбежал!")
                bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} сбежал!")
                bot.delete_state(username)
                bot.delete_state(opponent_username)
                return
            else:
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} не смог сбежать!")
                bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} не смог сбежать!")
        elif action == 5:
            if time.time() - my_pokemon.last_heal_time < COOLDOWN_TIME:
                remaining_time = COOLDOWN_TIME - (time.time() - my_pokemon.last_heal_time)
                minutes, seconds = divmod(int(remaining_time), 60)
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"Подожди {minutes} минут {seconds} секунд, чтобы излечить покемона снова.")
                return
            else:
                if my_pokemon.heal():
                    bot.send_message(username, f"{round_number} раунд.\n\n"
                                      f"{my_pokemon.name} излечен!")
                    bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                      f"{my_pokemon.name} был излечен!")
                else:
                    bot.send_message(username, "Некорректный ввод. Введите число от 1 до 5.")
        if opponent_pokemon.health <= 0:
            bot.send_message(username, f"{round_number} раунд.\n\n"
                              f"{opponent_pokemon.name} был побежден!")
            bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                              f"{opponent_pokemon.name} был побежден!")
            my_pokemon.trainer.gain_experience(50)
            if my_pokemon.trainer.experience >= my_pokemon.evolution_experience:
                bot.send_message(username, f"{my_pokemon.name} эволюционировал!")
            bot.delete_state(username)
            bot.delete_state(opponent_username)
            return
        if my_pokemon.health > 0:
            if opponent_pokemon.stunned:
                opponent_pokemon.stun_reset()
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"{opponent_pokemon.name} был оглушен и пропустил ход!")
                bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                  f"{opponent_pokemon.name} был оглушен и пропустил ход!")
            else:
                opponent_damage = opponent_pokemon.attack(my_pokemon)
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"{opponent_pokemon.name} атаковал {my_pokemon.name} и нанес {opponent_damage} урона.\n"
                                  f"У {my_pokemon.name} осталось {my_pokemon.health} ХП.")
                bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                  f"{opponent_pokemon.name} атаковал {my_pokemon.name} и нанес {opponent_damage} урона.\n"
                                  f"У {my_pokemon.name} осталось {my_pokemon.health} ХП.")
            if my_pokemon.health <= 0:
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} был побежден!")
                bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} был побежден!")
                opponent_pokemon.trainer.gain_experience(50)
                if opponent_pokemon.trainer.experience >= opponent_pokemon.evolution_experience:
                    bot.send_message(opponent_username, f"{opponent_pokemon.name} эволюционировал!")
                bot.delete_state(username)
                bot.delete_state(opponent_username)
                return
        if username == current_turn:
            current_turn = opponent_username
            FIGHT_DATA[opponent_username]['round'] += 1
            send_fight_menu(current_turn, FIGHT_DATA[current_turn], FIGHT_DATA[current_turn]['round'])
    except (ValueError, TypeError):
        bot.send_message(username, "Некорректный ввод. Введите число от 1 до 5.")


@bot.message_handler(func=lambda message: bot.get_state(message.chat.id) == FIGHT_MENU and int(message.text) > 3 and int(message.text) < 6, state=FIGHT_MENU)
def handle_fight_action_confirmation(message):
    username = message.from_user.username
    data = FIGHT_DATA[username]
    opponent_username = data['opponent_username']
    my_pokemon = data['my_pokemon']
    opponent_pokemon = data['opponent_pokemon']
    round_number = data['round']
    if int(message.text) == 3:
        trainer = trainers[username]
        if len(trainer.pokemons) > 1:
            try:
                index = int(message.text.split()[1]) - 1
                if trainer.switch_pokemon(index):
                    my_pokemon = trainer.get_current_pokemon()
                    bot.send_message(username, f"{round_number} раунд.\n\n"
                                      f"Вы сменили покемона на {my_pokemon.name}.\n\n"
                                      f"Ход {my_pokemon.name}.")
                    bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                      f"{username} сменил покемона на {my_pokemon.name}.\n\n"
                                      f"Ход {my_pokemon.name}.")
                    FIGHT_DATA[username]['my_pokemon'] = my_pokemon
                    FIGHT_DATA[opponent_username]['opponent_pokemon'] = my_pokemon
                else:
                    bot.send_message(username, "Некорректный номер покемона.")
            except (IndexError, ValueError):
                bot.send_message(username, "Необходимо указать номер покемона.")
        else:
            bot.send_message(username, "У вас только один покемон.")
    elif int(message.text) == 4:
        if random.randint(1, 3) == 1:
            bot.send_message(username, f"{round_number} раунд.\n\n"
                              f"{my_pokemon.name} успешно сбежал!")
            bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                              f"{my_pokemon.name} сбежал!")
            bot.delete_state(username)
            bot.delete_state(opponent_username)
            return
        else:
            bot.send_message(username, f"{round_number} раунд.\n\n"
                              f"{my_pokemon.name} не смог сбежать!")
            bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                              f"{my_pokemon.name} не смог сбежать!")
    elif int(message.text) == 5:
        if time.time() - my_pokemon.last_heal_time < COOLDOWN_TIME:
            remaining_time = COOLDOWN_TIME - (time.time() - my_pokemon.last_heal_time)
            minutes, seconds = divmod(int(remaining_time), 60)
            bot.send_message(username, f"{round_number} раунд.\n\n"
                              f"Подожди {minutes} минут {seconds} секунд, чтобы излечить покемона снова.")
            return
        else:
            if my_pokemon.heal():
                bot.send_message(username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} излечен!")
                bot.send_message(opponent_username, f"{round_number} раунд.\n\n"
                                  f"{my_pokemon.name} был излечен!")
        if username == current_turn:
            current_turn = opponent_username
            FIGHT_DATA[opponent_username]['round'] += 1
            send_fight_menu(current_turn, FIGHT_DATA[current_turn], FIGHT_DATA[current_turn]['round'])


@bot.message_handler(commands=['evolve'])
def evolve_command(message):
    if message.from_user.id in admin_ids:
        try:
            username, pokemon_index = message.text.split()[1:]
            pokemon_index = int(pokemon_index) - 1
            if username in trainers and 0 <= pokemon_index < len(trainers[username].pokemons):
                pokemon = trainers[username].pokemons[pokemon_index]
                if pokemon.evolve():
                    bot.send_message(message.chat.id, f"{pokemon.name} эволюционировал!")
                else:
                    bot.send_message(message.chat.id, f"{pokemon.name} уже эволюционировал!")
                return
            else:
                bot.send_message(message.chat.id, "Пользователь или покемон не найдены.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Неверный формат команды. Используйте /evolve @username [номер покемона]")
    else:
        bot.send_message(message.chat.id, "У вас нет прав на эту команду.")


@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'audio', 'video', 'document'])
def handle_default(message):
    try:
        if message.text.lower() == "/start":
            start(message)
        elif message.text.lower() == "/go":
            go(message)
        elif message.text.lower().startswith("/switch"):
            switch_pokemon(message)
        elif message.text.lower() == "/show":
            show_pokemons(message)
        elif message.text.lower() == "/heal":
            heal_pokemon(message)
        elif message.text.lower().startswith("/fight"):
            fight(message)
        elif message.text.lower().startswith("/evolve"):
            evolve_command(message)
        else:
            bot.send_message(message.chat.id,
                            "Неизвестная команда. Попробуйте /start, /go, /switch, /show, /heal, /fight, /evolve")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
