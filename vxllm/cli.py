import time
import ollama
from ragatouille import RAGPretrainedModel
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
import pyfiglet
import logging
import contextlib
import io
import os
import argparse

console = Console()
ollama_model = os.environ.get('OLLAMA_MODEL', 'mistral-nemo')
max_context = int(os.environ.get('MAX_CONTEXT', '2000'))

print(f"Ollama model: {ollama_model}")
print(f"Context length: {max_context}")

# suppress noisy output from ragatouille
logging.getLogger('ragatouille').setLevel(logging.WARNING)

# Attempt to use a more accurate tokenizer if possible
try:
    from transformers import AutoTokenizer
    # Initialize the tokenizer - just using gpt2 for quick estimation - llama needs a login so this is easier
    tokenizer = AutoTokenizer.from_pretrained("gpt2", clean_up_tokenization_spaces=True)

    def estimate_tokens(text):
        return len(tokenizer.encode(text))
except ImportError:
    # Fall back to simple estimation if transformers is not installed
    def estimate_tokens(text):
        # Simple estimation: assume average of 4 characters per token
        return len(text) / 4


def estimate_tokens_for_turn(turn):
    user_input = turn['user']
    assistant_response = turn['assistant']
    turn_text = f"User: {user_input}\nAssistant: {assistant_response}\n"
    return estimate_tokens(turn_text)


def estimate_tokens_in_conversation(conversation):
    total_tokens = 0
    for turn in conversation:
        total_tokens += estimate_tokens_for_turn(turn)
    return total_tokens


# qwen2.5-coder:1.5b-instruct - ok at summaries but won't answer code
# gemma2:2b - this one is pretty good and fast
# mistral-nemo - best
def query_ollama(prompt, model=ollama_model, client=None):
    # Start timer for Ollama response time
    start_time = time.time()
    if client:
        response = client.generate(model=model, prompt=prompt)
    else:
        response = ollama.generate(model=model, prompt=prompt)
    ollama_time_ms = (time.time() - start_time) * 1000  # Convert to milliseconds
    return response['response'], ollama_time_ms


def rag_search(query, conversation_history, num_docs=20, client=None):
    # Start timer for RAG response time
    start_time = time.time()

    # Suppress stdout and stderr during ragatouille usage
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        # Load the ColBERT index and perform the search
        rag = RAGPretrainedModel.from_index(".ragatouille/colbert/indexes/document_collection/")
        docs = rag.search(query, k=num_docs)
        doc_contents = [doc['content'] for doc in docs]
        reranked_docs = rag.rerank(query=query, documents=doc_contents, k=5)
        rag_time_ms = (time.time() - start_time) * 1000  # Convert to milliseconds
        # Construct the context from reranked documents
        context = "\n".join([doc['content'] for doc in reranked_docs])
        # Extract metadata from reranked documents
        all_tags = set()
        all_urls = set()
        for doc in docs:
            if 'document_metadata' in doc:
                metadata = doc['document_metadata']
                if 'tags' in metadata:
                    all_tags.update(metadata['tags'])
                if 'urls' in metadata:
                    all_urls.update(metadata['urls'])

    # set the maximum context window, should match ollama settings and model capabilities
    # max_context = 8096
    buffer = 100  # Buffer to ensure we don't exceed the context limit

    # Build the fixed parts of the prompt
    # might add -  The code examples must be thorough enough for a detection engineer to write detections.
    fixed_prompt = """You are an assistant helping with cybersecurity queries. When providing code examples, format them
as Markdown code blocks with the appropriate language specified for syntax highlighting.

Context:
{context}

Conversation History:
"""

    fixed_prompt_with_context = fixed_prompt.format(context=context)
    fixed_prompt_tokens = estimate_tokens(fixed_prompt_with_context)
    # Calculate the maximum tokens available for conversation history
    max_tokens_for_history = max_context - fixed_prompt_tokens - buffer
    # Update the conversation history with the new turn
    conversation_history.append({'user': query, 'assistant': None})

    # Estimate tokens in conversation history
    total_history_tokens = 0
    for turn in conversation_history:
        total_history_tokens += estimate_tokens_for_turn(turn)

    # Remove the oldest turns if necessary to fit within the max context window
    while total_history_tokens > max_tokens_for_history and conversation_history:
        oldest_turn = conversation_history.pop(0)
        total_history_tokens -= estimate_tokens_for_turn(oldest_turn)

    # Build the conversation history into the prompt
    history_text = ""
    for turn in conversation_history:
        user_input = turn['user']
        assistant_response = turn['assistant'] if turn['assistant'] else ""
        turn_text = f"User: {user_input}\nAssistant: {assistant_response}\n"
        history_text += turn_text

    # Construct the prompt for Ollama
    prompt = f"""{fixed_prompt_with_context}{history_text}"""

    # Estimate tokens for user query
    user_query_tokens = estimate_tokens(query)

    # Get the assistant's response and measure Ollama response time
    answer, ollama_time_ms = query_ollama(prompt)

    # Estimate tokens for Ollama response
    ollama_response_tokens = estimate_tokens(answer)

    # Update the last turn with the assistant's response
    conversation_history[-1]['assistant'] = answer

    # Return the answer and metrics
    return answer, rag_time_ms, ollama_time_ms, user_query_tokens, ollama_response_tokens, list(all_tags), list(all_urls)


