"""Local model chat example (no cloud API)."""


class LocalChatModel:
    def __init__(self, model_name: str = "distilgpt2") -> None:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError("Missing dependency 'transformers'. Install it before running this script.") from exc

        # device_map="auto" uses GPU when available.
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device_map="auto",
        )

    def ask(self, prompt: str, max_new_tokens: int = 120) -> str:
        prompt = prompt.strip()
        if not prompt:
            return "Please provide a prompt."

        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            eos_token_id=self.generator.tokenizer.eos_token_id,
        )
        generated = outputs[0]["generated_text"]
        # Return only the suffix when possible.
        if generated.startswith(prompt):
            return generated[len(prompt) :].strip() or generated.strip()
        return generated.strip()


if __name__ == "__main__":
    model = LocalChatModel()
    print("Local AI chat (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye 👋")
            break
        print("AI:", model.ask(user_input))
