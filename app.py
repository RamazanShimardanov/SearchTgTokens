import re
import time
import json
from github import Github
from datetime import datetime
import logging
from config import (
    GITHUB_TOKENS,
    SEARCH_SETTINGS,
    TELEGRAM_REGEX,
    TARGET_FILES,
    LOG_SETTINGS
)

class GitHubTokenScanner:
    def __init__(self):
        self._setup_logging()
        self.gh = Github(GITHUB_TOKENS[0]) if GITHUB_TOKENS else None
        self.current_repo = 0
        self.found_count = 0
        self.output_file = "found_tokens.json"  

    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, LOG_SETTINGS["level"]),
            format=LOG_SETTINGS["format"],
            filename=LOG_SETTINGS["file"]
        )
        self.logger = logging.getLogger(__name__)

    def scan_repositories(self):
        print("=== Начало сканирования GitHub репозиториев ===")
        print(f"Параметры поиска: {SEARCH_SETTINGS['query']}")
        print(f"Максимальное количество репозиториев: {SEARCH_SETTINGS['max_repos']}")
        print(f"Результаты будут сохранены в: {self.output_file}\n")

        found_tokens = set()
        try:
            repos = self.gh.search_repositories(
                SEARCH_SETTINGS["query"],
                sort="updated",
                order="desc"
            )

            for repo in repos[:SEARCH_SETTINGS["max_repos"]]:
                self.current_repo += 1
                repo_info = f"{self.current_repo}. {repo.full_name}"
                
                tokens = self._scan_repository(repo)
                if tokens:
                    self.found_count += 1
                    found_tokens.update(tokens)
                    status = "✅ Найдено токенов: " + ", ".join(t[:10] + "..." for t in tokens)
                    self._save_tokens(tokens, repo.full_name)  
                else:
                    status = "❌ Токены не найдены"
                
                print(f"{repo_info.ljust(60)} {status}")
                time.sleep(SEARCH_SETTINGS["request_delay"])

        except Exception as e:
            self.logger.error(f"Ошибка при сканировании: {str(e)}")
            print(f"\n⚠️ Произошла ошибка: {str(e)}")

        self._save_final_results(found_tokens)  
        return found_tokens

    def _scan_repository(self, repo):
        found_tokens = set()
        try:
            contents = repo.get_contents("")
            for content in contents:
                if content.name.lower() in [f.lower() for f in TARGET_FILES]:
                    try:
                        file_content = content.decoded_content.decode('utf-8')
                        tokens = re.findall(TELEGRAM_REGEX, file_content)
                        if tokens:
                            found_tokens.update(tokens)
                            self.logger.info(f"Найдены токены в {repo.full_name}/{content.name}")
                    except Exception as e:
                        self.logger.warning(f"Ошибка чтения файла {repo.full_name}/{content.name}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Ошибка сканирования репозитория {repo.full_name}: {str(e)}")
        
        return found_tokens

    def _save_tokens(self, tokens, repo_name):
        """Сохраняет найденные токены в файл"""
        try:
            data = []
            try:
    
                with open(self.output_file, 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            
         
            for token in tokens:
                data.append({
                    "token": token,
                    "repository": repo_name,
                    "timestamp": datetime.now().isoformat()
                })
            
    
            with open(self.output_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Ошибка сохранения токенов: {str(e)}")

    def _save_final_results(self, tokens):
        """Финальное сохранение результатов с статистикой"""
        if not tokens:
            return
            
        try:
            result = {
                "metadata": {
                    "total_repositories": self.current_repo,
                    "repositories_with_tokens": self.found_count,
                    "unique_tokens": len(tokens),
                    "scan_date": datetime.now().isoformat(),
                    "search_query": SEARCH_SETTINGS["query"]
                },
                "tokens": list(tokens)  
            }
            
            with open(self.output_file, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            print(f"\nВсе найденные токены сохранены в {self.output_file}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения финальных результатов: {str(e)}")


if __name__ == "__main__":
    start_time = datetime.now()
    scanner = GitHubTokenScanner()
    
    print("🔍 Запуск сканера Telegram токенов...")
    tokens = scanner.scan_repositories()
    
    duration = datetime.now() - start_time
    print("\n=== Результаты сканирования ===")
    print(f"Всего проверено репозиториев: {scanner.current_repo}")
    print(f"Репо с токенами: {scanner.found_count}")
    print(f"Всего уникальных токенов: {len(tokens)}")
    print(f"Время выполнения: {duration}")
    
    if tokens:
        print("\nПоследние обнаруженные токены:")
        for i, token in enumerate(list(tokens)[-5:], 1): 
            print(f"{i}. {token[:15]}...")  
    else:
        print("\nТокены не обнаружены")