from generator import create_commands_context

# Get the context with commands.py contents
context = create_commands_context()

# Print the first 500 characters to verify it worked
print("First 500 characters of the context:")
print(context[:500])
print("\n...")
print("Total length of context:", len(context)) 