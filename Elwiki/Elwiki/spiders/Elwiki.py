import scrapy
import os
import pandas as pd

class ElwikiSpider(scrapy.Spider):
    name = "elwiki"
    def __init__(self):
        self.all_skills = {}

    def start_requests(self):
        urls = [
            #'https://elwiki.net/w/Elsword',
            #'https://elwiki.net/w/Aisha',
            'https://elwiki.net/w/Chung'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        name = response.url.split("/")[-1]
        self.all_skills[name] = {}
        
        if not os.path.exists(name):
            os.mkdir(name)
        #Download copy of page
        filename = f'{name}/elwiki-{name}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
            
        #Extract Base Skills
        #with open(name+'/skillNames.txt', 'w') as f:
        base_skills = {}
        for skill in response.css('div.skill-outline'):
            skill_name = skill.css('a::attr(title)').extract()[0]
            if not skill_name == 'Extreme Heavenly Love':
                #Recurse to get skill information
                skill_link_sfx = skill.css('a::attr(href)').extract()[0]
                skill_link = 'https://elwiki.net'+skill_link_sfx
                print('***'+name+' - '+skill_name+'***')
                base_skills[skill_name] = self.skill_parse(skill_link)
            break
        
        #Define job classes and Add Base Skills
        not_list = response.css('div.class-tree').css('div.has-arrow').css('a::attr(title)').extract()
        for job_class in response.css('div.class-tree').css('a::attr(title)').extract():
            if not job_class in not_list:   #aka 3rd job class
                self.all_skills[name][job_class] = base_skills
        
        #Tranverse through classes and jobs
        for job_name in response.css('div.class-tree').css('a::attr(href)').extract()[1:]:
            job_link = 'https://elwiki.net'+job_name
            yield scrapy.Request(url=job_link, callback=self.parse_job)
    
    #Handle later
    def skill_parse(self, skill_link):
        #TODO - Handle Passives
        skill_export = {}
        tables = pd.read_html(skill_link)
        
        #Extract first table: base info
        skill_export['base_info'] = tables[1].to_numpy().tolist()
        
        #Extract second table: main info
        skill_export['info'] = tables[2].to_numpy().tolist()
        
        #Extract third table: traits
        skill_export['traits'] = tables[3].to_numpy().tolist()
        
        #Extract fourth table if exists: total damage
        if 'PvE' in tables[4].to_numpy()[0][0]:
            skill_export['total_damage'] = tables[4].to_numpy().tolist()
        return skill_export
            
    def parse_job(self, response):
        class_skills = {}
        base_class = response.css('div.has-arrow')[0].css('a::attr(title)').extract()[0]
        job_class = response.css('div.class-tree').css('div')[-1].css('a::attr(title)').extract()[0]
        skills = {}
        #with open(f'{base_class}/elwiki-{name}.html', 'wb') as f:
            #f.write(response.body)
        #with open(base_class+'/skillNames.txt', 'a') as f:
        for skill in response.css('div.skill-outline'):
            skill_name = skill.css('a::attr(title)').extract()[0]
            skill_link_sfx = skill.css('a::attr(href)').extract()[0]
            skill_link = 'https://elwiki.net'+skill_link_sfx
            print('***'+base_class+'/'+job_class+' - '+skill_name+'***')
            skills[skill_name] = self.skill_parse(skill_link)
            #f.write(skill_name+": "+skill_link+"\n")
            break
        
        #Update export
        yield self.all_skills[base_class][job_class].update(skills)