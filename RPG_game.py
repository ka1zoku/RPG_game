import json
import random
from datetime import datetime
from abc import ABC, abstractmethod
# КАРКАС ПРЕДМЕТА
class Item:
    
    def __init__(self, name, desc, weight, networth):
        self.name = name
        self.desc = desc
        self.weight = weight
        self.networth = networth

# ПРЕДМЕТЫ
# Оружие
class Weapon(Item):
    # В скобках пишем ВСЕ аргументы: и для родителя, и для себя
    def __init__(self, name, desc, weight, networth, damage):
        super().__init__(name, desc, weight, networth)
        self.damage = damage
# Броня
class Armor(Item):
    
    def __init__(self, name, desc, weight, networth, defence):
        super().__init__(name, desc, weight, networth)
        self.defence = defence
        

class PhysArmor(Armor):
    
    def __init__(self, name, desc, weight, networth, defence):
        super().__init__(name, desc, weight, networth, defence)
        self.armor = self.defence

# Зелья
class Potion(Item):
    
    def __init__(self, name, desc, weight, networth, amount):
        super().__init__(name, desc, weight, networth)
        self.heal_amount = amount
    
    def drink_potion(self, character):
        print(f'{character.name} выпивает {self.name} и восстанавливает себе {self.heal_amount}')
        

class HpPotion(Potion):
    
    def __init__(self, name, desc, weight, networth, amount):
        super().__init__(name, desc, weight, networth, amount)
    
    def drink_potion(self, character):
        Potionheal = self.heal_amount
        character.health = min(character.maxhealth, character.health + Potionheal)
        print(f"{character.name} использовал {self.name} и восстановил {self.heal_amount} ХП! Текущее ХП: {character.health}")

class ManaPotion(Potion):
    
    def __init__(self, name, desc, weight, networth, amount):
        super().__init__(name, desc, weight, networth, amount)
    
    def drink_potion(self, character):
        print(f"{character.name} использовал {self.name} и восстановил {self.heal_amount} Маны!")
        character.mana += self.heal_amount

#Аксессуары
class Accessories(Item):
    def __init__(self, name, desc, weight, networth, target_stat, bonus_stat):
        super().__init__(name, desc, weight, networth)
        self.target_stat = target_stat
        self.bonus_stat = bonus_stat
        
    def wear(self, character):
        current_bonus = getattr(character, self.target_stat)
        setattr(character, self.target_stat, current_bonus + self.bonus_stat)
        print(f'{character.name} надевает {self.name} и получает {self.bonus_stat} {self.target_stat}')
    
    def unequip(self, character):
        current_bonus = getattr(character, self.target_stat)
        setattr(character, self.target_stat, current_bonus - self.bonus_stat)
        print(f'{character.name} снимает {self.name} и теряет {self.bonus_stat} {self.target_stat}')
        
        # Если после снятия кольца текущее здоровье стало больше нового максимума - срезаем
        if self.target_stat == 'maxhealth' and character.health > character.maxhealth:
            character.health = character.maxhealth
        if self.target_stat == 'mana':
            character.mana = 20
#ИГРОВЫЕ ЭФФЕКТЫ
class Effect:
    
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        
    
    def apply(self, character):
        pass
    
    def tick(self, character):
        pass
    
    def remove(self, character):
        pass


class StatBuff(Effect):
    
    def __init__(self, name, duration, target_stat, bonus_value):
        super().__init__(name, duration)
        self.target_stat = target_stat
        self.bonus_value = bonus_value
    
    def apply(self, character):
        current_val = getattr(character, self.target_stat)
        setattr(character, self.target_stat, current_val + self.bonus_value)
    
    def remove(self, character):
        current_val = getattr(character, self.target_stat)
        setattr(character, self.target_stat, current_val - self.bonus_value)

class StatDebuff(Effect):
    
    def __init__(self, name, duration, debuff_effect, debuff_amount):
        super().__init__(name, duration)
        self.debuff_effect = debuff_effect
        self.debuff_amount = debuff_amount
    
    def apply(self, character):
        statdebuff = getattr(character, self.debuff_effect, None)
        if statdebuff:
            setattr(character, self.debuff_effect, statdebuff - self.debuff_amount)
        else:
            pass
    
    def remove(self, character):
        statdebuff = getattr(character, self.debuff_effect, None)
        if statdebuff:
            setattr(character, self.debuff_effect, statdebuff + self.debuff_amount)
        else:
            pass

class PoisonDebuff(Effect):
    
    def __init__(self, name, duration, amount):
        super().__init__(name, duration)
        self.amount = amount
    
    def tick(self, character):
        character.health -= self.amount
        print(f"{character.name} получает {self.amount:.1f} урона от яда [{self.name}]!")
        
            
# КАРКАС ПЕРСОНАЖА
class Character:
    
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.weight = 40
        self.maxhealth = 30
        self.health = 30
        self.mana = 20
        # Оставляем ЦЕЛЫЕ числа для MOBA-брони
        self.armor = 10 # 10%
        self.magicres = 15 # 15%
        # А шанс крита (вероятность) круто хранить в дробях
        self.critchance = 0.10 # 10%
        self.active_effects = []
    
    def attack(self, weapon, target):
        # 1. Берем базовый урон оружия во временную переменную
        actual_damage = weapon.damage
        
        # Настоящая MOBA-формула с целыми числами
        actual_damage = actual_damage * (100 / (100 + target.armor))
        
        # 2. Проверка на крит (используем <=, чтобы 10% были честными 1-10)
        
        # Правильная проверка шанса через random.random()
        if random.random() <= self.critchance:
            actual_damage *= 2
            # Слегка округлим урон, чтобы не писать 14.285714...
            print(f'{self.name} атакует {target.name} используя {weapon.name} КРИТОМ нанося {actual_damage:.1f} урона')
        else:
            print(f'{self.name} атакует {target.name} используя {weapon.name} нанося {actual_damage:.1f} урона')
        
        # 3. Наносим урон (сохраняем результат!)
        target.health -= actual_damage
        
        # Проверяем, выжил ли враг
        if not target.is_alive():
            print(f'{target.name} погиб!')
    
    def add_effect(self, effect):
        self.active_effects.append(effect)
        effect.apply(self)
        print(f'На {self.name} наложен эффект {effect.name} на {effect.duration} ходов')
    
    def update_effects(self):
        for effect in self.active_effects:
            effect.tick(self)
            effect.duration -= 1

            if effect.duration <= 0:
                effect.remove(self)
                self.active_effects.remove(effect)
                print(f'{effect.name} спал с {self.name}')
        
    
    def is_alive(self):
        # Метод просто возвращает True (если хп > 0) или False (если <= 0)
        return self.health > 0

