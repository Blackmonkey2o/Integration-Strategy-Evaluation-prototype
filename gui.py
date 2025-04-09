import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from calculations import evaluate_integration, save_results_to_csv
from utils import ToolTip

class IntegrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Integration Strategy Evaluation")
        self.root.geometry("1000x700")

        #theme and style
        self.style = ttk.Style(theme="darkly")
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TEntry", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 12))

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_initial_gui()

    def create_initial_gui(self):
        #welcome section
        welcome_frame = ttk.Frame(self.main_frame, bootstyle="secondary")
        welcome_frame.pack(fill="both", expand=True)

        #left side of first window
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

        #right side of first window
        right_frame = ttk.Frame(welcome_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        input_frame = ttk.Labelframe(right_frame,
                                     text="Start Evaluation",
                                     bootstyle="info",
                                     padding=20)
        input_frame.pack(fill="both", expand=True)

        ttk.Label(input_frame,
                  text="Enter the number of strategies to compare (2-4):",
                  bootstyle="light").pack(pady=(10, 5), anchor="w")

        self.strategy_count_entry = ttk.Entry(input_frame,
                                              font=("Segoe UI", 12),
                                              width=5,
                                              justify="center")
        self.strategy_count_entry.pack(pady=5, anchor="w")

        enter_button = ttk.Button(input_frame,
                                  text="Continue →",
                                  bootstyle="success",
                                  width=15,
                                  command=self.get_strategy_count)
        enter_button.pack(pady=20, anchor="w")

    def get_strategy_count(self):
        try:
            self.strategy_count = int(self.strategy_count_entry.get())
            if self.strategy_count < 2 or self.strategy_count > 4:
                messagebox.showerror("Error", "Please enter a number between 2 and 4.")
                return
            self.create_input_screen()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Enter a number between 2 and 4.")

    def create_input_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        #main container with notebook for tabs
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        #tab 1: Weighting Coefficients
        weights_frame = ttk.Frame(notebook)
        notebook.add(weights_frame, text="Weighting Coefficients")

        ttk.Label(weights_frame,
                  text="Set Criteria Weights (Sum should equal 1.0)",
                  style="Title.TLabel").pack(pady=20)

        weights_container = ttk.Frame(weights_frame)
        weights_container.pack(fill="both", expand=True, padx=40, pady=10)

        self.weights_entries = {}
        self.criteria = ["Compatibility", "Cost", "Time-consuming", "Risks", "Flexibility", "Security"]

        for i, criterion in enumerate(self.criteria):
            row = ttk.Frame(weights_container)
            row.pack(fill="x", pady=5)

            ttk.Label(row,
                      text=criterion,
                      width=15,
                      anchor="w").pack(side="left", padx=10)

            entry = ttk.Entry(row,
                              width=8,
                              justify="center")
            entry.pack(side="left")

            #tooltip with criteria description
            ToolTip(entry, text=self.get_criteria_tooltip(criterion))

            self.weights_entries[criterion] = entry

        #tab 2: Strategy Names
        strategy_frame = ttk.Frame(notebook)
        notebook.add(strategy_frame, text="Strategy Names")

        ttk.Label(strategy_frame,
                  text="Name Your Strategies",
                  style="Title.TLabel").pack(pady=20)

        strategy_container = ttk.Frame(strategy_frame)
        strategy_container.pack(fill="both", expand=True, padx=40, pady=10)

        self.strategy_entries = []
        for i in range(self.strategy_count):
            row = ttk.Frame(strategy_container)
            row.pack(fill="x", pady=10)

            ttk.Label(row,
                      text=f"Strategy {i + 1}:",
                      width=12).pack(side="left", padx=10)

            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            self.strategy_entries.append(entry)

        # Action buttons at bottom
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

    def get_criteria_tooltip(self, criterion):
        tooltips = {
            "Compatibility": "How well the systems can work together",
            "Cost": "Implementation and maintenance costs",
            "Time-consuming": "Estimated time required for integration",
            "Risks": "Potential risks and failure points",
            "Flexibility": "Ability to adapt to future changes",
            "Security": "Data protection and access control"
        }
        return tooltips.get(criterion, "")

    def process_input(self):
        try:
            self.strategies = [entry.get().strip() for entry in self.strategy_entries if entry.get().strip()]
            if len(self.strategies) != self.strategy_count:
                messagebox.showerror("Error", "Please enter names for all strategies.")
                return

            weights = [float(entry.get()) if entry.get() else 0 for entry in self.weights_entries.values()]

            #check sum of weights is equal to 1
            total_weight = sum(weights)
            if abs(total_weight - 1.0) > 0.01:
                messagebox.showwarning("Warning", "Weights don't sum to 1.0 - normalizing values")
                weights = np.array(weights) / total_weight  #normalize

            self.weights = weights
            self.get_strategy_scores()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers for weights.")

    def get_strategy_scores(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.main_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(main_frame,
                  text="Evaluate Strategy Performance",
                  style="Title.TLabel").pack(pady=20)

        #scoring table
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)

        #header
        ttk.Label(table_frame, text="Strategy", width=20, bootstyle="inverse-primary").grid(row=0, column=0,
                                                                                            sticky="nsew")
        for i, criterion in enumerate(self.criteria):
            ttk.Label(table_frame,
                      text=criterion,
                      width=15,
                      bootstyle="inverse-primary").grid(row=0, column=i + 1, sticky="nsew")

        #data rows
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

        #configure grid weights
        for i in range(len(self.criteria) + 1):
            table_frame.grid_columnconfigure(i, weight=1)

        #action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)

        ttk.Button(button_frame,
                   text="← Back",
                   bootstyle="outline",
                   command=self.back_to_input).pack(side="left", padx=5)

        ttk.Button(button_frame,
                   text="Calculate Results",
                   bootstyle="success",
                   command=self.calculate_results).pack(side="right", padx=5)

    def back_to_welcome(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_initial_gui()

    def back_to_input(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_input_screen()

    def calculate_results(self):
        try:
            #validate and collect scores
            scores = []
            for row in self.score_entries:
                row_scores = []
                for entry in row:
                    value = float(entry.get()) if entry.get() else 0
                    row_scores.append(value)
                scores.append(row_scores)

            scores = np.array(scores)

            #evaluate integration
            results = evaluate_integration(self.strategies, self.weights, scores)

            #results
            result_text = "\n".join(
                f"{strategy}: {score:.4f}"
                for strategy, score in results.items()
            )
            messagebox.showinfo("Results", f"Strategy Scores:\n\n{result_text}")

            #visualization
            self.visualize_results(results)

            #save results
            save_results_to_csv(results)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def visualize_results(self, results):
        strategies = list(results.keys())
        scores = list(results.values())

        plt.figure(figsize=(10, 6))
        plt.barh(strategies, scores, color='skyblue')
        plt.xlabel('Final Score')
        plt.title('Integration Strategy Evaluation Results')
        plt.xlim(0, 1)
        plt.grid(axis='x')
        plt.show()
