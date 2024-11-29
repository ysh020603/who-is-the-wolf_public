from package import LLM_model as llm
from dotenv import load_dotenv
import os
import json
from typing import List
import threading
import re
import time
import copy
import random



#  define relative function in gaming framework
class Gaming:
    # define variables in gaming framework

    lock = threading.Lock()

    prompt_system = """
==Game Rules==
- **游戏名称**：谁是卧底
- **角色分配**：每位玩家将获得一个词语，其中大多数玩家的词语相同，但**卧底**的词语**不同**。
- **描述阶段**：每位玩家用一句话描述自己的词语，注意不要直接说出词语本身。
- **投票环节**：每轮描述结束后，所有玩家将根据大家的描述投票选出可能是卧底的玩家。作为卧底的玩家，你的任务是尽量混淆视听，避免被淘汰。
- **淘汰机制**：得票最多的玩家将被淘汰。如果被淘汰的是卧底，则剩余玩家获胜；如果不是，则游戏继续，卧底有更大的机会获胜。
- **胜利条件**：游戏将持续进行，直至卧底被发现或卧底成功混淆视听，成为最后的胜者。

==strategy suggestion==
#### 卧底玩家建议：
- **模糊描述**：作为卧底，尝试使用更加模糊或广泛的描述，避免给出具体的信息，这样可以减少被猜中的风险。
- **模仿他人**：留意其他非卧底玩家的描述方式，尽量模仿他们的语气和风格，使自己的描述看起来更符合大众。
- **保持一致性**：即使描述较为模糊，也要确保前后描述的一致性，避免因前后矛盾而引起怀疑。

#### 平民玩家建议：
- **具体描述**：平民玩家应该尽量提供具体且相关的描述，这有助于增加描述的真实性和可信度。
- **避免过度解释**：虽然需要提供具体的描述，但避免过度解释或提供过多不必要的信息，以免显得过于刻意。
- **注意细节**：在描述时加入一些只有了解该词语的人才能注意到的小细节，这有助于增加描述的真实感。

==Describe example== 
它常常需要被重新系紧。
"""


    def __init__(self,
                api_key:str,
                words_table_path:str= "data/word_table.json", 
                state_record_path:str ="data/state/record_state.json", 
                result_record_path:str="data/record/",
                person_record_path:str="data/person.json",
                model:str="glm-4-flash",
                url:str="https://open.bigmodel.cn/api/paas/v4/",
                num_players: int=5,
                num_word:int=1,
                reverse:bool=False,
                wolf_order:List[int]=None,
                 ):
        '''
        - api_key # the api key to use

        - words_table_path # words_table_path word1 and word2 

        - state_record_path # the path where record the data in game 

        - model # the model to use 

        - record_path # the path where record the data in game

        - num_players # the number of players

        - mbti_record_path # the path where record person_mbti in game

        - result_record_path # the path where record result in game

        - num_word # the number of words

        - reverse # the order of word is reverse or not

        - wolf_order # the order of wolf
        '''
        self.api_key = api_key # the api key to use
        self.words_table_path = words_table_path # words_table_path word1 and word2
        self.state_record_path = state_record_path # the path where record process data in game
        self.model = model # the model to use
        self.result_record_path = result_record_path # the folder path where record the data in game
        self.num_players = num_players # the number of players
        self.record = {} # the record of the game
        self.url = url # the url to use
        self.person_record_path = person_record_path # the path where record person_mbti in game
        self.num_word = num_word
        self.reverse = reverse
        self.wolf_order = wolf_order

        '''
        record = {
            "word_plain": "",
            "word_wolf": "",
            "plain_order": [],
            "wolf_order": [],
            "result": "win", # wolf win or lose
            "Agent": true, # wolf Agent or simple
            "player_remain": [], 
            "now_round": 1，
            "turn_describe_1": {
                "player_1": "",
                "player_2": "",
                "player_3": "",
                "player_4": "",
                "player_5": ""
            },
            "experience":{
            "player_1": "",
            "player_2": ""
            },
            "turn_vote_1": {
                "player_1": "",
                "player_2": "" ...
            },
            "wolf_1": {

                
            } # wolf in Agent
            "plain_order_record": [],
            "wolf_order_record": [],
            "analyse_vote_1":{
                "player_1": "",
                "player_2": ""
            }
            "summary": {
                "player_1": "",
                "player_2": "" 
            },
            "analyse_describe_1":{
                "player_1": "",
                "player_2": "" 
            },
            player_out:[],
            "wrong_num":1,
            }
        '''

    def get_person_information(self)->None:
        '''
        get the person information from the mbti_record_path

        - num: the flag for the person
        '''
        self.record["person_information"] = {}
        with open(self.person_record_path,"r", encoding="utf-8") as f:
            person_table = json.load(f)
        for num in range(1,self.num_players+1):
            self.record["person_information"][f"player_{num}"] = f"""

==personality===
你需要在游戏中扮演如下的人格:

mbti为{random.choice(person_table["mbti"])}，年龄{random.choice(person_table["age"])}岁的{random.choice(person_table["gender"])}性{random.choice(person_table["career"])}。
"""

    
    def get_words(self,num:int, reverse:bool=False)->None:
        '''
        get the words from the words_table_path

        - reverse: if true, get the words in reverse order

        - num: the flag for the words
        '''
        with open(self.words_table_path,"r", encoding="utf-8") as f:
            words_table = json.load(f)
        if reverse:
            word2 = words_table["set%d"%num]["word1"]
            word1 = words_table["set%d"%num]["word2"]
        else:
            word1 = words_table["set%d"%num]["word1"]
            word2 = words_table["set%d"%num]["word2"]
        self.record["word_plain"] = word1
        self.record["word_wolf"] = word2
    
    def record_prompt(self,key_1:str,key_2:str,prompt_str:str)->None:
        '''
        record the prompt
        '''
        if f"{key_1}_prompt" not in self.record:
            self.record[f"{key_1}_prompt"] = {}
        else:
            pass
        self.record[f"{key_1}_prompt"][key_2] = prompt_str



    def call_and_record_simple(self, prompt_list:list, keyword_1:str, keyword_2:str)->None:
        '''
        call the api and record the response
        '''
        response = llm.api_call(self.api_key, self.url, self.model, prompt_list)
        self.lock.acquire()
        self.record[keyword_1][keyword_2] = response
        self.lock.release()


    def function_get_prompt_list(self, prompt_system:str, prompt_user_content:str)->list:
        '''
        get the prompt list by adding the prompt_user_content
        '''
        prompt_list = [{"role": "system", "content": prompt_system},
                       {"role": "user", "content": prompt_user_content}]
        return prompt_list


    def experience_simple(self, except_list:List[int]=[])->None:
        '''
        initialize the game
        '''
        self.get_person_information()
        wolf_order = self.wolf_order
        self.get_words(self.num_word,self.reverse)
        self.record["Agent"] = False
        self.record["wolf_order"] = wolf_order
        self.record["plain_order"] = [item for item in range(1,self.num_players+1) if item not in wolf_order]
        self.record["wolf_order_record"] = copy.deepcopy(wolf_order)
        self.record["plain_order_record"] = [item for item in range(1,self.num_players+1) if item not in wolf_order]
        self.record["player_remain"] = [item for item in range(1,self.num_players+1)]
        self.record["now_round"] = 1
        self.record["experience"] = {}
        self.record["player_out"] = []
        self.record["wrong_num"] = 0
        
        # experience
        threads = []
        for i in [item for item in self.record["player_remain"] if item not in except_list]:
            
            if i in wolf_order:
                word = self.record["word_wolf"]
            else:
                word = self.record["word_plain"]

            word_prompt = f"""
==task==
你现在正在这个游戏中，你的词汇是：{word}。
先对{word}进行分析，分析内容包括：

=={word}在游戏中可能对应的词==

==与{word}对应词的共同特征==


分析内容要求言简意赅，对应词汇不超过5个，特征要符合游戏规则。
只能生成相关分析，不要出现其他内容"""
            self.record_prompt("experience", "player_%d"%i, word_prompt)
            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], word_prompt)
            
            thread = threading.Thread(target=self.call_and_record_simple, 
                                      args=(prompt_list, "experience", "player_%d"%i))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    def describe_for_noerror(self, prompt_list:list, keyword_1:str, keyword_2:str)->None:
        '''
        check the describe result and repeat error process.
        '''
        response = llm.api_call(self.api_key, self.url, self.model, prompt_list)

        while True:
            prompt_error = ""

            if self.record["word_plain"] in response or self.record["word_wolf"] in response or "描述建议" in response:
                prompt_error = f"按照游戏规则,不能出现{[self.record['word_plain'], self.record['word_wolf']]}和“描述建议”,请你按照游戏规则重新描述。"
            elif len(response) > 40 :
                prompt_error = "按照游戏要求，你的描述过长或不符合要求，请按照游戏规则重新描述。"
            if prompt_error == "":
                self.lock.acquire()
                self.record[keyword_1][keyword_2] = response
                self.lock.release()
                break
            else:
                prompt_list.append({"role": "assistant", "content": response})
                prompt_list.append({"role": "user", "content": prompt_error})
                response = llm.api_call(self.api_key, self.url, self.model, prompt_list)
                self.record["wrong_num"]+=1


    def first_round_describe_simple(self,except_list:List[int]=[])->None:
        '''
        simple_state the first round of the game
        '''
        if "turn_describe_1" not in self.record:
            self.record["turn_describe_1"] = {}
        else:
            pass
        threads = []
        for i in [item for item in self.record["player_remain"] if item not in except_list]:
            
            if i in self.record["wolf_order"]:
                word = self.record["word_wolf"]
            else:
                word = self.record["word_plain"]    
            
            word_prompt = f"""==information before==
{self.record["experience"]["player_%d"%i]} 

==task==
你现在正在参与这个游戏，你的词汇是：{word}。
请你按照游戏规则进行本轮描述，不要出现{word}本身。
描述内容要求简短。最好只用几个字"""
            self.record_prompt("turn_describe_1", "player_%d"%i, word_prompt)
            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], word_prompt)
            
            thread = threading.Thread(target=self.describe_for_noerror, 
                                      args=(prompt_list, "turn_describe_1", "player_%d"%i))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    def vote_for_noerror(self, prompt_list:list, keyword_1:str, keyword_2:str, i:int)->None:
        '''
        check the vote result and repeat error process.
        '''
        response = llm.api_call(self.api_key, self.url, self.model, prompt_list)
        pattern = r'\[(.*?)\]'
        matches = re.findall(pattern, response)
        first_match = matches[0] if matches else None
        while True:
            prompt_error = ""
            try:
                first_match = first_match.split("_")[1]
                if int(first_match) in self.record["player_remain"]:
                    pass
                else:
                    prompt_error = "投票的玩家已经出局，请按照游戏规则重新投票。"
                if int(first_match) == i:
                    prompt_error = "不要把票投给自己，请按照游戏规则重新投票。"
            except:
                prompt_error = "投票格式错误，请重新生成。"

            if prompt_error == "":
                self.lock.acquire()
                self.record[keyword_1][keyword_2] = response
                self.lock.release()
                break
            else:
                prompt_list.append({"role": "assistant", "content": response})
                prompt_list.append({"role": "user", "content": prompt_error})
                response = llm.api_call(self.api_key, self.url, self.model, prompt_list)
                pattern = r'\[(.*?)\]'
                matches = re.findall(pattern, response)
                first_match = matches[0] if matches else None
                self.record["wrong_num"]+=1





    def vote_analyse_simple(self, except_list:List[int]=[])->None:
        '''
        analyse history in the game
        '''
        if "analyse_vote_%d"%self.record["now_round"] not in self.record:
            self.record["analyse_vote_%d"%self.record["now_round"]] = {}
        else:
            pass
        threads = []

        for i in [item for item in self.record["player_remain"] if item not in except_list]:
            if i in self.record["wolf_order"]:
                word_player = self.record["word_wolf"]
            else:
                word_player = self.record["word_plain"]
            
            if len(self.record["player_out"]) == 0:
                prompt = "==Describe history of other player==\n\n"
                prompt_end = f"""==task==
你是**player_{i}**,你现在正在参与这个游戏，
你的词汇是:**{word_player}**，请你根据游戏规则，分析Describe history
分析内容包括:
== {word_player}与Describe history of other player中每名玩家的描述是否相符==

==自己在游戏中的身份==
进行简短分析后给出自己身份的判断

==这轮投票要投给哪位玩家==
根据分析结果，投票要有理有据，不能进行随机选择
必须要**明确**投票给哪位玩家，**不能**投票给自己**player_{i}**。

内容要求言简意赅。
"""
            else:
                prompt = f"==summary of you in the game==\n\n {self.record["summary_%d"%(self.record["now_round"])]["player_%d"%i]}\n\n ==Describe history of other player=="
                prompt_end = f"""==task==
你是**player_{i}**,你现在正在参与这个游戏，
你的词汇是:**{word_player}**，请你根据游戏规则，分析Describe history
分析内容包括:
== {word_player}与Describe history of other player中每名玩家的描述是否相符==

==自己在游戏中的身份==
进行简短分析后给出判断

==这轮投票要投给哪位玩家==
根据分析结果，投票要有理有据，不能进行随机选择
必须要**明确**投票给哪位玩家，**不能**投票给自己**player_{i}**。
{str(self.record["player_out"])}里的玩家已经被淘汰了，请不要投给他们。

内容要求言简意赅。
"""

            for round_num in range(1, self.record["now_round"]+1):
                prompt += "- 第%s轮\n"%round_num
                for j in [item for item in self.record["player_remain"] if item != i]:
                    prompt += " - player_%d: "%j + self.record["turn_describe_%d"%round_num]["player_%d"%j] + "\n"
            
            prompt += prompt_end
            self.record_prompt("analyse_vote_%d"%self.record["now_round"], "player_%d"%i, prompt)
            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], prompt)
            thread = threading.Thread(target=self.call_and_record_simple, args=(prompt_list, 
                                                                                "analyse_vote_%d"%self.record["now_round"], 
                                                                                "player_%d"%i))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()


    def vote_simple(self, except_list:List[int]=[])->None:
        '''
        vote round of the game in simple state
        '''
        
        threads = []
        if "turn_vote_%d"%self.record["now_round"] not in self.record:
            self.record["turn_vote_%d"%self.record["now_round"]] = {}
        else:
            pass
        for i in [item for item in self.record["player_remain"] if item not in except_list]:
            player_in = set(["player_%d"%item for item in self.record["player_remain"] if item != i]) 
            prompt = self.record["analyse_vote_%d"%self.record["now_round"]]["player_%d"%i]
            if i in self.record["wolf_order"]:
                word_player = self.record["word_wolf"]
            else:
                word_player = self.record["word_plain"]
            prompt += f"""

==task==
你是**player_{i}**,你现在正在参与这个游戏，你的词汇是:**{word_player}**.
请你按照游戏规则，根据上面的分析进行投票。**必须要投给**除自己player_{i}外的**某一个**仍然存活的玩家**。
**必须做出投票**。使用[]包括投票结果，只生成投票结果，不要生成其他内容。
**投票请选择这里的玩家{player_in}**

投票示例:[player_x]
"""
            self.record_prompt("turn_vote_%d"%self.record["now_round"], "player_%d"%i, prompt)
            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], prompt)
            thread = threading.Thread(target=self.vote_for_noerror, args=(prompt_list, 
                                                                                "turn_vote_%d"%self.record["now_round"], 
                                                                                "player_%d"%i, i))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()


    def check_vote_result(self)->None:
        '''
        check the vote result in simple state
        '''
        result = []
        for key,value in self.record["turn_vote_%d"%self.record["now_round"]].items():
            pattern = r'\[(.*?)\]'
            matches = re.findall(pattern, value)
            first_match = matches[0] if matches else None
            try:
                first_match = first_match.split("_")[1]
                if int(first_match) in self.record["player_remain"]:
                    result.append(first_match)
            except:
                pass
        counts = {item: result.count(item) for item in set(result)}
        max_count = max(counts.values())
        vote_result = [item for item, count in counts.items() if count == max_count]
        if len(vote_result) == 1:
            try:
                self.record["player_remain"].remove(int(vote_result[0]))
                self.record["player_out"].append("player_%d"%int(vote_result[0]))
            except:
                pass
            try:
                self.record["wolf_order"].remove(int(vote_result[0]))
            except:
                pass
        else:
            pass
        if len(self.record["wolf_order"]) == len(self.record["player_remain"]) - len(self.record["wolf_order"]):
            self.record["result"] = "win"
        elif len(self.record["wolf_order"]) == 0:
            self.record["result"] = "lose"
        else:
            self.record["now_round"] = self.record["now_round"] + 1
        

    def summary_simple(self, except_list:List[int]=[])->None:
        '''
        summary the experience of players in game
        '''
        threads = []
        if "summary_%d"%self.record["now_round"] not in self.record.keys():
            self.record["summary_%d"%self.record["now_round"]] = {}
        else:
            pass
        for person in [item for item in self.record["player_remain"] if item not in except_list]:
            if person in self.record["wolf_order"]:
                word = self.record["word_wolf"]
            else:
                word = self.record["word_plain"]

            if (self.record["now_round"]-1) == 1:
                prompt = f'''
==information of your word {word}==
{self.record["experience"]["player_%d"%person]}

==analyse of you before==
{self.record["analyse_vote_%d"%(self.record["now_round"]-1)]["player_%d"%person]}

==task==
你是**player_{person}**,你正作为一个玩家参与游戏，你的词汇是:**{word}**。
请你根据游戏规则，对以上内容进行总结。以帮助你在后续的描述中能采用最优的策略。内容包括:

==自己可能的身份==）

==描述策略==
根据自己的身份，给出描述策略

内容要求言简意赅。
'''
            else:
                prompt = f'''
==analyse of you before==
{self.record["summary_%d"%(self.record["now_round"]-1)]["player_%d"%person]}

{self.record["analyse_vote_%d"%(self.record["now_round"]-1)]["player_%d"%person]}

==task==
你是**player_{person}**,你正作为一个玩家参与游戏，你的词汇是:**{word}**。
请你根据游戏规则，对以上内容进行总结。以帮助你在后续的描述中能采用最优的策略。内容包括:

==自己可能的身份==

==描述策略==
根据自己的身份，给出描述策略

{str(self.record["player_out"])},大括号里的玩家已经被淘汰了，总结时请忽略他们。

内容要求言简意赅。
'''
            self.record_prompt("summary_%d"%self.record["now_round"], "player_%d"%person, prompt)
            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%person], prompt)
            thread = threading.Thread(target=self.call_and_record_simple, args=(prompt_list, 
                                                                                "summary_%d"%self.record["now_round"], 
                                                                                "player_%d"%person))
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()

    
    def describe_simple(self, except_list:List[int]=[])->None:
        '''
        describe round of the game in simple state after first round
        '''
        if "turn_describe_%d"%self.record["now_round"] not in self.record:
            self.record["turn_describe_%d"%self.record["now_round"]] = {}
        else:
            pass
        threads = []
        # get record for vote
        history = ""
        for i in range(1,self.record["now_round"]):
            for key,value in self.record["turn_describe_%d"%i].items():
                if int(key.split("_")[-1]) in self.record["player_remain"]:
                    history += f"- {value}\n"

        # request
        for person in [item for item in self.record["player_remain"] if item not in except_list]:
            if person in self.record["wolf_order"]:
                word = self.record["word_wolf"]
            else:
                word = self.record["word_plain"]
            prompt = f"""
==summary of you==
{self.record["summary_%d"%(self.record["now_round"])]["player_%d"%person]}

==Describe history of other player==
{history}

==task==
你现在正在参与游戏，你的词汇是:**{word}**，请你根据summary of you进行本轮的描述。
注意不要与Describe history of other player重复。
只生成描述内容，不要出现{word}本身，也不要出现其他近似的词汇本身。
描述内容要求简短，最好只用几个字。
"""
            self.record_prompt("turn_describe_%d"%self.record["now_round"], "player_%d"%person, prompt)
            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%person], prompt)
            thread = threading.Thread(target=self.describe_for_noerror, args=(prompt_list, 
                                                                                "turn_describe_%d"%self.record["now_round"], 
                                                                                "player_%d"%person))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()
            

    def record_process(self)->None:
        '''
        record the process of the game
        '''
        with open(self.state_record_path,"w", encoding="utf-8") as f:
            json.dump(self.record,f,ensure_ascii=False,indent=4)
        
    def record_result(self, document_name:str)->None:
        '''
        record the state of the game

        - document_name sample.json
        '''
        with open(self.result_record_path+document_name,"w", encoding="utf-8") as f:
            json.dump(self.record,f,ensure_ascii=False,indent=4)

    def simple_game_sample(self,
                           doc_name: str = "sample",
                           draw_num: int = 7)->None:
        '''
        simulate the game in simple state
        '''
        try:
            self.experience_simple()
            self.first_round_describe_simple()
            self.vote_analyse_simple()
            self.vote_simple()
            self.check_vote_result()
            self.record_process()
            print("#",end="")
            while True:
                if "result" in self.record:
                    break
                else:
                    if self.record["now_round"] == draw_num:
                        self.record["result"] = "draw"
                        break
                    else:
                        self.summary_simple()
                        self.describe_simple()
                        self.vote_analyse_simple()
                        self.vote_simple()
                        self.check_vote_result()
                        self.record_process()
                        print("#",end="")
            self.record_result(f"{doc_name}_{self.record["result"]}.json")
            return None
        except Exception as e:
            print(e)
            print(f"{doc_name} error")
            return doc_name


