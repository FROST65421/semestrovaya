# import tkinter as tk
# from tkinter import ttk, messagebox
# import time

# # ========== МИР ==========
# class World:
#     def __init__(self, width=10, height=10):
#         self.width = width
#         self.height = height
#         self.obstacles = set()
#         self.items = {}  # {(x,y): имя_предмета}
#         self.goal = None

#     def add_obstacle(self, x, y):
#         if 0 <= x < self.width and 0 <= y < self.height:
#             self.obstacles.add((x, y))

#     def add_item(self, x, y, name="cargo"):
#         if 0 <= x < self.width and 0 <= y < self.height:
#             self.items[(x, y)] = name

#     def set_goal(self, x, y):
#         self.goal = (x, y)

#     def is_free(self, x, y):
#         return (0 <= x < self.width and 0 <= y < self.height
#                 and (x, y) not in self.obstacles)


# # ========== РОБОТ ==========
# class Robot:
#     DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left
#     DIR_NAMES = ["↑", "→", "↓", "←"]

#     def __init__(self, x=0, y=0):
#         self.x = x
#         self.y = y
#         self.dir_index = 1  # смотрит вправо
#         self.cargo = None
#         self.log = []

#     @property
#     def direction(self):
#         return self.DIR_NAMES[self.dir_index]

#     def _log(self, msg):
#         self.log.append(msg)

#     def turn_left(self):
#         self.dir_index = (self.dir_index - 1) % 4
#         self._log(f"Повернул налево, теперь смотрю {self.direction}")

#     def turn_right(self):
#         self.dir_index = (self.dir_index + 1) % 4
#         self._log(f"Повернул направо, теперь смотрю {self.direction}")

#     def move(self, world):
#         dx, dy = self.DIRECTIONS[self.dir_index]
#         nx, ny = self.x + dx, self.y + dy
#         if world.is_free(nx, ny):
#             self.x, self.y = nx, ny
#             self._log(f"Двинулся на ({self.x},{self.y})")
#             return True
#         else:
#             self._log(f"Стена/препятствие впереди! Стою на ({self.x},{self.y})")
#             return False

#     def scan(self, world):
#         dx, dy = self.DIRECTIONS[self.dir_index]
#         nx, ny = self.x + dx, self.y + dy
#         if not world.is_free(nx, ny):
#             info = "препятствие"
#         elif (nx, ny) in world.items:
#             info = f"предмет '{world.items[(nx,ny)]}'"
#         elif world.goal == (nx, ny):
#             info = "ЦЕЛЬ!"
#         else:
#             info = "пусто"
#         self._log(f"Сканирую вперёд ({nx},{ny}): {info}")
#         return info

#     def take(self, world):
#         if (self.x, self.y) in world.items:
#             self.cargo = world.items.pop((self.x, self.y))
#             self._log(f"Взял предмет '{self.cargo}'")
#             return True
#         self._log("Здесь нечего брать")
#         return False

#     def drop(self, world):
#         if self.cargo:
#             world.items[(self.x, self.y)] = self.cargo
#             self._log(f"Оставил '{self.cargo}' на ({self.x},{self.y})")
#             self.cargo = None
#             return True
#         self._log("Нечего оставлять")
#         return False

#     def at_goal(self, world):
#         return world.goal and (self.x, self.y) == world.goal


# # ========== ИНТЕРПРЕТАТОР КОМАНД ==========
# def run_program(robot, world, program_text):
#     robot.log.clear()
#     commands = [line.strip() for line in program_text.splitlines()
#                 if line.strip() and not line.strip().startswith("#")]
#     for cmd in commands:
#         parts = cmd.lower().replace("(", " ").replace(")", " ").split()
#         name = parts[0]
#         if name == "move":
#             robot.move(world)
#         elif name == "turn_left":
#             robot.turn_left()
#         elif name == "turn_right":
#             robot.turn_right()
#         elif name == "scan":
#             robot.scan(world)
#         elif name == "take":
#             robot.take(world)
#         elif name == "drop":
#             robot.drop(world)
#         elif name == "repeat":
#             n = int(parts[1])
#             # простой repeat: следующие команды до 'end' повторяются n раз
#             # (упрощённая версия — не реализована полностью)
#             pass
#     return robot.log


