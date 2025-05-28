import os
import subprocess
import tempfile

def test_files_to_prompt_integration():
    # Create some test files
    with tempfile.TemporaryDirectory() as tmpdir:
        file1_path = os.path.join(tmpdir, 'file1.txt')
        file2_path = os.path.join(tmpdir, 'file2.py')

        with open(file1_path, 'w') as f:
            f.write('Test content 1')

        with open(file2_path, 'w') as f:
            f.write('Test content 2')

        # Create a list of files to process
        file_list = os.path.join(tmpdir, 'file_list.txt')
        with open(file_list, 'w') as f:
            f.write(file1_path + '\n' + file2_path)

        # Install the files-to-prompt package from the cloned repository
        subprocess.run(['pip', 'install', '-e', './files-to-prompt'], check=True)

        # Run the files-to-prompt command with our test files
        output_file = os.path.join(tmpdir, 'testing.json')
        env = {**os.environ, 'SANDBOX_INPUT_FILE': file_list}
        subprocess.run(['files-to-prompt', '-o', output_file, file1_path, file2_path], env=env, check=True)

        # Check the output
        with open(output_file, 'r') as f:
            content = f.read()
            print("Output content:", content[:200] + "..." if len(content) > 200 else content)
            assert 'file1.txt' in content
            assert 'Test content 1' in content
            assert 'file2.py' in content
            assert 'Test content 2' in content

        print("Integration test passed!")

# Run the test
test_files_to_prompt_integration()