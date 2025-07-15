
GITHUB_TOKENS = [
    "your_token_1",
    "your_token_2",
    "your_token_3"   
]


SEARCH_SETTINGS = {
    "query": "language:python",
    "max_repos": 1000,               # Максимальное количество репозиториев
    "per_page": 50,                 # Репозиториев на страницу
    "request_delay": 1,             # Задержка между запросами (сек)
    "rate_limit_delay": 60          # Задержка при лимите (сек)
}

TELEGRAM_REGEX = r"\d{8,10}:[A-Za-z0-9_-]{35}"

# Ищем в этих файлах
TARGET_FILES = [
    "config.py",
    ".env",
    "settings.py",
    "configuration.yml",
    "docker-compose.yml"
]

# Logs
LOG_SETTINGS = {
    "level": "INFO",                
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "scan_log.txt"          
    #"file": None  -  для вывода только в консоль
}