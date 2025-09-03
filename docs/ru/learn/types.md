# Типы данных

При разработке приложений особенно важно, чтобы среда разработки (IDE) подсказывала доступные методы и параметры классов.
Однако роутер (Router) передаёт в обработчики разные типы данных, и IDE не всегда может корректно определить их тип. Поэтому ей необходимо «подсказать», какой именно объект приходит.

В **{{product_name}}** для этого предусмотрен пакет [`trueconf.types`](../../en/reference/Types.md), в котором описаны все входящие от сервера события и запросы (уведомления).
А для ответов на клиентские запросы используется отдельный модуль — `trueconf.types.responses`.

Таким образом:

- при работе с событиями используйте типы из [`trueconf.types`](../../en/reference/Types.md);
- при работе с результатами запросов клиента используйте типы из `trueconf.types.responses`.

Это обеспечивает:

- автодополнение в IDE (подсказки по атрибутам и методам);
- статическую проверку типов (type checking) с помощью mypy или аналогичных инструментов;
- более удобную навигацию по коду и документации.

## Пример использования

### Событие о добавлении участника в чат

Предположим, вы хотите обработать событие о [добавлении нового участника в чат](https://trueconf.com/docs/chatbot-connector/en/server-requests/#addChatParticipant) (1): 
{ .annotate }

1.  Согласно [API](https://trueconf.com/docs/chatbot-connector/en/server-requests/#addChatParticipant), это запрос с `"method": "addChatParticipant"`.

```python
from trueconf import Router

r = Router()

@r.added_chat_participant()
async def on_added_user(event): ...
```

Чтобы IDE подсказывала доступные атрибуты объекта event, необходимо указать правильный тип данных:

```python
from trueconf import Router
from trueconf.types import AddedChatParticipant

r = Router()

@r.added_chat_participant()
async def on_added_user(event: AddedChatParticipant):
    who_add = event.added_by
```

!!! abstract "В данном примере:"

    - `AddedChatParticipant` описывает структуру входящего события,
    - вы получаете удобное автодополнение в IDE,
    - при использовании инструментов статической типизации (например, mypy) автоматически проверяется корректность обращения к полям объекта.

### "Сырое" событие

При использовании декоратора @<router>.event вы получаете доступ ко всем полям объекта события, включая те, которые обычно скрываются при преобразовании JSON в класс:

```json
{
  "method": "name",
  "type": 1,
  "id": 11,
  "payload": {}
}
```
В такой ситуации лучше обратиться к [`trueconf.types.Update`](../../en/reference/Types.md/#trueconf.types.Update), который описывает структуру полного обновления, приходящего от сервера.

```python
from trueconf import Router
from trueconf.types import Update
from trueconf.enums import IncomingUpdateMethod

r = Router()

@r.event()
async def raw_event(event: Update):
    if event.method == IncomingUpdateMethod.MESSAGE:
        pass
    
    # Alternatively, without importing enum
    if event.method == "SendMessage":
        pass
```



