import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from calculations import evaluate_integration, save_results_to_csv
from utils import ToolTip  # Assuming ToolTip is defined in utils
import json
import os
from datetime import datetime
import csv

class IntegrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Integration Strategy Evaluation")
        self.root.geometry("1000x700")

        self.style = ttk.Style(theme="darkly")
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TEntry", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 12))

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.integration_pair_name_var = tk.StringVar()
        self.session_history = []

        self.create_initial_gui()

    def create_initial_gui(self):
        welcome_frame = ttk.Frame(self.main_frame, bootstyle="secondary")
        welcome_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(welcome_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=40, pady=40)

        ttk.Label(left_frame,
                  text="Welcome to\nIntegration\nStrategy\nEvaluation\nprototype",
                  style="Title.TLabel",
                  bootstyle="light").pack(pady=(40, 10), anchor="w")

        features = [
            "The prototype is a tool for evaluating IS\nintegration strategies in the context of\nM&A"
        ]

        for feature in features:
            ttk.Label(left_frame,
                      text=feature,
                      bootstyle="light",
                      font=("Segoe UI", 11)).pack(anchor="w", pady=5)

        right_frame = ttk.Frame(welcome_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        input_frame = ttk.Labelframe(right_frame,
                                     text="Start Evaluation",
                                     bootstyle="info",
                                     padding=20)
        input_frame.pack(fill="both", expand=True)

        self.strategy_types = ["Symbiosis", "Absorption", "Preservation", "Transformation"]
        self.selected_types = {type_: tk.BooleanVar() for type_ in self.strategy_types}

        ttk.Label(input_frame,
                  text="Select Strategy Types (2-4):",
                  bootstyle="light").pack(pady=(10, 5), anchor="w")

        for type_ in self.strategy_types:
            ttk.Checkbutton(input_frame,
                            text=type_,
                            variable=self.selected_types[type_]).pack(anchor="w")

        enter_button = ttk.Button(input_frame,
                                  text="Continue →",
                                  bootstyle="success",
                                  width=15,
                                  command=self.get_strategy_count)
        enter_button.pack(pady=20, anchor="w")

    def get_strategy_count(self):
        self.selected_strategy_types = [type_ for type_, var in self.selected_types.items() if var.get()]
        count = len(self.selected_strategy_types)
        if count < 2 or count > 4:
            messagebox.showerror("Error", "Please select between 2 and 4 strategy types.")
            return
        self.strategy_count = count
        self.create_input_screen()

    def create_input_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.weights_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.weights_frame, text="Weighting Coefficients")

        ttk.Label(self.weights_frame,
                  text="Set Criteria Weights (Sum should equal 1.0)",
                  style="Title.TLabel").pack(pady=20)

        weights_container = ttk.Frame(self.weights_frame)
        weights_container.pack(fill="both", expand=True, padx=40, pady=10)

        self.criteria = [
            "Contribution to PMI goals",
            "Stakeholder support",
            "User  satisfaction",
            "Integration cost",
            "Integration time",
            "Integration risk"
        ]

        self.weight_vars = {}
        for i, criterion in enumerate(self.criteria):
            row = ttk.Frame(weights_container)
            row.pack(fill="x", pady=5)

            ttk.Label(row,
                      text=criterion,
                      width=25,
                      anchor="w").pack(side="left", padx=10)

            weight_var = tk.StringVar(value="Low")
            combo = ttk.Combobox(row, textvariable=weight_var, values=["Low", "Medium", "High"], state="readonly")
            combo.pack(side="left")
            combo.bind("<<ComboboxSelected>>", self.update_weight_sum)

            self.weight_vars[criterion] = weight_var

        self.current_sum_label = ttk.Label(weights_container, text="Current Sum of Weights: 0.00", bootstyle="light")
        self.current_sum_label.pack(pady=(10, 0))
        self.update_weight_sum()

        # Second tab with only the IS Integration Pair name entry
        self.pair_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pair_frame, text="IS Integration Pair")

        ttk.Label(self.pair_frame,
                  text="Name the IS Integration Pair:",
                  style="Title.TLabel").pack(pady=20)

        pair_container = ttk.Frame(self.pair_frame)
        pair_container.pack(fill="both", expand=True, padx=40, pady=10)

        pair_entry = ttk.Entry(pair_container, textvariable=self.integration_pair_name_var)
        pair_entry.pack(fill="x")

        # Buttons below notebook
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(button_frame,
                   text="← Back",
                   bootstyle="outline",
                   command=self.back_to_welcome).pack(side="left", padx=5)

        ttk.Button(button_frame,
                   text="Continue →",
                   bootstyle="success",
                   command=self.process_input).pack(side="right", padx=5)

    def update_weight_sum(self, event=None):
        WEIGHT_MAP = {"Low": 0.1, "Medium": 0.3, "High": 0.5}
        raw_weights = [WEIGHT_MAP[w.get()] for w in self.weight_vars.values()]
        total_weight = sum(raw_weights)
        self.current_sum_label.config(text=f"Current Sum of Weights: {total_weight:.2f}")

    def back_to_welcome(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_initial_gui()

    def process_input(self):
        try:
            weights = []
            for criterion in self.criteria:
                selection = self.weight_vars[criterion].get()
                weights.append({"Low": 0.1, "Medium": 0.3, "High": 0.5}[selection])
            total_weight = sum(weights)
            if abs(total_weight - 1.0) > 0.01:
                weights = [w / total_weight for w in weights]
                messagebox.showwarning("Warning", "Weights were normalized to sum to 1.0.")
            self.weights = weights

            self.strategies = self.selected_strategy_types

            pair_name = self.integration_pair_name_var.get().strip()
            if not pair_name:
                messagebox.showerror("Error", "Please enter a name for the IS Integration Pair.")
                return
            self.integration_pair_name = pair_name

            self.get_strategy_scores()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def get_strategy_scores(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.main_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(main_frame,
                  text="Evaluate Strategy Performance",
                  style="Title.TLabel").pack(pady=20)

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)

        ttk.Label(table_frame, text="Strategy", width=20, bootstyle="inverse-primary").grid(row=0, column=0, sticky="nsew")
        for i, criterion in enumerate(self.criteria):
            ttk.Label(table_frame,
                      text=criterion,
                      width=15,
                      bootstyle="inverse-primary").grid(row=0, column=i + 1, sticky="nsew")

        self.score_entries = []
        for row_idx, strategy in enumerate(self.strategies):
            ttk.Label(table_frame,
                      text=strategy,
                      width=20).grid(row=row_idx + 1, column=0, sticky="nsew")

            row_entries = []
            for col_idx in range(len(self.criteria)):
                entry = ttk.Entry(table_frame, width=15, justify="center")
                entry.grid(row=row_idx + 1, column=col_idx + 1, sticky="nsew")
                row_entries.append(entry)
            self.score_entries.append(row_entries)

        for i in range(len(self.criteria) + 1):
            table_frame.grid_columnconfigure(i, weight=1)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)

        ttk.Button(button_frame,
                   text="← Back",
                   bootstyle="outline",
                   command=self.back_to_input).pack(side="left", padx=5)

        ttk.Button(button_frame,
                   text="Session History",
                   bootstyle="info",
                   command=self.show_session_history_window).pack(side="left", padx=5)

        ttk.Button(button_frame,
                   text="Calculate Results",
                   bootstyle="success",
                   command=self.calculate_results).pack(side="right", padx=5)

    def back_to_input(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_input_screen()

    def calculate_results(self):
        try:
            scores = []
            for row in self.score_entries:
                row_scores = []
                for entry in row:
                    val = float(entry.get()) if entry.get() else 0.0
                    row_scores.append(val)
                scores.append(row_scores)

            scores = np.array(scores)
            directions = ["max", "max", "max", "min", "min", "min"]

            results = evaluate_integration(self.strategies, self.weights, scores, directions)

            best_strategy = max(results, key=results.get)
            best_score = results[best_strategy]

            result_text = "\n".join(
                f"{s}: {sc:.4f}" + ("  <-- Best result" if s == best_strategy else "")
                for s, sc in results.items()
            )
            messagebox.showinfo("Results", f"Strategy Scores:\n\n{result_text}\n\nBest: {best_strategy} ({best_score:.4f})")

            self.visualize_results(results, best_strategy)

            # Save session history
            self.save_session_history({
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "integration_pair": self.integration_pair_name,
                "strategies": self.strategies,
                "weights": self.weights,
                "scores": results,
                "final_results": results
            })

            # Save results to CSV
            self.save_results_to_csv(results)

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def save_session_history(self, record):
        if not hasattr(self, 'session_history'):
            self.session_history = []
        self.session_history.append(record)

        # Save to JSON file
        folder = "sessions"
        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = os.path.join(folder, f"session_{self.integration_pair_name}.json")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.session_history, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session history: {e}")

    def save_results_to_csv(self, results):
        folder = "results"
        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = os.path.join(folder, f"results_{self.integration_pair_name}.csv")
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Strategy", "Score"])
                for strategy, score in results.items():
                    writer.writerow([strategy, score])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results to CSV: {e}")

    def show_session_history_window(self):
        win = tk.Toplevel(self.root)
        win.title("Session Evaluation History")
        win.geometry("800x400")

        ttk.Label(win, text="Session Evaluation History", style="Title.TLabel").pack(pady=10)

        listbox = tk.Listbox(win, font=("Segoe UI", 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for rec in getattr(self, 'session_history', []):
            best_strat = max(rec["scores"], key=rec["scores"].get)
            display_text = f"{rec['datetime']} | Pair: {rec['integration_pair']} | Best: {best_strat} ({rec['scores'][best_strat]:.4f})"
            listbox.insert(tk.END, display_text)

        ttk.Button(win, text="Close", bootstyle="secondary", command=win.destroy).pack(pady=5)

    def visualize_results(self, results, best_strategy):
        strategies = list(results.keys())
        scores = list(results.values())

        plt.figure(figsize=(10, 6))
        bars = plt.barh(strategies, scores, color='skyblue')

        for bar, strategy in zip(bars, strategies):
            if strategy == best_strategy:
                bar.set_color('orange')

        plt.xlabel('Final Score')
        plt.title('Integration Strategy Evaluation Results')
        plt.xlim(0, 1)
        plt.grid(axis='x')
        plt.show()

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = IntegrationGUI(root)
    root.mainloop()
