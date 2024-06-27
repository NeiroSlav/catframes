import os


DIRECRORY = "src/catframes/catmanager_sample"  # путь к сборочным файлам
OUTPUT_FILE = "src/catframes/catmanager.py" # путь к выходному файлу 

FILE_NAMES = [  # порядок файлов для сборки
    'task_flows.py',
    'sets_utils.py',
    'windows_utils.py',
    'windows.py',
    'main.py'
]


# сборка всех строк кода, есть флаг игнорирования строк импортов
def collect_code(file_path, ignore_imports: bool) -> list:
    code_lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            # если стоит флаг, то игнорируем строки с импортами
            if ignore_imports:
                if line.strip().startswith("import") or line.strip().startswith("from"):
                    continue
            code_lines.append(line)

    return code_lines


# запись всех строк кода в файл
def write_to_file(output_file: str, code_lines: list) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(code_lines)


def main():

    # добавление в начало строк из префикса
    all_code_lines = collect_code(
        os.path.join(DIRECRORY, "_prefix.py"),
        ignore_imports=False  # импорты не игнорируются
    )
    
    for fn in FILE_NAMES:
        all_code_lines += ['\n'] * 2  # украшательства
        all_code_lines += f'\n    #  из файла {fn}:'

        file_path = os.path.join(DIRECRORY, fn)
        all_code_lines += collect_code(file_path, ignore_imports=True)

        all_code_lines += ['\n'] * 2  # украшательства

    write_to_file(OUTPUT_FILE, all_code_lines)

if __name__ == "__main__":
    main()