# # ========== ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ==========
# class RobotSimulatorApp:
#     CELL = 50

#     def __init__(self, root):
#         self.root = root
#         self.root.title("Симулятор робота")

#         self.world = World(10, 10)
#         # добавим препятствия и предметы
#         for x, y in [(3,3),(3,4),(3,5),(5,5),(6,5),(7,5),(7,3)]:
#             self.world.add_obstacle(x, y)
#         self.world.add_item(2, 2, "коробка")
#         self.world.add_item(8, 8, "посылка")
#         self.world.set_goal(9, 9)

#         self.robot = Robot(0, 0)

#         self._build_ui()
#         self._draw()

#     def _build_ui(self):
#         # холст
#         self.canvas = tk.Canvas(self.root,
#                                 width=self.world.width * self.CELL,
#                                 height=self.world.height * self.CELL,
#                                 bg="white")
#         self.canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

#         # панель управления
#         frame = tk.Frame(self.root)
#         frame.grid(row=0, column=1, sticky="n", padx=5, pady=5)

#         tk.Label(frame, text="Программа робота:", font=("Arial", 11, "bold")).pack()
#         self.code = tk.Text(frame, width=28, height=14, font=("Consolas", 11))
#         self.code.pack()
#         self.code.insert("1.0",
#             "# Пример программы\n"
#             "move()\n"
#             "move()\n"
#             "turn_right()\n"
#             "move()\n"
#             "scan()\n"
#             "take()\n"
#             "turn_right()\n"
#             "move()\n"
#             "move()\n"
#             "drop()\n")

#         btn_run = tk.Button(frame, text="▶ Запустить", bg="lightgreen",
#                             command=self._run)
#         btn_run.pack(fill="x", pady=3)
#         btn_reset = tk.Button(frame, text="↺ Сброс", command=self._reset)
#         btn_reset.pack(fill="x", pady=3)

#         # лог
#         log_frame = tk.Frame(self.root)
#         log_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
#         tk.Label(log_frame, text="Лог действий:", font=("Arial", 11, "bold")).pack()
#         self.log_text = tk.Text(log_frame, width=28, height=10,
#                                 font=("Consolas", 10), state="disabled")
#         self.log_text.pack(fill="both", expand=True)

#         # статус
#         self.status = tk.Label(self.root, text="Готов", bd=1, relief="sunken",
#                                anchor="w")
#         self.status.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

#     def _draw(self):
#         self.canvas.delete("all")
#         w, h = self.world.width, self.world.height
#         C = self.CELL

#         # сетка
#         for x in range(w):
#             for y in range(h):
#                 self.canvas.create_rectangle(x*C, y*C, (x+1)*C, (y+1)*C,
#                                              outline="gray")

#         # препятствия
#         for (x, y) in self.world.obstacles:
#             self.canvas.create_rectangle(x*C+2, y*C+2,
#                                          (x+1)*C-2, (y+1)*C-2, fill="black")

#         # предметы
#         for (x, y), name in self.world.items.items():
#             self.canvas.create_oval(x*C+8, y*C+8, (x+1)*C-8, (y+1)*C-8,
#                                     fill="gold", outline="orange")
#             self.canvas.create_text(x*C+C//2, y*C+C//2, text="★",
#                                     font=("Arial", 14))

#         # цель
#         if self.world.goal:
#             gx, gy = self.world.goal
#             self.canvas.create_rectangle(gx*C+2, gy*C+2,
#                                          (gx+1)*C-2, (gy+1)*C-2,
#                                          fill="lightgreen", outline="green",
#                                          width=2)
#             self.canvas.create_text(gx*C+C//2, gy*C+C//2, text="Ф",
#                                     font=("Arial", 16, "bold"))

