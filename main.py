import re
from bs4 import BeautifulSoup
from aiohttp import ClientSession
import asyncio
from fastapi import FastAPI, Path, Query, HTTPException, status
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()


async def retrieve_html_content(target_url: str) -> str:
    async with ClientSession() as client:
        resp = await client.get(target_url)
        if resp.status == 200:
            return await resp.text(encoding="utf-8")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ заборонено або сторінку не знайдено")


@app.get("/parse/{element_tag}")
async def parse_html_by_tag(element_tag: str = Path(..., description="HTML елемент для пошуку"),
                             page_url: str = Query(..., description="Посилання на веб-сторінку"),
                             keyword: str = Query(..., description="Ключове слово або фраза")):
    try:
        page_html = await retrieve_html_content(page_url)
        parser = BeautifulSoup(page_html, "lxml")
        matched_string = parser.find(string=re.compile(re.escape(keyword)))

        if matched_string:
            parent_elem = matched_string.find_parent(element_tag)
            if parent_elem:
                return {"element": element_tag, "text": parent_elem.get_text(strip=True)}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Відповідний вміст не знайдено")

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
