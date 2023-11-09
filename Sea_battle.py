from random import randint


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Coordinate {self.x}, {self.y}"


class Ships:
    def __init__(self, bow_point, l, position):
        self.l = l
        self.bow_point = bow_point
        self.position = position
        self.hit_points = l

    @property
    def dots(self):
        dots_ship = []
        for i in range(self.l):
            pos_x = self.bow_point.x
            pos_y = self.bow_point.y

            if self.position == 0:
                pos_x += i

            elif self.position == 1:
                pos_y += i

            dots_ship.append(Coordinate(pos_x, pos_y))

        return dots_ship

    def shooting(self, shot):
        return shot in self.dots


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class PlayingField:
    def __init__(self, hid=False, field_size=6):
        self.hid = hid
        self.field_size = field_size
        self.counter = 0
        self.field = [["O"] * field_size for _i in range(field_size)]

        self.was_shot = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.field_size) and (0 <= d.y < self.field_size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Coordinate(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.was_shot:
                    if verb:
                        self.field[cur.x][cur.y] = "T"
                    self.was_shot.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.was_shot:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.was_shot.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.was_shot:
            raise BoardUsedException()

        self.was_shot.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.hit_points -= 1
                self.field[d.x][d.y] = "X"
                if ship.hit_points == 0:
                    self.counter += 1
                    self.contour(ship, verb=True)
                    print("Корабль потоплен")
                    return False
                else:
                    print("Корабль подбит")
                    return True

        self.field[d.x][d.y] = "T"
        print("Мимо")
        return False

    def begin(self):
        self.was_shot = []


class Player:
    def __init__(self, field, enemy):
        self.field = field
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Coordinate(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Coordinate(x - 1, y - 1)


class Game:
    def __init__(self, field_size=6):
        self.field_size = field_size
        pl = self.random_field()
        co = self.random_field()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_field(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        field = PlayingField(field_size=self.field_size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ships(Coordinate(randint(0, self.field_size), randint(0, self.field_size)), l, randint(0, 1))
                try:
                    field.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        field.begin()
        return field

    def random_field(self):
        field = None
        while field is None:
            field = self.try_field()
        return field

    def welcome(self):
        print('                    ')
        print(' Игра "Морской бой" ')
        print('                    ')
        print(' x - номер строки   ')
        print(' y - номер столбца  ')

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.field)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.field)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.field.counter == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.field.counter == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.welcome()
        self.loop()


start_game = Game()
start_game.start()