#         # робот
#         rx, ry = self.robot.x, self.robot.y
#         self.canvas.create_oval(rx*C+5, ry*C+5,
#                                 (rx+1)*C-5, (ry+1)*C-5,
#                                 fill="dodgerblue", outline="navy", width=2)
#         # направление
#         dx, dy = Robot.DIRECTIONS[self.robot.dir_index]
#         cx = rx*C + C//2
#         cy = ry*C + C//2
#         self.canvas.create_line(cx, cy, cx + dx*C//3, cy + dy*C//3,
#                                 arrow="last", fill="red", width=3)

#         # груз
#         if self.robot.cargo:
#             self.canvas.create_text(rx*C+C//2, ry*C+12,
#                                     text="📦", font=("Arial", 12))

#     def _run(self):
#         program = self.code.get("1.0", tk.END)
#         logs = run_program(self.robot, self.world, program)
#         self.log_text.config(state="normal")
#         self.log_text.delete("1.0", tk.END)
#         self.log_text.insert("1.0", "\n".join(logs))
#         self.log_text.config(state="disabled")

#         if self.robot.at_goal(self.world):
#             msg = "🎉 Робот достиг цели!"
#             if self.robot.cargo:
#                 msg += f" (с грузом '{self.robot.cargo}')"
#             self.status.config(text=msg, fg="green")
#         else:
#             self.status.config(
#                 text=f"Робот на ({self.robot.x},{self.robot.y}), "
#                      f"направление {self.robot.direction}", fg="black")
#         self._draw()

#     def _reset(self):
#         self.robot = Robot(0, 0)
#         self.world = World(10, 10)
#         for x, y in [(3,3),(3,4),(3,5),(5,5),(6,5),(7,5),(7,3)]:
#             self.world.add_obstacle(x, y)
#         self.world.add_item(2, 2, "коробка")
#         self.world.add_item(8, 8, "посылка")
#         self.world.set_goal(9, 9)
#         self.log_text.config(state="normal")
#         self.log_text.delete("1.0", tk.END)
#         self.log_text.config(state="disabled")
#         self.status.config(text="Сброшено", fg="black")
#         self._draw()


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = RobotSimulatorApp(root)
#     root.mainloop()
import tkinter as tk

