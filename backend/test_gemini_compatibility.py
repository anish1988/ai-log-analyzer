import os

from openai import OpenAI


GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)


def main() -> None:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    chat_model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    )

    embedding_model = os.getenv(
        "GEMINI_EMBEDDING_MODEL",
        "gemini-embedding-001",
    )

    client = OpenAI(
        api_key=api_key,
        base_url=GEMINI_BASE_URL,
    )

    print("=" * 100)
    print("GEMINI OPENAI-COMPATIBILITY TEST")
    print("=" * 100)

    # ------------------------------------------------------------------
    # 1. CHAT / LLM TEST
    # ------------------------------------------------------------------

    print()
    print("===== GEMINI CHAT TEST =====")
    print("Model:", chat_model)

    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a connectivity test assistant."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Reply with exactly: "
                    "GEMINI CHAT TEST PASS"
                ),
            },
        ],
    )

    chat_text = (
        response.choices[0].message.content
        or ""
    )

    print("Response:", chat_text)

    # ------------------------------------------------------------------
    # 2. EMBEDDING TEST
    # ------------------------------------------------------------------

    print()
    print("===== GEMINI EMBEDDING TEST =====")
    print("Model:", embedding_model)

    embedding_response = (
        client.embeddings.create(
            model=embedding_model,
            input=(
                "Phase 3 Gemini embedding "
                "connectivity test"
            ),
        )
    )

    embedding = (
        embedding_response.data[0].embedding
    )

    print(
        "Embedding size:",
        len(embedding),
    )

    # ------------------------------------------------------------------
    # RESULT
    # ------------------------------------------------------------------

    print()
    print("=" * 100)
    print("GEMINI CHAT TEST: PASS")
    print("GEMINI EMBEDDING TEST: PASS")
    print("=" * 100)


if __name__ == "__main__":
    main()