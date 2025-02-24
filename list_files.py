import os

def list_files(directory):
    try:
        files = os.listdir(directory)
        for file in files:
            print(file)
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    directory_path = 'c:\\Users\\josep\\Projects\\personal\\omni-engineer-personal'
    list_files(directory_path)