"""files-to-prompt module for OpenHands agent.

This module provides a function to use the files-to-prompt tool to process a list of file names and output
the result in a specified format.
"""

import os
import subprocess
import json

def process_files_to_prompt(file_names, output_file='testing.json', markdown=False, line_numbers=False):
    """Processes a list of file names using the files-to-prompt tool.

    Args:
        file_names: List of file paths to include.
        output_file: The path to the output file. Defaults to 'testing.json'.
        markdown: Output in Markdown format with fenced code blocks. Defaults to False.
        line_numbers: Add line numbers to the output. Defaults to False.

    Returns:
        The content of the output file.
    """
    if not file_names:
        return '' if not output_file else ''

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Prepare arguments
    args = ['files-to-prompt', '-o', output_file]
    if markdown:
        args.append('--markdown')
    if line_numbers:
        args.append('--line-numbers')

    # Use subprocess to run the files-to-prompt command
    try:
        with open(f'{os.environ["SANDBOX_ENV_DIR"]}/tmp/files_to_prompt_input.txt', 'w') as f:
            for file_name in file_names:
                f.write(file_name + '\n')

        env = {**os.environ, 'SANDBOX_INPUT_FILE': f'{os.environ["SANDBOX_ENV_DIR"]}/tmp/files_to_prompt_input.txt'}
        subprocess.run(args, check=True, env=env)

        # Read the output file
        with open(output_file, 'r') as f:
            return f.read()
    except Exception as e:
        return f'Error processing files: {str(e)}'