# This class is used to define classes that interact with humans or reserve werewolves for simulation
class Gaming_sub(Gaming):
    '''
    class for sub game n-x participant

    - sub_list: list of players who not need llm request in bacth
    '''
    def __init__(self,
                api_key:str,
                words_table_path:str= "data/word_table.json", 
                state_record_path:str ="data/state/record_state.json", 
                result_record_path:str="data/record/",
                person_record_path:str="data/person.json",
                model:str="glm-4-flash",
                url:str="https://open.bigmodel.cn/api/paas/v4/",
                num_players: int=5,
                num_word:int=1,
                reverse:bool=False,
                wolf_order:List[int]=None,
                sub_list:List[int]=None
                 ):
        super().__init__(api_key,
                         words_table_path,
                         state_record_path,
                         result_record_path,
                         person_record_path,
                         model,
                         url,
                         num_players,
                         num_word,
                         reverse,
                         wolf_order)
        self.sub_list = sub_list
        self.other_list = [i for i in range(1,self.num_players+1) if i not in self.sub_list]

    def sub_first_round_describe_simple(self, sub_describe:List[str])->None:
        '''
        first describe and add sub_list describe
        '''
        self.first_round_describe_simple(except_list=self.sub_list)
        for index,value in enumerate(self.sub_list):
            if value in self.record["player_remain"]:
                self.record["turn_describe_1"]["player_%d"%value] = sub_describe[index]
    
    def sub_vote_simple(self, sub_vote:List[str])->None:
        '''
        vote and add sub_list vote
        sub_vote = ["[player_1]","[player_2]"]
        '''
        self.vote_simple(except_list=self.sub_list)
        for index,value in enumerate(self.sub_list):
            if value in self.record["player_remain"]:
                self.record["turn_vote_%d"%self.record["now_round"]]["player_%d"%value] = sub_vote[index]

    def sub_describe_simple(self, sub_describe:List[str])->None:
        '''
        describe and add sub_list describe
        '''
        self.describe_simple(except_list=self.sub_list)
        for index,value in enumerate(self.sub_list):
            if value in self.record["player_remain"]:
                self.record["turn_describe_%d"%self.record["now_round"]]["player_%d"%value] = sub_describe[index]

    def sub_identity_for_no_error(self, prompt_list:list, keyword_1:str, keyword_2:str)->None:
        '''
        call api for no error in indentity
        '''
        response = llm.api_call(self.api_key, self.url, self.model, prompt_list)
        pattern = r'\[(.*?)\]'
        matches = re.findall(pattern, response)
        first_match = matches[0] if matches else None
        # print(first_match)
        while True:
            prompt_error = ""
            try:
                if first_match in ["N","Y"]:
                    pass
                else:
                    prompt_error = "投票格式错误，请重新生成。"
            except:
                prompt_error = "投票格式错误，请重新生成。"

            if prompt_error == "":
                self.lock.acquire()
                self.record[keyword_1][keyword_2] = response
                self.lock.release()
                break
            else:
                prompt_list.append({"role": "assistant", "content": response})
                prompt_list.append({"role": "user", "content": prompt_error})
                response = llm.api_call(self.api_key, self.url, self.model, prompt_list)
                pattern = r'\[(.*?)\]'
                matches = re.findall(pattern, response)
                first_match = matches[0] if matches else None
                self.record["wrong_num"]+=1


    def sub_identity_sublist(self, sub_list:list)->None:
        '''
        identity for sublist players
        '''
        if "identity_%d"%self.record["now_round"] not in self.record:
            self.record["identity_%d"%self.record["now_round"]] = {}
        else:
            pass

        threads = []
        for num in [i for i in self.record["player_remain"] if i not in sub_list]:
            if num in self.record["player_remain"]:
                if num in self.record["wolf_order"]:
                    word_sub = self.record["word_wolf"]
                else:
                    word_sub = self.record["word_plain"]
                history_without_sub = ""
                for i in range(1,self.record["now_round"]+1):
                    history_without_sub += f"第{i}轮：\n"
                    for key,value in self.record["turn_describe_%d"%i].items():
                        if int(key.split("_")[-1]) in [item for item in range(1,self.num_players+1) if item not in self.sub_list]:
                            history_without_sub += f"- {value}\n"
                history_without_sub_self = ""
                for i in range(1,self.record["now_round"]+1):
                    for key,value in self.record["turn_describe_%d"%i].items():
                        if int(key.split("_")[-1])  == num:
                            history_without_sub_self += f"- {value}\n"
                if self.record["now_round"] == 1:
                      prompt = f"""==Describe History of other players==
{history_without_sub}

==task==
判断自己是不是卧底
你在游戏中分到的词汇为{word_sub}。
分析{word_sub}是否与**Describe History of other players**中的内容相符。（与多数player有差异则有很大概率是卧底）。
判断你自己的身份是不是卧底，如果不是请回复[N]，如果是卧底请回复[Y]。
只需要生成[Y]或[N]，不要生成其他内容。
"""
                else:
                    if self.record["identity_%d"%(self.record["now_round"]-1)] == "[Y]":
                        prompt_add = "你在之前的游戏中认为自己的是**卧底**。"
                    else:
                        prompt_add = "你在之前的游戏中认为自己的是**平民**。"
                    prompt = f"""
==analyse of you before==
{self.record["summary_%d"%(self.record["now_round"]-1)]["player_%d"%num]}
                    
==Describe History of other players==
{history_without_sub}

==task==
判断自己是不是卧底
你在游戏中分到的词汇为{word_sub}，{prompt_add}。
分析{word_sub}是否与**Describe History of other players**中的内容相符。（与多数player有差异则有很大概率是卧底）。
判断你自己的身份是不是卧底，如果不是请回复[N]，如果是卧底请回复[Y]。
只需要生成[Y]或[N]，不要生成其他内容。
"""
                self.record_prompt("identity_%d"%self.record["now_round"],"player_%d"%num ,prompt)
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%num], prompt)
                thread = threading.Thread(target=self.sub_identity_for_no_error, args=(prompt_list, 
                                                                                "identity_%d"%self.record["now_round"], 
                                                                                "player_%d"%num))
                thread.start()
                threads.append(thread)
            else:
                pass
        for t in threads:
            t.join()


    def sub_identity_first_round_describe_simple(self)->None:
        '''
        first describe with sublist identity
        '''
        self.first_round_describe_simple()
        self.sub_identity_sublist(sub_list=self.other_list)

    def sub_identity_vote_analyse_single(self, sub_list:List[int]=[])->None:
        '''
        vote analyse for specific players
        '''
        threads = []
        if "analyse_vote_%d"%self.record["now_round"] not in self.record:
            self.record["analyse_vote_%d"%self.record["now_round"]] = {}
        else:
            pass

        for i in [j for j in self.record["player_remain"] if j not in sub_list]:
            if i in self.record["player_remain"]:
                if i in self.record["wolf_order"]:
                    word_player = self.record["word_wolf"]
                else:
                    word_player = self.record["word_plain"]
                if self.record["identity_%d"%(self.record["now_round"])] == "[Y]":
                    prompt_add = "你在之前的游戏中认为自己的是**卧底**。"
                else:
                    prompt_add = "你在之前的游戏中认为自己的是**平民**。"
                
                if len(self.record["player_out"]) == 0:
                    prompt = "==Describe history of other player==\n\n"
                    prompt_end = f"""==task==
你是**player_{i}**,你现在正在参与游戏，{prompt_add}
你的词汇是:**{word_player}**，请你根据游戏规则，分析Describe history
分析内容包括:
== {word_player}与Describe history of other player中每名玩家的描述是否相符==

==自己在游戏中的身份==
进行简短分析后给出判断

==这轮投票要投给哪位玩家==
根据分析结果，投票要有理有据，不能进行随机选择
必须要**明确**投票给哪位玩家，**不能**投票给自己**player_{i}**。

内容要求言简意赅。
"""
                else:
                    prompt = f"==summary of you in the game==\n\n {self.record["summary_%d"%(self.record["now_round"])]["player_%d"%i]}\n\n ==Describe history of other player=="
                    prompt_end = f"""==task==
你是**player_{i}**,你现在正在参与这个游戏，{prompt_add}
你的词汇是:**{word_player}**，请你根据的游戏规则，分析Describe history
分析内容包括:
== {word_player}与Describe history of other player中每名玩家的描述是否相符==

==自己在游戏中的身份==
进行简短分析后给出判断

==这轮投票要投给哪位玩家==
根据分析结果，投票要有理有据，不能进行随机选择
必须要**明确**投票给哪位玩家，**不能**投票给自己**player_{i}**。
{str(self.record["player_out"])}里的玩家已经被淘汰了，请不要投给他们。

内容要求言简意赅。
"""
                for round_num in range(1, self.record["now_round"]+1):
                    prompt += "- 第%s轮\n"%round_num
                    for j in [item for item in self.record["player_remain"] if item != i]:
                        prompt += " - player_%d: "%j + self.record["turn_describe_%d"%round_num]["player_%d"%j] + "\n"
                
                prompt += prompt_end

                self.record_prompt("analyse_vote_%d"%self.record["now_round"], "player_%d"%i, prompt)
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], prompt)
                thread = threading.Thread(target=self.call_and_record_simple, args=(prompt_list, 
                                                                                    "analyse_vote_%d"%self.record["now_round"], 
                                                                                    "player_%d"%i))
                thread.start()
                threads.append(thread)
        else:
            pass

        for t in threads:
            t.join()


    def sub_identity_summary_single(self, sub_list:List[int]=[])->None:
        '''
        summary for specific players
        '''
        if "summary_%d"%self.record["now_round"] not in self.record.keys():
            self.record["summary_%d"%self.record["now_round"]] = {}
        else:
            pass
        threads = []
        for person in [i for i in self.record["player_remain"] if i not in sub_list]:
            if person in self.record["player_remain"]:
                if person in self.record["wolf_order"]:
                    word = self.record["word_wolf"]
                else:
                    word = self.record["word_plain"]
                if self.record["identity_%d"%(self.record["now_round"]-1)] == "[Y]":
                    prompt_add = "你在之前的游戏中认为自己的是**卧底**。"
                else:
                    prompt_add = "你在之前的游戏中认为自己的是**平民**。"

                if (self.record["now_round"]-1) == 1:
                    prompt = f'''
==information of your word {word}==
{self.record["experience"]["player_%d"%person]}

==analyse of you before==
{self.record["analyse_vote_%d"%(self.record["now_round"]-1)]["player_%d"%person]}

==task==
你是**player_{person}**,你正作为一个玩家参与游戏，你的词汇是:**{word}**，{prompt_add}
请你根据游戏规则，对以上内容进行总结。以帮助你在后续的描述中能采用最优的策略。内容包括:

==自己可能的身份==

==描述策略==
根据自己的身份，给出描述策略

内容要求言简意赅。
'''
                else:
                    prompt = f'''
==analyse of you before==
{self.record["summary_%d"%(self.record["now_round"]-1)]["player_%d"%person]}

{self.record["analyse_vote_%d"%(self.record["now_round"]-1)]["player_%d"%person]}

==task==
你是**player_{person}**,你正作为一个玩家参与游戏，你的词汇是:**{word}**，{prompt_add}
请你根据游戏规则，对以上内容进行总结。以帮助你在后续的描述中能采用最优的策略。内容包括:

==自己可能的身份==


==描述策略==
根据自己的身份，给出描述策略

{str(self.record["player_out"])},大括号里的玩家已经被淘汰了，总结时请忽略他们。

内容要求言简意赅。
'''
                self.record["summary_%d"%self.record["now_round"]]["player_%d"%person] = prompt
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%person], prompt)
                thread = threading.Thread(target=self.call_and_record_simple, args=(prompt_list, 
                                                                                    "summary_%d"%self.record["now_round"], 
                                                                                    "player_%d"%person))
                thread.start()
                threads.append(thread)
            else:
                pass
        for t in threads:
            t.join()

    def sub_identity_describe_single(self, sub_list:list)->None:
        '''
        describe single with specified list
        '''
        if "turn_describe_%d"%self.record["now_round"] not in self.record:
            self.record["turn_describe_%d"%self.record["now_round"]] = {}
        else:
            pass
        threads = []
        # get record for vote
        history = ""
        for i in range(1,self.record["now_round"]):
            for key,value in self.record["turn_describe_%d"%i].items():
                if int(key.split("_")[-1]) in self.record["player_remain"]:
                    history += f"- {value}\n"

        # request
        for person in [i for i in self.record["player_remain"] if i not in sub_list]:
            if person in self.record["player_remain"]:
                if person in self.record["wolf_order"]:
                    word = self.record["word_wolf"]
                else:
                    word = self.record["word_plain"]
                if self.record["identity_%d"%(self.record["now_round"]-1)] == "[Y]":
                    prompt_add = "你在之前的游戏中认为自己的是**卧底**"
                else:
                    prompt_add = "你在之前的游戏中认为自己的是**平民**"
                prompt = f"""
==summary of you==
{self.record["summary_%d"%(self.record["now_round"])]["player_%d"%person]}

==Describe history of other player==
{history}

==task==
你现在正在参与这个游戏，{prompt_add}，你的词汇是:**{word}**，请你根据summary of you进行本轮的描述。
注意不要与Describe history of other player重复。
只生成描述内容，不要出现{word}本身，也不要出现其他近似的词汇本身。
描述内容要求简短，最好只用几个字。
"""
                self.record_prompt("turn_describe_%d"%self.record["now_round"], "player_%d"%person, prompt)
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%person], prompt)
                thread = threading.Thread(target=self.describe_for_noerror, args=(prompt_list, 
                                                                                    "turn_describe_%d"%self.record["now_round"], 
                                                                                    "player_%d"%person))
                thread.start()
                threads.append(thread)
            else:
                pass

        for t in threads:
            t.join()
        

    def sub_identity_vote_single(self,sub_list:list)->None:
        '''
        vote single with specified list
        '''
        if "turn_vote_%d"%self.record["now_round"] not in self.record:
            self.record["turn_vote_%d"%self.record["now_round"]] = {}
        else:
            pass
        threads = []
        for i in [j for j in self.record["player_remain"] if j not in sub_list]:
            if i in self.record["player_remain"]:
                player_in = set(["player_%d"%item for item in self.record["player_remain"] if item != i]) 
                prompt = self.record["analyse_vote_%d"%self.record["now_round"]]["player_%d"%i]
                if i in self.record["wolf_order"]:
                    word_player = self.record["word_wolf"]
                else:
                    word_player = self.record["word_plain"]
                if self.record["identity_%d"%(self.record["now_round"])] == "[Y]":
                    prompt_add = "你在之前的游戏中认为自己的是**卧底**"
                else:
                    prompt_add = "你在之前的游戏中认为自己的是**平民**"

                prompt += f"""

==task==
你是**player_{i}**，{prompt_add}，你现在正在参与这个游戏，你的词汇是:**{word_player}**.
请你按照游戏规则，根据上面的分析进行投票。**必须要投给**除自己player_{i}外的**某一个**仍然存活的玩家**。
**必须做出投票**。使用[]包括投票结果，只生成投票结果，不要生成其他内容。
**投票请选择这里的玩家{player_in}**

投票示例:[player_x]
    """

                self.record_prompt("turn_vote_%d"%self.record["now_round"], "player_%d"%i, prompt)
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], prompt)
                thread = threading.Thread(target=self.vote_for_noerror, args=(prompt_list, 
                                                                                    "turn_vote_%d"%self.record["now_round"], 
                                                                                    "player_%d"%i, i))
                thread.start()
                threads.append(thread)
            else:
                pass

        for t in threads:
            t.join()

    def sub_describe_strategy_llm_needsummary(self, sub_list:list, indentity_flag:bool = False)->None:
        '''
        describe single with specified listy_flag:
        '''
        if "turn_describe_%d"%self.record["now_round"] not in self.record:
            self.record["turn_describe_%d"%self.record["now_round"]] = {}
        else:
            pass
        threads = []

        if self.record["now_round"] != 1:
            history = ""
            for i in range(1,self.record["now_round"]):
                for key,value in self.record["turn_describe_%d"%i].items():
                    if int(key.split("_")[-1]) in self.record["player_remain"]:
                        history += f"- {value}\n"

            # request
            for person in [item for item in self.record["player_remain"] if item in sub_list]: 
                if person in self.record["player_remain"]:
                    if person in self.record["wolf_order"]:
                        word = self.record["word_wolf"]
                    else:
                        word = self.record["word_plain"]
                    if indentity_flag == True:
                        if self.record["identity_%d"%(self.record["now_round"]-1)] == "[Y]":
                            prompt_add = "你在之前的游戏中认为自己的是**卧底**"
                        else:
                            prompt_add = "你在之前的游戏中认为自己的是**平民**"
                    else:
                        prompt_add = ""
                    prompt = f"""
    已经进行过的游戏中你的分析:
    {self.record["summary_%d"%(self.record["now_round"])]["player_%d"%person]}

    历史发言记录：
    {history}

    你现在正在参与这个游戏，你的词汇是:**{word}**，**{prompt_add}**，请你根据**已经进行过的游戏中你的分析**进行本轮的描述。
    描述要求**简短**只概括相关词汇**某一个共性特征**，注意**不要**与**历史发言记录**中出现的特征重复。
    只生成描述内容，不要出现{word}本身，也不要出现其他近似的词汇本身。
    """
                    ### prompt 改成生成很多个可能
                    self.record_prompt("turn_describe_%d"%self.record["now_round"], "player_%d"%person, prompt)
                    prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%person], prompt)
                    thread = threading.Thread(target=self.describe_for_noerror, args=(prompt_list, 
                                                                                        "turn_describe_%d"%self.record["now_round"], 
                                                                                        "player_%d"%person))
                    thread.start()
                    threads.append(thread)
                else:
                    pass

            for t in threads:
                t.join()
        else: 
            if "turn_describe_1" not in self.record:
                self.record["turn_describe_1"] = {}
            else:
                pass
            threads = []
            for i in [item for item in self.record["player_remain"] if item not in sub_list]:
                
                if i in self.record["wolf_order"]:
                    word = self.record["word_wolf"]
                else:
                    word = self.record["word_plain"]    
                
                word_prompt = f"""
    ### 关于{word}与**可能对应的词**，你之前的分析是：
    {self.record["experience"]["player_%d"%i]} 

    你现在正在参与这个游戏，你的词汇是：{word}。
    请你根据**上面的文字与描述建议**简短地描述**上文相关词汇**的**一个共性**特征。只生成特征的内容，不要出现{word}本身。"""
                self.record_prompt("turn_describe_1", "player_%d"%i, word_prompt)
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], word_prompt)
                
                thread = threading.Thread(target=self.describe_for_noerror, 
                                        args=(prompt_list, "turn_describe_1", "player_%d"%i))
                thread.start()
                threads.append(thread)

            for t in threads:
                t.join()
        
        



    def sub_identity_summary_simple(self)->None:
        '''
        summary with sublist identity
        '''
        self.summary_simple(except_list=self.sub_list)
        self.sub_identity_summary_single(sub_list=self.other_list)
        


    def sub_identity_vote_simple(self)->None:
        '''
        vote simple with sublist identity
        '''
        self.vote_simple(except_list=self.sub_list)
        self.sub_identity_vote_single(sub_list=self.other_list)

    
    def sub_identity_describe_simple(self)->None:
        '''
        describe simple with sublist identity
        '''
        self.describe_simple(except_list=self.sub_list)
        self.sub_identity_describe_single(sub_list=self.other_list)


    def sub_identity_vote_analyse_simple(self)->None:
        '''
        analyse history in the game in sub class include a simple analyse
        '''
        self.vote_analyse_simple(except_list = self.sub_list )
        self.sub_identity_vote_analyse_single(sub_list=self.other_list)


