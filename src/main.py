import sys
from .llm import generate_action
from .router import route_action
from .memory import memory


def main():
    print("=====================================================")
    print(" REYNA (Retrieval Engine, Yarn & Narrative Assistant)")
    print("=====================================================")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nUser> ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("REYNA shutting down. Goodbye!")
                break

            memory.append("user", user_input)

            context_string = memory.get_context_string()

            action_obj = generate_action(user_input, context_string)
            if action_obj:
                route_action(action_obj)
            else:
                print("REYNA: Sorry, I had trouble processing that action.")
                memory.append(
                    "system", "Failed to process user intent into a valid tool action."
                )

        except KeyboardInterrupt:
            print("\nForce quitting...")
            sys.exit(0)


if __name__ == "__main__":
    main()
