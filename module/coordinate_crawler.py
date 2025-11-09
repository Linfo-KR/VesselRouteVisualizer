import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tqdm import tqdm
import os
from typing import Union

class CoordinateCrawler:
    """
    shipxplorer.com에서 항만 기본 정보와 상세 좌표를 병렬 처리로 빠르게 크롤링하는 클래스.
    
    - 1단계: 전체 항만 목록에서 국가명, 항만명, 항만 코드를 수집합니다.
    - 2단계: 각 항만 코드를 병렬로 처리하여 상세 페이지에서 위도(Latitude)와 경도(Longitude)를 수집합니다.
    """

    BASE_URL = "https://www.shipxplorer.com/data/ports"

    def __init__(self, headless=True, max_workers=10):
        """
        크롤러를 초기화합니다.
        :param headless: True일 경우 브라우저 UI 없이 백그라운드에서 실행합니다.
        :param max_workers: 동시에 실행할 최대 스레드(일꾼) 수.
        """
        self.headless = headless
        self.max_workers = max_workers

    @staticmethod
    def _setup_driver(headless: bool) -> webdriver.Chrome:
        """
        최적화된 옵션으로 Selenium WebDriver를 설정하고 반환합니다.
        :param headless: 헤드리스 모드 사용 여부
        :return: 설정된 Chrome WebDriver 객체
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        
        # 간단한 최적화: 이미지 로딩 비활성화
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def get_port_list(self) -> list[dict]:
        """
        1단계: 전체 항만 목록 페이지에서 국가, 항만명, 항만 코드를 크롤링합니다.
        """
        driver = self._setup_driver(self.headless)
        port_list = []
        print("Starting to collect the main port list...")
        
        try:
            driver.get(self.BASE_URL)
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list.port-list")))
            
            country_sections = driver.find_elements(By.CSS_SELECTOR, "ul.list.port-list > li:not([id])")
            
            for section in country_sections:
                # Find the country name from the collapsible header
                country_div = section.find_element(By.CSS_SELECTOR, "div.collapsible.hidden")
                country_name_raw = country_div.get_attribute("id")
                country_name = country_name_raw.replace('-collapse', '').replace('_', ' ').title()

                # Find all port links within that country section
                port_links = country_div.find_elements(By.CSS_SELECTOR, "div.ports > a")
                
                for link in port_links:
                    href = link.get_attribute('href')
                    if not href or '/data/ports/' not in href:
                        continue
                    
                    # Extract port_code from href
                    port_code = href.split('/')[-1]
                    
                    # Use JavaScript to get the full text content, which can be more reliable
                    full_text = driver.execute_script("return arguments[0].textContent;", link).strip()
                    
                    # Extract clean port_name from the link's text
                    port_name = full_text.replace(port_code, '').strip()
                    
                    port_list.append({
                        "country_name": country_name,
                        "port_name": port_name,
                        "port_code": port_code
                    })
        except (TimeoutException, NoSuchElementException) as e:
            print(f"An error occurred while getting the port list: {e}")
        finally:
            driver.quit()
            
        print(f"Collected basic info for {len(port_list)} ports. Now starting to fetch coordinates.")
        return port_list

    @staticmethod
    def _fetch_coordinates_worker(port_info: dict, headless: bool) -> Union[dict, None]:
        """
        (일꾼 함수) 단일 항만 코드에 대한 좌표를 크롤링합니다.
        두 가지 전략을 순차적으로 시도하여 데이터 추출 성공률을 높입니다.
        1. 페이지 소스에서 window.init() JSON 객체를 파싱 (빠르고 효율적).
        2. 1번 실패 시, Selenium으로 DOM 요소를 직접 스크레이핑 (느리지만 다른 구조에 대응).
        
        :param port_info: 개별 항만 정보 딕셔너리
        :param headless: 헤드리스 모드 사용 여부
        :return: 위도, 경도 정보가 추가된 딕셔너리 또는 실패 시 None
        """
        driver = CoordinateCrawler._setup_driver(headless)
        port_code = port_info['port_code']
        port_url = f"{CoordinateCrawler.BASE_URL}/{port_code}"
        
        try:
            driver.get(port_url)
            
            # --- Strategy 1: Parse JSON from <script> tag ---
            try:
                page_source = driver.page_source
                match = re.search(r'window\.init\((.*?)\);?\s*<\/script>', page_source, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    data = json.loads(json_str)
                    if 'port' in data and 'lat' in data['port'] and 'lng' in data['port']:
                        lat = data['port']['lat']
                        lng = data['port']['lng']
                        port_info.update({'lat': lat, 'lng': lng})
                        # print(f"[{port_code}] Success with JSON method.") # Optional: for debugging which method worked
                        return port_info
            except Exception:
                # If JSON parsing fails for any reason, silently proceed to the next strategy.
                pass

            # --- Strategy 2: Scrape DOM elements (Fallback) ---
            # This strategy is for pages with the other HTML structure.
            try:
                wait = WebDriverWait(driver, 10)
                info_list_ul = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ListNew__ListStyle-sc-1kdnh14-1")))
                info_items = info_list_ul.find_elements(By.CSS_SELECTOR, "li.ListItem__ListItemStyle-sc-k0s881-0")
                
                if info_items:
                    first_list_item = info_items[0]
                    # Wait for content to load within the list item
                    WebDriverWait(first_list_item, 5).until(EC.presence_of_element_located((By.ID, "title")))
                    
                    titles = first_list_item.find_elements(By.ID, "title")
                    values = first_list_item.find_elements(By.ID, "value")
                    
                    lat, lng = None, None
                    for title, value in zip(titles, values):
                        title_text = title.text.strip().lower()
                        if 'latitude' in title_text:
                            lat = value.text.strip()
                        elif 'longitude' in title_text:
                            lng = value.text.strip()
                    
                    if lat and lng:
                        port_info.update({'lat': lat, 'lng': lng})
                        # print(f"[{port_code}] Success with DOM method.") # Optional: for debugging
                        return port_info
            except Exception:
                # If DOM scraping also fails, we'll proceed to the final return None.
                pass

            # If both strategies fail, silently return None.
            return None

        except Exception as e:
            print(f"[{port_code}] A critical error occurred: {e}")
            return None
        finally:
            driver.quit()

    def run(self) -> pd.DataFrame:
        """
        전체 크롤링 파이프라인을 병렬로 실행합니다.
        :return: 국가, 항만명, 항만코드, 위도, 경도 정보가 포함된 pandas DataFrame
        """
        ports = self.get_port_list()
        if not ports:
            return pd.DataFrame()

        all_port_data = []
        
        # ThreadPoolExecutor를 사용하여 병렬로 좌표 수집
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 각 항만 정보에 대한 작업을 제출
            futures = [executor.submit(self._fetch_coordinates_worker, port, self.headless) for port in ports]
            
            # tqdm을 사용하여 진행 상황을 시각적으로 표시
            for future in tqdm(as_completed(futures), total=len(ports), desc="Fetching Coordinates"):
                result = future.result()
                if result:
                    all_port_data.append(result)
                    
        return pd.DataFrame(all_port_data)


if __name__ == '__main__':
    try:
        # 최적화를 위해 headless=True로 설정, 동시 작업 스레드 수(max_workers)는 10으로 설정
        # PC 사양과 네트워크 환경에 따라 max_workers 수를 조절하여 성능을 최적화할 수 있습니다. (예: 5 ~ 20)
        crawler = CoordinateCrawler(headless=True, max_workers=10)
        
        port_data_df = crawler.run()
        
        if not port_data_df.empty:
            # CSV 파일 저장을 위한 디렉토리 생성
            output_dir = "./data/coordinate"
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, "port_coordinates.csv")
            
            port_data_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"\nCrawling complete! Saved {len(port_data_df)} port coordinates to '{output_path}'.")
        else:
            print("\nNo data was collected.")

    except Exception as e:
        print(f"An unexpected error occurred during the crawling process: {e}")