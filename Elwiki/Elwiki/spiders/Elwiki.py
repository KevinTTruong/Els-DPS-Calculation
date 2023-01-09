import scrapy
import os

class QuotesSpider(scrapy.Spider):
    name = "elwiki"

    def start_requests(self):
        urls = [
            'https://elwiki.net/w/Chung',
            'https://elwiki.net/w/Elsword',
            'https://elwiki.net/w/Aisha'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-1]
        
        if not os.path.exists(page):
            os.mkdir(page)
        #Download copy of page
        filename = f'{page}/elwiki-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
            
        #Extract Skills
        with open(page+'/skillNames.txt', 'w') as f:
            for skill in response.css('div.skill-outline'):
                skill_name = skill.css('a::attr(title)').extract()[0]
                skill_link_sfx = skill.css('a::attr(href)').extract()[0]
                skill_link = 'https://elwiki.net/w/'+skill_link_sfx
                f.write(skill_name+": "+skill_link+"\n")
                #Recurse to get skill information
                #yield scrapy.Request(url=skill_link, callback=self.base_skill_parse)
        
        #Tranverse through classes and jobs
        for job_name in response.css('div.class-tree').css('a::attr(href)').extract()[1:]:
            job_link = 'https://elwiki.net'+job_name
            yield scrapy.Request(url=job_link, callback=self.parse_job)
        self.log(f'Saved file {filename}')
    
    #Handle later
    def base_skill_parse(self, response):
        skill = response.url.split("/")[-1]
        mc = response.css('div.image-wrap').css('a::attr(title)').extract()[0]
        with open(mc+'/'+skill+'.html', 'wb') as f:
            f.write(response.body)
        info = response.css('table')[4].css('tbody').css('tr')[4].css('td')[1].css('td::text').get(0)
        with open(mc+'/skills.txt','w') as f:
            f.write(skill+': '+info+'\n')
            
    def parse_job(self, response):
        base_class = response.css('div.has-arrow')[0].css('a::attr(title)').extract()[0]
        with open(base_class+'/skillNames.txt', 'a') as f:
            for skill in response.css('div.skill-outline'):
                skill_name = skill.css('a::attr(title)').extract()[0]
                skill_link_sfx = skill.css('a::attr(href)').extract()[0]
                skill_link = 'https://elwiki.net/w/'+skill_link_sfx
                f.write(skill_name+": "+skill_link+"\n")
                #Recurse to get skill information
                #yield scrapy.Request(url=skill_link, callback=self.base_skill_parse)