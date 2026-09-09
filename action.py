import os
import warnings
from duckduckgo_search import DDGS
import primp

def search(query: str) -> str:
    """
    基于 DuckDuckGo 的网页搜索引擎工具。
    无需 API Key，响应迅速，返回前 3 条搜索结果的标题与内容摘要。
    """
    print(f"🔍 正在执行 [DuckDuckGo] 网页搜索: {query}")
    try:
        # 屏蔽库内部由于更名打印的警告提示
        with warnings.catch_warnings():
            old_warn = warnings.warn
            warnings.warn = lambda *args, **kwargs: None
            ddgs_context = DDGS()
            warnings.warn = old_warn

        with ddgs_context as ddgs:
            # 兼容国内代理网络环境（开启重定向，避免随机 TLS 指纹冲突）
            ddgs.client = primp.Client(
                proxy=ddgs.proxy,
                timeout=ddgs.timeout,
                cookie_store=True,
                referer=True,
                impersonate=None,
                follow_redirects=True,
                verify=True,
            )
            results = ddgs.text(query, max_results=6)

            if not results:
                return f"对不起，没有找到关于 '{query}' 的信息。"

            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('body', '')}"
                for i, res in enumerate(results)
            ]
            return "\n\n".join(snippets)

    except Exception as e:
        return f"搜索时发生错误: {e}"


if __name__ == "__main__":
    test_query = "英伟达最新的GPU型号是什么"
    print(search(test_query))