from  werewolf import *
import streamlit as st
from dotenv import load_dotenv
import os
import random
import copy
from typing import Literal

current_file_path = __file__
current_directory = os.path.dirname(current_file_path)


def show_and_record(show_content:str, role:str=Literal["assistant", "user"])-> None:
    st.chat_message(role).write(show_content)
    st.session_state.messages.append({"role": role, "content": show_content})

def get_describe_content(game_record:dict,id_user:int)-> str:
    get_str = f"###### Round {game_record["now_round"]} description:\n\n"
    data_describe_dict = copy.deepcopy(game_record["turn_describe_%d"%game_record["now_round"]])
    data_describe_dict = dict(sorted(data_describe_dict.items(), key=lambda x: int(str(x[0]).split("_")[1])))

    for player,value in data_describe_dict.items():
        if player != f"player_%d"%id_user:
            get_str += f"- **{player}**:\n{value.replace('- ','')}\n\n"
    return get_str

def get_vote_content(game_record:dict,id_user:int)-> str:
    get_str = f"###### Round {game_record["now_round"]} vote:\n\n"
    data_vote_dict = copy.deepcopy(game_record["turn_vote_%d"%game_record["now_round"]])
    data_vote_dict = dict(sorted(data_vote_dict.items(), key=lambda x: int(str(x[0]).split("_")[1])))

    for player,value in data_vote_dict.items():
        if player != f"player_%d"%id_user:
            get_str += f"- **{player}**  voted for  **{value.replace('- ','').replace("[", '').replace("]", '')}**\n\n"
    return get_str

st.sidebar.write("You can set the **number of players** here, when the number of players is **5 or 6**, there can only be **one werewolf**. When the number of participants is **7 or 8**, there **can be two werewolves**.")

number_player = st.sidebar.number_input("player number 🤗", min_value=5, max_value=8)

if number_player <= 6:
    max_wolf_num = 1
else:
    max_wolf_num = 2


wolf_num = st.sidebar.number_input("player number 🐺", min_value=1, max_value=max_wolf_num)   



st.title("🤗 Who is the wolf? 🐺")

st.divider()


load_dotenv("api.env")
api_key = os.getenv("API_KEY")  

