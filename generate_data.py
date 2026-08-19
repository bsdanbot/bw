#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
generate_data.py - 将 source_list.csv 转换为 data/wallpapers.json
用于网站和 API 的数据源
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime
import hashlib

# 设置输出编码（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def ensure_directory(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)

def get_file_hash(filepath):
    """获取文件的 MD5 哈希值，用于检测文件是否变化"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def transform_record(row):
    """
    转换单条记录
    将 CSV 中的字段映射为 JSON 格式
    """
    base_url = row['url']
    
    # 去除 _UHD 或 _1920x1080 等后缀，保留基础部分
    # 例如: https://cn.bing.com/th?id=OHR.AdorableOwlet_ZH-CN6929234033_UHD.jpg
    # 基础部分: https://cn.bing.com/th?id=OHR.AdorableOwlet_ZH-CN6929234033
    base = base_url.replace('_UHD.jpg', '').replace('_1920x1080.jpg', '')
    
    # 处理可能存在的其他后缀
    if '_UHD' in base_url:
        base = base_url.replace('_UHD.jpg', '')
    elif '_1920x1080' in base_url:
        base = base_url.replace('_1920x1080.jpg', '')
    else:
        # 如果没有后缀，移除 .jpg 后缀
        base = base_url.replace('.jpg', '')
    
    return {
        'date': row['date'],
        'copyright': row['title'],  # 对应原有的 title 字段
        'description': row['description'],
        'jpg': f"{base}_UHD.jpg",
        'webp': f"{base}_UHD.jpg",  # 如果 webp 不同，可单独处理
        'thumb': f"{base}_400x240.jpg"
    }

def main():
    """主函数"""
    print("=" * 60)
    print(f"  generate_data.py 开始运行")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 检查源文件是否存在
    csv_path = 'source_list.csv'
    if not os.path.exists(csv_path):
        print(f"❌ 错误: {csv_path} 不存在！")
        print("   请先运行 main.py 生成数据文件。")
        sys.exit(1)
    
    # 2. 检查 CSV 是否为空
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"📖 读取到 {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
        sys.exit(1)
    
    if len(df) == 0:
        print("⚠️ 警告: CSV 文件为空，无法生成 JSON")
        sys.exit(0)
    
    # 3. 数据验证
    required_columns = ['date', 'title', 'description', 'url']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ CSV 缺少必需列: {missing_columns}")
        print(f"   当前列: {list(df.columns)}")
        sys.exit(1)
    
    # 4. 格式化日期：20260804 -> 2026-08-04
    df['date'] = df['date'].astype(str).apply(
        lambda x: f"{x[:4]}-{x[4:6]}-{x[6:8]}" if len(x) == 8 else x
    )
    
    # 5. 检查是否有重复日期
    duplicate_dates = df[df['date'].duplicated()]
    if len(duplicate_dates) > 0:
        print(f"⚠️ 发现 {len(duplicate_dates)} 条重复日期记录:")
        for date in duplicate_dates['date'].head(5):
            print(f"   - {date}")
        # 去重：保留第一条
        df = df.drop_duplicates(subset=['date'], keep='first')
        print(f"   ✅ 去重后剩余 {len(df)} 条记录")
    
    # 6. 转换数据
    print("🔄 正在转换数据...")
    records = df.apply(transform_record, axis=1).tolist()
    
    # 7. 按日期排序（最新的在前）
    records = sorted(records, key=lambda x: x['date'], reverse=True)
    
    # 8. 确保 data 目录存在
    ensure_directory('data')
    
    # 9. 生成 JSON
    json_path = 'data/wallpapers.json'
    
    # 检查是否需要更新
    old_hash = get_file_hash(json_path)
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"✅ 已生成 {json_path}，共 {len(records)} 条记录")
    except Exception as e:
        print(f"❌ 保存 JSON 失败: {e}")
        sys.exit(1)
    
    # 10. 验证生成的 JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            if len(saved_data) != len(records):
                print(f"⚠️ 验证失败: 期望 {len(records)} 条，实际 {len(saved_data)} 条")
            else:
                print(f"✅ 验证通过: {len(saved_data)} 条记录")
    except Exception as e:
        print(f"⚠️ 验证 JSON 失败: {e}")
    
    # 11. 显示数据概览
    if records:
        latest = records[0]
        oldest = records[-1]
        print(f"\n📊 数据概览:")
        print(f"   - 最新日期: {latest['date']}")
        print(f"   - 最旧日期: {oldest['date']}")
        print(f"   - 总记录数: {len(records)}")
        print(f"   - 字段列表: {list(records[0].keys())}")
        
        # 显示最新一条的示例
        print(f"\n📋 最新记录示例:")
        print(f"   - 日期: {latest['date']}")
        print(f"   - 标题: {latest['copyright'][:50]}..." if len(latest['copyright']) > 50 else f"   - 标题: {latest['copyright']}")
        print(f"   - 图片: {latest['jpg'][:60]}...")
    
    # 12. 检查是否真的有变化
    new_hash = get_file_hash(json_path)
    if old_hash != new_hash:
        print(f"\n🔄 JSON 文件已更新")
        print(f"   旧哈希: {old_hash}")
        print(f"   新哈希: {new_hash}")
    else:
        print(f"\nℹ️ JSON 文件内容无变化")
    
    print("\n" + "=" * 60)
    print("  ✅ generate_data.py 执行完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)