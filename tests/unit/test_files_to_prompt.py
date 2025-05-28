import os
import tempfile
from unittest import mock

from openhands.runtime.plugins.agent_skills.files_to_prompt import process_files_to_prompt

def test_process_files_to_prompt():
    # Create some test files
    with tempfile.TemporaryDirectory() as tmpdir:
        file1_path = os.path.join(tmpdir, 'file1.txt')
        file2_path = os.path.join(tmpdir, 'file2.py')

        with open(file1_path, 'w') as f:
            f.write('Test content 1')

        with open(file2_path, 'w') as f:
            f.write('Test content 2')

        # Test with default output file
        result = process_files_to_prompt([file1_path, file2_path])
        assert os.path.exists('testing.json')
        with open('testing.json', 'r') as f:
            content = f.read()
            assert 'file1.txt' in content
            assert 'Test content 1' in content
            assert 'file2.py' in content
            assert 'Test content 2' in content

        # Test with custom output file
        custom_output = os.path.join(tmpdir, 'custom_output.txt')
        result = process_files_to_prompt([file1_path, file2_path], output_file=custom_output)
        assert os.path.exists(custom_output)

        # Test with markdown format
        md_output = os.path.join(tmpdir, 'output.md')
        result = process_files_to_prompt([file1_path, file2_path], output_file=md_output, markdown=True)
        with open(md_output, 'r') as f:
            content = f.read()
            assert 'file1.txt' in content
            assert '```' in content  # Check for code block marker

        # Test with line numbers
        ln_output = os.path.join(tmpdir, 'output_ln.txt')
        result = process_files_to_prompt([file1_path, file2_path], output_file=ln_output, line_numbers=True)
        with open(ln_output, 'r') as f:
            content = f.read()
            assert '1  Test content 1' in content

        # Test with empty file list
        empty_output = os.path.join(tmpdir, 'empty_output.txt')
        process_files_to_prompt([], output_file=empty_output)
        assert os.path.exists(empty_output)

        # Test error handling
        with mock.patch('subprocess.run', side_effect=Exception('Test error')):
            assert 'Error processing files: ' in process_files_to_prompt([file1_path], output_file=custom_output)