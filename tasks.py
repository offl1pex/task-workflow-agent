import json
from datetime import datetime


def load_tasks():
    try:
        with open('tasks.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def add_task(title, deadline=''):
    data = load_tasks()
    with open('tasks.json', 'w', encoding='utf-8') as file:
        new_data = {
            'id': len(data) + 1,
            'title': title,
            'status': 'todo',
            'deadline': deadline,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        data.append(new_data)
        json.dump(data, file, ensure_ascii=False, indent=4)
        return f'''Задача #{new_data['id']} добавлена: {new_data['title']}'''


def list_tasks(status=''):
    tasks = load_tasks()
    if tasks:
        if status:
            nec_tasks = [f'''{task['id']} | {task['title']} | {task['status']} | {task['deadline'] if task['deadline'] else 'дедлайна нет'}''' for task in tasks if task['status'] == status]

        else:
            nec_tasks = [f'''{task['id']} | {task['title']} | {task['status']} | {task['deadline'] if task['deadline'] else 'дедлайна нет'}''' for task in tasks]
    else:
        return 'На данный момент нет задач'
    if nec_tasks:
        return '\n'.join(nec_tasks)
    else:
        return f'''Задач со статусом {status} нет'''


def update_status(task_id, status):
    statuses = ['todo', 'doing', 'done']
    change = False
    if status in statuses:
        tasks = load_tasks()
        if tasks:
            for task in tasks:
                if str(task['id']) == str(task_id):
                    task['status'] = status
                    change = True
                    with open('tasks.json', 'w', encoding='utf-8') as file:
                        json.dump(tasks, file, ensure_ascii=False, indent=4)
                    return f'''Задача #{task['id']} переведена в статус {status}'''
            if not change:
                return 'Записи с данным id не существует'
        else:
            return 'На данный момент нет задач'
    else:
        return 'Неверный формат записи статуса'


def get_overdue():
    tasks = load_tasks()
    if tasks:
        deadline = datetime.now().strftime('%Y-%m-%d')
        deadline_tasks = [f'''{task['id']} | {task['title']} | {task['status']} | {task['deadline'] if task['deadline'] else 'дедлайна нет'}''' for task in tasks if task['deadline'] and task['deadline'] < deadline and task['status'] != 'done']
        if deadline_tasks:
            return f'''Просрочено:\n {'\n'.join(deadline_tasks)}'''
        else:
            return 'Просроченных задач нет'
    else:
        return 'На данный момент нет задач'


def daily_summary():
    tasks = load_tasks()
    if tasks:
        todo = len([task for task in tasks if task['status'] == 'todo'])
        doing = len([task for task in tasks if task['status'] == 'doing'])
        done = len([task for task in tasks if task['status'] == 'done'])
        overdue = len([task for task in tasks if task['deadline'] if task['deadline'] < datetime.now().strftime('%Y-%m-%d') and task['status'] != 'done'])
        return f'''Всего: {len(tasks)}\ntodo: {todo}\ndoing: {doing}\ndone: {done}\nПросрочено: {overdue}'''
    else:
        return 'На данный момент нет задач'


def tasks_for_today():
    tasks = load_tasks()
    if tasks:
        deadline = datetime.now().strftime('%Y-%m-%d')
        deadline_tasks = [task['title'] for task in tasks if task['deadline'] == deadline]
        if deadline_tasks:
            return '\n'.join(deadline_tasks)
        else:
            return 'Задач с крайним сроком "сегодня" нет'
    else:
        return 'На данный момент нет задач'