import atexit
import json
from datetime import datetime
from pathlib import Path


class OpenAICostEstimator:
    """
    A simple class to track and estimate costs for OpenAI API usage.
    Tracks input tokens, cached input tokens, and output tokens separately.
    Writes statistics to a file when the program ends.
    """
    
    def __init__(
        self,
        application_name,
        model_name="gpt-4.1-mini",
        stats_dir="costs/"
    ):
        """
        Initialize the cost estimator with token costs for a specific model.
        
        Args:
            model_name: Name of the OpenAI model being used
            input_cost_per_1k: Cost in USD per 1000 input tokens
            output_cost_per_1k: Cost in USD per 1000 output tokens
            cached_input_cost_per_1k: Cost in USD per 1000 cached input tokens
            stats_file_path: Path to save the usage statistics
        """
        self.application_name = application_name
        self.model_name = model_name

        if self.model_name == "gpt-4.1-mini":
            self.uncached_input_cost_per_1m = 0.40
            self.output_cost_per_1m = 1.60
            self.cached_input_cost_per_1m = 0.10
        elif self.model_name == "o4-mini":
            self.uncached_input_cost_per_1m = 1.10
            self.output_cost_per_1m = 4.40
            self.cached_input_cost_per_1m = 0.275
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = Path(stats_dir) / f"{model_name}_cost_{timestamp}.json"
        # Initialize counters
        self.uncached_input_tokens = 0
        self.cached_input_tokens = 0
        self.output_tokens = 0
        
        # Register the write_stats method to be called when the program exits
        atexit.register(self.write_stats)
    
    def handle_usage(self, usage):
        self.output_tokens += usage.completion_tokens
        self.cached_input_tokens += usage.prompt_tokens_details.cached_tokens
        self.uncached_input_tokens += usage.prompt_tokens - self.cached_input_tokens
    def get_stats(self):
        """Get a dictionary of all usage statistics."""
        uncached_input_cost = (self.uncached_input_tokens / 1e6) * self.uncached_input_cost_per_1m
        cached_input_cost = (self.cached_input_tokens / 1e6) * self.cached_input_cost_per_1m
        output_cost = (self.output_tokens / 1e6) * self.output_cost_per_1m
        return {
            "application_name": self.application_name,
            "timestamp": datetime.now().isoformat(),
            "model_name": self.model_name,
            "token_counts": {
                "uncached_input_tokens": self.uncached_input_tokens,
                "cached_input_tokens": self.cached_input_tokens,
                "output_tokens": self.output_tokens,

            },
            "costs": {
                "uncached_input_cost": uncached_input_cost,
                "cached_input_cost": cached_input_cost,
                "output_cost": output_cost,
                "total_cost": uncached_input_cost + cached_input_cost + output_cost
            },
        }
    
    def write_stats(self):
        """Write the usage statistics to a file."""
        stats = self.get_stats()
        
        # Create directory if it doesn't exist
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Write stats to file
        with open(self.output_file, 'w') as f:
            json.dump(stats, f, indent=4)
        
        # print(f"OpenAI usage statistics written to {self.stats_file_path}")
        # print(f"Total cost: ${stats['costs']['total_cost']:.4f}")


# Example usage:
# cost_estimator = OpenAICostEstimator(model_name="gpt-4")
# cost_estimator.add_input_tokens(500)
# cost_estimator.add_output_tokens(200)
# print(f"Current cost: ${cost_estimator.get_total_cost():.4f}")
