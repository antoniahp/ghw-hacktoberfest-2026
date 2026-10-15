import json
import os
import sys
import time
from pathlib import Path


TASKS_FILE = Path("tasks.json")
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def color(text, code):
    if USE_COLOR:
        return f"\033[{code}m{text}\033[0m"
    return text


def load_tasks():
    if not TASKS_FILE.exists():
        return []
    try:
        with TASKS_FILE.open("r", encoding="utf-8") as file:
            tasks = json.load(file)
        if not isinstance(tasks, list):
            raise ValueError("the content is not a list")
        return [
            task
            for task in tasks
            if isinstance(task, dict)
            and isinstance(task.get("text"), str)
            and isinstance(task.get("done"), bool)
        ]
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(color(f"Could not load tasks: {error}", "31"))
        return []


def save_tasks(tasks):
    temporary_file = TASKS_FILE.with_suffix(TASKS_FILE.suffix + ".tmp")
    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_file.replace(TASKS_FILE)
    except OSError as error:
        print(color(f"Could not save tasks: {error}", "31"))
        try:
            temporary_file.unlink(missing_ok=True)
        except OSError:
            pass


def show_tasks(tasks):
    print(color("\n  YOUR TASKS", "1;36"))
    if not tasks:
        print("  No tasks yet. Add your first one! ✨")
        return
    for index, task in enumerate(tasks, start=1):
        marker = color("✓", "32") if task["done"] else color("○", "33")
        label = color(task["text"], "2") if task["done"] else task["text"]
        print(f"  {index:>2}. {marker} {label}")


def add_task(tasks):
    text = input(color("\n  What task do you want to add? ", "36")).strip()
    if not text:
        print(color("  The task cannot be empty.", "33"))
        return
    tasks.append({"text": text, "done": False})
    save_tasks(tasks)
    print(color("  Task added. One more step! ✨", "32"))


def choose_task(tasks, prompt):
    if not tasks:
        print(color("  There are no tasks to select.", "33"))
        return None
    show_tasks(tasks)
    try:
        selection = int(input(prompt).strip())
    except ValueError:
        print(color("  Please type the task number.", "33"))
        return None
    if selection < 1 or selection > len(tasks):
        print(color("  That number does not match any task.", "33"))
        return None
    return selection - 1


def mark_task_done(tasks):
    index = choose_task(tasks, "\n  Number of the completed task: ")
    if index is None:
        return
    tasks[index]["done"] = True
    save_tasks(tasks)
    print(color("  Task completed! Great job. 🎉", "32"))


def delete_task(tasks):
    index = choose_task(tasks, "\n  Number of the task to delete: ")
    if index is None:
        return
    removed = tasks.pop(index)
    save_tasks(tasks)
    print(color(f"  Task deleted: {removed['text']}", "32"))


def countdown(seconds, label):
    """Show a countdown using monotonic time to avoid drift."""
    started = time.monotonic()
    while True:
        remaining = max(0, seconds - int(time.monotonic() - started))
        minutes, seconds_left = divmod(remaining, 60)
        display = f"{minutes:02d}:{seconds_left:02d}"
        print(f"\r  ⏳ {label}: {color(display, '1;32')}  ", end="", flush=True)
        if remaining == 0:
            break
        time.sleep(min(1, remaining))
    print("\r  \033[K", end="", flush=True)
    print(color(f"  🔔 Time's up! {label} finished.", "1;33"))
    print("\a", end="", flush=True)


def start_pomodoro():
    print(color("\n  🍅 Focus block: 25 minutes.", "1;31"))
    countdown(25 * 60, "Focus")
    answer = input("  Start the 5-minute break now? [Y/n]: ").strip().lower()
    if answer in ("", "y", "yes"):
        print(color("\n  🌿 Time to take a break.", "1;36"))
        countdown(5 * 60, "Break")
    else:
        print("  Break skipped. Great job! 💪")


def show_menu():
    print(color("\n╭────────────────────────────────────╮", "36"))
    print(color("│        ✦  R I T M O  ✦             │", "1;36"))
    print(color("╰────────────────────────────────────╯", "36"))
    print("  1. Add task")
    print("  2. View tasks")
    print("  3. Mark as done")
    print("  4. Delete task")
    print("  5. Start Pomodoro")
    print("  6. Exit")


def main():
    tasks = load_tasks()
    actions = {
        "1": lambda: add_task(tasks),
        "2": lambda: show_tasks(tasks),
        "3": lambda: mark_task_done(tasks),
        "4": lambda: delete_task(tasks),
        "5": start_pomodoro,
    }
    while True:
        show_menu()
        choice = input(color("\n  Choose an option [1-6]: ", "1;35")).strip()
        if choice == "6":
            print(color("\n  Goodbye! Have a great day. 👋", "1;32"))
            break
        action = actions.get(choice)
        if action is None:
            print(color("  Invalid option. Choose a number from 1 to 6.", "33"))
            continue
        action()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(color("\n\n  App closed. See you soon! 👋", "1;32"))