#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
generate_data.py - 将 source_list.csv 转换为 data/wallpapers.json
用于网站和 API 的数据源
支持从在线接口合并历史数据
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime
import hashlib
import requests

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

def fetch_history_data():
    """从在线接口获取历史数据（已经是目标格式）"""
    url = 'https://bw-2f9.pages.dev/data/data.json'
    try:
        print(f"📥 正在从 {url} 获取历史数据...")
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取到 {len(data)} 条历史记录")
            return data
        else:
            print(f"⚠️ 获取历史数据失败: HTTP {response.status_code}")
            return []
    except requests.exceptions.Timeout:
        print("⚠️ 获取历史数据超时，跳过")
        return []
    except Exception as e:
        print(f"⚠️ 获取历史数据出错: {e}")
        return []

def transform_record(row):
    """
    转换单条记录
    如果数据来自历史数据（已有完整字段），直接返回
    如果数据来自 CSV，进行转换
    """
    # ★★★ 如果已经有完整的 jpg 字段（来自历史数据），直接返回 ★★★
    if 'jpg' in row and row.get('jpg') and isinstance(row['jpg'], str) and row['jpg'].startswith('http'):
        return {
            'date': row['date'],
            'copyright': row.get('copyright', row.get('title', '')),
            'description': row.get('description', ''),
            'jpg': row['jpg'],
            'webp': row.get('webp', row['jpg']),
            'thumb': row.get('thumb', row['jpg'])
        }
    
    # ★★★ CSV 数据的处理逻辑 ★★★
    base_url = row['url']
    
    if pd.isna(base_url) or not isinstance(base_url, str):
        return {
            'date': row['date'],
            'copyright': row.get('title', ''),
            'description': row.get('description', ''),
            'jpg': '',
            'webp': '',
            'thumb': ''
        }
    
    base = base_url.replace('_UHD.jpg', '').replace('_1920x1080.jpg', '')
    
    if '_UHD' in base_url:
        base = base_url.replace('_UHD.jpg', '')
    elif '_1920x1080' in base_url:
        base = base_url.replace('_1920x1080.jpg', '')
    else:
        base = base_url.replace('.jpg', '')
    
    return {
        'date': row['date'],
        'copyright': row['title'],
        'description': row['description'],
        'jpg': f"{base}_UHD.jpg",
        'webp': f"{base}_UHD.jpg",
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
    
    # 2. 读取 CSV
    try:
        df_local = pd.read_csv(csv_path, encoding='utf-8')
        print(f"📖 本地 CSV 读取到 {len(df_local)} 条记录")
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
        sys.exit(1)
    
    if len(df_local) == 0:
        print("⚠️ 警告: CSV 文件为空，无法生成 JSON")
        sys.exit(0)
    
    # 3. CSV 数据验证
    required_columns = ['date', 'title', 'description', 'url']
    missing_columns = [col for col in required_columns if col not in df_local.columns]
    if missing_columns:
        print(f"❌ CSV 缺少必需列: {missing_columns}")
        print(f"   当前列: {list(df_local.columns)}")
        sys.exit(1)
    
    # 4. 格式化日期：20260804 -> 2026-08-04
    df_local['date'] = df_local['date'].astype(str).apply(
        lambda x: f"{x[:4]}-{x[4:6]}-{x[6:8]}" if len(x) == 8 else x
    )
    
    # 5. 获取历史数据（已经是目标格式，直接使用）
    history_data = fetch_history_data()
    history_records = []
    if history_data:
        print(f"✅ 历史数据已经是目标格式，无需转换")
        history_records = history_data
        print(f"📖 历史数据共 {len(history_records)} 条记录")
        # 显示历史数据的时间范围
        if history_records:
            dates = [r.get('date', '') for r in history_records if r.get('date')]
            if dates:
                print(f"   - 历史数据范围: {min(dates)} ~ {max(dates)}")
    else:
        print("ℹ️ 没有获取到历史数据")
    
    # 6. 合并数据
    if history_records:
        df_history = pd.DataFrame(history_records)
        # 只保留本地没有的历史数据（按日期去重）
        existing_dates = set(df_local['date'])
        df_history_new = df_history[~df_history['date'].isin(existing_dates)]
        print(f"🆕 新增历史数据 {len(df_history_new)} 条（已跳过本地已存在的日期）")
        
        # 合并
        df_combined = pd.concat([df_local, df_history_new], ignore_index=True)
    else:
        df_combined = df_local
    
    # 7. 按日期去重
    df_combined = df_combined.drop_duplicates(subset=['date'], keep='first')
    print(f"📊 合并后总记录数: {len(df_combined)}")
    
    # ★★★ 8. 过滤掉 jpg 为空的行（而不是 url） ★★★
    # 检查是否有 jpg 字段，如果没有则用 url 字段
    if 'jpg' in df_combined.columns:
        df_combined = df_combined[df_combined['jpg'].notna()]
        df_combined = df_combined[df_combined['jpg'].astype(str).str.len() > 0]
        print(f"📊 过滤掉 jpg 为空的行后: {len(df_combined)} 条记录")
    else:
        # 如果没有 jpg 字段，用 url 字段过滤
        df_combined = df_combined[df_combined['url'].notna()]
        df_combined = df_combined[df_combined['url'].astype(str).str.len() > 0]
        print(f"📊 过滤掉 url 为空的行后: {len(df_combined)} 条记录")
    
    # 9. 转换数据
    print("🔄 正在转换数据...")
    records = df_combined.apply(transform_record, axis=1).tolist()
    
    # 10. 按日期排序（最新的在前）
    records = sorted(records, key=lambda x: x['date'], reverse=True)
    
    # 11. 确保 data 目录存在
    ensure_directory('data')
    
    # 12. 生成 JSON
    json_path = 'data/wallpapers.json'
    old_hash = get_file_hash(json_path)
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"✅ 已生成 {json_path}，共 {len(records)} 条记录")
    except Exception as e:
        print(f"❌ 保存 JSON 失败: {e}")
        sys.exit(1)
    
    # 13. 验证生成的 JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            if len(saved_data) != len(records):
                print(f"⚠️ 验证失败: 期望 {len(records)} 条，实际 {len(saved_data)} 条")
            else:
                print(f"✅ 验证通过: {len(saved_data)} 条记录")
    except Exception as e:
        print(f"⚠️ 验证 JSON 失败: {e}")
    
    # 14. 显示数据概览
    if records:
        latest = records[0]
        oldest = records[-1]
        print(f"\n📊 数据概览:")
        print(f"   - 最新日期: {latest['date']}")
        print(f"   - 最旧日期: {oldest['date']}")
        print(f"   - 总记录数: {len(records)}")
        print(f"   - 字段列表: {list(records[0].keys())}")
        
        print(f"\n📋 最新记录示例:")
        print(f"   - 日期: {latest['date']}")
        copyright_text = latest['copyright']
        if len(copyright_text) > 50:
            print(f"   - 标题: {copyright_text[:50]}...")
        else:
            print(f"   - 标题: {copyright_text}")
        print(f"   - 图片: {latest['jpg'][:60]}...")
    
    # 15. 检查是否有变化
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
