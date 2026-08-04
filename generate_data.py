import pandas as pd
import json
import os

# 确保 data 目录存在
os.makedirs('data', exist_ok=True)

try:
    # 读取 CSV
    df = pd.read_csv('source_list.csv', encoding='utf-8')
    print(f"📖 读取到 {len(df)} 条记录")
    
    # 删除 region 列（如果存在）
    if 'region' in df.columns:
        df = df.drop(columns=['region'])
        print("🗑️ 已移除 region 列")
    
    # 确保字段顺序统一
    columns_order = ['date', 'title', 'url', 'description']
    # 只保留存在的列
    existing_columns = [col for col in columns_order if col in df.columns]
    df = df[existing_columns]
    
    # 转换为字典列表
    records = df.to_dict(orient='records')
    
    # 保存为 JSON
    with open('data/wallpapers.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成 data/wallpapers.json，共 {len(records)} 张壁纸")
    print(f"📋 字段: {list(records[0].keys()) if records else '无数据'}")
    
except FileNotFoundError:
    print("❌ 错误: 找不到 source_list.csv 文件")
except Exception as e:
    print(f"❌ 错误: {str(e)}")