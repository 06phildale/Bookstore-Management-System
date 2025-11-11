# Notes: 
# 1. Use the following username and password to access the admin rights 
# username: admin
# password: password
# 2. Ensure you open the whole folder for this task in VS Code otherwise the 
# program will look in your root directory for the text files.


"""
Task Manager Application
------------------------
This program allows users to register, add, view, and manage tasks.
It also supports generating reports for tasks and users.
"""

import os
from datetime import datetime, date

DATETIME_STRING_FORMAT = "%Y-%m-%d"


def reg_user(username_password):
    """
    Register a new user and update user.txt, avoiding duplicate usernames.
    Only accessible by the admin user.
    """
    while True:
        new_username = input("New Username: ")
        if new_username in username_password:
            print("Error: Username already exists. Please try a different username.")
            continue

        new_password = input("New Password: ")
        confirm_password = input("Confirm Password: ")

        if new_password == confirm_password:
            print("New user added")
            username_password[new_username] = new_password

            with open("user.txt", "w") as out_file:
                user_data = [f"{k};{v}" for k, v in username_password.items()]
                out_file.write("\n".join(user_data))
            break
        else:
            print("Passwords do not match. Please try again.")


def add_task(username_password, task_list):
    """
    Allows a user to add a new task to the task list and save to file.
    """
    task_username = input("Name of person assigned to task: ")
    if task_username not in username_password:
        print("User does not exist. Please enter a valid username.")
        return

    task_title = input("Title of Task: ")
    task_description = input("Description of Task: ")

    while True:
        try:
            task_due_date = input("Due date of task (YYYY-MM-DD): ")
            due_date_time = datetime.strptime(task_due_date, DATETIME_STRING_FORMAT)
            break
        except ValueError:
            print("Invalid datetime format. Please use the format YYYY-MM-DD.")

    curr_date = date.today()

    new_task = {
        "username": task_username,
        "title": task_title,
        "description": task_description,
        "due_date": due_date_time,
        "assigned_date": curr_date,
        "completed": False
    }

    task_list.append(new_task)
    save_tasks(task_list)
    print("Task successfully added.")


def view_all(task_list, date_format="%Y-%m-%d"):
    """
    Displays all tasks in a readable format.
    """
    for t in task_list:
        disp_str = (
            f"Task: \t\t {t['title']}\n"
            f"Assigned to: \t {t['username']}\n"
            f"Date Assigned: \t {t['assigned_date'].strftime(date_format)}\n"
            f"Due Date: \t {t['due_date'].strftime(date_format)}\n"
            f"Task Description: \n {t['description']}\n"
        )
        print(disp_str)


def view_mine(task_list, curr_user, username_password, date_format="%Y-%m-%d"):
    """
    Display current user's tasks with options to mark complete or edit.
    """
    while True:
        user_tasks = [t for t in task_list if t['username'] == curr_user]

        if not user_tasks:
            print("You have no assigned tasks.")
            return

        for i, t in enumerate(user_tasks, 1):
            status = "Yes" if t['completed'] else "No"
            print(f"{i}. Task: {t['title']} (Completed: {status})")

        selection = input("Select a task by number to manage or enter -1 to return: ")

        if selection == '-1':
            return

        if not selection.isdigit() or int(selection) < 1 or int(selection) > len(user_tasks):
            print("Invalid selection, please try again.")
            continue

        task = user_tasks[int(selection) - 1]

        print(
            f"\nSelected Task: {task['title']}\n"
            f"Assigned to: {task['username']}\n"
            f"Date Assigned: {task['assigned_date'].strftime(date_format)}\n"
            f"Due Date: {task['due_date'].strftime(date_format)}\n"
            f"Completed: {'Yes' if task['completed'] else 'No'}\n"
            f"Task Description:\n{task['description']}"
        )

        if task['completed']:
            print("Task is already completed and cannot be edited.")
            mark_complete = input(
                "Enter 'm' to mark complete again (no effect) or '-1' to return: "
            )
            if mark_complete == '-1':
                continue
            elif mark_complete.lower() == 'm':
                print("Task already marked complete.")
            else:
                print("Invalid input.")
            continue

        action = input("Enter 'c' to mark as complete, 'e' to edit, or '-1' to return: ").lower()

        if action == '-1':
            continue
        elif action == 'c':
            task['completed'] = True
            save_tasks(task_list)
            print("Task marked as complete and saved.")
        elif action == 'e':
            modified = False
            new_username = input(
                "Enter new username to assign task (leave blank to keep current): "
            ).strip()
            if new_username:
                if new_username in username_password:
                    task['username'] = new_username
                    print(f"Task reassigned to {new_username}.")
                    modified = True
                else:
                    print("Username does not exist. Username not changed.")

            while True:
                new_due_date = input(
                    f"Enter new due date (YYYY-MM-DD) or leave blank to keep current: "
                ).strip()
                if not new_due_date:
                    break
                try:
                    new_due_date_dt = datetime.strptime(new_due_date, date_format)
                    task['due_date'] = new_due_date_dt
                    print("Due date updated.")
                    modified = True
                    break
                except ValueError:
                    print("Invalid date format. Please try again.")

            if modified:
                save_tasks(task_list)
                print("Changes saved.")


