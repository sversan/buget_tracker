
import customtkinter as ctk
from tkinter import messagebox
from datetime import date

import database
from dashboard import Dashboard


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0B1120"
SIDEBAR = "#111827"
CARD = "#182235"
CARD_LIGHT = "#202D42"
ACCENT = "#3B82F6"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"


def format_money(amount):
    return (
        f"{amount:,.2f} RON"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ==========================================
# MAIN APPLICATION
# ==========================================

class BudgetApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        database.initialize_database()

        self.title("My Budget Manager")
        self.geometry("1200x760")
        self.minsize(950, 650)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()

        self.content = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=25,
            pady=20
        )

        self.show_dashboard()

    # ======================================
    # SIDEBAR
    # ======================================

    def create_sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=SIDEBAR,
            corner_radius=0
        )

        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="◈  MY BUDGET",
            font=("Arial", 22, "bold"),
            text_color=TEXT
        ).pack(pady=(35, 45), padx=20)

        buttons = [
            ("▦   Dashboard", self.show_dashboard),
            ("↔   Transactions", self.show_transactions),
        ]

        for label, command in buttons:

            ctk.CTkButton(
                sidebar,
                text=label,
                command=command,
                height=45,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                hover_color=CARD_LIGHT,
                text_color=TEXT,
                font=("Arial", 14)
            ).pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            sidebar,
            text="PERSONAL FINANCE",
            text_color=MUTED,
            font=("Arial", 10, "bold")
        ).pack(side="bottom", pady=25)

    # ======================================
    # CONTENT MANAGEMENT
    # ======================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def create_header(self, title, subtitle):

        header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        header.pack(fill="x", pady=(5, 25))

        ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 28, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=subtitle,
            font=("Arial", 13),
            text_color=MUTED
        ).pack(anchor="w", pady=(5, 0))

    # ======================================
    # DASHBOARD
    # ======================================

    def show_dashboard(self):

        self.clear_content()

        Dashboard(self.content)

    # ======================================
    # TRANSACTION HISTORY
    # ======================================

    def show_transactions(self):

        self.clear_content()

        self.create_header(
            "Transactions",
            "Manage your income and expenses"
        )

        toolbar = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        toolbar.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(
            toolbar,
            text="+ Add Transaction",
            command=self.add_transaction_window,
            fg_color=ACCENT,
            hover_color="#2563EB",
            height=40
        ).pack(side="right")

        self.create_transaction_table()

    # ======================================
    # TRANSACTION TABLE
    # ======================================

    def create_transaction_table(self):

        container = ctk.CTkFrame(
            self.content,
            fg_color=CARD,
            corner_radius=12
        )

        container.pack(fill="both", expand=True)

        # Table header

        headers = [
            ("DATE", 1),
            ("TYPE", 1),
            ("CATEGORY", 1),
            ("DESCRIPTION", 2),
            ("AMOUNT", 1)
        ]

        header = ctk.CTkFrame(
            container,
            fg_color=CARD_LIGHT,
            corner_radius=8
        )

        header.pack(fill="x", padx=12, pady=12)

        for title, _ in headers:

            ctk.CTkLabel(
                header,
                text=title,
                text_color=MUTED,
                font=("Arial", 11, "bold")
            ).pack(side="left", expand=True, fill="x", padx=5, pady=12)

        # Transactions

        transactions = database.get_transactions()

        if not transactions:

            ctk.CTkLabel(
                container,
                text="No transactions yet.",
                text_color=MUTED,
                font=("Arial", 14)
            ).pack(pady=40)

            return

        for transaction in transactions:

            row = ctk.CTkFrame(
                container,
                fg_color="transparent"
            )

            row.pack(fill="x", padx=12, pady=5)

            kind = transaction["transaction_type"]

            color = (
                "#22C55E"
                if kind == "Income"
                else "#EF4444"
            )

            sign = "+" if kind == "Income" else "-"

            values = [
                transaction["transaction_date"],
                kind,
                transaction["category"],
                transaction["description"] or "-",
                sign + format_money(transaction["amount"])
            ]

            for index, value in enumerate(values):

                ctk.CTkLabel(
                    row,
                    text=value,
                    text_color=color if index == 4 else TEXT,
                    font=("Arial", 12),
                    anchor="w"
                ).pack(side="left", expand=True, fill="x", padx=5, pady=10)

            ctk.CTkFrame(
                container,
                height=1,
                fg_color=CARD_LIGHT
            ).pack(fill="x", padx=12)

    # ======================================
    # ADD TRANSACTION WINDOW
    # ======================================

    def add_transaction_window(self):

        window = ctk.CTkToplevel(self)

        window.title("Add Transaction")
        window.geometry("430x540")
        window.resizable(False, False)
        window.configure(fg_color=BG)

        window.transient(self)
        window.grab_set()

        ctk.CTkLabel(
            window,
            text="New Transaction",
            font=("Arial", 24, "bold"),
            text_color=TEXT
        ).pack(pady=(25, 20))

        ctk.CTkLabel(
            window,
            text="Transaction Type",
            text_color=MUTED
        ).pack(anchor="w", padx=35)

        transaction_type = ctk.CTkOptionMenu(
            window,
            values=["Expense", "Income"],
            fg_color=CARD_LIGHT,
            button_color=ACCENT,
            width=350
        )

        transaction_type.pack(pady=(5, 15))

        fields = {}

        field_data = [
            ("Amount (RON)", "0.00"),
            ("Category", "Food"),
            ("Description", "Optional description"),
            ("Date (YYYY-MM-DD)", date.today().isoformat())
        ]

        for label, placeholder in field_data:

            ctk.CTkLabel(
                window,
                text=label,
                text_color=MUTED
            ).pack(anchor="w", padx=35)

            entry = ctk.CTkEntry(
                window,
                width=350,
                height=38,
                placeholder_text=placeholder
            )

            entry.pack(pady=(5, 12))

            fields[label] = entry

            if label == "Date (YYYY-MM-DD)":
                entry.insert(0, date.today().isoformat())

        # Save transaction

        def save_transaction():

            try:

                amount = float(
                    fields["Amount (RON)"]
                    .get()
                    .replace(",", ".")
                )

                if amount <= 0:
                    raise ValueError("Amount must be positive.")

                category = fields["Category"].get().strip()

                description = fields["Description"].get().strip()

                transaction_date = fields[
                    "Date (YYYY-MM-DD)"
                ].get().strip()

                if not category:

                    messagebox.showerror(
                        "Invalid category",
                        "Please enter a category.",
                        parent=window
                    )

                    return

                date.fromisoformat(transaction_date)

                database.add_transaction(
                    transaction_type.get(),
                    amount,
                    category,
                    description,
                    transaction_date
                )

                window.destroy()

                # Refresh current page
                self.show_dashboard()

            except ValueError:

                messagebox.showerror(
                    "Invalid input",
                    "Enter a valid positive amount and date (YYYY-MM-DD).",
                    parent=window
                )

            except Exception as error:

                messagebox.showerror(
                    "Database error",
                    str(error),
                    parent=window
                )

        ctk.CTkButton(
            window,
            text="Save Transaction",
            command=save_transaction,
            width=350,
            height=42,
            fg_color=ACCENT,
            hover_color="#2563EB"
        ).pack(pady=15)


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    app = BudgetApp()
    app.mainloop()

