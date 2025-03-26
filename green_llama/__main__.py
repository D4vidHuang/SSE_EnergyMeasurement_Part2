from rich.console import Console
from rich.prompt import Prompt
import threading
import ollama

from green_llama.metrics.metrics import test_all
from . import models
from . import monitoring
from . import utils
from . import interface
def main():
        console = Console()
        interface.display_banner()
        model_choice = False
        while True:  # Main loop to allow restarting
            while not model_choice:  # keep trying to find a model
                available_models = models.list_available_models()
                interface.display_model_list(available_models)

                model = Prompt.ask("Enter model name", default="llama2")

                if model.lower() == "exit":
                    console.print("[bold red]Exiting wrapper...[/bold red]")
                    return
                elif model not in available_models:
                    model_choice = models.handle_missing_model(model)
                else:
                    model_choice = True

            metrics = interface.choose_metric()
            metrics_storage = {metric: {"prompts": [], "values": [], "times": []} for metric in metrics}

            # monitoring_threads = []
            # for metric_name, measure_function in metrics.items():
            #     thread = threading.Thread(target=monitoring.real_time_monitoring,
            #                               args=(model, metric_name, measure_function, metrics_storage[metric_name]))
            #     thread.daemon = True
            #     monitoring_threads.append(thread)
            #     thread.start()

            while True:
                prompt = Prompt.ask(
                    "Enter your prompt ('restart' to change model, 'exit' to quit, 'summary' for stats)")
                if prompt.lower() == "exit":
                    console.print("[bold red]Exiting wrapper...[/bold red]")
                    utils.save_all_metrics_to_csv(model, metrics_storage)
                    return
                elif prompt.lower() == "restart":
                    model_choice = False
                    console.print("[bold yellow]Restarting model selection...[/bold yellow]")
                    break
                elif prompt.lower() == "summary":
                    utils.display_summary(metrics_storage)
                else:
                    console.print("[yellow]Thinking...[/yellow]")
                    response, metrics_data = test_all(model, prompt)
                    monitoring.record_metrics(prompt, metrics_data, metrics_storage)
                    console.print(f"[yellow]{response['message']['content']}[/yellow]")


if __name__ == "__main__":
    main()