# КАРКАС ИГРОКА (Теперь он официально Абстрактный)
class Player(Character, ABC):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.inventory = [] # Инвентарь лучше делать списком (list), чтобы хранить объекты Item
        self.gold = 0
        self.x = 4
        self.y = 4
        
    @abstractmethod
    def First_Spell(self, target):
        pass
    
    @abstractmethod
    def Second_Spell(self, target):
        pass
    
    @abstractmethod
    def Third_Spell(self, target):
        pass

# Игровые классы        
class Warrior(Player):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.maxhealth = 120
        self.health = 120
        self.mana = 15 
        self.weapon = Weapon('Меч воина', 'Обычный стальной меч, ничего необычного', 5, 5 ,7)
        self.itemarmor = PhysArmor('Кольчуга воина', 'Обычная кольчуга', 4, 5, 10)
        self.accessory = Accessories("Обычное кольцо", "-", 5, 10, "maxhealth", 5)
        self.armor = self.itemarmor.defence
        
    def First_Spell(self, target): # Серия ударов, воин атакует врага двумя ударами которые имеют пониженный урон на 15%, но имеют повышенный шанс крита (на 20%)
        
        if self.mana < 10:
            print(f'У {self.name} недостаточно маны для тройного удара!')
            return
        
        # Отнимаем ману за спелл
        self.mana -= 10
        
        print(f'{self.name} использует двойную атаку!')
        # Повышаем шанс крит урона для спелла
        spell_critchance = self.critchance + 0.15
        
        # Цикл выполнится ровно 2 раза (Вместо range (1, 2))
        for _ in range(2):
            # Считаем базовый урон ЗАНОВО для каждого удара! (минус 20%)
            spell_damage = self.weapon.damage * 0.90 
            spell_damage = spell_damage * (100 / (100 + target.armor))
            
            if random.random() <= spell_critchance:
                spell_damage *= 2
                print(f'{self.name} атакует {target.name} КРИТОМ нанося {spell_damage:.1f}')
            else:
                print(f'{self.name} атакует {target.name} нанося {spell_damage:.1f}')
            
            # Отнимаем ХП врагу в любом случае (и при крите, и без него)
            target.health -= spell_damage
            
            # Проверяем, умер ли враг от ЭТОГО удара
            if not target.is_alive():
                print(f'{target.name} погиб!')
            
    def Second_Spell(self, target):
        
        if self.mana < 5:
            print(f"У {self.name} недостаточно маны на Точный удар!")
            return
        
        self.mana -= 5
        print(f'{self.name} использует Точный удар!')
        
        spell_damage = self.weapon.damage
        
        if random.random() <= self.critchance:
            spell_damage *= 2
            prefix = "КРИТОМ"
        else: 
            prefix = None
        
        print(f'{self.name} атакует {target.name} {prefix} нанося {spell_damage:.1f}')
        target.health -= spell_damage
        
        if not target.is_alive():
            print(f'{target.name} погиб!')
        
    def Third_Spell(self, target=None): # Получает доп. броню на 2 хода
        
        if self.mana < 15:
            print(f"У {self.name} недостаточно маны на повышение брони!")
            return
        
        self.mana -= 15
        armor_protection = StatBuff("Защита брони", 3, "armor", 40)
        self.add_effect(armor_protection)
        
        print(f"{self.name} использует повышение брони!")
        
        
        
class Mage(Player):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.maxhealth = 90
        self.health = 90
        self.mana = 30
        self.weapon = Weapon('Посох', 'Обычная магическая палочка', 5, 10, 6)
        self.itemarmor = PhysArmor('Накидка мага', "Обычная накидка", 5, 10, 4)
        self.accessory = Accessories("Обычное кольцо", "-", 5, 10, "maxhealth", 5)
        self.armor = self.itemarmor.defence
    
    def First_Spell(self, target): # Огненный шар, урон зависит от оружия * 2, игнорирует магическую броню врага.
        
        if self.mana < 15:
            print(f'У {self.name} недостаточно маны для огненного шара!')
            return
        
        self.mana -= 15
        
        print(f'{self.name} использует огненный шар!')
        spell_damage = self.weapon.damage * 2
        
        if random.random() <= self.critchance:
            spell_damage *= 2
            print(f'{self.name} атакует {target.name} Огненным шаром с КРИТОМ нанося {spell_damage:.1f}')
        else:
            print(f'{self.name} атакует {target.name} Огненным шаром нанося {spell_damage:.1f}')
        
        target.health -= spell_damage
        
        # Проверяем, умер ли враг от ЭТОГО удара
        if not target.is_alive():
            print(f'{target.name} погиб!')
        
    
    def Second_Spell(self, target): # Грозовой шквал, наносит трижды урон врагу молниями, которые имеют больше шанс на крит урон, но меньше урона
        
        if self.mana < 20:
            print(f'У {self.name} недостаточно маны для Грозового шквала!')
            return
        
        # Отнимаем ману за спелл
        self.mana -= 20
        
        print(f'{self.name} использует грозовой шквал!')
        
        spell_critchance = self.critchance + 0.25
        for _ in range(3):
            spell_damage = self.weapon.damage * 0.80 
            spell_damage = spell_damage * (100 / (100 + target.magicres))
            
            if random.random() <= spell_critchance:
                spell_damage *= 2
                print(f'{self.name} атакует {target.name} Грозовой атакой КРИТОМ нанося {spell_damage:.1f}')
            else:
                print(f'{self.name} атакует {target.name} Грозовой атакой нанося {spell_damage:.1f}')
            
        # Отнимаем ХП врагу в любом случае (и при крите, и без него)
            target.health -= spell_damage
            
            if not target.is_alive():
                print(f'{target.name} погиб!')
                break
        
    
    def Third_Spell(self, target=None): # Лечение, маг лечит себя на 30% за счёт маны
        if self.mana < 25:
            print(f"У {self.name} недостаточно маны для Лечения!")
            return
        
        self.mana -= 25
        
        print(f'{self.name} излечивает себя, используя заклинание!')
        
        heal = self.maxhealth * 0.3
        # 4. Лечимся, но не превышаем maxhealth
        self.health = min(self.maxhealth, self.health + heal)
        
        print(f"Здоровье восстановлено! Текущее ХП: {self.health:.1f}/{self.maxhealth}")
        
