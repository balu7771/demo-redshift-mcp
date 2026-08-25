def main() -> None:
    """Launch the Insurance Customer Migration Analyzer."""
    import gradio as gr
    from .app import create_interface
    interface = create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft())
