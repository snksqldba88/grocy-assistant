# from assistant.conversation import ConversationState
#
#
# state = ConversationState()
#
# print("Initial state:")
# print(state.active)
# print(state.flow)
# print(state.step)
# print(state.data)
#
# assert state.active is False
# assert state.flow is None
# assert state.step is None
# assert state.data == {}
#
# print("✅ Initial state PASS")
#
#
# state.start("add_product")
# state.step = "product_name"
# state.data["name"] = "Toor Dal"
#
# print("\nAfter starting conversation:")
# print(state.active)
# print(state.flow)
# print(state.step)
# print(state.data)
#
# assert state.active is True
# assert state.flow == "add_product"
# assert state.step == "product_name"
# assert state.data["name"] == "Toor Dal"
#
# print("✅ Start conversation PASS")
#
#
# state.end()
#
# print("\nAfter ending conversation:")
# print(state.active)
# print(state.flow)
# print(state.step)
# print(state.data)
#
# assert state.active is False
# assert state.flow is None
# assert state.step is None
# assert state.data == {}
#
# print("✅ End conversation PASS")
#
# from assistant.engine import process_message
#
# print(process_message("add product"))