class Assassin(Player):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.maxhealth = 95
        self.health = 95
        self.mana = 20
        self.weapon = Weapon('Кинжал', 'Обычный кинжал', 4, 5, 7)
        self.critchance = 0.25
        self.itemarmor = PhysArmor("Накидка", "Обычная накидка", 5, 10, 5)
        self.accessory = Accessories("Обычное кольцо", "-", 5, 10, "maxhealth", 5)
        self.armor = self.itemarmor.defence
    
    def attack(self, weapon, target):
        
        actual_damage = weapon.damage
        spell_critchance = self.critchance
        actual_damage = actual_damage * (100 / (100 + target.armor))
        
        has_mark = any(eff.name == "Метка преследования" for eff in target.active_effects)
        if has_mark:
            spell_critchance += 0.40
        
        if random.random() <= spell_critchance:
            actual_damage *= 2
            # Слегка округлим урон, чтобы не писать 14.285714...
            print(f'{self.name} атакует {target.name} используя{weapon.name} КРИТОМ нанося {actual_damage:.1f}')
        else:
            print(f'{self.name} атакует {target.name} {weapon.name} нанося {actual_damage:.1f}')
        
        # 3. Наносим урон (сохраняем результат!)
        target.health -= actual_damage
        
        # Проверяем, выжил ли враг
        if not target.is_alive():
            print(f'{target.name} погиб!')
    
    
    def First_Spell(self, target): # Фокусированный удар, ассассин атакует врага своим оружием с сильно повышенным шансом на критический урон (на 50%), в случае 100% критического шанса Ассасин имеет шанс СУПЕР-крита, наносящего в два с половиной больше урона
        
        if self.mana < 5:
            print(f'У {self.name} нет маны на фокусированный удар!')
            return
        
        self.mana -= 5
        
        spell_damage = self.weapon.damage
        spell_damage = spell_damage * (100 / (100 + target.armor))
        
        spell_critchance = self.critchance + 0.50
        
        has_mark = any(eff.name == "Метка преследования" for eff in target.active_effects)
        if has_mark:
            spell_critchance += 0.40
        
        if spell_critchance > 1:
            megacrit_chance = spell_critchance - 1
            if random.random() <= megacrit_chance:
                spell_damage *= 3
                prefix = 'МЕГАКРИТОМ'
            else:
                spell_damage *= 2
                prefix = 'ГАРАНТ КРИТОМ'
        
        else:
            if random.random() <= spell_critchance:
                spell_damage *= 2
                prefix = 'КРИТОМ'
            else:
                prefix = 'обычной атакой'
        
        print(f'{self.name} атакует Фокусированным ударом {target.name} с {prefix} нанося {spell_damage:.1f}')
        
        target.health -= spell_damage
        
        if not target.is_alive():
            print(f'{target.name} был повержен!')
        
    
    def Second_Spell(self, target):
        
        if self.mana < 10:
            print(f'У {self.name} нет маны на Метку!')
            return
        
        precision_mark = StatDebuff("Метка преследования", 5, "None", "None")
        
        target.add_effect(precision_mark)
        
        print(f"{self.name} использует на {target.name} Метку преследования на {precision_mark.duration} хода!")
        
        self.mana -= 10
    
    def Third_Spell(self, target):
        
        if self.mana < 15:
            print(f'У {self.name} недостаточно маны на Ядовитый кинжал!')
            return
        
        print(f"{self.name} использует на {target.name} Ядовитый дротик!")
        
        poison_dagger = PoisonDebuff("Ядовитый дротик", 4, self.weapon.damage * 0.4)
        target.add_effect(poison_dagger)
        
        

# КАРКАС ВРАГА
class Enemy(Character):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.maxhealth = self.health
        self.bounty = 0
        self.enemyinv = [] # Инвентарь лучше делать списком (list), чтобы хранить объекты Item
        self.damage = 0
    
    def attack(self, target):

        actual_damage = self.damage
        
        actual_damage = actual_damage * (100 / (100 + target.armor))
        
        if random.random() <= self.critchance:
            actual_damage *= 2
            print(f'{self.name} атакует {target.name} КРИТОМ нанося {actual_damage:.1f}')
        else:
            print(f'{self.name} атакует {target.name} нанося {actual_damage:.1f}')
        
        target.health -= actual_damage
        
        if not target.is_alive():
            print(f'{target.name} погиб!')
    
        
# Функция рандомайзера
def rand(num1, num2):
    return random.randint(num1, num2)


# Типы врагов
class Goblin(Enemy):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.health = rand(10, 15)
        self.armor = rand(10, 20)
        self.magicres = rand(10, 25)
        self.damage = rand(3, 6)
        self.bounty = rand(10, 15)    

class Bandit(Enemy):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.health = rand(15, 20)
        self.armor = rand(15, 20)
        self.magicres = rand(10, 20)
        self.damage = rand(4, 7)
        self.bounty = rand(10, 20)

class Ogre(Enemy):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.health = rand(15, 25)
        self.armor = rand(20, 30)
        self.magicres = rand(15, 25)
        self.damage = rand(7, 12)
        self.bounty = rand(15, 25)

class Shadow(Enemy):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.health = rand(25, 30)
        self.armor = rand(20, 30)
        self.magicres = rand(25, 30)
        self.damage = rand(10, 14)
        self.bounty = rand(20, 30)
        
class Wizard(Enemy):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.health = rand(30, 40)
        self.armor = rand(10, 20)
        self.magicres = rand(30, 60)
        self.damage = rand(12, 16)
        self.bounty = rand(25, 35)

class MiniBoss(Enemy):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.health = rand(75, 125)
        self.armor = rand(40, 70)
        self.magicres = rand(40, 70)
        self.damage = rand(20, 25)
        self.bounty = rand(60, 90)
        
class FinalBoss(Enemy):
    
    def __init__(self, name, desc):
        super().__init__(name, desc)
        self.health = rand(250, 300)
        self.armor = rand(60, 100)
        self.magicres = rand(70, 100)
        self.damage = rand(35, 45)
        self.bounty = 1000
        
