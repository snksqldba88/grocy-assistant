# from assistant.engine import process_message
#
# print(process_message("add product"))
# print(process_message("Cancellation Test Product"))
# print(process_message("Dal & Legumes"))
# print(process_message("Shelf"))
# print(process_message("kilogram"))
# print(process_message("kilogram"))
# print(process_message("no"))

# from assistant.engine import process_message
#
# print(process_message("help"))

# from assistant.engine import process_message
#
# print(process_message("add product group"))
# print(process_message("Cancellation Test Group"))
# print(process_message("no"))
#
# print(process_message("stock Cancellation Test Group"))

from assistant.masterdata import lookup_product_group

print(lookup_product_group("Cancellation Test Group"))