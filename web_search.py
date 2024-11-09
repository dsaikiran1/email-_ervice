# web_search.py
import requests
import time


def perform_web_search(query, api_key):
    """Performs a web search using SerpAPI and returns the JSON response."""
    try:
        response = requests.get(f"https://serpapi.com/search?q={query}&key={api_key}")
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Return JSON data if successful
    except requests.exceptions.RequestException as e:
        print(f"Error with search API: {e}")
        return None


def run_searches_for_entities(df, query_template, primary_column, api_key):
    """Iterates through each entity in the DataFrame and performs searches."""
    results = []
    for index, row in df.iterrows()[:10]:
        # Replace placeholders in the query
        try:
            query = query_template.format(**row)
            print(f"Performing search for: {query}")

            # Perform the web search
            search_result = perform_web_search(query, api_key)

            # Extract URLs and snippets if the search was successful
            if search_result:
                urls = [item["link"] for item in search_result.get("organic_results", [])]
                snippets = [item["snippet"] for item in search_result.get("organic_results", [])]

                # Append structured results
                results.append({
                    "entity": row[primary_column],
                    "query": query,
                    "urls": urls,
                    "snippets": snippets
                })

            # Rate limiting to avoid hitting API limits
            time.sleep(1)

        except KeyError as e:
            print(f"Error: The placeholder {e} does not match any column in the data.")

    return results