# Каркас сражения
class Battle:
    
    def __init__(self, player, enemy, worlditems):
        self.player = player
        self.enemy = enemy
        self.worlditems = worlditems
        self.is_flee = False
        self.rounds = 1
    
    
    def Fight(self):
        print(f"Тебя атакует {self.enemy.name}!")
        
        # Правильное условие (оба должны быть живы)
        while self.player.is_alive() and self.enemy.is_alive():
            
            print(f'    Раунд {self.rounds}')
            print(f'Твоё ХП: {self.player.health:.1f} | Мана: {self.player.mana}')
            print(f'ХП Врага: {self.enemy.health:.1f}')
            
            action_taken = self.player_choice()
            
            if self.is_flee:
                print(f'{self.player.name} позорно сбежал от {self.enemy.name}!')
                break 
            
            if action_taken == False:
                continue
            
            self.player.update_effects()
            self.enemy.update_effects()
            self.rounds += 1
            
            if not self.enemy.is_alive():
                self.victory()
                
                if random.random() <= 0.30: 
                    loot = random.choice(self.worlditems)
                    print(f'Выпал лут: {loot.name}!')
                    self.player.inventory.append(loot)
                
                break
            
            print('Ход врага!')
            self.enemy.attack(self.player)

            if not self.player.is_alive():
                self.lose(self.player)
                break
    
    def player_choice(self):
        while True:
            turn = input("""
            1. Атаковать
            2. Использовать заклинание
            3. Выпить зелье
            4. Проверить характеристики врага
            5. Проверить свои характеристики
            6. Попытаться сбежать (45%)             
            
            Твой выбор: """)
            match turn:
                case '1':
                    self.player.attack(self.player.weapon, self.enemy)
                    return True
                
                case '2':
                    return self.use_spell()
                
                case '3':
                    return self.use_potion()
                
                case '4':
                    self.check_stats(self.enemy)
                    return False
                
                case '5':
                    self.check_selfstats(self.player)
                    return False
                
                case '6':
                    return self.flee()
                
                case _:
                    print('Неверный выбор!')
                
    def use_potion(self):
        potions = [item for item in self.player.inventory if isinstance(item, Potion)]
        
        if not potions:
            print('У тебя нет зелий!')
            return False

        for i, item in enumerate(potions, 1):
            print(f"{i}. {item.name}, {item.heal_amount}")
        
        while True:
            try:
                player_choice = int(input('Какое зелье ты хочешь выпить? (по номеру) (0 для отмены)'))
                if player_choice == 0:
                    return False
                
                idx = player_choice - 1
                
                if -1 <= idx < len(potions):
                    potion = potions[idx]
                    potion.drink_potion(self.player)
                    self.player.inventory.remove(potion)
                    return True
                else:
                    print('Неверный номер!')
        
            except ValueError:
                print('Неверный ввод!')

        
    def use_spell(self):
        spell_choice = input('Какое по числу заклинание ты будешь использовать (1, 2 ,3) (0 если передумал)?: ')
        match spell_choice:
            case '1':
                self.player.First_Spell(self.enemy)
            case '2':
                self.player.Second_Spell(self.enemy)
            case '3':
                self.player.Third_Spell(self.enemy)
            case '0':
                return False
            case _:
                print('А всё! Циферку написать не смог - ход потерял!')
        
        return True
    
        
    def check_stats(self, enemy):
        print(f"""
            Характеристики врага
        Здоровье = {enemy.health:.1f}
        Броня = {enemy.armor}
        Урон = {enemy.damage}
        Награда = {enemy.bounty}""")
        print("        Активные эффекты = ")
        for eff in enemy.active_effects:
            print(f'       {eff.name}, Осталось: {eff.duration} ходов\n')
    
    def flee(self):
        flee_chance = 0.45
        if random.random() <= flee_chance:
            self.is_flee = True
            # 1. Возвращаем врагу полное здоровье
            self.enemy.health = self.enemy.maxhealth
            # 2. Очищаем все яды и дебаффы
            self.enemy.active_effects.clear()
            return True
        else:
            print(f'Тебе не удалось сбежать! {self.enemy.name} делает удар!')
            return True
    
    def check_selfstats(self, player):
        print(F"""
            Твои характеристики
        Здоровье = {player.health:.1f}
        Мана = {player.mana}
        Броня = {player.armor}
        Урон = {player.weapon.damage}""")
        print("        Активные эффекты = ")
        for eff in player.active_effects:
            print(f'       {eff.name}, Осталось: {eff.duration} ходов\n')
    
    def victory(self):
        print(f'Ты победил {self.enemy.name}! Ты получил {self.enemy.bounty} золота!')
        self.player.gold += self.enemy.bounty
        
    def lose(self, character):
        print(f'{self.enemy.name} победил тебя! Да ты лох!')
        print(f'Ты оказался на 4, 4 и потерял {character.gold // 2} золота')
        character.gold //= 2
        character.health = character.maxhealth // 2
        character.x = 4
        character.y = 4
        # 1. Возвращаем врагу полное здоровье
        self.enemy.health = self.enemy.maxhealth
        # 2. Очищаем все яды и дебаффы
        self.enemy.active_effects.clear()
        
