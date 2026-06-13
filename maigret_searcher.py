import asyncio
import logging
import sys
import os
import io
from maigret import search as maigret_search
from maigret.sites import MaigretDatabase

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger("maigret")
logger.setLevel(logging.ERROR)

async def run_search(username, top, timeout, db):
    print(f"\n[*] Начало поиска для пользователя: {username}")
    print(f"[*] Проверка на топ-{top} сайтах...")

    previous_level = logger.level
    logger.setLevel(logging.CRITICAL)

    try:
        sites = db.ranked_sites_dict(top=top)
        
        results = await maigret_search(
            username=username,
            site_dict=sites,
            logger=logger,
            timeout=timeout,
            is_parsing_enabled=True,
            no_progressbar=False,
        )

        found_count = 0
        print("\n[+] Найденные аккаунты:")
        for site_name, result in results.items():
            if result["status"].is_found():
                found_count += 1
                url = result.get("url_user", "URL не найден")
                print(f" - {site_name}: {url}")
        
        if found_count == 0:
            print("[-] Аккаунтов не найдено.")
        else:
            print(f"\n[*] Поиск завершен. Найдено аккаунтов: {found_count}")

    except Exception as e:
        print(f"[!] Произошла ошибка во время поиска: {e}")
    finally:
        logger.setLevel(previous_level)

async def main():
    print("="*50)
    print("      MAIGRET USERNAME SEARCHER     ")
    print("="*50)

    try:
        db = MaigretDatabase()
        import maigret.sites
        data_path = os.path.join(os.path.dirname(maigret.sites.__file__), 'resources', 'data.json')
        
        if not os.path.exists(data_path):
            print(f"[!] Ошибка: Файл базы данных не найден по пути {data_path}")
            return

        db.load_from_path(data_path)
        print("[*] База данных успешно загружена.")

        while True:
            try:
                print("\n" + "-"*30)
                username = input("Введите имя пользователя для поиска (или 'exit' для выхода): ").strip()
                
                if not username:
                    continue
                if username.lower() in ['exit', 'quit', 'выход']:
                    print("[*] Завершение работы. До свидания!")
                    break

                top_input = input("Количество сайтов для проверки [по умолчанию 500]: ").strip()
                top = int(top_input) if top_input.isdigit() else 500

                timeout_input = input("Таймаут в секундах [по умолчанию 30]: ").strip()
                timeout = int(timeout_input) if timeout_input.isdigit() else 30

                await run_search(username, top, timeout, db)
            except KeyboardInterrupt:
                print("\n[*] Поиск прерван. Возврат в меню...")
                continue

    except Exception as e:
        print(f"[!] Критическая ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Программа закрыта.")
        sys.exit(0)
