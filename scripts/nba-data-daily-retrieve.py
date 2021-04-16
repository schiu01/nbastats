#!/usr/bin/env python
# coding: utf-8

# In[3]:


import urllib3
from datetime import datetime, timedelta
import json as js



class NBADataRetrieve:
    
    ## Init routine 
    def __init__(self, **kwargs):
        
        ## offet day
        offset_days = kwargs.get("offset_days")
        self.json_dir = kwargs.get("json_dir")
        
        ## schedule gameday template url
        self.schedule_url_tmpl = "https://ca.global.nba.com/stats2/season/schedule.json?countryCode=CA&gameDate={{game_date}}&locale=en&tz=-5"
        
        ## Play by Play URL 
        self.pbp_url_tmpl  = "https://ca.global.nba.com/stats2/game/playbyplay.json?gameId={{game_id}}&locale=en&period={{period_num}}"
        
        ## Calculate the day by offset
        schedule_date = datetime.now() - timedelta(offset_days)
        self.schedule_date_str = schedule_date.strftime("%Y-%m-%d")
        
        ## Rebuild the schedule URL.
        self.schedule_url = self.schedule_url_tmpl.replace("{{game_date}}", self.schedule_date_str)
        
        ## SEt User Agent - simulate browser
        user_agent_header = urllib3.make_headers(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")
        self.http = urllib3.PoolManager(headers=user_agent_header)

        ##
        self.games_array = []
        self.pbp = {}

    def run(self):
        if(self.get_schedule() == True):
            self.get_pbp()
    def get_pbp(self):
        for game_id in (self.games_array):
            self.pbp[game_id] = []
            for period_num in range(1,5):
                pbp_url = self.pbp_url_tmpl.replace("{{game_id}}", str(game_id))
                pbp_url = pbp_url.replace("{{period_num}}", str(period_num))
                pbp_response = self.http.request("GET", pbp_url)
                pbp_filename = "%spbp_%s_%s_p%s.json"%(self.json_dir, self.schedule_date_str, str(game_id), str(period_num))
                pbp_fd = open(pbp_filename,"w")
                pbp_fd.write(pbp_response.data.decode())
                pbp_fd.close()

    def get_schedule(self):
        return_status = False
        try:
            response = self.http.request("GET", self.schedule_url)
            schedule_json_data = js.loads(response.data.decode())
            if(self.save_schedule_data(schedule_json_data) == True):
                self.parse_schedule(schedule_json_data)
                print(self.games_array)
                return_status = True
            
        except Exception as e:
            self.log(e)
        
        return return_status


    def save_schedule_data(self, json_data):
        try:
            fd = open(self.json_dir + "nba_schedule_%s.json"%(self.schedule_date_str),"w")
            fd.write(str(json_data))
            fd.close()
            return True
        except Exception as e:
            self.log("Error in writing nba schedule file %s"%(self.schedule_date_str))
            self.log(str(e))
            return False

    def parse_schedule(self, json_data):
        payload_dates = json_data["payload"].get("dates")
        for gamedates in (payload_dates):
            for gamedate in (gamedates["games"]):
                self.games_array.append(gamedate["profile"]["gameId"])
        
    def log(self, message):
        print(message)
        
        
## main routine
data_retrieve = NBADataRetrieve(offset_days=1, json_dir = "/opt/sports/nba/json/")
data_retrieve.run()