class GameDatabase:
        
    def __init__(self):
        self.weapons = []
        self.manapotions = []
        self.healthpotions = []
        self.accessories = []
        self.physarmor = []
        
        self.load_game()
    
    def load_game(self):
        with open ('rpgdata.json', 'r', encoding='utf-8') as file:
            items = json.load(file)
        
        # Перебираем словарь: category - это ключ ("Weapon"), items_list - список предметов
        for category, items_list in items.items():
            
            # Перебираем каждый предмет внутри категории
            for item in items_list:
                
                match category:
                    # Создаем объект Weapon, распаковывая словарь через **
                    case "Weapon":
                        new_item = Weapon(**item)
                        self.weapons.append(new_item)
                        
                    case "ManaPotion":
                        new_item = ManaPotion(**item)
                        self.manapotions.append(new_item)
                        
                    case "HpPotion":
                        new_item = HpPotion(**item)
                        self.healthpotions.append(new_item)
                    
                    case "Accessories":
                        new_item = Accessories(**item)
                        self.accessories.append(new_item)
                    
                    case "PhysArmor":
                        new_item = PhysArmor(**item)
                        self.physarmor.append(new_item)
                        
    
    def load_map(self):
        with open ("rpgmap.json", 'r', encoding='utf-8') as file:
            map = json.load(file)
            worldmap = {}
        
        for coords, location in map.items():
            locenemy = location["enemy_type"]
            enemy = self.create_enemy_by_name(locenemy)
            match location["type"]:
                case "Forest":
                    new_loc = Forest(location["name"], location["desc"], enemy)
                    worldmap[coords] = new_loc
                case "Camp":
                    new_loc = Camp(location["name"], location["desc"], enemy)
                    worldmap[coords] = new_loc
                case "Shop":
                    if location["name"] == "Алхимическая Лавка 'Ведьмин Корень'":
                        items = self.get_alchemistry_items()
                    elif location["name"] == "Кузница 'Стальной Клык'":
                        items = self.get_weaponry_items()
                    else:
                        items = self.get_all_items()
                    new_loc = Shop(location["name"], location["desc"], items, None)
                    worldmap[coords] = new_loc
                case "Castle":
                    new_loc = Castle(location["name"], location["desc"], enemy)
                    worldmap[coords] = new_loc
                case "Town":
                    new_loc = Town(location["name"], location["desc"], None)
                    worldmap[coords] = new_loc
        return worldmap
    def create_enemy_by_name(self, enemy_type_string):
        # Словарь сопоставляет строку из JSON с созданием реального объекта
        spawners = {
            "Goblin": lambda: Goblin("Гоблин-разведчик", "Мерзкий и зеленый"),
            "Bandit": lambda: Bandit("Головорез", "Хочет забрать твое золото"),
            "Ogre": lambda: Ogre("Свирепый Огр", "Огромная гора мышц"),
            "Shadow": lambda: Shadow("Ассасин Культа", "Прячется в тенях"), # Имя исправлено!
            "Wizard": lambda: Wizard("Темный Маг", "Бормочет проклятия"),
            "MiniBoss": lambda: MiniBoss("Страж Цитадели", "Его броня непробиваема"),
            "FinalBoss": lambda: FinalBoss("Лорд Тьмы", "Воплощение чистого зла"),
            "None": lambda: None # Для безопасных зон
        }
        
        # Достаем нужную функцию и вызываем её ()
        spawn_function = spawners.get(enemy_type_string, lambda: None)
        return spawn_function()
    
    def get_alchemistry_items(self):
        # Оператор + умеет склеивать списки Питона вместе
        items =(self.healthpotions + 
                self.manapotions + 
                self.accessories)
        return items
    
    def get_weaponry_items(self):
        items = (self.weapons + 
                 self.physarmor +
                 self.accessories)
        return items
    
    def get_all_items(self):
        all_items = (self.weapons +
                     self.physarmor +
                     self.accessories +
                     self.healthpotions +
                     self.manapotions)
        return all_items

#Каркас клетки локации
class Location:
    
    def __init__(self, name, desc, enemy):
        self.name = name
        self.desc = desc
        self.items = GameDatabase()
        self.worlditems = self.items.get_all_items()
        if random.random() <= 0.10:
            self.enemy = Shadow("Наёмный убийца", "-")
        else:
            self.enemy = enemy
    
    def has_enemy(self):
        if random.random()<= 0.40:
            return True
        else:
            self.enemy = None
            return False
    
    def has_item(self):
        if random.random() <= 0.50:
            self.items = random.choice(self.worlditems)
            return True
        else:
            return False

class Camp(Location):
    
    def __init__(self, name, desc, enemy):
        super().__init__(name, desc, enemy)
        
class Forest(Location):
    
    def __init__(self, name, desc, enemy):
        super().__init__(name, desc, enemy)

class Cave(Location):
    
    def __init__(self, name, desc, enemy):
        super().__init__(name, desc, enemy)

class Castle(Location):
    
    def __init__(self, name, desc, enemy):
        super().__init__(name, desc, enemy)

class Town(Location):
    
    def __init__(self, name, desc, enemy=None):
        super().__init__(name, desc, enemy)

class Shop(Location):
    
    def __init__(self, name, desc, items_list, character, enemy=None):
        super().__init__(name, desc, enemy)
        self.inventory = items_list
        self.character = character
        
    
    def main_menu(self):
        self.items = []
        print(f"Добро пожаловать в {self.name}! Вот наши предметы: ")
        for i, item in enumerate(self.inventory, 1):
                        
            print(f'{i}: {item.name} | {item.desc} | Цена: {item.networth} | Вес: {item.weight}')
            
            if isinstance(item, HpPotion):
                print(f"  Лечение: {item.heal_amount} ХП\n")
            elif isinstance(item, ManaPotion):
                print(f"  Восстановление: {item.heal_amount} Маны\n")
            elif isinstance(item, Weapon):
                print(f'  Урон: {item.damage}\n')
            elif isinstance(item, PhysArmor):
                print(f'  Физ. защита: {item.armor}\n')
            elif isinstance(item, Accessories):
                print(f'  Бонус: [{item.target_stat}]: +{item.bonus_stat}\n')
            
            self.items.append(item)
        
        while True:
            player_choice = input(f"Что ты хочешь сделать? (У тебя {self.character.gold} золота (1 - Купить предмет, 2. Продать предмет, Уйти =  0)")
            match player_choice:
                case "1": self.sell_item(self.character)
                case "2": self.buy_item(self.character)
                case "0":
                    return
                case _:
                    print("Неверный выбор!")
    
    def sell_item(self, character):
        while True:
            try:
                choice = int(input('Что ты хочешь купить? (по номеру) (0 для отмены)'))
                if choice == 0: 
                    return
                
                idx = choice - 1
                
                if idx < 0 or idx >= len(self.items):
                    print('Такого номера в списке нет!')
                    continue
                
                item = self.items[idx]
                
                if character.gold < item.networth:
                    print('У тебя нехватает денег!')
                    continue
                
                print(f"Поздравляю! Ты купил {item.name} за {item.networth}! {item.name} был добавлен в твой инвентарь!")
                character.gold -= item.networth
                character.inventory.append(item)
                break
                
            except ValueError:  
                print("Неверный ввод!")
    
    def buy_item(self, character):
        if not character.inventory:
            print('У тебя ничего нет!')
            return
        
        while True:
            for i, item in enumerate(character.inventory, 1):
                print(f'{i}: {item.name} | Стоимость: {item.networth}')
            
            try:
                choice = int(input("Что ты хочешь продать? (0 для отмены)"))
                if choice == 0:
                    return
                
                idx = choice - 1
                
                if 0 <= idx <= len(character.inventory):
                    item_to_sell = character.inventory[idx]
                    character.gold += item_to_sell.networth
                    character.inventory.remove(item_to_sell)
                    print(f"Ты успешно продал {item_to_sell.name}, получив {item_to_sell.networth} золота!")
                    return
                else:
                    print("Неверный номер!")
            except ValueError:
                print('Неверный ввод!')

