import os
import openai

def main():
    with open("../secret_keys/open_ai.key", "rt") as f:
        openai.api_key = f.read()


    response = openai.Completion.create(
      engine = "text-davinci-001",
      prompt = "Create an outline for an essay about Nikola Tesla and his contributions to technology:",
      max_tokens = 1
    )

    print(response)

if __name__ == '__main__':
    main()
