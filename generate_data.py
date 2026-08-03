# generate_data.py - 完整修正版（包含 region 字段 + 增量更新）

import pandas as pd
import json
import os

# ★★★ 读取现有 JSON（增量更新）★★★
def load_existing_json(json_path):
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# 读取 CSV
df = pd.read_csv('source_list.csv', encoding='utf-8')

# 转换 CSV 为记录列表
records = []
for _, row in df.iterrows():
    date_str = str(row['date']).strip()
    if len(date_str) == 8:
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    else:
        formatted_date = date_str
    
    img_url = row['url']
    if pd.isna(img_url) or not img_url:
        continue
    if not img_url.startswith('http'):
        img_url = 'https://cn.bing.com' + img_url
    
    # ★★★ 读取 region 字段 ★★★
    region = row.get('region', 'zh-CN')
    if pd.isna(region):
        region = 'zh-CN'
    
    record = {
        'date': formatted_date,
        'copyright': str(row['title']) if pd.notna(row['title']) else '',
        'description': str(row['description']) if pd.notna(row['description']) else '',
        'jpg': img_url,
        'webp': img_url,
        'thumb': img_url.replace('_UHD.jpg', '_400x240.jpg'),
        'region': str(region)  # ★★★ 新增 region 字段 ★★★
    }
    records.append(record)

# ★★★ 合并现有数据（增量更新）★★★
existing_records = load_existing_json('data/wallpapers.json')

# 按 date + region 去重，保留新数据优先
all_records = {}
for r in existing_records:
    key = f"{r['date']}_{r.get('region', 'zh-CN')}"
    all_records[key] = r

for r in records:
    key = f"{r['date']}_{r.get('region', 'zh-CN')}"
    all_records[key] = r  # 新数据覆盖旧数据

# 转回列表并排序
merged_records = list(all_records.values())
merged_records.sort(key=lambda x: x['date'], reverse=True)

# ★★★ 保存 ★★★
os.makedirs('data', exist_ok=True)
with open('data/wallpapers.json', 'w', encoding='utf-8') as f:
    json.dump(merged_records, f, ensure_ascii=False, indent=2)

print(f'✅ 已生成 data/wallpapers.json，共 {len(merged_records)} 张壁纸')
