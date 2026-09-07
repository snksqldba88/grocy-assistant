# from assistant.parser import (
#     parse_shopping_add_command,
#     parse_shopping_remove_command,
# )
#
# tests = [
#     "add tomato 3 kg",
#     "add 3 kg tomato",
#     "remove tomato 1 kg",
#     "remove 1 kg tomato",
# ]
#
# for test in tests:
#     print(test)
#     print(parse_shopping_add_command(test))
#     print(parse_shopping_remove_command(test))
#     print()

from assistant.engine import process_message

# print(process_message("add tomato 3 kg"))
# print()
# print(process_message("shopping list"))

print(process_message("remove tomato 1 kg"))
print()
print(process_message("shopping list"))