class Gaming_raw(Gaming_sub):
    '''
    class for raw Agent

    - sub_list: list of players who not need llm request in bacth

    - other_list: get automaticly from sub_list and players_num
    '''
    def __init__(self,
                api_key:str,
                words_table_path:str= "data/word_table.json", 
                state_record_path:str ="data/state/record_state.json", 
                result_record_path:str="data/record/",
                person_record_path:str="data/person.json",
                model:str="glm-4-flash",
                url:str="https://open.bigmodel.cn/api/paas/v4/",
                num_players: int=5,
                num_word:int=1,
                reverse:bool=False,
                wolf_order:List[int]=None,
                sub_list:List[int]=None
                 ):
        super().__init__(api_key,
                         words_table_path,
                         state_record_path,
                         result_record_path,
                         person_record_path,
                         model,
                         url,
                         num_players,
                         num_word,
                         reverse,
                         wolf_order,
                         sub_list)
        self.other_list = [item for item in range(1,self.num_players+1) if item not in self.sub_list]
    
    def raw_describe(self, sub_list:List[int]=[]) -> None:
        '''
        describe for raw Agent
        '''

        if "turn_describe_%d"%self.record["now_round"] in self.record:
            pass
        else:
            self.record["turn_describe_%d"%self.record["now_round"]] = {}

        threads = []
        # get record for vote

        # request
        for person in [item for item in self.record["player_remain"] if item not in sub_list]:
            if person in self.record["wolf_order"]:
                word = self.record["word_wolf"]
            else:
                word = self.record["word_plain"]
            if self.record["now_round"] == 1:
                prompt = f"""
==Task==
你现在正在参与这个游戏，你的词汇是:**{word}**，请你进行本轮的描述。
描述要求**简短**只概括相关词汇**某一个共性特征**。
只生成描述内容，不要出现{word}本身，也不要出现其他近似的词汇本身。
"""
            else:
                history = ""
                for i in range(1,self.record["now_round"]):
                    for key,value in self.record["turn_describe_%d"%i].items():
                        if int(key.split("_")[-1]) in self.record["player_remain"]:
                            history += f"- {value}\n"
                prompt = f"""==Describe History==
{history}

==Task==
你现在正在参与这个游戏，你的词汇是:**{word}**，请你进行本轮的描述。
描述要求**简短**只概括相关词汇**某一个共性特征**，注意**不要**与==Describe History==中出现的特征重复。
只生成描述内容，不要出现{word}本身，也不要出现其他近似的词汇本身。
"""
            self.record_prompt("turn_describe_%d"%self.record["now_round"], "player_%d"%person, prompt)
            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%person], prompt)
            thread = threading.Thread(target=self.describe_for_noerror, args=(prompt_list, 
                                                                                "turn_describe_%d"%self.record["now_round"], 
                                                                                "player_%d"%person))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        
    def raw_vote(self, sub_list:List[int]=[]) -> None:
        '''
        vote for raw Agent
        '''

        threads = []
        if "turn_vote_%d"%self.record["now_round"] in self.record:
            pass
        else:
            self.record["turn_vote_%d"%self.record["now_round"]] = {}
    


        for i in [item for item in self.record["player_remain"] if item not in sub_list]:
            player_in = set(["player_%d"%item for item in self.record["player_remain"] if item != i]) 
            prompt_history = ""
            if i in self.record["wolf_order"]:
                word_player = self.record["word_wolf"]
            else:
                word_player = self.record["word_plain"]

            for round_num in range(1, self.record["now_round"]+1):
                prompt_history += "- 第%s轮\n"%round_num
                for j in [item for item in self.record["player_remain"] if item != i]:
                    prompt_history += " - player_%d: "%j + self.record["turn_describe_%d"%round_num]["player_%d"%j] + "\n"
            
            prompt = f"""==Describe History==
{prompt_history}

==Task==
你是**player_{i}**,你现在正在参与这个游戏，你的词汇是:**{word_player}**.
请你按照游戏规则，进行投票。**必须要投给**除自己外的**某一个**仍然存活的玩家**{player_in}。
使用[]包括投票结果，只生成投票结果，不要生成其他内容。

==example==
[player_x]
"""
            self.record_prompt("turn_vote_%d"%self.record["now_round"], "player_%d"%i, prompt)

            prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], prompt)
            thread = threading.Thread(target=self.vote_for_noerror, args=(prompt_list, 
                                                                                "turn_vote_%d"%self.record["now_round"], 
                                                                                "player_%d"%i, i))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    def raw_identify(self, sub_list:List[int]=[]) -> None:
        '''
        identify for raw Agent
        '''
        if "identity_%d"%self.record["now_round"] not in self.record:
            self.record["identity_%d"%self.record["now_round"]] = {}
        else:
            pass

        threads = []
        for num in [item for item in self.record["player_remain"] if item not in sub_list]:
            if num in self.record["player_remain"]:
                if num in self.record["wolf_order"]:
                    word_sub = self.record["word_wolf"]
                else:
                    word_sub = self.record["word_plain"]
                history_without_sub = ""
                for i in range(1,self.record["now_round"]+1):
                    history_without_sub += f"第{i}轮：\n"
                    for key,value in self.record["turn_describe_%d"%i].items():
                        if int(key.split("_")[-1]) in [item for item in range(1,self.num_players+1) if item not in self.sub_list]:
                            history_without_sub += f"- {value}\n"
                history_without_sub_self = ""
                for i in range(1,self.record["now_round"]+1):
                    for key,value in self.record["turn_describe_%d"%i].items():
                        if int(key.split("_")[-1])  == num:
                            history_without_sub_self += f"- {value}\n"
                if self.record["now_round"] == 1:
                      prompt = f"""==Describe History of other players==
{history_without_sub}

==task==
判断自己是不是卧底
你在游戏中分到的词汇为{word_sub}。
分析{word_sub}是否与**Describe History of other players**中的内容相符。（与多数player有差异则有很大概率是卧底）。
判断你自己的身份是不是卧底，如果不是请回复[N]，如果是卧底请回复[Y]。
只需要生成[Y]或[N]，不要生成其他内容。
"""
                else:
                    if self.record["identity_%d"%(self.record["now_round"]-1)] == "[Y]":
                        prompt_add = "你在之前的游戏中认为自己的是**卧底**。"
                    else:
                        prompt_add = "你在之前的游戏中认为自己的是**平民**。"
                    prompt = f"""==Describe History of other players==
{history_without_sub}

==task==
判断自己是不是卧底
你在游戏中分到的词汇为{word_sub}，{prompt_add}。
分析{word_sub}是否与**Describe History of other players**中的内容相符。（与多数player有差异则有很大概率是卧底）。
依据分析**更新你的判断**。重新判断你自己的身份是不是卧底，如果不是请回复[N]，如果是卧底请回复[Y]。
只需要生成[Y]或[N]，不要生成其他内容。
"""
                self.record_prompt("identify_%d"%self.record["now_round"],"player_%d"%num ,prompt)
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%num], prompt)
                thread = threading.Thread(target=self.sub_identity_for_no_error, args=(prompt_list, 
                                                                                "identity_%d"%self.record["now_round"], 
                                                                                "player_%d"%num))
                thread.start()
                threads.append(thread)
            else:
                pass
        for t in threads:
            t.join()


    def raw_describe_strategy_llm_needhistory_identityoptional(self, sub_list:list, indentity_flag:bool = False)->None:
        '''
        describe single with specified listy_flag:
        '''
        if "turn_describe_strategy_%d"%self.record["now_round"] not in self.record:
            self.record["turn_describe_strategy_%d"%self.record["now_round"]] = {}
        else:
            pass
        threads = []

        if self.record["now_round"] != 1:
            history = ""
            for i in range(1,self.record["now_round"]):
                for key,value in self.record["turn_describe_%d"%i].items():
                    if int(key.split("_")[-1]) in self.record["player_remain"]:
                        history += f"- {value}\n"

            # request
            for person in [item for item in self.record["player_remain"] if item not in sub_list]: 
                if person in self.record["player_remain"]:
                    if person in self.record["wolf_order"]:
                        word = self.record["word_wolf"]
                    else:
                        word = self.record["word_plain"]
                    if indentity_flag == True:
                        if self.record["identity_%d"%(self.record["now_round"]-1)] == "[Y]":
                            prompt_add = "你在之前的游戏中认为自己的是**卧底**"
                        else:
                            prompt_add = "你在之前的游戏中认为自己的是**平民**"
                    else:
                        prompt_add = ""
                    prompt = f"""==Describe History of other players==
{history}

==task==
你现在正在参与这个游戏，你的词汇是:**{word}**，**{prompt_add}**。
请你对本轮描述生成几个可选方案，注意**不要**与==Describe History of other players==中出现的描述重复。
只生成可选方案，不要出现{word}本身，也不要出现其他近似的词汇本身。
每一条方案以- 开头，不要出现其他内容。

==example== 如果你的词汇是飞机。
- 能飞的东西
- 常用的交通工具
- 快捷的出行方式
"""
                    ### prompt 改成生成很多个可能
                    self.record_prompt("turn_describe_strategy_%d"%self.record["now_round"], "player_%d"%person, prompt)
                    prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%person], prompt)
                    thread = threading.Thread(target=self.describe_for_noerror, args=(prompt_list, 
                                                                                        "turn_describe_strategy_%d"%self.record["now_round"], 
                                                                                        "player_%d"%person))
                    thread.start()
                    threads.append(thread)
                else:
                    pass

            for t in threads:
                t.join()
        else: 
            if "turn_describe_1" not in self.record:
                self.record["turn_describe_1"] = {}
            else:
                pass
            threads = []
            for i in [item for item in self.record["player_remain"] if item not in sub_list]:
                
                if i in self.record["wolf_order"]:
                    word = self.record["word_wolf"]
                else:
                    word = self.record["word_plain"]    
                
                word_prompt = f"""==task==
你现在正在参与这个游戏，你的词汇是：{word}。
请你对本轮描述生成几个可选方案，只生成可选方案，不要出现{word}本身，也不要出现其他近似的词汇本身。
每一条方案以- 开头，不要出现其他内容。

==example== 如果你的词汇是飞机。
- 能飞的东西
- 常用的交通工具
- 快捷的出行方式"""
                #### prompt 改成生成很多个可能
                word_prompt += self.prompt_sample
                self.record_prompt("turn_describe_strategy_1", "player_%d"%i, word_prompt)
                prompt_list = self.function_get_prompt_list(self.prompt_system + self.record["person_information"]["player_%d"%i], word_prompt)
                
                thread = threading.Thread(target=self.describe_for_noerror, 
                                        args=(prompt_list, "turn_describe_1", "player_%d"%i))
                thread.start()
                threads.append(thread)

            for t in threads:
                t.join()

    def raw_game_sample(self,
                           doc_name: str = "sample",
                           draw_num: int = 7)->None:
        '''
        simulate the game in raw
        '''
        try:
            self.experience_simple(self.other_list)
            while True:
                if "result" in self.record:
                    break
                else:
                    if self.record["now_round"] == draw_num:
                        self.record["result"] = "draw"
                        break
                    else:
                        
                        self.raw_describe()
                        self.raw_vote()
                        self.check_vote_result()
                        self.record_process()
                        print("#",end="")
            self.record_result(f"{doc_name}_{self.record["result"]}.json")
            return None
        except Exception as e:
            print(e)
            print(f"{doc_name} error")
            return doc_name
        
    def raw_experience_mix_simple(self,
                                    doc_name: str = "sample",
                                    draw_num: int = 7)->None:
        '''
        simulate the game in raw and experience mix

        - sublist use experience
        '''
        try:
            self.experience_simple(self.other_list)
            self.first_round_describe_simple(self.other_list)
            self.raw_describe(self.sub_list)
            self.vote_analyse_simple(self.other_list)
            self.vote_simple(self.other_list)
            self.raw_vote(self.sub_list)
            self.check_vote_result()
            self.record_process()
            print("#",end="")
            while True:
                if "result" in self.record:
                    break
                else:
                    if self.record["now_round"] == draw_num:
                        self.record["result"] = "draw"
                        break
                    else:
                        self.summary_simple(self.other_list)
                        self.describe_simple(self.other_list)
                        self.raw_describe(self.sub_list)
                        self.vote_analyse_simple(self.other_list)
                        self.vote_simple(self.other_list)
                        self.raw_vote(self.sub_list)
                        self.check_vote_result()
                        self.record_process()
                        print("#",end="")
            self.record_result(f"{doc_name}_{self.record["result"]}.json")
            return None
        except Exception as e:
            print(e)
            print(f"{doc_name} error")
            return doc_name    