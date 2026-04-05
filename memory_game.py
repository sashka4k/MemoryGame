import tkinter as tk
from tkinter import messagebox
import random
import time


class MemoryGame:
    """
    Основной класс игры "Найди пару".
    Реализует игровую логику и графический интерфейс.
    """

    def __init__(self):
        """
        Инициализация главного окна, переменных состояния и создание интерфейса.
        """
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("Найди пару — Игра для тренировки памяти")
        self.root.resizable(False, False)  # Запрещаем изменение размера окна

        # Игровые параметры
        self.rows = 4
        self.cols = 4
        self.total_cards = self.rows * self.cols
        self.total_pairs = self.total_cards // 2

        # Состояние игры
        self.icons = []  # Список символов для карточек (дублируются для пар)
        self.buttons = []  # 2D список кнопок (игровое поле)
        self.is_revealed = []  # Маска: открыта карта или нет (True/False)
        self.is_matched = []  # Найдена ли пара (True/False) -> зеленая кнопка

        self.first_index = None  # Индекс первой открытой карты (линейный)
        self.second_index = None  # Индекс второй открытой карты
        self.waiting = False  # Блокировка кликов при ожидании закрытия карт
        self.moves = 0  # Счётчик ходов
        self.pairs_found = 0  # Счётчик найденных пар
        self.start_time = None  # Время начала текущей игры
        self.timer_running = False

        # Интерфейсные элементы
        self.moves_label = None
        self.pairs_label = None
        self.timer_label = None
        self.info_frame = None
        self.game_frame = None

        # Запускаем создание интерфейса и первой игры
        self.setup_ui()
        self.new_game()

    # ------------------- Игровая логика -------------------

    def generate_icons(self):
        """
        Генерирует список иконок (символов) для карточек.
        Всего 8 пар → 16 элементов, затем перемешивает.
        """
        # Используем символы эмодзи и простые символы для наглядности
        symbols = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼']
        # Каждый символ берется 2 раза (пара)
        icons = symbols * 2
        random.shuffle(icons)
        return icons

    def new_game(self):
        """
        Полностью сбрасывает игру: перемешивает карты, обнуляет счётчики,
        сбрасывает таймер, перерисовывает поле.
        """
        # Сброс игровых переменных
        self.icons = self.generate_icons()
        self.is_revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.is_matched = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.first_index = None
        self.second_index = None
        self.waiting = False
        self.moves = 0
        self.pairs_found = 0
        self.start_time = time.time()
        self.timer_running = True

        # Обновление интерфейса
        self.update_stats()
        self.update_board()

        # Если таймер уже обновляется, он продолжит, иначе запускаем
        self.update_timer()

    def update_board(self):
        """
        Обновляет текст и цвет всех кнопок в соответствии с текущим состоянием.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                idx = i * self.cols + j
                card_text = ""
                btn = self.buttons[i][j]

                if self.is_matched[i][j]:
                    # Найденная пара — зеленая и показывает символ
                    card_text = self.icons[idx]
                    btn.config(text=card_text, state=tk.DISABLED, bg='light green')
                elif self.is_revealed[i][j]:
                    # Открытая, но не найденная карта
                    card_text = self.icons[idx]
                    btn.config(text=card_text, state=tk.NORMAL, bg='white')
                else:
                    # Закрытая карта
                    card_text = "?"
                    btn.config(text=card_text, state=tk.NORMAL, bg='light gray')

    def update_stats(self):
        """
        Обновляет текстовые метки счётчика ходов и найденных пар.
        """
        self.moves_label.config(text=f"Ходы: {self.moves}")
        self.pairs_label.config(text=f"Пары: {self.pairs_found} / {self.total_pairs}")

    def update_timer(self):
        """
        Обновляет отображение таймера (вызывается каждую секунду).
        """
        if self.timer_running and self.start_time is not None:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"Время: {minutes:02d}:{seconds:02d}")
            # Запланировать следующий вызов через 1 секунду
            self.root.after(1000, self.update_timer)

    def check_win(self):
        """
        Проверяет, все ли пары найдены. Если да — показывает сообщение о победе.
        """
        if self.pairs_found == self.total_pairs:
            self.timer_running = False
            elapsed = int(time.time() - self.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            messagebox.showinfo(
                "Победа!",
                f"🎉 Вы нашли все пары! 🎉\n\n"
                f"Ходов сделано: {self.moves}\n"
                f"Затраченное время: {mins:02d}:{secs:02d}"
            )
            # После победы можно начать новую игру (кнопка уже есть)

    def on_card_click(self, row, col):
        """
        Обработчик клика по карточке.
        Реализует всю игровую логику: открытие, сравнение, блокировку.
        """
        # Если сейчас ожидание или карта уже открыта/найдена — игнорируем клик
        if self.waiting:
            return
        if self.is_matched[row][col]:
            return
        if self.is_revealed[row][col]:
            return

        # Открываем текущую карту
        self.is_revealed[row][col] = True
        self.update_board()

        # Если первая карта ещё не выбрана
        if self.first_index is None:
            self.first_index = (row, col)
        # Если вторая карта не выбрана и это не клик по той же карте
        elif self.second_index is None:
            # Это второй клик — увеличиваем счётчик ходов
            self.moves += 1
            self.update_stats()
            self.second_index = (row, col)

            # Получаем символы карт
            r1, c1 = self.first_index
            r2, c2 = self.second_index
            idx1 = r1 * self.cols + c1
            idx2 = r2 * self.cols + c2

            # Сравниваем карты
            if self.icons[idx1] == self.icons[idx2]:
                # Карты совпали → оставляем открытыми и помечаем как найденные
                self.is_matched[r1][c1] = True
                self.is_matched[r2][c2] = True
                self.is_revealed[r1][c1] = True
                self.is_revealed[r2][c2] = True
                self.pairs_found += 1
                self.update_stats()
                self.update_board()
                # Сбрасываем индексы открытых карт
                self.first_index = None
                self.second_index = None
                self.check_win()
            else:
                # Карты не совпали — запускаем таймер на закрытие
                self.waiting = True
                self.root.after(1000, self.reset_unmatched_cards)
        else:
            # Если уже две открытые карты (теоретически не должно случиться из-за блокировки)
            pass

    def reset_unmatched_cards(self):
        """
        Закрывает две несовпавшие карты (вызывается через 1 секунду).
        """
        if self.first_index is not None and self.second_index is not None:
            r1, c1 = self.first_index
            r2, c2 = self.second_index
            # Закрываем, только если они не были найдены (на всякий случай)
            if not self.is_matched[r1][c1]:
                self.is_revealed[r1][c1] = False
            if not self.is_matched[r2][c2]:
                self.is_revealed[r2][c2] = False

        # Сбрасываем индексы и снимаем блокировку
        self.first_index = None
        self.second_index = None
        self.waiting = False
        self.update_board()

    # ------------------- Интерфейс -------------------

    def setup_ui(self):
        """
        Создаёт все графические элементы: информационную панель и игровое поле.
        """
        # Верхняя панель со статистикой
        self.info_frame = tk.Frame(self.root, bg='#f0f0f0', padx=10, pady=10)
        self.info_frame.pack(fill=tk.X)

        self.moves_label = tk.Label(self.info_frame, text="Ходы: 0", font=("Arial", 12, "bold"), bg='#f0f0f0')
        self.moves_label.pack(side=tk.LEFT, padx=20)

        self.pairs_label = tk.Label(self.info_frame, text="Пары: 0 / 8", font=("Arial", 12, "bold"), bg='#f0f0f0')
        self.pairs_label.pack(side=tk.LEFT, padx=20)

        self.timer_label = tk.Label(self.info_frame, text="Время: 00:00", font=("Arial", 12, "bold"), bg='#f0f0f0')
        self.timer_label.pack(side=tk.LEFT, padx=20)

        new_game_btn = tk.Button(self.info_frame, text="🔄 Новая игра", font=("Arial", 10),
                                 command=self.new_game, bg='light blue', padx=10)
        new_game_btn.pack(side=tk.RIGHT, padx=20)

        # Игровое поле (сетка кнопок 4x4)
        self.game_frame = tk.Frame(self.root, bg='white')
        self.game_frame.pack(pady=20)

        self.buttons = []
        for i in range(self.rows):
            row_buttons = []
            for j in range(self.cols):
                btn = tk.Button(
                    self.game_frame,
                    text="?",
                    font=("Arial", 24, "bold"),
                    width=4,
                    height=2,
                    bg='light gray',
                    command=lambda r=i, c=j: self.on_card_click(r, c)
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    def run(self):
        """
        Запускает главный цикл приложения tkinter.
        """
        self.root.mainloop()


# Точка входа в программу
if __name__ == "__main__":
    game = MemoryGame()
    game.run()
