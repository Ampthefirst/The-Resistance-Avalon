import tkinter as tk
from tkinter import messagebox, scrolledtext
import random

class AvalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Avalon Game")

        
        self.original_players = []    
        self.entries = []
        self.use_merlin = tk.BooleanVar(value=True)
        self.use_percival = tk.BooleanVar(value=True)
        self.roles = {}                
        self.current_player_index = 0  

      
        self.round_number = 1
        self.failed_proposals = 0
        self.previous_leaders = []
        self.selected_team = []
        self.mission_results = []      
        self.metadata = []             # for metadata section in the app; contains auxililary data about the game used for deduction aspects.
        self.past_missions = []        # additional history for deduction

        # Config
        self.max_failed_proposals = 5  # fixed

        self.setup_ui()


    def setup_ui(self):
        self.clear_root()
        tk.Label(self.root, text="Enter 5–10 player names:", font=("Arial", 14)).pack(pady=10)
        frame = tk.Frame(self.root)
        frame.pack()
        for i in range(10):
            e = tk.Entry(frame, width=20)
            e.grid(row=i, column=0, padx=5, pady=2)
            self.entries.append(e)
        cb_frame = tk.Frame(self.root)
        cb_frame.pack(pady=10)
        tk.Checkbutton(cb_frame, text="Include Merlin & Assassin", variable=self.use_merlin).pack(anchor='w')
        tk.Checkbutton(cb_frame, text="Include Percival & Morgana", variable=self.use_percival).pack(anchor='w')
        tk.Button(self.root, text="Start Game", command=self.validate_and_confirm).pack(pady=15)

    def validate_and_confirm(self):
        names = [e.get().strip() for e in self.entries if e.get().strip()]
        if len(names) < 5 or len(names) > 10:
            messagebox.showerror("Invalid Player Count", "Please enter between 5 and 10 player names.")
            return
        if self.use_percival.get() and not self.use_merlin.get():
            messagebox.showerror("Invalid Role Combo", "Percival & Morgana require Merlin & Assassin.")
            return
        self.original_players = names
        self.metadata.append(f"Game start with players: {', '.join(self.original_players)}")
        self.show_confirmation()

    def show_confirmation(self):
        self.clear_root()
        n = len(self.original_players)
        num_evil = {5:2,6:2,7:3,8:3,9:3,10:4}[n]
        num_good = n - num_evil
        summary = (
            f"Players: {n}   Good: {num_good}   Evil: {num_evil}\n"
            f"Merlin/Assassin: {'Yes' if self.use_merlin.get() else 'No'}   "
            f"Percival/Morgana: {'Yes' if self.use_percival.get() else 'No'}\n"
            f"Missions: 5 fixed"
        )
        tk.Label(self.root, text="Game Setup Summary", font=("Arial",16,"bold")).pack(pady=10)
        tk.Label(self.root, text=summary, font=("Arial",12), justify="left").pack(padx=20)
        tk.Button(self.root, text="Continue", command=self.assign_roles).pack(pady=15)


    def assign_roles(self):
        n = len(self.original_players)
        num_evil = {5:2,6:2,7:3,8:3,9:3,10:4}[n]
        num_good = n - num_evil
        roles = ['Evil']*num_evil + ['Good']*num_good
        specials = []
        if self.use_merlin.get():
            roles.remove('Good'); specials.append('Merlin')
            roles.remove('Evil'); specials.append('Assassin')
        if self.use_percival.get():
            roles.remove('Good'); specials.append('Percival')
            roles.remove('Evil'); specials.append('Morgana')
        all_roles = roles + specials
        random.shuffle(all_roles)
        self.roles = dict(zip(self.original_players, all_roles))
        self.current_player_index = 0
        self.metadata.append("Roles assigned.")
        self.show_role_privacy()


    def show_role_privacy(self):
        self.clear_root()
        if self.current_player_index >= len(self.original_players):
            self.start_team_proposal()
            return
        player = self.original_players[self.current_player_index]
        tk.Label(self.root, text=f"{player}, pass phone and press to view your role.", font=("Arial",14)).pack(pady=30)
        tk.Button(self.root, text="Show Role", command=self.show_actual_role).pack(pady=15)

    def show_actual_role(self):
        self.clear_root()
        player = self.original_players[self.current_player_index]
        role = self.roles[player]
        color = 'blue' if role in ['Good','Merlin','Percival'] else 'red'
        team = 'Good guys' if color=='blue' else 'Evil guys'
        tk.Label(self.root, text=f"{player}, your role:", font=("Arial",16)).pack(pady=10)
        tk.Label(self.root, text=role, font=("Arial",24,"bold"), fg=color).pack(pady=5)
        tk.Label(self.root, text=f"Team: {team}", font=("Arial",14), fg=color).pack(pady=5)
        extra = ""
        if role == 'Merlin':
            ev = [p for p,r in self.roles.items() if r in ['Evil','Assassin','Morgana']]
            extra = "Evil guys:\n" + "\n".join(ev)
        elif role == 'Percival':
            ml = [p for p,r in self.roles.items() if r in ['Merlin','Morgana']]
            random.shuffle(ml)
            extra = "Merlin is one of:\n" + "\n".join(ml)
        elif role in ['Evil','Assassin','Morgana']:
            mates = [p for p,r in self.roles.items() if r in ['Evil','Assassin','Morgana'] and p != player]
            if mates: extra = "Your fellow Evil:\n" + "\n".join(mates)
        if extra:
            tk.Label(self.root, text=extra, font=("Arial",12), justify="center").pack(pady=10)
        tk.Button(self.root, text="Continue", command=self.next_reveal).pack(pady=15)

    def next_reveal(self):
        self.current_player_index += 1
        self.show_role_privacy()


    def start_team_proposal(self):
        self.clear_root()
 
        if self.failed_proposals == 0 and not any(f"Round {self.round_number} start" in e for e in self.metadata):
            self.metadata.append(f"Round {self.round_number} start.")

        eligible = [p for p in self.original_players if p not in self.previous_leaders]
        leader = random.choice(eligible)
        self.current_leader = leader
        self.metadata.append(f"Leader {leader} selected for Round {self.round_number}")


        sizes = {5:[2,3,2,3,3],6:[2,3,4,3,4],7:[2,3,3,4,4],8:[3,4,4,5,5],9:[3,4,4,5,5],10:[3,4,4,5,5]}
        ts = sizes[len(self.original_players)][self.round_number-1]

 
        past = ""
        for idx,m in enumerate(self.past_missions,1):
            res = "Passed" if m['pass'] else 'Failed'
            line = f"M{idx}: Leader {m['leader']} team {m['team']} -> {res}"
            if not m['pass']:
                line += f" (Fails: {m.get('fails',0)})"
            past += line + "\n"


        tk.Label(self.root, text="Team Proposal Phase", font=("Arial",14,"bold")).pack()
        info = (
            f"Round {self.round_number}/5 | Leader: {leader}\n"
            f"Team size: {ts}\n"
            f"Previous leaders: {', '.join(self.previous_leaders) or 'None'}\n"
            f"Failed proposals: {self.failed_proposals}/{self.max_failed_proposals}\n"
            f"Mission sizes: {sizes[len(self.original_players)]}\n"
        )
        tk.Label(self.root, text=info, font=("Arial",10), justify="left").pack(padx=10)
        if past:
            tk.Label(self.root, text="Past Missions:", font=("Arial",12,"underline")).pack(pady=(5,0))
            tk.Label(self.root, text=past, font=("Arial",10), justify="left").pack(padx=10)
        tk.Label(self.root, text="Metadata:", font=("Arial",12,"underline")).pack(pady=(5,0))
        txt = scrolledtext.ScrolledText(self.root, width=40, height=8, state='normal')
        for line in reversed(self.metadata[-10:]): txt.insert('end', line+"\n")
        txt.config(state='disabled'); txt.pack(pady=5)

        self.check_vars = {}
        for p in self.original_players:
            v = tk.BooleanVar(); cb = tk.Checkbutton(self.root, text=p, variable=v)
            cb.pack(anchor='w'); self.check_vars[p] = v
        tk.Button(self.root, text="Submit Team", command=lambda:self.submit_team(ts)).pack(pady=10)

    def submit_team(self, req):
        sel = [p for p,v in self.check_vars.items() if v.get()]
        if len(sel) != req:
            messagebox.showerror("Team Size Incorrect", f"Select exactly {req} players.")
            return
        self.selected_team = sel
        self.metadata.append(f"Proposal by {self.current_leader}: {sel}")
        self.ask_vote_result()

    def ask_vote_result(self):
        self.clear_root()
        tk.Label(self.root, text="Team Vote", font=("Arial",16)).pack(pady=10)
        tk.Label(self.root, text="Was the team approved by majority?", font=("Arial",12)).pack(pady=5)
        tk.Button(self.root, text="Approved", command=self.team_approved).pack(pady=5)
        tk.Button(self.root, text="Rejected", command=self.team_rejected).pack(pady=5)

    def team_rejected(self):
        self.failed_proposals += 1
        self.previous_leaders.append(self.current_leader)
        self.metadata.append(f"Proposal by {self.current_leader} rejected")
        if self.failed_proposals >= self.max_failed_proposals:
            # rule exception with mission failing
            self.metadata.append(f"Mission {self.round_number} auto-failed after {self.failed_proposals} rejections")
            self.past_missions.append({
                'leader': self.current_leader,
                'team': [],
                'pass': False,
                'fails': 0
            })
       
            self.round_number += 1
            self.failed_proposals = 0
            self.previous_leaders = []
            self.start_team_proposal()
            return
        self.start_team_proposal()

    def team_approved(self):
        self.metadata.append(f"Proposal by {self.current_leader} approved")
        self.begin_mission_voting()


    def begin_mission_voting(self):
        self.mission_votes = []
        self.mission_vote_index = 0
        self.show_next_mission_vote()

    def show_next_mission_vote(self):
        self.clear_root()
        if self.mission_vote_index >= len(self.selected_team):
            self.show_mission_result()
            return
        player = self.selected_team[self.mission_vote_index]
        role = self.roles[player]
        is_evil = role in ['Evil','Assassin','Morgana']
        tk.Label(self.root, text=f"{player}, your mission vote:", font=("Arial",14)).pack(pady=10)
        def sub(v):
            if not is_evil and v=='Fail': v='Pass'
            self.mission_votes.append(v)
            self.mission_vote_index += 1
            self.show_next_mission_vote()
        tk.Button(self.root, text="Pass", command=lambda: sub('Pass')).pack(pady=5)
        tk.Button(self.root, text="Fail", command=lambda: sub('Fail')).pack(pady=5)

    def show_mission_result(self):
        self.clear_root()
        fails = self.mission_votes.count('Fail')
        passed = (fails == 0)
        # Record mission
        self.past_missions.append({
            'leader': self.current_leader,
            'team': self.selected_team,
            'pass': passed,
            'fails': fails
        })
        self.metadata.append( f"Mission {self.round_number} result: {'Passed' if passed else 'Failed'} ({fails}/{len(self.selected_team)})")

        tk.Label(self.root, text="Mission Results", font=("Arial",16)).pack(pady=10)
        tk.Label(self.root, text=f"Fails: {fails}", font=("Arial",12)).pack()
        tk.Label(self.root, text=("PASSED!" if passed else "FAILED!"), font=("Arial",14,"bold"), fg=('green' if passed else 'red')).pack(pady=5)

        self.mission_results.append(passed)
        gw = self.mission_results.count(True)
        ew = self.mission_results.count(False)
        if gw >= 3:
            tk.Label(self.root, text="Good wins 3 missions! Assassin phase pending.").pack(pady=5)
            tk.Button(self.root, text="End Game", command=self.root.quit).pack(pady=5)
        elif ew >= 3:
            tk.Label(self.root, text="Evil wins 3 failed missions!", fg='red').pack(pady=5)
            tk.Button(self.root, text="End Game", command=self.root.quit).pack(pady=5)
        else:
            self.round_number += 1
            self.failed_proposals = 0
            self.previous_leaders = []
            tk.Button(self.root, text="Continue", command=self.start_team_proposal).pack(pady=10)

    def clear_root(self):
        for w in self.root.winfo_children(): w.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AvalonApp(root)
    root.mainloop()

