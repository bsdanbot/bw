// functions/api/list.js
export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  // 获取分页参数
  const page = parseInt(url.searchParams.get('page')) || 1;
  const pageSize = parseInt(url.searchParams.get('size')) || 30;

  // 验证参数
  if (page < 1) {
    return new Response(JSON.stringify({
      error: 'page 参数必须大于等于 1'
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  if (pageSize < 1 || pageSize > 100) {
    return new Response(JSON.stringify({
      error: 'size 参数必须在 1-100 之间'
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const host = url.origin;
    
    // ★★★ 修改：从完整数据中分页，而不是读取分页文件 ★★★
    const jsonUrl = `${host}/data/wallpapers.json`;
    const fetchResp = await fetch(jsonUrl, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'CloudflarePages-Function'
      }
    });

    if (!fetchResp.ok) {
      return new Response(JSON.stringify({
        error: '无法加载壁纸数据'
      }), {
        status: 502,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const allData = await fetchResp.json();

    if (!Array.isArray(allData) || allData.length === 0) {
      return new Response(JSON.stringify({
        error: '暂无壁纸数据'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // ★★★ 分页计算（按日期降序） ★★★
    const sortedData = [...allData].sort((a, b) => b.date.localeCompare(a.date));
    const total = sortedData.length;
    const totalPages = Math.ceil(total / pageSize);
    const start = (page - 1) * pageSize;
    const end = Math.min(start + pageSize, total);
    const items = sortedData.slice(start, end);

    // ★★★ 返回分页数据 ★★★
    return new Response(JSON.stringify({
      code: 0,
      data: {
        items: items,
        page: page,
        pageSize: pageSize,
        total: total,
        totalPages: totalPages,
        hasMore: page < totalPages
      }
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=3600',
        'Access-Control-Allow-Origin': '*'
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      error: '服务器错误',
      message: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
