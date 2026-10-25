
import json
from pathlib import Path

import requests

# API configuration
API_URL = "https://jsonplaceholder.typicode.com/posts"

# File used to store processed results
OUTPUT_FILE = Path("results.json")


def get_user_input():
    """Step 1: Accept and validate user input."""
    while True:
        user_input = input(
            "\nEnter a post ID (1-100) or 'q' to quit: "
        ).strip()

        if user_input.lower() == "q":
            return None

        if user_input.isdigit():
            post_id = int(user_input)

            if 1 <= post_id <= 100:
                return post_id

        print("Invalid input. Please enter a number from 1 to 100.")


def call_api(post_id):
    """Step 2: Call the external API."""
    try:
        response = requests.get(
            f"{API_URL}/{post_id}",
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict) or not data:
            print("Error: The API returned unexpected data.")
            return None

        return data

    except requests.exceptions.Timeout:
        print("Error: The API request timed out.")
    except requests.exceptions.HTTPError as error:
        print(f"HTTP error: {error}")
    except requests.exceptions.RequestException as error:
        print(f"API request failed: {error}")
    except ValueError:
        print("Error: The API returned invalid JSON.")

    return None


def process_data(data):
    """Step 3: Process the API response."""
    title = data.get("title")
    body = data.get("body")

    if not isinstance(title, str) or not isinstance(body, str):
        print("Error: Required fields are missing.")
        return None

    processed_data = {
        "post_id": data.get("id"),
        "user_id": data.get("userId"),
        "title": title.strip().title(),
        "body": body.strip(),
        "word_count": len(body.split())
    }

    return processed_data


def store_result(result):
    """Step 4: Save processed data to a JSON file."""
    try:
        if OUTPUT_FILE.exists():
            with OUTPUT_FILE.open("r", encoding="utf-8") as file:
                saved_results = json.load(file)

            if not isinstance(saved_results, list):
                print("Error: Existing JSON data must be a list.")
                return False
        else:
            saved_results = []

        # Replace an existing record with the same post ID
        saved_results = [
            item for item in saved_results
            if isinstance(item, dict)
            and item.get("post_id") != result["post_id"]
        ]

        saved_results.append(result)

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                saved_results,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except (OSError, json.JSONDecodeError) as error:
        print(f"Storage error: {error}")
        return False


def display_output(result):
    """Step 5: Display the result to the user."""
    print("\n" + "=" * 50)
    print("             PROCESSED API RESULT")
    print("=" * 50)
    print(f"Post ID:    {result['post_id']}")
    print(f"User ID:    {result['user_id']}")
    print(f"Title:      {result['title']}")
    print(f"Body:       {result['body']}")
    print(f"Word count: {result['word_count']}")
    print(f"\nSaved file: {OUTPUT_FILE.resolve()}")
    print("=" * 50)


def main():
    """Run the CLI application."""
    print("=" * 50)
    print("           PYTHON API CLI APPLICATION")
    print("=" * 50)

    while True:
        # 1. Accept user input
        post_id = get_user_input()

        if post_id is None:
            print("Application closed. Goodbye!")
            break

        # 2. Call the API
        data = call_api(post_id)

        if data is None:
            continue

        # 3. Process the API data
        result = process_data(data)

        if result is None:
            continue

        # 4. Store the result
        if not store_result(result):
            print("The result could not be stored.")
            continue

        # 5. Return output
        display_output(result)


if __name__ == "__main__":
    main()
