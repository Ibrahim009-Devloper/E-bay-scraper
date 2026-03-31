from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp
import os
from proxy import proxy
import pandas as pd
import concurrent.futures


class EbayProductScraper():
    def collact_product_scraper(self,start,end):
        sb = sb_cdp.Chrome(uc=True,headless =True)
        endpoint_url = sb.get_endpoint_url()
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(endpoint_url)
            context = browser.new_context(proxy= proxy)
            page = context.new_page()
            
            try:
                add_count = 0
                all_product_info = []
                
                query = "Mobile phone"
                for page_no in range(start,end+1):
                    print(f"scraping page no. {page_no}")
                    page.goto(f"https://www.ebay.com/sch/i.html?_nkw={query}&_sacat=0&_from=R40&_pgn={page_no}")
                    page.wait_for_load_state("domcontentloaded")
                    
                    product_containers = page.locator("//div[@class='su-card-container__content']")
                    count = product_containers.count()
                    print(count)
                    product_container = product_containers.all()
                    for container in product_container:
                        add_count += 1
                        product_link = container.locator("//a[@class='s-card__link']")
                        if product_link.count()> 0:
                            link = product_link.first.get_attribute("href")
                            if link:
                                
                                short_url = link.split("?")[0]
                                title_el = container.locator("//div[@role='heading']//span[contains(@class,'su-styled-text primary default')]")
                                
                                title = title_el.first.inner_text() if title_el.count() > 0 else "No title found"
                                if "Shop on eBay" in title:
                                    continue
                                price_el = container.locator("//span[contains(@class,'s-card__price')]")
                                if price_el.count()> 0:
                                    price = "".join(price_el.all_inner_texts())
                                else:
                                    pass

                                location_el = container.locator("//span[contains(text(),'Located in')]")
                                location = location_el.inner_text() if location_el.count()>0 else "N/A"
                                sold_el = container.locator("//span[contains(text(),'sold')]")
                                sold = sold_el.inner_text() if sold_el.count() > 0 else "N/A"
                                condition_el = container.locator("//div[@class='s-card__subtitle']//span")
                                condition = "N/A"
                                if condition_el.count() > 0:
                                    con_text = condition_el.first.inner_text()
                                    if "Brand New" in con_text or "Pre-Owned" in con_text:
                                        condition = con_text
                                

                                delevary_el = container.locator("//span[contains(text(),'delivery')]")
                                delevary = delevary_el.inner_text() if delevary_el.count() > 0 else "N/A"

                                positive_review_el = container.locator("//span[contains(text(),'positive')]")
                                positive_review = positive_review_el.inner_text() if positive_review_el.count() > 0 else "No Review"

                                Rating_el = container.locator("//div[@class='x-star-rating']//span[@class='clipped']")
                                Rating = Rating_el.inner_text() if Rating_el.count() > 0 else "NO Rating"

                                all_product_info.append({
                                    "title": title,
                                    "price": price,
                                    "location": location,
                                    "sold": sold,
                                    "delevary":delevary,
                                    "condition":condition,
                                    "positive_review": positive_review,
                                    "Rating":Rating,
                                    "url": short_url
                                })
                return all_product_info
            except Exception as e:
                print(f"the errro is {e}")
            
    def run_parallel_browser(self):
        total_page = 1
        theath = 1
        page_par_thread = total_page // theath
        all_product_info = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=theath) as executor:
            future = []
            for i in range(theath):
                start = i*page_par_thread+1
                end = start +page_par_thread - 1
                future.append(executor.submit(self.collact_product_scraper,start,end))
            for future in concurrent.futures.as_completed(future):
                all_product_info.extend(future.result())

        folder_path = "Row_Data"
        file_name = "Ebay_mobile_product.xlsx"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        df = pd.DataFrame(all_product_info)
        df.to_excel(f"{folder_path}/{file_name}")
        print(f"product save to {folder_path} as {file_name}")


if __name__ == "__main__":
    scrape = EbayProductScraper()
    scrape.run_parallel_browser()