def save_tasks(task_list):
    """
    Saves the current task_list to tasks.txt.
    """
    with open("tasks.txt", "w") as task_file:
        task_list_to_write = []
        for t in task_list:
            str_attrs = [
                t['username'],
                t['title'],
                t['description'],
                t['due_date'].strftime(DATETIME_STRING_FORMAT),
                t['assigned_date'].strftime(DATETIME_STRING_FORMAT),
                "Yes" if t['completed'] else "No"
            ]
            task_list_to_write.append(";".join(str_attrs))
        task_file.write("\n".join(task_list_to_write))


def generate_reports(task_list, username_password, date_format=DATETIME_STRING_FORMAT):
    """
    Generate task_overview.txt and user_overview.txt with detailed stats.
    """
    num_tasks = len(task_list)
    num_users = len(username_password)

    completed_tasks = sum(1 for t in task_list if t['completed'])
    uncompleted_tasks = num_tasks - completed_tasks
    overdue_tasks = sum(
        1 for t in task_list if not t['completed'] and t['due_date'].date() < date.today()
    )

    # --- task_overview.txt ---
    with open("task_overview.txt", "w") as task_file:
        task_file.write("TASK OVERVIEW REPORT\n")
        task_file.write("--------------------\n")
        task_file.write(f"Total tasks generated: {num_tasks}\n")
        task_file.write(f"Total completed tasks: {completed_tasks}\n")
        task_file.write(f"Total uncompleted tasks: {uncompleted_tasks}\n")
        task_file.write(f"Total overdue tasks (uncompleted): {overdue_tasks}\n")
        if num_tasks > 0:
            task_file.write(f"Percentage incomplete: {uncompleted_tasks / num_tasks * 100:.2f}%\n")
            task_file.write(f"Percentage overdue: {overdue_tasks / num_tasks * 100:.2f}%\n")

    # --- user_overview.txt ---
    with open("user_overview.txt", "w") as user_file:
        user_file.write("USER OVERVIEW REPORT\n")
        user_file.write("--------------------\n")
        user_file.write(f"Total users registered: {num_users}\n")
        user_file.write(f"Total tasks generated: {num_tasks}\n\n")

        for user in username_password:
            user_tasks = [t for t in task_list if t['username'] == user]
            user_task_count = len(user_tasks)
            user_completed = sum(1 for t in user_tasks if t['completed'])
            user_uncompleted = user_task_count - user_completed
            user_overdue = sum(
                1 for t in user_tasks if not t['completed'] and t['due_date'].date() < date.today()
            )

            user_file.write(f"User: {user}\n")
            user_file.write(f"  Total tasks assigned: {user_task_count}\n")
            if num_tasks > 0:
                user_file.write(f"  % of total tasks assigned: {user_task_count / num_tasks * 100:.2f}%\n")
            if user_task_count > 0:
                user_file.write(f"  % completed: {user_completed / user_task_count * 100:.2f}%\n")
                user_file.write(f"  % uncompleted: {user_uncompleted / user_task_count * 100:.2f}%\n")
                user_file.write(f"  % overdue and uncompleted: {user_overdue / user_task_count * 100:.2f}%\n")
            else:
                user_file.write("  No tasks assigned.\n")
            user_file.write("\n")

    print("Reports generated successfully.")