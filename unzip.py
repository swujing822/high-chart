import zipfile
import os

# 路径配置
zip_path = 'drive.zip'
extract_to = './drive'  # 解压到 drive 文件夹（可改成你想要的位置）

# 创建目标目录（如果不存在）
os.makedirs(extract_to, exist_ok=True)

# 解压
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

print(f"✅ 解压完成，文件已提取到：{extract_to}")
