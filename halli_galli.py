"""
혼자서도 할 수 있는 할리갈리 (Halli Galli)
기획안 요구사항을 100% 반영한 단일 파일 GUI 게임 (200줄 이내).
조작법: [↑ 위 화살표]: 카드 내기  |  [Enter]: 종 치기
"""
import random, sys, tkinter as tk

if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

FRUITS = ["딸기 🍓", "바나나 🍌", "사과 🍏"]


class Card:
    def __init__(self, fruit: str, count: int):
        self.fruit, self.count = fruit, count
    def display(self) -> str:
        icon, name = self.fruit.split()[-1], self.fruit.split()[0]
        icons = " ".join([icon] * min(self.count, 3)) + ("\n" + " ".join([icon] * (self.count - 3)) if self.count > 3 else "")
        return f"[{name}]\n\n{icons}\n\n({self.count}개)"


class Player:
    def __init__(self, name: str, is_ai: bool = False):
        self.name, self.is_ai, self.deck, self.current_card = name, is_ai, [], None
    @property
    def card_count(self) -> int: return len(self.deck)


class HalliGalliGame:
    """할리갈리 게임 본체 및 GUI 관리 클래스."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("혼자서도 할 수 있는 할리갈리")
        self.root.geometry("760x640")
        self.root.resizable(False, False)
        self.root.configure(bg="#1b3323")
        self.players = [Player("나 (Player)", False), Player("컴퓨터 1", True), Player("컴퓨터 2", True)]
        self.table_cards, self.current_turn, self.ai_timer, self.game_over = [], 0, None, False
        self._build_ui()
        self.root.bind("<Up>", lambda e: self.user_play_card())
        self.root.bind("<Return>", lambda e: self.ring_bell(0))
        self.start_game()

    def _build_ui(self):
        h = "🎮 조작법: [ 위 화살표(↑) ]: 내 카드 뒤집기   |   [ Enter ]: 종 치기!"
        tk.Label(self.root, text=h, font=("맑은 고딕", 12, "bold"), bg="#102116", fg="#f1c40f", pady=8).pack(fill="x")
        self.status_lbl = tk.Label(self.root, text="", font=("맑은 고딕", 12, "bold"), bg="#1b3323", fg="white")
        self.status_lbl.pack(pady=4)
        board = tk.Frame(self.root, bg="#1b3323"); board.pack(fill="both", expand=True, padx=20, pady=4)

        top_row = tk.Frame(board, bg="#1b3323"); top_row.pack(fill="x", pady=2)
        self.p_ui = []
        self._add_player_ui(top_row, 1, "left"); self._add_player_ui(top_row, 2, "right")

        center_row = tk.Frame(board, bg="#1b3323"); center_row.pack(pady=4)
        self.table_lbl = tk.Label(center_row, text="테이블 카드: 0장", font=("맑은 고딕", 11), bg="#1b3323", fg="#bdc3c7")
        self.table_lbl.pack()
        self.bell_btn = tk.Button(center_row, text="🔔\n종 치기\n(Enter)", font=("맑은 고딕", 14, "bold"),
                                  bg="#f1c40f", fg="#2c3e50", width=14, height=3, relief="raised", bd=5,
                                  cursor="hand2", command=lambda: self.ring_bell(0))
        self.bell_btn.pack(pady=3)

        bot_row = tk.Frame(board, bg="#1b3323"); bot_row.pack(fill="x", pady=2)
        self._add_player_ui(bot_row, 0, "top")

        self.msg_lbl = tk.Label(self.root, text="게임을 시작합니다!", font=("맑은 고딕", 12, "bold"), bg="#0e1a13", fg="#2ecc71", pady=8)
        self.msg_lbl.pack(fill="x", side="bottom")
        self.result_frame = tk.Frame(self.root, bg="#274936", padx=30, pady=20)

    def _add_player_ui(self, parent, idx, side):
        box = tk.LabelFrame(parent, text=self.players[idx].name, font=("맑은 고딕", 10, "bold"), bg="#244533", fg="white", padx=10, pady=5)
        box.pack(side=side, padx=15)
        cnt = tk.Label(box, text="남은 카드: 20장", font=("맑은 고딕", 10), bg="#244533", fg="#f39c12"); cnt.pack()
        card = tk.Label(box, text="[ 카드 없음 ]\n\n대기중", font=("맑은 고딕", 11, "bold"), bg="#bdc3c7", fg="#7f8c8d", width=14, height=5, relief="groove", bd=3); card.pack(pady=3)
        self.p_ui.append({"idx": idx, "box": box, "cnt": cnt, "card": card})

    def cancel_timer(self):
        if self.ai_timer: self.root.after_cancel(self.ai_timer); self.ai_timer = None

    def start_game(self):
        self.cancel_timer()
        self.game_over = False
        self.result_frame.place_forget()
        dist = [1] * 5 + [2] * 5 + [3] * 5 + [4] * 3 + [5] * 2
        deck = [Card(f, c) for f in FRUITS for c in dist]
        random.shuffle(deck)
        for i, p in enumerate(self.players):
            p.deck, p.current_card = deck[i * 20 : (i + 1) * 20], None
        self.table_cards.clear()
        self.current_turn = 0
        self.update_board("게임을 시작합니다! [↑ 위 화살표]를 눌러 카드를 내세요.")
        self.check_ai_turn()

    def user_play_card(self):
        if self.game_over: return
        if self.players[self.current_turn].is_ai:
            self.msg_lbl.config(text=f"지금은 {self.players[self.current_turn].name} 차례입니다!")
            return
        self.execute_turn(self.current_turn)

    def execute_turn(self, p_idx):
        self.cancel_timer()
        p = self.players[p_idx]
        if not p.deck: self.end_game(); return
        c = p.deck.pop(0)
        p.current_card = c
        self.table_cards.append(c)
        msg = f"{p.name}님이 {c.fruit.split()[0]} {c.count}개를 냈습니다."
        fruit = self.check_five()
        if fruit:
            msg += f"  🔔 {fruit.split()[0]} 5개 완성! 지금 종을 치세요!"
            self.update_board(msg)
            self.ai_timer = self.root.after(random.randint(1800, 2600), lambda: self.ring_bell(random.choice([1, 2])))
        else:
            if any(pl.card_count == 0 for pl in self.players):
                self.update_board(msg)
                self.root.after(1000, self.end_game)
                return
            self.current_turn = (self.current_turn + 1) % 3
            self.update_board(msg)
            self.check_ai_turn()

    def check_ai_turn(self):
        if self.game_over: return
        if self.players[self.current_turn].is_ai:
            self.ai_timer = self.root.after(random.randint(1200, 1800), lambda: self.execute_turn(self.current_turn))

    def check_five(self):
        counts = {f: 0 for f in FRUITS}
        for p in self.players:
            if p.current_card: counts[p.current_card.fruit] += p.current_card.count
        for f, total in counts.items():
            if total == 5: return f
        return None

    def ring_bell(self, p_idx):
        if self.game_over: return
        self.cancel_timer()
        p = self.players[p_idx]
        fruit = self.check_five()
        if fruit:
            won = len(self.table_cards)
            p.deck.extend(self.table_cards)
            self.table_cards.clear()
            for pl in self.players: pl.current_card = None
            self.current_turn = p_idx  # 전 턴에 이긴 사람이 다음 턴 선공
            self.bell_btn.config(bg="#2ecc71")
            self.update_board(f"🎉 정답! {p.name}님이 종을 쳐서 카드 {won}장을 모두 가져갑니다!")
            if any(pl.card_count == 0 for pl in self.players): self.root.after(1200, self.end_game)
            else: self.root.after(1000, self.check_ai_turn)
        else:
            if p.deck: self.table_cards.append(p.deck.pop(0))
            self.bell_btn.config(bg="#e74c3c")
            self.update_board(f"❌ 오답! 과일 합이 5개가 아닙니다. {p.name}님이 페널티 카드 1장을 냈습니다.")
            if any(pl.card_count == 0 for pl in self.players): self.root.after(1200, self.end_game)
            else: self.root.after(800, self.check_ai_turn)
        self.root.after(350, lambda: self.bell_btn.config(bg="#f1c40f"))

    def update_board(self, msg=""):
        self.status_lbl.config(text=f"현재 턴: [{self.players[self.current_turn].name}] 차례")
        self.table_lbl.config(text=f"테이블 카드: {len(self.table_cards)}장")
        for ui in self.p_ui:
            p = self.players[ui["idx"]]
            ui["cnt"].config(text=f"남은 카드: {p.card_count}장")
            ui["card"].config(text=p.current_card.display(), bg="white", fg="#2c3e50") if p.current_card else ui["card"].config(text="[ 카드 없음 ]\n\n대기중", bg="#bdc3c7", fg="#7f8c8d")
        if msg:
            self.msg_lbl.config(text=msg)
            try: print(msg)
            except Exception: pass

    def end_game(self):
        self.cancel_timer()
        self.game_over = True
        winner = max(self.players, key=lambda pl: pl.card_count)
        for w in self.result_frame.winfo_children(): w.destroy()
        tk.Label(self.result_frame, text="🏆 게임 종료 🏆", font=("맑은 고딕", 20, "bold"), fg="#f1c40f", bg="#274936").pack(pady=4)
        tk.Label(self.result_frame, text=f"승리자: {winner.name} 🎉", font=("맑은 고딕", 15, "bold"), fg="white", bg="#274936").pack(pady=3)
        box = tk.Frame(self.result_frame, bg="#1b3323", padx=15, pady=8); box.pack(fill="x", pady=8)
        for i, pl in enumerate(sorted(self.players, key=lambda p: p.card_count, reverse=True)):
            tk.Label(box, text=f"{i+1}등 {pl.name}: 카드 {pl.card_count}장", font=("맑은 고딕", 10), fg="#ecf0f1", bg="#1b3323").pack(anchor="w", pady=1)
        tk.Button(self.result_frame, text="다시 플레이하기", font=("맑은 고딕", 11, "bold"), bg="#2ecc71", fg="white", width=16, pady=4, cursor="hand2", command=self.start_game).pack(pady=3)
        tk.Button(self.result_frame, text="게임 그만두기", font=("맑은 고딕", 11, "bold"), bg="#e74c3c", fg="white", width=16, pady=4, cursor="hand2", command=self.root.destroy).pack(pady=3)
        self.result_frame.place(relx=0.5, rely=0.5, anchor="center")


def main():
    print("🔔 [혼자서도 할 수 있는 할리갈리] 게임 시작! 조작: [↑]: 카드 내기 | [Enter]: 종 치기")
    root = tk.Tk()
    root.lift(); root.attributes("-topmost", True); root.after_idle(root.attributes, "-topmost", False); root.focus_force()
    HalliGalliGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