class Game:
    
    def __init__(self, character):
        self.character = character
        self.database = GameDatabase()
        self.worldmap = self.database.load_map()
        self.worlditems = self.database.get_all_items()
        self.victory = False
    
    def main_menu(self):
        while self.victory == False:
            player_choice = input(f"""
                Меню твоего персонажа {self.character.name}
                Ты находишься на x: {self.character.x} , y: {self.character.y}
                Что будешь делать?
                
            1. Идти
            2. Проверить характеристики
            3. Посмотреть инвентарь
            4. Экипировать предмет
            5. Выпить зелье
            6. Посмотреть скиллы
            7. Выход (сохраниться)
            """)
            match player_choice:
                case "1": self.move()
                case "2": self.Check_Stats()
                case "3": self.Check_Inventory()
                case "4": self.equip_item()
                case "5": self.Drink_Potion()
                case "6": self.Check_Skills() 
                case "7":
                    self.save_game()
                    break
                case _: 
                    print("Неверный ввод")
                    continue
    
    def move(self):
        while True:
            player_choice = input(f"""
                Текущее место положение: x: {self.character.x} , y: {self.character.y}
                В каком направлении ты пойдёшь?        
            1. Впёред   (y + 1)
            2. Назад    (y - 1)
            3. Налево   (x - 1)
            4. Направо  (x + 1)
            5. Отмена
            """)
            match player_choice:
                case "1":
                    self.character.y += 1
                case "2":
                    self.character.y -= 1
                case "3":
                    self.character.x -= 1
                case "4":
                    self.character.x += 1
                case "5":
                    break
                case _:
                    print("Неверный ввод")

            if self.character.x < 0 or self.character.x > 7 or self.character.y < 0 or self.character.y > 7:
                print("Дальше пути нет, конец мира!")
                match player_choice:
                    case "1":
                        self.character.y -= 1
                    case "2":
                        self.character.y += 1
                    case "3":
                        self.character.x += 1
                    case "4":
                        self.character.x -= 1
                continue
            
            coords = f"{self.character.x},{self.character.y}"
            
            if coords in self.worldmap:
                loc = self.worldmap[coords] 
                
                
                if isinstance(loc, Shop):
                    loc.character = self.character
                    print("Здесь расположился магазин. Хочешь зайти?")
                    print(loc.name)
                    print(loc.desc)
                    if input("1 = Да, для Нет просто Enter") == "1":
                        loc.main_menu()    
                
                elif isinstance(loc, Town):
                    print(" Ты отдыхаешь у костра. Здоровье и мана восстановлены!")
                    self.character.health = self.character.maxhealth
                    self.character.mana = 20 
                        
            else:
                goblin = Goblin("Гоблин-разведчик", "Мерзкий и зеленый")
                loc = Forest("Лес", "Обычный лес, листья шелестят.", goblin)

            
            print(f""" 
                Ты находишься на {self.character.x}, {self.character.y}. 
            {loc.name}
            {loc.desc} 
                """)
            
            # ИСПРАВЛЕНО: Сначала проверяем, есть ли враг, а уже потом - жив ли он
            if loc.enemy and not loc.enemy.is_alive():
                loc.enemy = None
            
            if loc.enemy:
                print(f"Тут оказался {loc.enemy.name}! ")
                Battle(self.character, loc.enemy, self.worlditems).Fight()
                
                if not self.character.is_alive():
                    break
                
                if loc.enemy.name == "Лорд Тьмы" and not loc.enemy.is_alive():
                    print("УРА! Ты убил финального босса! Ты выиграл!")
                    self.victory = True
                
                # СОВЕТ: Можно убрать труп сразу после победы, чтобы он не лежал до следующего захода!
                if not loc.enemy.is_alive():
                    loc.enemy = None
            
            elif loc.has_item():
                print(f"Ты нашёл {loc.items.name}")
                self.character.inventory.append(loc.items)
                loc.items = None
            
            else:
                print("Тут ничего не оказалось")

            break
    
    def Check_Stats(self):
        print(f"""
        Имя: {self.character.name}
        Биография: {self.character.desc}
        Золото: {self.character.gold}
        Оружие: {self.character.weapon.name} | {self.character.weapon.desc} | 
            Урон : {self.character.weapon.damage} | Стоимость: {self.character.weapon.networth}
        Броня: {self.character.itemarmor.name} | {self.character.itemarmor.desc} |
            Стоимость: {self.character.itemarmor.networth} | Защита: {self.character.itemarmor.defence}
        Аксессуар: {self.character.accessory.name} | {self.character.accessory.desc} |
            Бонус: {self.character.accessory.target_stat} | Кол-во: {self.character.accessory.bonus_stat}
        Макс. ХП: {self.character.maxhealth}
        Здоровье: {self.character.health:.1f}
        Мана: {self.character.mana}
        Физ. защита: {self.character.armor}
        Крит. шанс: {self.character.critchance}
        """)
    
    def Check_Inventory(self):
        if self.character.inventory:
            print('Вот твой инвентарь:')
            for i, inv in enumerate(self.character.inventory, 1):
                print(f'{i}: {inv.name} | {inv.desc}')
        else:
            print('Твой инвентарь пуст!')
    
    def Check_Skills(self):
        match type(self.character).__name__:
            case "Warrior":
                print("""
                    Воин: Имеет повышенную броню и здоровье, но взамен имеет маленький запас маны. 
                    Его навыки направлены на быстрые удары оружием и повышением брони.
    
                    ПЕРВЫЙ НАВЫК: Двойной удар. Атакует врага дважды с повышенным шансом крита на 15% но имеют пониженный урон на 10%. Стоимость: 10
                    ВТОРОЙ НАВЫК: Точный удар. Атакует врага игнорируя броню врага. Стоимость: 5
                    ТРЕТИЙ НАВЫК: Повышение брони. Повышает свою броню на 40 на 2 хода. Стоимость: 15
                    """)
            case "Mage":
                print("""
                    Маг: Имеет повышенную ману, жертвуя здоровьем. 
                    Его заклинания наносят большой урон врагу и может себя излежить.
                        
                    ПЕРВЫЙ НАВЫК: Огненный шар. Атакует врага с двойным уроном игнорируя магическую защиту врага. Стоимость: 15
                    ВТОРОЙ НАВЫК: Грозовой шквал. Атакует врага трижды с повышенным крит шансом на 25% но с пониженным уроном на 20%. Стоимость: 20
                    ТРЕТИЙ НАВЫК: Лечение. Лечит себя на 30% максимального хп. Стоимость: 25
                    """)
            case "Assassin":
                print("""
                    Ассассин: Имеет повышенный шанс крит атаки и ману но жертвует небольшим количеством здоровья.
                    Его заклинания завязаны на механике критов и уникальной механиков МЕГАКРИТА (урон повышен в три раза вместо два)
                    
                    ПЕРВЫЙ НАВЫК: Фокусированный удар. Атакует врага своим оружием с сильно повышенным шансом на критический урон (на 50%), 
                    в случае 100% критического шанса Ассасин имеет шанс МЕГАКРИТА (необходимо 200% для гарантированного мегакрита). Стоимость: 5
                    ВТОРОЙ НАВЫК: Метка точности. Вешает метку на врага на 3 хода, которая увеличивает крит шанс по нему на 40%. Стоимость: 10
                    ТРЕТИЙ НАВЫК: Ядовитый кинжал. Ударяет врага ядом, от чего получает (урон от оружия * 0.4) урона ядом следующие 4 хода. Стоимость: 15
                    """)
                        
    def Drink_Potion(self):
        potion = [item for item in self.character.inventory if isinstance(item, Potion)]
        if not potion:
            print("У тебя нет зелий!")
            return
        
        for i, inv in enumerate(potion, 1):
            print(f'{i}: {inv.name} | {inv.desc} | Стоимость: {inv.networth}')
        while True:
            try:
                choice = int(input("Что ты выпьешь? (по номеру, 0 для отмены)"))
                if choice == 0:
                    return
                
                idx = choice - 1
                if 0 <= idx <= len(potion):
                    drink_item = potion[idx]
                    drink_item.drink_potion(self.character)
                    self.character.inventory.remove(drink_item)
                    return
                
            except ValueError:
                print("Неверный ввод!")
    
    def equip_item(self):
        while True:
            usdata = input("Что ты хочешь одеть? (0 для отмены) 1. Оружие, 2. Броня, 3. Аксессуар: ")
            if usdata == '0':
                return
            elif '0' < usdata < '4':
                items = []
                match usdata:
                    case "1":
                        itemprefix = "Оружий"
                        for weapon in self.character.inventory:
                            if isinstance(weapon, Weapon):
                                items.append(weapon)
                        
                        for i, weapon in enumerate(items, 1):
                            print(f'{i}, Имя: {weapon.name} | Описание: {weapon.desc} | Урон: {weapon.damage} | Стоимость: {weapon.networth}')

                    case "2":
                        itemprefix = "Брони"
                        for armor in self.character.inventory:
                            if isinstance(armor, PhysArmor):
                                items.append(armor)
                        
                        for i, armor in enumerate(items, 1):
                            print(f"{i}: Имя: {armor.name} | Описание: {armor.desc} | Физ. защита: {armor.defence}")
                    
                    case "3":
                        itemprefix = "Аксессуаров"
                        for accs in self.character.inventory:
                            if isinstance(accs, Accessories):
                                items.append(accs)
                        
                        for i, accs in enumerate(items, 1):
                            print(f"{i}: Имя: {accs.name} | Описание: {accs.desc} | Бафф: {accs.target_stat} | Количество: {accs.bonus_stat} ")
                
                if not items:
                    print(f"У тебя нет {itemprefix}!")
                    return
                
                while True:
                    try:
                        choice = int((input("Какой предмет ты будешь экипировать? (по номеру, 0 для отмены): ")))
                        if choice == 0:
                            return
                        
                        idx = choice - 1
                        
                        if 0 <= idx <= len(items):
                            new_item = items[idx]
                            match itemprefix:
                                case "Оружий":
                                    current_weapon = self.character.weapon
                                    self.character.inventory.append(current_weapon)
                                    self.character.inventory.remove(new_item)
                                    self.character.weapon = new_item
                                    
                                case "Брони":
                                    # 1. Берем сам ПРЕДМЕТ, а не цифру
                                    current_armor = self.character.itemarmor
                                    self.character.inventory.append(current_armor)
                                    self.character.inventory.remove(new_item)
                                    # 2. Надеваем новую броню
                                    self.character.itemarmor = new_item
                                    # 3. Обновляем цифру защиты у персонажа!
                                    self.character.armor = new_item.defence 
                                                                       
                                case "Аксессуаров":
                                    current_accessory = self.character.accessory
                                    # 1. Снимаем старый бафф (вызываем твой метод unequip)
                                    current_accessory.unequip(self.character)
                                    
                                    self.character.inventory.append(current_accessory)
                                    self.character.inventory.remove(new_item)
                        
                                    self.character.accessory = new_item
                                    # 2. Надеваем новый бафф (вызываем твой метод wear)
                                    new_item.wear(self.character)
                                    
                            print(f"Ты успешно экипировал {new_item.name}\n")
                            return
                            
                        else: 
                            print("Неверный номер!")
                    except ValueError:
                        print("Неверный ввод!")
            else:
                print("Неверный диапазон!")
        
    def serialize_item(self, item):
        data = {
            "name":    item.name,
            "desc":     item.desc,
            "weight":   item.weight,
            "networth":  item.networth,
        }

        if isinstance(item, Weapon):
            data["type"] = "Weapon"
            data["damage"] = item.damage
        elif isinstance(item, PhysArmor):
            data["type"] = "PhysArmor"
            data["defence"] = item.defence
        elif isinstance(item, HpPotion):
            data["type"] = "HpPotion"
            data["amount"] = item.heal_amount
        elif isinstance(item, ManaPotion):
            data["type"] = "ManaPotion"
            data["amount"] = item.heal_amount
        elif isinstance(item, Accessories):
            data["type"] = "Accessories"
            data["target_stat"] = item.target_stat
            data["bonus_stat"]  = item.bonus_stat
        
        return data
        
        
    def save_game(self):
        with open("save_RPGgame.json", "w", encoding='UTF-8') as file:
            player = {
                "name": self.character.name,
                "desc": self.character.desc,
                "class": type(self.character).__name__,
                "hp": self.character.health,
                "weapon": self.serialize_item(self.character.weapon),
                "itemarmor": self.serialize_item(self.character.itemarmor),
                "accessory": self.serialize_item(self.character.accessory),
                "maxhp": self.character.maxhealth,
                "mana": self.character.mana,
                "armor": self.character.armor,
                "critchance": self.character.critchance,
                "gold": self.character.gold,
                "x": self.character.x,
                "y": self.character.y,
                "save_date":  datetime.now().strftime("%d.%m.%Y %H:%M"),
                "inventory": [self.serialize_item(item) for item in self.character.inventory]
            }
            json.dump(player, file, ensure_ascii=False, indent=4)
    
