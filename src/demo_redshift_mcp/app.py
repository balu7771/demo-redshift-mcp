"""Gradio UI for Insurance Customer Migration Analysis."""

import gradio as gr
from .crew_agents import run_customer_migration_analysis
from .data_generator import generate_all_data
from pathlib import Path

# ============================================================================
# Initialize Data (if needed)
# ============================================================================

def ensure_data_exists():
    """Ensure mock data is generated."""
    data_dir = Path("./data")
    required_files = [
        data_dir / "competitor_expat_plans.xlsx",
        data_dir / "ratha_chakram_customers.csv",
        data_dir / "expat_competitive_tracking.csv",
    ]

    if not all(f.exists() for f in required_files):
        print("Mock data not found. Generating...")
        generate_all_data()

# ============================================================================
# Main Handler
# ============================================================================

def handle_question(user_query: str):
    """Execute the crew workflow and return results."""
    if not user_query:
        return "Please enter a question about customer migration."

    return run_customer_migration_analysis(user_query)

# ============================================================================
# Gradio Interface
# ============================================================================

def create_interface():
    """Create and return the Gradio interface."""
    ensure_data_exists()

    with gr.Blocks(
        title="Insurance Customer Migration Analyzer",
    ) as demo:
        gr.Markdown(
            """
            # 📊 Insurance Customer Migration Analyzer

            Ask questions about customer migration patterns from legacy to new product.

            **Example questions:**
            - "How many customers renewed into the new product?"
            - "How many customers left for competitors?"
            - "How many came back from competitors and why?"
            - "What's the overall migration summary?"
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., How many customers renewed into the new product?",
                    lines=3,
                )
                submit_btn = gr.Button("Analyze", variant="primary", size="lg")

            with gr.Column(scale=2):
                response_output = gr.Textbox(
                    label="Analysis Results",
                    lines=20,
                    max_lines=30,
                )

        # Connect button to handler
        submit_btn.click(
            fn=handle_question,
            inputs=question_input,
            outputs=response_output,
        )

        # Add example questions
        gr.Examples(
            examples=[
                "How many customers renewed into the new product?",
                "How many customers left and went to competitors?",
                "How many customers came back from competitors?",
                "Why did customers come back? What were the main reasons?",
                "Show me the overall migration summary.",
            ],
            inputs=question_input,
        )

    return demo

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft())
