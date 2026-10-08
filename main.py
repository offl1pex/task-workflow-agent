from tasks import add_task, list_tasks, update_status, get_overdue, daily_summary, tasks_for_today
from openai import OpenAI
import json


class Agent:
    def __init__(self):
        self.messages = [{
            'role': 'system',
            'content': '''Ты Task Workflow Agent — помощник по задачам.
Статусы только: todo, doing, done.
Дедлайн только в формате YYYY-MM-DD.
            
Какой инструмент вызывать:
- «покажи задачи / список / что есть» → list_tasks
- «summary / итог / статистика» → daily_summary
- «что просрочено» → get_overdue
- смена статуса → update_status (нужен id из списка)
- перед сменой статуса, если id неизвестен, сначала list_tasks
            
Отвечай кратко. Не выдумывай id и статусы.'''
        }]
        self.tools = [{
            'type': 'function',
            'function': {
                'name': 'add_task',
                'description': 'Добавить задачу',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'title': {
                            'type': 'string',
                            'description': 'Название задачи'
                        },
                        'deadline': {
                            'type': 'string',
                            'description': 'Записать дедлайн задания в формате Y-m-d'
                        }
                    },
                    'required': ['title']
                }
            }
        }, {
            'type': 'function',
            'function': {
                'name': 'list_tasks',
                'description': '''Показать список задач с id, названием, статусом и дедлайном.
Вызывать, когда пользователь просит показать, вывести или перечислить задачи.''',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'string',
                            'description': 'по какому статусу фильтровать'
                        }
                    },
                    'required': []
                }
            }
        }, {
            'type': 'function',
            'function': {
                'name': 'update_status',
                'description': 'Изменить статус задачи по id',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'task_id': {
                            'type': 'string',
                            'description': 'номер из списка задач/id задачи'
                        },
                        'status': {
                            'type': 'string',
                            'description': 'на какой статус изменить, только todo, doing, done'
                        }
                    },
                    'required': ['task_id', 'status']
                }
            }
        }, {
            'type': 'function',
            'function': {
                'name': 'get_overdue',
                'description': 'Получить просроченные задачи',
                'parameters': {
                    'type': 'object',
                    'properties': {
                    },
                    'required': []
                }
            }
        }, {
            'type': 'function',
            'function': {
                'name': 'daily_summary',
                'description': '''Краткая сводка: сколько задач в todo/doing/done и сколько просрочено.
Вызывать только когда просят итог, summary, статистику. Не использовать вместо списка задач.''',
                'parameters': {
                    'type': 'object',
                    'properties': {
                    },
                    'required': []
                }
            }
        }, {
            'type': 'function',
            'function': {
                'name': 'tasks_for_today',
                'description': 'Задачи у которых дедлайн это сегодняшний день',
                'parameters': {
                    'type': 'object',
                    'properties': {
                    },
                    'required': []
                }
            }
        }]
        self.client = OpenAI()

    def load_messages(self):
        try:
            with open('chat.json', 'r', encoding='utf-8') as file:
                self.messages = json.load(file)
        except FileNotFoundError:
            with open('chat.json', 'w', encoding='utf-8') as file:
                json.dump(self.messages, file, ensure_ascii=False, indent=4)

    def save_messages(self):
        with open('chat.json', 'w', encoding='utf-8') as file:
            json.dump(self.messages, file, ensure_ascii=False, indent=4)

    def ask_model(self):
        response = self.client.chat.completions.create(
            model='gpt-4.1-mini',
            messages=self.messages,
            tools=self.tools,
            max_completion_tokens=300
        )
        return response.choices[0].message

    def run_tool(self, name, args):
        try:
            if name == 'add_task':
                return add_task(args['title'], args.get('deadline', ''))
            elif name == 'list_tasks':
                return list_tasks(args.get('status', ''))
            elif name == 'update_status':
                return update_status(args['task_id'], args['status'])
            elif name == 'get_overdue':
                return get_overdue()
            elif name == 'daily_summary':
                return daily_summary()
            elif name == 'tasks_for_today':
                return tasks_for_today()
            else:
                return 'Неизвестная инструкция'
        except KeyError:
            return 'Переданы не все аргументы'

    def handle_tool_calls(self, message):
        self.messages.append(message.model_dump())
        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            result = self.run_tool(name, args)
            self.messages.append({
                'role': 'tool',
                'tool_call_id': call.id,
                'content': result
            })
        return self.ask_model()

    def chat(self, user_message):
        self.messages.append({
            'role': 'user',
            'content': user_message
        })
        message = self.ask_model()
        if message.tool_calls:
            message = self.handle_tool_calls(message)
        self.messages.append({
            'role': 'assistant',
            'content': message.content
        })
        return message.content

    def run(self):
        user_message = input('Ваш ввод: ')
        self.load_messages()
        while user_message != 'выход':
            if user_message == 'сброс':
                self.messages = [self.messages[0]]
                print('Успешный сброс истории чата')
            else:
                print(self.chat(user_message))
            self.save_messages()
            user_message = input('Ваш ввод: ')


agent = Agent()
agent.run()