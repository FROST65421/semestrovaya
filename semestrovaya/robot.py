# ========== ИНТЕРПРЕТАТОР ОДНОЙ КОМАНДЫ ==========
def execute_one_command(robot, world, cmd_text):
    cmd = cmd_text.lower().replace("(", " ").replace(")", " ").split()
    if not cmd:
        return "пустая строка"

    name = cmd[0]
    count = 1

    if len(cmd) > 1:
        try:
            count = int(cmd[1])
            if count < 1:
                count = 1
            # ДОБАВЛЕНО: ограничение максимум 12 повторений
            if count > 12:
                count = 12
                robot._log(f"⚠️ Ограничение: команда '{name}' выполнена 12 раз (максимум)")
        except ValueError:
            robot._log(f"Ошибка: некорректное число в '{cmd_text}'")
            return name

    for i in range(count):
        if name == "move":
            result = robot.move(world)
            if not result:
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
        elif name == "jump":
            result = robot.jump(world)
            if not result:
                break
        elif name == "break":
            robot.break_wall(world)
        elif name == "paint":
            robot.start_paint()
        elif name == "stop_paint":
            robot.stop_paint()
        else:
            robot._log(f"Неизвестная команда: '{name}'")
            break

    if count > 1:
        robot._log(f"  ↳ Выполнено {count} раз")

    return name
