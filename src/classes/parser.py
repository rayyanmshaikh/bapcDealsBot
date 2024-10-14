import json
from typing import List, Dict
from httpx import AsyncClient, Response
from parsel import Selector
from loguru import logger as log

client = AsyncClient(
    http2=True,
    headers={
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": "intl_splash=false"
    },
    follow_redirects=True
)


def parse_subreddit(response: Response) -> List[Dict]:
    """parse article data from HTML"""
    selector = Selector(response.text)

    post_data = []
    for box in selector.xpath("//article"):
        link = box.xpath(".//a/@href").get()
        post_data.append({
            box.xpath("./@aria-label").get().lower(): {
                "link": "https://www.reddit.com" + link if link else None,
                "publishingDate": box.xpath(".//shreddit-post/@created-timestamp").get()}
        })

    cursor_id = selector.xpath("//shreddit-post/@more-posts-cursor").get()
    return {"post_data": post_data, "cursor": cursor_id}


async def scrape_subreddit(subreddit_id: str, sort, max_pages: int = None):
    """scrape articles on a subreddit"""
    base_url = f"https://www.reddit.com/r/{subreddit_id}/new"
    response = await client.get(base_url)
    subreddit_data = {}
    data = parse_subreddit(response)
    subreddit_data["posts"] = data["post_data"]
    cursor = data["cursor"]

    def make_pagination_url(cursor_id: str):
        return f"https://new.reddit.com/svc/shreddit/community-more-posts/new/?after={cursor_id}%3D%3D&t=DAY&name=bapcsalescanada&feedLength=3&sort={sort}"

    while cursor and (max_pages is None or max_pages > 0):
        url = make_pagination_url(cursor)
        response = await client.get(url)
        data = parse_subreddit(response)
        cursor = data["cursor"]
        post_data = data["post_data"]
        subreddit_data["posts"].extend(post_data)
        if max_pages is not None:
            max_pages -= 1

    log.success(f"scraped {len(subreddit_data['posts'])} posts from the subreddit: r/{subreddit_id}")
    return subreddit_data


async def run():
    data = await scrape_subreddit(
        subreddit_id="bapcsalescanada",
        sort="new",
        max_pages=1
    )

    with open("data/subreddit.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
