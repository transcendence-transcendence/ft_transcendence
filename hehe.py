import os

# 파일 내용을 저장할 파일 이름
output_file = "test.txt"

# 검색할 디렉토리와 파일 확장자 목록
directories = [
    "game/templates",
    "main/static/js/components",
    # "main/templates/",
    # "main/views",
]
extensions = [".html", ".py", ".js"]

# 특정 파일 절대 경로 목록
specific_files = [
    os.path.abspath("main/urls.py"),  # 원하는 파일의 절대 경로 추가
    os.path.abspath("game/urls.py"),  # 예: views.py의 절대 경로
    os.path.abspath("game/views.py"),  # 예: views.py의 절대 경로
]

# 결과 저장
with open(output_file, "w", encoding="utf-8") as outfile:
    for directory in directories:
        if os.path.exists(directory):  # 디렉토리가 존재하는지 확인
            for root, _, files in os.walk(directory):  # 디렉토리 내 모든 파일 탐색
                for file in files:
                    file_path = os.path.join(root, file)
                    abs_file_path = os.path.abspath(file_path)  # 파일의 절대 경로
                    if abs_file_path in specific_files or any(file.endswith(ext) for ext in extensions):  # 절대 경로 또는 확장자 필터링
                        try:
                            with open(file_path, "r", encoding="utf-8") as infile:
                                outfile.write(f"### {file_path}\n")
                                outfile.write("```\n")
                                outfile.write(infile.read())
                                outfile.write("\n```\n\n")
                        except Exception as e:
                            outfile.write(f"### {file_path}\n")
                            outfile.write("```\n")
                            outfile.write(f"Error reading file: {e}")
                            outfile.write("\n```\n\n")
        else:
            print(f"Directory {directory} does not exist. Skipping.")

print(f"File contents have been saved to {output_file}.")
