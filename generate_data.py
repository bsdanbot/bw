import pandas as pd
import json
import os

os.makedirs('data', exist_ok=True)

# 读取 CSV
df = pd.read_csv('source_list.csv', encoding='utf-8')
print(f"📖 读取到 {len(df)} 条记录")

# 1. 格式化日期：20260804 -> 2026-08-04
df['date'] = df['date'].astype(str).apply(
    lambda x: f"{x[:4]}-{x[4:6]}-{x[6:8]}" if len(x) == 8 else x
)

# 2. 字段映射和拆分
def transform_record(row):
    base_url = row['url']
    # 去除 _UHD 或 _1920x1080 等后缀，保留基础部分
    # 例如: https://cn.bing.com/th?id=OHR.AdorableOwlet_ZH-CN6929234033_UHD.jpg
    # 基础部分: https://cn.bing.com/th?id=OHR.AdorableOwlet_ZH-CN6929234033
    base = base_url.replace('_UHD.jpg', '').replace('_1920x1080.jpg', '')
    
    return {
        'date': row['date'],
        'copyright': row['title'],
        'description': row['description'],
        'jpg': f"{base}_UHD.jpg",
        'webp': f"{base}_UHD.jpg",  # 如果 webp 不同，可单独处理
        'thumb': f"{base}_400x240.jpg"
    }

# 应用转换
records = df.apply(transform_record, axis=1).tolist()

# 保存为 JSON
with open('data/wallpapers.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"✅ 已生成 data/wallpapers.json，共 {len(records)} 条记录")
print(f"📋 字段: {list(records[0].keys()) if records else '无数据'}")