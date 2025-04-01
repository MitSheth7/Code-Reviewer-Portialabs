from dotenv import load_dotenv
from portia import Portia, default_config, example_tool_registry, LLMProvider, LLMModel, StorageClass
import time
import json
import logging
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

def wait_with_message(seconds, message):
    """Wait for specified seconds while showing a countdown message."""
    for i in range(seconds, 0, -1):
        console.print(f"\r{message} {i} seconds...", end="", soft_wrap=False)
        time.sleep(1)
    console.print("\r" + " " * 50 + "\r", end="", soft_wrap=False)

def display_code_review(review_results):
    """Display the code review results in a user-friendly way."""
    try:
        if hasattr(review_results, 'state'):
            console.print(f"\n[bold]Review State:[/bold] {review_results.state}")
            
        if hasattr(review_results, 'outputs'):
            console.print("\n[bold]Review Results:[/bold]")
            for output in review_results.outputs:
                if hasattr(output, 'value'):
                    # Try to parse as JSON for structured output
                    try:
                        value = json.loads(output.value)
                        if isinstance(value, dict):
                            for key, val in value.items():
                                console.print(f"\n[bold]{key}:[/bold]")
                                console.print(val)
                        else:
                            console.print(f"- {output.value}")
                    except json.JSONDecodeError:
                        console.print(f"- {output.value}")
                else:
                    console.print(f"- {output}")
        else:
            console.print("\n[bold]Review Results:[/bold]")
            console.print(review_results)
            
    except Exception as e:
        console.print(f"\n[red]Error displaying results:[/red] {e}")
        console.print("\n[bold]Raw output:[/bold]")
        console.print(review_results)

def is_rate_limit_error(error_msg):
    """Check if the error is a rate limit error."""
    rate_limit_indicators = [
        "rate limit",
        "429",
        "too many requests",
        "requests rate limit exceeded"
    ]
    return any(indicator in error_msg.lower() for indicator in rate_limit_indicators)

def review_code(code_snippet, review_type="general"):
    """Review a code snippet and return the results."""
    try:
        # Create a custom config using Mistral AI and local storage
        config = default_config(
            llm_provider=LLMProvider.MISTRALAI,
            llm_model_name=LLMModel.MISTRAL_LARGE,
            storage_class=StorageClass.MEMORY
        )
        
        # Instantiate a Portia client with Mistral config and example tools
        portia = Portia(config=config, tools=example_tool_registry)
        
        # Create a more focused review query to reduce API calls
        if review_type == "general":
            query = f"""Review this code and provide a single, comprehensive analysis covering:
- Code quality and best practices
- Potential bugs and issues
- Key improvements needed

Code:
{code_snippet}"""
        elif review_type == "security":
            query = f"""Review this code for security issues and provide a single, comprehensive analysis covering:
- Security vulnerabilities
- Input validation issues
- Key security improvements needed

Code:
{code_snippet}"""
        elif review_type == "performance":
            query = f"""Review this code for performance issues and provide a single, comprehensive analysis covering:
- Time and space complexity
- Performance bottlenecks
- Key optimization opportunities

Code:
{code_snippet}"""
        
        # Generate and execute plan
        console.print("\n[bold]Generating review plan...[/bold]")
        plan = portia.plan(query)
        
        console.print("\n[bold]Executing review...[/bold]")
        plan_run = portia.run_plan(plan)
        return plan_run
        
    except Exception as e:
        logger.error(f"Error in code review: {e}")
        raise

def main():
    # Load environment variables
    load_dotenv()
    
    try:
        console.print(Panel.fit(
            "[bold blue]Code Review Assistant[/bold blue]\n"
            "An AI-powered tool for code review and analysis\n\n"
            "[yellow]Note: This tool uses rate-limited APIs. Please be patient between requests.[/yellow]",
            title="Welcome",
            border_style="blue"
        ))
        
        while True:
            console.print("\n[bold]Available Review Types:[/bold]")
            console.print("1. General Review (code quality, bugs, best practices)")
            console.print("2. Security Review (vulnerabilities, input validation)")
            console.print("3. Performance Review (complexity, optimization)")
            console.print("4. Exit")
            
            choice = input("\nSelect review type (1-4): ")
            
            if choice == "4":
                break
                
            if choice not in ["1", "2", "3"]:
                console.print("[red]Invalid choice. Please try again.[/red]")
                continue
                
            review_type = {
                "1": "general",
                "2": "security",
                "3": "performance"
            }[choice]
            
            console.print("\n[bold]Enter your code snippet (press Ctrl+D or Ctrl+Z when done):[/bold]")
            code_lines = []
            try:
                while True:
                    line = input()
                    code_lines.append(line)
            except (EOFError, KeyboardInterrupt):
                pass
                
            code_snippet = "\n".join(code_lines)
            
            if not code_snippet.strip():
                console.print("[red]No code provided. Please try again.[/red]")
                continue
                
            # Display the code with syntax highlighting
            syntax = Syntax(code_snippet, "python", theme="monokai")
            console.print(Panel(syntax, title="Code to Review", border_style="green"))
            
            max_retries = 3
            retry_count = 0
            base_wait_time = 60  # Increased from 30 to 60 seconds
            
            while retry_count < max_retries:
                try:
                    # Add initial delay before first attempt
                    if retry_count == 0:
                        console.print("\n[yellow]Waiting 60 seconds before starting review (rate limit protection)...[/yellow]")
                        wait_with_message(60, "Waiting")
                    
                    review_results = review_code(code_snippet, review_type)
                    display_code_review(review_results)
                    break
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error occurred: {error_msg}")
                    
                    if is_rate_limit_error(error_msg):
                        retry_count += 1
                        # Exponential backoff: 60s, 120s, 240s
                        wait_time = base_wait_time * (2 ** (retry_count - 1))
                        console.print(f"\n[yellow]Rate limit reached. Attempt {retry_count} of {max_retries}[/yellow]")
                        console.print(f"Waiting {wait_time} seconds before retrying (exponential backoff)...")
                        wait_with_message(wait_time, "Waiting")
                        continue
                    else:
                        console.print(f"\n[red]Error:[/red] {error_msg}")
                        break
            
            if retry_count >= max_retries:
                console.print("\n[red]Maximum retries reached. Please try again later.[/red]")
                console.print("[yellow]Tip: Wait at least 5 minutes before trying again to avoid rate limits.[/yellow]")
                break  # Exit the program to prevent further rate limit issues
            
            # Add a longer delay between successful requests
            console.print("\n[yellow]Waiting 60 seconds before next request...[/yellow]")
            wait_with_message(60, "Waiting")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\n[bold]Detailed error information:[/bold]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 