def load_game():
    try:
        with open("save_RPGgame.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        # Создаём персонажа нужного класса
        match data["class"]:
            case "Warrior":  player = Warrior(data["name"], data["desc"])
            case "Mage":     player = Mage(data["name"], data["desc"])
            case "Assassin": player = Assassin(data["name"], data["desc"])

        # Восстанавливаем характеристики
        weapon = data["weapon"]
        itemarmor = data["itemarmor"]
        accessory = data["accessory"]
        player.health    = data["hp"]
        player.maxhealth = data["maxhp"]
        player.mana      = data["mana"]
        player.weapon    = deserialize_item(weapon)
        player.itemarmor = deserialize_item(itemarmor)
        player.accessory = deserialize_item(accessory)
        player.armor     = data["armor"]
        player.critchance = data["critchance"]
        player.gold      = data["gold"]
        player.x         = data["x"]
        player.y         = data["y"]

        # ✅ Восстанавливаем инвентарь — каждый словарь превращаем в объект
        player.inventory = []
        for item_data in data["inventory"]:
            item = deserialize_item(item_data)
            if item:
                player.inventory.append(item)

        print(f"Загружено сохранение от {data['save_date']}")
        return player

    except FileNotFoundError:
        print("Файл сохранения не найден!")
        return None
    except json.JSONDecodeError:
        print("Файл сохранения повреждён!")
        return None

def deserialize_item(data):
    item_type = data["type"]

    match item_type:
        case "Weapon":
            return Weapon(
                data["name"], data["desc"],
                data["weight"], data["networth"],
                data["damage"]
            )
        case "HpPotion":
            return HpPotion(
                data["name"], data["desc"],
                data["weight"], data["networth"],
                data["amount"]
            )
        case "ManaPotion":
            return ManaPotion(
                data["name"], data["desc"],
                data["weight"], data["networth"],
                data["amount"]
            )
        case "PhysArmor":
            return PhysArmor(
                data["name"], data["desc"],
                data["weight"], data["networth"],
                data["defence"]
            )
        case "Accessories":
            return Accessories(
                data["name"], data["desc"],
                data["weight"], data["networth"],
                data["target_stat"], data["bonus_stat"]
            )
            
def create_character():
    name = input("Как будут звать твоего персонажа: ")
    desc = input("Какое описание будет у твоего персонажа: ")
    print("""               
                        Классы персонажей
            
    1. Воин: Имеет повышенную броню и здоровье, но взамен имеет маленький запас маны. Его навыки направлены на быстрые удары оружием и повышением брони.
    
    ПЕРВЫЙ НАВЫК: Двойной удар. Атакует врага дважды с повышенным шансом крита на 15% но имеют пониженный урон на 10%. Стоимость: 10
    ВТОРОЙ НАВЫК: Точный удар. Атакует врага игнорируя броню врага. Стоимость: 5
    ТРЕТИЙ НАВЫК: Повышение брони. Повышает свою броню на 40 на 2 хода. Стоимость: 15
    
    -------------------------------------------------------------------------------------------------------------------------------------
    
    2. Маг: Имеет повышенную ману, жертвуя здоровьем. 
    Его заклинания наносят большой урон врагу и может себя излежить.
    
    ПЕРВЫЙ НАВЫК: Огненный шар. Атакует врага с двойным уроном игнорируя магическую защиту врага. Стоимость: 15
    ВТОРОЙ НАВЫК: Грозовой шквал. Атакует врага трижды с повышенным крит шансом на 25% но с пониженным уроном на 20%. Стоимость: 20
    ТРЕТИЙ НАВЫК: Лечение. Лечит себя на 30% максимального хп. Стоимость: 25
    
    --------------------------------------------------------------------------------------------------------------------------------------
    
    3. Ассассин: Имеет повышенный шанс крит атаки и ману но жертвует небольшим количеством здоровья.
    Его заклинания завязаны на механике критов и уникальной механиков МЕГАКРИТА (урон повышен в три раза вместо два)
    
    ПЕРВЫЙ НАВЫК: Фокусированный удар. Атакует врага своим оружием с сильно повышенным шансом на критический урон (на 50%), 
    в случае 100% критического шанса Ассасин имеет шанс МЕГАКРИТА (необходимо 200% для гарантированного мегакрита). Стоимость: 5
    ВТОРОЙ НАВЫК: Метка точности. Вешает метку на врага на 3 хода, которая увеличивает крит шанс по нему на 40%. Стоимость: 10
    ТРЕТИЙ НАВЫК: Ядовитый кинжал. Ударяет врага ядом, от чего получает (урон от оружия * 0.4) урона ядом следующие 4 хода. Стоимость: 15
    """)
    print("""
    
            Правила игры
    Мир состоит из координат х и y. Размер карты 8х8. Изначально ты находишься в центре, 4, 4. Рядом также расположены магазины.
    Твоя задача в мире найти логово финального босса "Лорд Тьмы" и уничтожить его. Для этого вокруг карты ты разбросаны враги 
    с которых ты получаешь золото и с шансом предмет (Выпасть предмет может вообще любой, тут лютый рандомайзер) За золото ты 
    можешь купить в магазинах (Алхимии и Кузнеца) темовы́е предметы. Магазины расположены в центре, рядом со стартом игры.
    Сверху будут представлены три класса персонажа с тремя уникальными скиллами за которые ты можешь поиграть.
    
    """)
    while True:
        usdata = input("Какой класс ты выберешь? (по номеру): ")
        match usdata:
            case "1": 
                player = Warrior(name, desc)
                break
            case "2": 
                player = Mage(name, desc)
                break
            case "3": 
                player = Assassin(name, desc)
                break
            case _: print("Неверный ввод!")
    game = Game(player)
    game.main_menu()
    

    
if __name__ == "__main__":
    
    while True:
        user_choice = input("""
        Добро пожаловать в игру!
    1. Создать персонажа
    2. Продолжить игру
    3. Выход
    """)
        match user_choice:
            case "1": create_character()
            case "2": 
                game = Game(load_game())
                game.main_menu()
            case "3":
                print("Удачи!")
                break