if "gaming" not in st.session_state:
    st.session_state["if_begin"] = False

    begin_prompt = """
##### Play **Who is the wolf** with LLMs 🤖

###### Game Preparation
- **Role Assignment**: Among all players, one or two are randomly selected to be the "wolves," while the rest are "Civilians." The identities of the wolves and Civilians are kept secret from each other.
- **Word Selection**: All players are given the same word, but the wolves receive a different, related word. For example, if the Civilians' word is "apple," the wolves' word might be "fruit."

###### Game Process
- **Discribe Round**: Each player takes turns describing their understanding of the word. The wolves must try to blend in with the discussion without being discovered and may attempt to mislead other players.
- **Voting Round**: At the end of each round, all players vote to eliminate the person they believe is most likely to be a Spy. The player with the most votes is eliminated.
- **Victory Conditions**:
   - If the wolves are correctly identified and eliminated, the Civilians win.
   - If the number of wolves equals or exceeds the number of Civilians, the wolves win.
   - If the game is not finished within a certain period, it is considered a draw.
"""

    st.session_state["messages"] = [{"role": "assistant", "content": begin_prompt}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if st.sidebar.button("restart 🎈"):
    if "gaming" in st.session_state:
        del st.session_state["gaming"]
    if "messages" in st.session_state:
        del st.session_state["messages"]
    if "user_word" in st.session_state:
        del st.session_state["user_word"]
    if "user_id" in st.session_state:
        del st.session_state["user_id"]
    if "state" in st.session_state:
        del st.session_state["state"]
    if "selection" in st.session_state:
        del st.session_state["selection"]
    try:
        os.remove(f"{current_directory}/data/record/result.json")
    except:
        pass
    st.session_state["if_begin"] = False
    st.rerun()

if st.session_state["if_begin"] == False:
    if st.sidebar.button("begin 🎯"):
        st.session_state["if_begin"] = True

        # 定义几个初始量
        player_num = number_player

        # 狼人编号
        id_wolf = []
        while len(id_wolf) !=  wolf_num:
            temp = random.randint(1, number_player)
            if temp not in id_wolf:
                id_wolf.append(temp)

        # 用户编号
        id_user = random.randint(1, number_player)
        # 词号
        num_word = random.randint(1, 150)
        # 词是否反转
        reverse = random.choice([True, False])
        # 定义一局游戏
        st.session_state["gaming"] = Gaming_sub(api_key,
                                                result_record_path=f"{current_directory}/data/record/",
                                                num_players=player_num,
                                                wolf_order=id_wolf,
                                                sub_list=[id_user],
                                                num_word=num_word,
                                                reverse=reverse,)

        with st.spinner("loading...🤖"):
            # 游戏初始化
            st.session_state["gaming"].experience_simple(except_list=st.session_state["gaming"].sub_list)
            if id_user == id_wolf:
                st.session_state["user_word"] = st.session_state["gaming"].record["word_wolf"]
            else:
                st.session_state["user_word"] = st.session_state["gaming"].record["word_plain"]
            
            st.session_state["user_id"] = id_user

            information_for_user_prompt = f"""
- You are **player_{id_user}**
- Your word is  **{st.session_state['user_word']}**"""

            show_and_record(information_for_user_prompt, "assistant")
            st.session_state["state"] = "describe"
            show_and_record("It's your turn to describe 😃", "assistant")
            st.rerun()



if "user_id" in st.session_state:
    st.sidebar.divider()
    st.sidebar.markdown(f"""### In this game    
- Your id: **player_{st.session_state['user_id']}**
- Your word:  **{st.session_state['user_word']}**""")




if prompt := st.chat_input():
    if "gaming" not in st.session_state:
        st.info("Please initiate the game first")
        st.stop()
    elif "result" in st.session_state["gaming"].record:
        pass
        # st.stop()
    elif st.session_state["user_id"] not in st.session_state["gaming"].record["player_remain"]:
        st.info("You're out of the game 😇")
    elif st.session_state["state"] == "vote":
        st.info("please vote first 🎯")
    else:
        if st.session_state["state"] == "describe":
            show_and_record(prompt, "user")
            with st.spinner("Other players are thinking 🤗"):
                if st.session_state["gaming"].record["now_round"] !=1:
                    st.session_state["gaming"].summary_simple(except_list=[st.session_state["user_id"]])
                    st.session_state["gaming"].sub_describe_simple([prompt])
                    show_dedcribe = get_describe_content(st.session_state["gaming"].record,st.session_state["user_id"])
                    show_and_record(show_dedcribe, "assistant")
                else:
                    st.session_state["gaming"].sub_first_round_describe_simple([prompt])
                    show_dedcribe = get_describe_content(st.session_state["gaming"].record,st.session_state["user_id"])
                    show_and_record(show_dedcribe, "assistant")
            st.session_state["state"] = "vote"
            if st.session_state["user_id"] in st.session_state["gaming"].record["player_remain"] and "result" not in st.session_state["gaming"].record:
                show_and_record("It's your turn to vote 🎯", "assistant")
            st.rerun()
        


if "gaming" in st.session_state:
    if st.session_state["state"] == "vote" and st.session_state["user_id"] in st.session_state["gaming"].record["player_remain"]:
        options = []
        for id in [item for item in st.session_state["gaming"].record["player_remain"] if item != st.session_state["user_id"]]:
            options.append(f"player_{id}")
        selection = st.pills("Please vote 🎯", options, selection_mode="single")
        st.markdown(f"Your vote: {selection}.")
        if st.button("Submit 🎈"):
            if selection:
                st.session_state["selection"] = selection
                st.session_state["state"] = "vote_post"
                st.rerun()
            else:
                st.info("Please select a player to vote for 🤗")

    if st.session_state["state"] == "vote_post":
        show_and_record(f"I voted for {st.session_state["selection"]}", "user")
        with st.spinner("Other players are voting 🤗"):
            st.session_state["gaming"].vote_analyse_simple(except_list=[st.session_state["user_id"]])
            st.session_state["gaming"].sub_vote_simple([f"[{st.session_state["selection"]}]"])
            show_vote = get_vote_content(st.session_state["gaming"].record,st.session_state["user_id"])
            show_and_record(show_vote, "assistant")
            st.session_state["gaming"].check_vote_result()
        st.session_state["state"] = "describe"
        if st.session_state["user_id"] in st.session_state["gaming"].record["player_remain"] and "result" not in st.session_state["gaming"].record:
            show_and_record("It's your turn to describe 😃", "assistant")
        st.rerun()


if "gaming" in st.session_state:
    if st.session_state["user_id"] not in st.session_state["gaming"].record["player_remain"] and "result" not in st.session_state["gaming"].record:
        st.session_state["show_information"] = f"The wolf is "
        for id_user in st.session_state["gaming"].record["wolf_order_record"]:
            st.session_state["show_information"] += f"**player_{id_user}**   "

        st.session_state["show_information_2"] = f"The wolf word is  **{st.session_state["gaming"].record["word_wolf"]}**"
        st.session_state["show_information_3"] = f"The civilian word is  **{st.session_state["gaming"].record["word_plain"]}**"

        show_and_record(f"""You're out of the game 😇
- {st.session_state["show_information"]}
- {st.session_state["show_information_2"]}

The game will automatically continue until the end.""", "assistant")
        if "show_information" in st.session_state:
            st.sidebar.markdown(f"""You're out of the game 😇
- {st.session_state["show_information"]}
- {st.session_state["show_information_2"]}
- {st.session_state["show_information_3"]}""")
        while True:
                    if "result" in st.session_state["gaming"].record:
                        break
                    else:
                        if st.session_state["gaming"].record["now_round"] == 7:
                            st.session_state["gaming"].record["result"] = "draw"
                            break
                        else:
                            with st.spinner("LLM players are thinking 🤗"):
                                st.session_state["gaming"].summary_simple()
                                st.session_state["gaming"].describe_simple()
                            show_dedcribe = get_describe_content(st.session_state["gaming"].record,st.session_state["user_id"])
                            show_and_record(show_dedcribe, "assistant")
                            with st.spinner("LLM players are voting 🤗"):
                                st.session_state["gaming"].vote_analyse_simple()
                                st.session_state["gaming"].vote_simple()
                            show_vote = get_vote_content(st.session_state["gaming"].record,st.session_state["user_id"])
                            show_and_record(show_vote, "assistant")
                            st.session_state["gaming"].check_vote_result()


    if "result" in st.session_state["gaming"].record:
        st.session_state["gaming"].record_result("result.json")
        wolf_show = f"The wolf is "
        for id_user in st.session_state["gaming"].record["wolf_order_record"]:
            wolf_show += f"**player_{id_user}** "
        wolf_word_show = f"The wolf word is  **{st.session_state["gaming"].record["word_wolf"]}**"
        civilian_word_show = f"The civilian word is  **{st.session_state["gaming"].record["word_plain"]}**"
        show_result = f"""- {wolf_show}
- {wolf_word_show}
- {civilian_word_show}"""
        if st.session_state["gaming"].record["result"] == "draw":
            show_and_record(f"###### The game is draw.🎯 \n\n {show_result}", "assistant")
        elif st.session_state["gaming"].record["result"] == "win":
            show_and_record(f"###### The wolf win.🐺 \n\n {show_result}", "assistant")
        elif st.session_state["gaming"].record["result"] == "lose":
            show_and_record(f"###### The Civilians win.🤗 \n\n {show_result}", "assistant")

st.sidebar.divider()
with st.sidebar.expander("Get more information 🌍"):
    st.write("You can get the game's progress data at the end of the game.")
    try:
        with open(f"{current_directory}/data/record/result.json", "rb") as file:
            st.download_button(
                label="Download data in game",
                data=file,
                file_name="result.json",
                mime="data/record/result.json",
                )   
    except:
        st.write("The game is not over yet.")

if "gaming" in st.session_state:
    if "result" in st.session_state["gaming"].record:
        st.info("The game is over 🎈")