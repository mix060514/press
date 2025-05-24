# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from psql.PG import PG
import pandas as pd
from datetime import datetime


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PressPipeline:
    def process_item(self, item, spider):
        self.items.append(item)
        return item

    def open_spider(self, spider):
        self.items = []
        spider.logger.info(f"Open {spider.name} spider")
        spider.start_time = datetime.now()
        
        # Initialize PostgreSQL connection
        self.pg = PG()
        
        # Create table if it doesn't exist
        self.pg.query("""
            CREATE TABLE IF NOT EXISTS press_release (
                id SERIAL PRIMARY KEY,
                spider TEXT,
                url TEXT UNIQUE,
                title TEXT,
                date TIMESTAMP,
                content TEXT,
                crawled_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # 加載已爬取的URL並設置在爬蟲中
        result = self.pg.query(f"SELECT url FROM press_release WHERE spider = '{spider.name}'")
        if result is not None and not result.empty:
            spider.crawled_urls = set(result['url'].tolist())
        else:
            spider.crawled_urls = set()
        
        
        spider.logger.info(f"已加載 {len(spider.crawled_urls)} 個已爬取的URL")
    
    def close_spider(self, spider):
        spider.logger.info(f"關閉 {spider.name} 爬蟲")
        spider.end_time = datetime.now()
        
        # 將項目轉換為DataFrame並插入數據庫
        if self.items:
            # 將datetime對象轉換為字符串以用於DataFrame
            items_processed = []
            for item in self.items:
                item_dict = ItemAdapter(item).asdict()
                # 添加爬取時間
                item_dict['crawled_at'] = datetime.now()
                items_processed.append(item_dict)
            
            df = pd.DataFrame(items_processed)
            
            # 使用臨時表來處理資料插入，避免重複鍵值錯誤
            temp_table_name = f'temp_press_release_{spider.name}_{int(datetime.now().timestamp())}'
            
            try:
                # 1. 創建臨時表並插入資料
                self.pg.insert_pg(df, temp_table_name, overwrite=True)
                
                # 2. 在單一事務中刪除重複資料並插入新資料
                upsert_sql = f"""
                DELETE FROM press_release 
                WHERE url IN (SELECT url FROM {temp_table_name});
                
                INSERT INTO press_release (spider, url, title, date, content, crawled_at)
                SELECT spider, url, title, date, content, crawled_at 
                FROM {temp_table_name}
                """
                self.pg.query(upsert_sql)
                
                spider.logger.info(f"已保存 {len(self.items)} 個項目到數據庫")
                
            finally:
                # 4. 清理臨時表
                self.pg.query(f"DROP TABLE IF EXISTS {temp_table_name}")
        
        # 關閉數據庫連接
        self.pg.close()
