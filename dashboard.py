
import customtkinter as ctk
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date
import calendar

import database


BG = "#0B1120"
CARD = "#182235"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
GREEN = "#22C55E"
RED = "#EF4444"
BLUE = "#3B82F6"

ROMANIAN_MONTHS = [
    "Ianuarie", "Februarie", "Martie", "Aprilie",
    "Mai", "Iunie", "Iulie", "August",
    "Septembrie", "Octombrie", "Noiembrie", "Decembrie"
]


def money(value):
    return f"{value:,.2f} RON".replace(
        ",", "X"
    ).replace(".", ",").replace("X", ".")


class Dashboard(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color=BG)

        self.year = date.today().year
        self.month = date.today().month

        self.pack(fill="both", expand=True)

        self.create_interface()
        self.refresh()

    def create_interface(self):

        self.header = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        self.header.pack(fill="x", pady=15)

        ctk.CTkLabel(
            self.header,
            text="Financial Overview",
            font=("Arial", 27, "bold"),
            text_color=TEXT
        ).pack(side="left")

        navigation = ctk.CTkFrame(
            self.header, fg_color="transparent"
        )
        navigation.pack(side="right")

        ctk.CTkButton(
            navigation, text="◀",
            width=35, command=self.previous_month
        ).pack(side="left", padx=3)

        self.month_label = ctk.CTkLabel(
            navigation,
            text="",
            font=("Arial", 14, "bold"),
            text_color=TEXT,
            width=150
        )
        self.month_label.pack(side="left", padx=5)

        ctk.CTkButton(
            navigation, text="▶",
            width=35, command=self.next_month
        ).pack(side="left", padx=3)

        # Statistics cards

        self.stats_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        self.stats_frame.pack(fill="x", pady=10)

        self.stats_frame.grid_columnconfigure(
            (0, 1, 2, 3), weight=1
        )

        self.stat_values = []

        stats = [
            ("INCOME", GREEN),
            ("EXPENSES", RED),
            ("BALANCE", BLUE),
            ("SAVINGS RATE", "#A78BFA")
        ]

        for index, (title, color) in enumerate(stats):

            card = ctk.CTkFrame(
                self.stats_frame,
                fg_color=CARD,
                corner_radius=12
            )
            card.grid(
                row=0, column=index,
                sticky="ew", padx=5, ipady=15
            )

            ctk.CTkLabel(
                card,
                text=title,
                text_color=MUTED,
                font=("Arial", 11, "bold")
            ).pack(anchor="w", padx=15, pady=(12, 5))

            value = ctk.CTkLabel(
                card,
                text="0 RON",
                text_color=color,
                font=("Arial", 17, "bold")
            )
            value.pack(anchor="w", padx=15, pady=(0, 12))

            self.stat_values.append(value)

        # Charts area

        self.charts = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        self.charts.pack(fill="both", expand=True, pady=10)

        self.charts.grid_columnconfigure((0, 1), weight=1)
        self.charts.grid_rowconfigure(0, weight=1)

        self.cashflow_card = self.make_chart_card(
            self.charts, 0, 0, "Income vs Expenses"
        )

        self.category_card = self.make_chart_card(
            self.charts, 0, 1, "Spending by Category"
        )

    def make_chart_card(self, parent, row, column, title):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=12
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=5,
            pady=5
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 16, "bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=15, pady=15)

        return card

    def previous_month(self):

        self.month -= 1

        if self.month < 1:
            self.month = 12
            self.year -= 1

        self.refresh()

    def next_month(self):

        self.month += 1

        if self.month > 12:
            self.month = 1
            self.year += 1

        self.refresh()

    def refresh(self):

        self.month_label.configure(
            text=f"{ROMANIAN_MONTHS[self.month - 1]} {self.year}"
        )

        totals = database.get_monthly_totals(
            self.year, self.month
        )

        income = totals["Income"]
        expenses = totals["Expense"]
        balance = income - expenses

        savings = (
            (balance / income) * 100
            if income > 0 else 0
        )

        values = [
            money(income),
            money(expenses),
            money(balance),
            f"{savings:.1f}%"
        ]

        for label, value in zip(self.stat_values, values):
            label.configure(text=value)

        self.draw_cashflow()
        self.draw_categories()

    def draw_cashflow(self):

        for widget in self.cashflow_card.winfo_children()[1:]:
            widget.destroy()

        records = database.get_daily_totals(
            self.year, self.month
        )

        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor(CARD)

        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        days = [row["transaction_date"][-2:] for row in records]
        incomes = [row["income"] for row in records]
        expenses = [row["expenses"] for row in records]

        x = list(range(len(days)))
        width = 0.38

        ax.bar(
            [i - width / 2 for i in x],
            incomes, width,
            color=GREEN, label="Income"
        )

        ax.bar(
            [i + width / 2 for i in x],
            expenses, width,
            color=RED, label="Expenses"
        )

        ax.set_xticks(x)
        ax.set_xticklabels(days, color=MUTED)
        ax.tick_params(colors=MUTED)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(MUTED)

        ax.legend(
            facecolor=CARD,
            labelcolor=TEXT,
            frameon=False
        )

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(
            fig, master=self.cashflow_card
        )
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10
        )

    def draw_categories(self):

        for widget in self.category_card.winfo_children()[1:]:
            widget.destroy()

        records = database.get_category_totals(
            self.year, self.month
        )

        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor(CARD)

        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        if records:
            labels = [row["category"] for row in records]
            amounts = [row["total"] for row in records]

            colors = [
                "#3B82F6", "#22C55E", "#F59E0B",
                "#A78BFA", "#EF4444", "#06B6D4",
                "#EC4899", "#84CC16"
            ]

            ax.pie(
                amounts,
                labels=labels,
                colors=colors[:len(labels)] if len(labels) <= len(colors) else colors,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"color": TEXT, "fontsize": 9},
                wedgeprops={"width": 0.4}
            )

        else:
            ax.text(
                0.5, 0.5,
                "No expenses this month",
                ha="center", va="center",
                color=MUTED,
                transform=ax.transAxes
            )

        ax.axis("equal")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(
            fig, master=self.category_card
        )
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=10
        )

