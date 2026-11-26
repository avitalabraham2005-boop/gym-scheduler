"""בדיקה מינימלית לחיבור ה-LLM באמצעות Chat Completions."""

try:
    from source.llm_client import MODEL, get_client
except ImportError:
    from llm_client import MODEL, get_client


def main() -> None:
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "In one sentence, what is an LLM?"}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