def main():
    parser = argparse.ArgumentParser(description="vxLLM CLI with optional Ollama client URL")
    parser.add_argument("--client", help="Ollama client URL (e.g., https://1.2.3.4:11434)")
    args = parser.parse_args()

    # Initialize Ollama client if URL is provided
    ollama_client = None
    if args.client:
        ollama_client = ollama.Client(host=args.client)
        console.print(f"[bold green]Connected to Ollama at {args.client}[/bold green]")

    f = pyfiglet.Figlet(font='bloody')
    ascii_art = f.renderText('vxLLM')

    # Display the ASCII art banner
    console.print(f"[bold red]{ascii_art}[/bold red]")

    conversation_history = []

    while True:
        # Get user input with a prompt
        user_query = Prompt.ask("[bold green]You[/bold green]", console=console)
        if user_query.lower() in ['exit', 'quit']:
            console.print("[bold red]Goodbye![/bold red]")
            break
        # Get the assistant's response
        try:
            with console.status("[bold yellow]Searching...[/bold yellow]", spinner="dots"):
                answer, rag_time_ms, ollama_time_ms, user_query_tokens, ollama_response_tokens, tags, urls = rag_search(
                    user_query, conversation_history, client=ollama_client)
        except Exception as e:
            console.print(f"[bold red]An error occurred:[/bold red] {e}")
            continue

        # Render the assistant's response as Markdown with syntax highlighting
        markdown = Markdown(answer)
        console.print(Panel(markdown, title="[bold magenta]Assistant[/bold magenta]", border_style="magenta"))

        # Display tags and references
        if tags:
            console.print("[bold blue]Tags:[/bold blue]", ", ".join(tags))
        if urls:
            console.print("[bold blue]References:[/bold blue]")
            for url in urls:
                console.print(f"  - {url}")

        # Print metrics after the assistant's response
        metrics_text = Text()
        metrics_text.append(f"rag: {rag_time_ms / 1000:.4f} s  | ", style="italic green")
        metrics_text.append(f"ollama: {ollama_time_ms / 1000:.4f} s  | ", style="italic green")
        metrics_text.append(f"user (tokens): {user_query_tokens}  | ", style="italic green")
        metrics_text.append(f"ollama (tokens): {ollama_response_tokens}\n", style="italic green")

        # Print the metrics
        console.print(metrics_text)


if __name__ == "__main__":
    main()
