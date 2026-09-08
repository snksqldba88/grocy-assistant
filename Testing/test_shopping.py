from assistant.parser import parse_shopping_add_command

message = "add 1 kg tomato to shopping list"

print(parse_shopping_add_command(message))

from assistant.engine import process_message

print(process_message("remove 1 kg tomato from shopping list"))