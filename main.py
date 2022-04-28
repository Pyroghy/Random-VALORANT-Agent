import base64
import requests
import random
import os
import tkinter
import tkinter.font as font

class Random_Agent:
    def __init__(self):
        self.region = 'na'
        self.lockfile = self.get_lockfile()
        self.agents = requests.get("https://valorant-api.com/v1/agents").json()['data']
        self.pregame_url = f"https://glz-{self.region}-1.{self.region}.a.pvp.net/pregame/v1"
        self.entitlements = self.get_entitlements()
        self.player = self.get_player()
        
    def get_lockfile(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')

        with open(path) as lockfile:
            data = lockfile.read().split(':')
            keys = ['name', 'PID', 'port', 'password', 'protocol']
            return dict(zip(keys, data))
    
    def get_entitlements(self):
        response = requests.get(f"https://127.0.0.1:{self.lockfile['port']}/entitlements/v1/token", 
            headers = {
                'Authorization': "Basic " + base64.b64encode((f"riot:{self.lockfile['password']}").encode()).decode()
            },
            verify = False
        )
        return response.json()
    
    def get_player(self):
        response = requests.get(f"{self.pregame_url}/players/{self.entitlements['subject']}",
            headers = {
                'Authorization': f"Bearer {self.entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': self.entitlements['token'],
            }
        )
        return response.json()

    def get_match(self):
        response = requests.get(f"{self.pregame_url}/matches/{self.player['MatchID']}",
            headers = {
                'Authorization': f"Bearer {self.entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': self.entitlements['token'],
            }
        )
        return response.json()

    def select_random_agent(self):
        agent_id = self.agents[random.randint(0, len(self.agents) - 1)]['uuid']
        requests.post(f"{self.pregame_url}/matches/{self.player['MatchID']}/select/{agent_id}", 
            headers = {
                'Authorization': f"Bearer {self.entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': self.entitlements['token'],
            }
        )
        return


random_agent = Random_Agent()
window = tkinter.Tk()
window.geometry("300x100")
window.resizable(False, False)
window.title("VALORANT Random Agent")
window.attributes('-topmost',True)

button = tkinter.Button(window, text="RANDOM AGENT", command=random_agent.select_random_agent, bg="#7AD7F0", activebackground="#29b6f6")
button['font'] = font.Font(size=20, weight="bold")
button.pack(expand=True, fill="both")

def check_for_lock():
    match = random_agent.get_match()
    data = match["AllyTeam"]["Players"]

    for i in data:
        if (i['Subject'] == random_agent.entitlements['subject'] and i['CharacterSelectionState'] == 'locked'):
            return window.destroy()
    window.after(1000, check_for_lock)

window.after(1000, check_for_lock)
window.mainloop()
