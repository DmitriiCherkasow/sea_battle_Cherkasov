from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardError(Exception):
    pass


class BoardOut(BoardError):
    def __str__(self):
        return "Выстрел за поле"


class BoardRepeat(BoardError):
    def __str__(self):
        return "Повторное попадание"


class BoardWrong(BoardError):
    pass


class Ship:
    def __init__(self, deck, h, z):
        self.deck = deck
        self.h = h
        self.z = z
        self.heart = h

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.h):
            course_x = self.deck.x
            course_y = self.deck.y

            if self.z == 0:
                course_x += i

            elif self.z == 1:
                course_y += i

            ship_dots.append(Dot(course_x, course_y))

        return ship_dots

    def hit(self, shot):
        return shot in self.dots


class PlayingField:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrong()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        environment = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d in ship.dots:
            for dx, dy in environment:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "&"
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOut()
        if d in self.busy:
            raise BoardRepeat()
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.dots:
                ship.heart -= 1
                self.field[d.x][d.y] = "X"
                if ship.heart == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль потоплен")
                    return False
                else:
                    print("Есть попадание")
                    return True

        self.field[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardError as e:
                print(e)


class II(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class Human(Player):
    def ask(self):
        while True:
            cords = input("Ход игрока(X Y): ").split()

            if len(cords) != 2:
                print("Введите X и Y")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Только числа")
                continue

            x, y = int(y), int(x)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ii = II(co, pl)
        self.hu = Human(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = PlayingField(size=self.size)
        attempts = 0
        for h in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), h, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrong:
                    pass
        board.begin()
        return board

    def greet(self):
        print("Морской бой")
        print("формат ввода:X Y")
        print("X - номер строки")
        print("Y - номер столбца")

    def loop(self):
        num = 0
        while True:
            print("#" * 20)
            print("Доска игрока:")
            print(self.hu.board)
            print("#" * 20)
            print("Доска компьютера:")
            print(self.ii.board)
            if num % 2 == 0:
                print("#" * 20)
                print("Ходит игрок")
                repeat = self.hu.move()
            else:
                print("#" * 20)
                print("Ходит компьютер!")
                repeat = self.ii.move()
            if repeat:
                num -= 1

            if self.ii.board.count == 7:
                print("#" * 20)
                print("Игрок победил")
                break

            if self.hu.board.count == 7:
                print("#" * 20)
                print("Ты проиграл")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