# ========== МИР ==========
class World:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.obstacles = set()
        self.items = {}
        self.goal = None

    def add_obstacle(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.obstacles.add((x, y))

    def add_item(self, x, y, name="cargo"):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.items[(x, y)] = name

    def set_goal(self, x, y):
        self.goal = (x, y)

    def is_free(self, x, y):
        return (0 <= x < self.width and 0 <= y < self.height
                and (x, y) not in self.obstacles)


# ========== РОБОТ ==========
class Robot:
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left
    DIR_NAMES = ["↑", "→", "↓", "←"]

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.dir_index = 1  # смотрит вправо
        self.cargo = None
        self.log = []

    @property
    def direction(self):
        return self.DIR_NAMES[self.dir_index]

    def _log(self, msg):
        self.log.append(msg)

    def turn_left(self):
        self.dir_index = (self.dir_index - 1) % 4
        self._log(f"Повернул налево, теперь смотрю {self.direction}")

    def turn_right(self):
        self.dir_index = (self.dir_index + 1) % 4
        self._log(f"Повернул направо, теперь смотрю {self.direction}")

    def move(self, world):
        dx, dy = self.DIRECTIONS[self.dir_index]
        nx, ny = self.x + dx, self.y + dy
        if world.is_free(nx, ny):
            self.x, self.y = nx, ny
            self._log(f"Двинулся на ({self.x},{self.y})")
            return True
        else:
            self._log(f"Стена/препятствие впереди! Стою на ({self.x},{self.y})")
            return False

    def scan(self, world):
        dx, dy = self.DIRECTIONS[self.dir_index]
        nx, ny = self.x + dx, self.y + dy
        if not world.is_free(nx, ny):
            info = "препятствие"
        elif (nx, ny) in world.items:
            info = f"предмет '{world.items[(nx,ny)]}'"
        elif world.goal == (nx, ny):
            info = "ЦЕЛЬ!"
        else:
            info = "пусто"
        self._log(f"Сканирую вперёд ({nx},{ny}): {info}")
        return info

    def take(self, world):
        if (self.x, self.y) in world.items:
            self.cargo = world.items.pop((self.x, self.y))
            self._log(f"Взял предмет '{self.cargo}'")
            return True
        self._log("Здесь нечего брать")
        return False

    def drop(self, world):
        if self.cargo:
            world.items[(self.x, self.y)] = self.cargo
            self._log(f"Оставил '{self.cargo}' на ({self.x},{self.y})")
            self.cargo = None
            return True
        self._log("Нечего оставлять")
        return False

    def at_goal(self, world):
        return world.goal and (self.x, self.y) == world.goal


# ========== ИНТЕРПРЕТАТОР ОДНОЙ КОМАНДЫ ==========
def execute_one_command(robot, world, cmd_text):
    """
    Выполняет одну команду. Поддерживает числа в скобках:
    move(7) - двигаться 7 раз
    turn_right(2) - повернуть направо 2 раза
    """
    # Парсим: "move(7)" -> ["move", "7"]
    cmd = cmd_text.lower().replace("(", " ").replace(")", " ").split()
    if not cmd:
        return "пустая строка"

    name = cmd[0]
    count = 1  # по умолчанию 1 раз

    # Если есть число в скобках
    if len(cmd) > 1:
        try:
            count = int(cmd[1])
            if count < 1:
                count = 1
        except ValueError:
            robot._log(f"Ошибка: некорректное число в '{cmd_text}'")
            return name

    # Выполняем команду count раз
    for i in range(count):
        if name == "move":
            result = robot.move(world)
            if not result:  # уперлись в стену — останавливаемся
                break
        elif name == "turn_left":
            robot.turn_left()
        elif name == "turn_right":
            robot.turn_right()
        elif name == "scan":
            robot.scan(world)
        elif name == "take":
            robot.take(world)
        elif name == "drop":
            robot.drop(world)
        else:
            robot._log(f"Неизвестная команда: '{name}'")
            break

    if count > 1:
        robot._log(f"  ↳ Выполнено {count} раз")

    return name


# ========== ПРИЛОЖЕНИЕ ==========
class RobotSimulatorApp:
    CELL = 50

    def __init__(self, root):
        self.root = root
        self.root.title("Симулятор робота")

        self.world = World(10, 10)
        for x, y in [(3, 3), (3, 4), (3, 5), (5, 5), (6, 5), (7, 5), (7, 3)]:
            self.world.add_obstacle(x, y)
        self.world.add_item(2, 2, "коробка")
        self.world.add_item(8, 8, "посылка")
        self.world.set_goal(9, 9)

        self.robot = Robot(0, 0)

        # Для пошагового выполнения
        self.commands = []
        self.current_index = 0
        self.running = False
        self.delay = 500
        self.last_program_text = ""

        self._build_ui()
        self._draw()

    def _build_ui(self):
        self.canvas = tk.Canvas(self.root,
                                width=self.world.width * self.CELL,
                                height=self.world.height * self.CELL,
                                bg="white")
        self.canvas.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

        frame = tk.Frame(self.root)
        frame.grid(row=0, column=1, sticky="n", padx=5, pady=5)

        tk.Label(frame, text="Программа робота:", font=("Arial", 11, "bold")).pack()
        self.code = tk.Text(frame, width=28, height=14, font=("Consolas", 11))
        self.code.pack()
        self.code.insert("1.0",
            "# Пример программы\n"
            "# move(7) - двигаться 7 раз\n"
            "move(2)\n"
            "turn_right()\n"
            "move(2)\n"
            "scan()\n"
            "take()\n"
            "turn_right(2)\n"
            "move(3)\n"
            "turn_left()\n"
            "move(3)\n"
            "drop()\n")

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=3)

        self.btn_run = tk.Button(btn_frame, text="▶ Запустить", bg="lightgreen",
                                 command=self._start_run)
        self.btn_run.pack(side="left", expand=True, fill="x", padx=1)

        self.btn_pause = tk.Button(btn_frame, text="⏸ Пауза", bg="lightyellow",
                                   command=self._pause, state="disabled")
        self.btn_pause.pack(side="left", expand=True, fill="x", padx=1)

        self.btn_step = tk.Button(btn_frame, text="👣 Шаг", bg="lightblue",
                                  command=self._step)
        self.btn_step.pack(side="left", expand=True, fill="x", padx=1)

        tk.Button(frame, text="↺ Сброс", command=self._reset).pack(fill="x", pady=3)

        speed_frame = tk.Frame(frame)
        speed_frame.pack(fill="x", pady=3)
        tk.Label(speed_frame, text="Скорость:").pack(side="left")
        self.speed_var = tk.IntVar(value=500)
        self.speed_scale = tk.Scale(speed_frame, from_=100, to=1500,
                                    orient="horizontal", variable=self.speed_var,
                                    command=self._change_speed)
        self.speed_scale.pack(side="left", expand=True, fill="x")
        self.speed_label = tk.Label(speed_frame, text="500 мс")
        self.speed_label.pack(side="right")

        log_frame = tk.Frame(self.root)
        log_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        tk.Label(log_frame, text="Лог действий:", font=("Arial", 11, "bold")).pack()
        self.log_text = tk.Text(log_frame, width=28, height=10,
                                font=("Consolas", 10), state="disabled")
        self.log_text.pack(fill="both", expand=True)

        self.current_label = tk.Label(frame, text="Готов", font=("Arial", 10),
                                      fg="blue")
        self.current_label.pack(pady=2)

        self.status = tk.Label(self.root, text="Готов", bd=1, relief="sunken",
                               anchor="w")
        self.status.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

    def _change_speed(self, val):
        self.delay = int(val)
        self.speed_label.config(text=f"{val} мс")

    def _parse_commands(self):
        """Парсит команды из редактора кода."""
        text = self.code.get("1.0", tk.END)
        return [line.strip() for line in text.splitlines()
                if line.strip() and not line.strip().startswith("#")]

    def _start_run(self):
        """Запуск или продолжение выполнения."""
        new_commands = self._parse_commands()

        if self.last_program_text != self.code.get("1.0", tk.END):
            if self.current_index > 0:
                old_commands = self.commands
                if new_commands[:self.current_index] == old_commands[:self.current_index]:
                    pass  # продолжаем
                else:
                    self._reset_robot_state()
                    self.current_index = 0
            else:
                self.current_index = 0

        self.commands = new_commands
        self.last_program_text = self.code.get("1.0", tk.END)

        if self.current_index >= len(self.commands):
            self.current_label.config(text="Все команды выполнены", fg="green")
            return

        self.running = True
        self.btn_run.config(state="disabled")
        self.btn_step.config(state="disabled")
        self.btn_pause.config(state="normal")
        self._run_next()

    def _run_next(self):
        """Выполняет следующую команду с задержкой."""
        if not self.running:
            return
        if self.current_index >= len(self.commands):
            self._finish()
            return
        cmd = self.commands[self.current_index]
        execute_one_command(self.robot, self.world, cmd)
        self.current_index += 1
        self._update_log()
        self._draw()
        self.current_label.config(
            text=f"Команда {self.current_index}/{len(self.commands)}: {cmd}")
        self.root.after(self.delay, self._run_next)

    def _step(self):
        """Выполнить одну команду вручную."""
        new_commands = self._parse_commands()

        if self.last_program_text != self.code.get("1.0", tk.END):
            if self.current_index > 0:
                if new_commands[:self.current_index] != self.commands[:self.current_index]:
                    self._reset_robot_state()
                    self.current_index = 0
            else:
                self.current_index = 0

        self.commands = new_commands
        self.last_program_text = self.code.get("1.0", tk.END)

        if self.current_index >= len(self.commands):
            self.current_label.config(text="Программа завершена", fg="red")
            return
        cmd = self.commands[self.current_index]
        execute_one_command(self.robot, self.world, cmd)
        self.current_index += 1
        self._update_log()
        self._draw()
        self.current_label.config(
            text=f"Команда {self.current_index}/{len(self.commands)}: {cmd}")

    def _pause(self):
        self.running = False
        self.btn_run.config(state="normal")
        self.btn_step.config(state="normal")
        self.btn_pause.config(state="disabled")
        self.current_label.config(text="Пауза", fg="orange")

    def _finish(self):
        self.running = False
        self.btn_run.config(state="normal")
        self.btn_step.config(state="normal")
        self.btn_pause.config(state="disabled")
        if self.robot.at_goal(self.world):
            msg = "🎉 Робот достиг цели!"
            if self.robot.cargo:
                msg += f" (с грузом '{self.robot.cargo}')"
            self.status.config(text=msg, fg="green")
        else:
            self.status.config(
                text=f"Робот на ({self.robot.x},{self.robot.y}), "
                     f"направление {self.robot.direction}", fg="black")
        self.current_label.config(text="✅ Программа завершена", fg="green")

    def _reset_robot_state(self):
        """Сбрасывает только состояние робота, не мир."""
        self.robot = Robot(0, 0)
        self.world = World(10, 10)
        for x, y in [(3, 3), (3, 4), (3, 5), (5, 5), (6, 5), (7, 5), (7, 3)]:
            self.world.add_obstacle(x, y)
        self.world.add_item(2, 2, "коробка")
        self.world.add_item(8, 8, "посылка")
        self.world.set_goal(9, 9)
        self.robot.log.clear()

    def _update_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert("1.0", "\n".join(self.robot.log))
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _draw(self):
        self.canvas.delete("all")
        w, h = self.world.width, self.world.height
        C = self.CELL

        for x in range(w):
            for y in range(h):
                self.canvas.create_rectangle(x*C, y*C, (x+1)*C, (y+1)*C,
                                             outline="gray")

        for (x, y) in self.world.obstacles:
            self.canvas.create_rectangle(x*C+2, y*C+2,
                                         (x+1)*C-2, (y+1)*C-2, fill="black")

        for (x, y), name in self.world.items.items():
            self.canvas.create_oval(x*C+8, y*C+8, (x+1)*C-8, (y+1)*C-8,
                                    fill="gold", outline="orange")
            self.canvas.create_text(x*C+C//2, y*C+C//2, text="★",
                                    font=("Arial", 14))

        if self.world.goal:
            gx, gy = self.world.goal
            self.canvas.create_rectangle(gx*C+2, gy*C+2,
                                         (gx+1)*C-2, (gy+1)*C-2,
                                         fill="lightgreen", outline="green",
                                         width=2)
            self.canvas.create_text(gx*C+C//2, gy*C+C//2, text="Ф",
                                    font=("Arial", 16, "bold"))

        rx, ry = self.robot.x, self.robot.y
        self.canvas.create_oval(rx*C+5, ry*C+5,
                                (rx+1)*C-5, (ry+1)*C-5,
                                fill="dodgerblue", outline="navy", width=2)
        dx, dy = Robot.DIRECTIONS[self.robot.dir_index]
        cx = rx*C + C//2
        cy = ry*C + C//2
        self.canvas.create_line(cx, cy, cx + dx*C//3, cy + dy*C//3,
                                arrow="last", fill="red", width=3)

        if self.robot.cargo:
            self.canvas.create_text(rx*C+C//2, ry*C+12,
                                    text="📦", font=("Arial", 12))

    def _reset(self):
        self.running = False
        self.commands = []
        self.current_index = 0
        self.last_program_text = ""
        self._reset_robot_state()
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")
        self.status.config(text="Сброшено", fg="black")
        self.current_label.config(text="Готов", fg="blue")
        self.btn_run.config(state="normal")
        self.btn_step.config(state="normal")
        self.btn_pause.config(state="disabled")
        self._draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotSimulatorApp(root)
    root.mainloop()