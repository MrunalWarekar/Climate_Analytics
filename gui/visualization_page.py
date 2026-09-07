import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def generate_matplotlib_figure(df, graph_type, country_name="Selected Country", 
                               month_filter="All", start_year=1961, end_year=2019, 
                               show_moving_avg=True):
    """
    Reusable chart generator function.
    Can be imported by dashboard.py and reports.py to generate PNGs or embedded plots.
    """
    if df is None or df.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.text(0.5, 0.5, "No Data Available for Selection", ha='center', va='center', fontsize=12)
        return fig

    # Standardize Column Names from DataManager
    data = df.copy()
    
    # Filter by Year Range if Year column exists
    if 'Year' in data.columns:
        data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
        data = data[(data['Year'] >= start_year) & (data['Year'] <= end_year)]

    # Filter by Month if Months column exists
    if 'Months' in data.columns and month_filter != "All":
        data = data[data['Months'] == month_filter]

    # Target temperature change column identification
    val_col = None
    for col in ['Temperature_Change', 'Value', 'Temp_Change', 'Measurement']:
        if col in data.columns:
            val_col = col
            break
    if val_col is None:
        # Fallback to first numeric column that isn't Year
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if 'Year' in numeric_cols:
            numeric_cols.remove('Year')
        val_col = numeric_cols[0] if numeric_cols else None

    if val_col is None or data.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.text(0.5, 0.5, "Insufficient Data for Plotting", ha='center', va='center', fontsize=12)
        return fig

    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=100)
    sns.set_theme(style="whitegrid")

    # 1. Line Chart + 5-Year Moving Average
    if graph_type == "Line Chart (YEAR vs Temp Change)":
        if 'Year' in data.columns:
            data = data.sort_values('Year')
            sns.lineplot(data=data, x='Year', y=val_col, ax=ax, label="Annual Temp Change (°C)", marker='o', color='#1f77b4')
            
            if show_moving_avg and len(data) >= 5:
                data['5Yr_MA'] = data[val_col].rolling(window=5, min_periods=1).mean()
                sns.lineplot(data=data, x='Year', y='5Yr_MA', ax=ax, label="5-Year Moving Avg", color='#ff7f0e', linewidth=2, linestyle='--')
            
            ax.set_ylabel("Temperature Change (°C)")
            ax.set_xlabel("Year")
        else:
            ax.text(0.5, 0.5, "Line chart requires 'Year' column", ha='center', va='center')

    # 2. Histogram
    elif graph_type == "Histogram":
        sns.histplot(data[val_col], kde=True, ax=ax, color='#2ca02c', bins=15)
        ax.set_xlabel("Temperature Change (°C)")
        ax.set_ylabel("Frequency")

    # 3. Box Plot
    elif graph_type == "Box Plot":
        sns.boxplot(y=data[val_col], ax=ax, color='#9467bd', width=0.3)
        ax.set_ylabel("Temperature Change (°C)")

    # 4. Scatter Plot
    elif graph_type == "Scatter Plot":
        if 'Year' in data.columns:
            sns.scatterplot(data=data, x='Year', y=val_col, ax=ax, color='#d62728', s=60)
            # Add linear trendline overlay
            if len(data) > 1:
                sns.regplot(data=data, x='Year', y=val_col, ax=ax, scatter=False, color='black', line_kws={'linestyle': ':'})
            ax.set_xlabel("Year")
            ax.set_ylabel("Temperature Change (°C)")
        else:
            sns.scatterplot(data=data, x=data.index, y=val_col, ax=ax, color='#d62728')

    # 5. Bar Chart (Decadal Averages)
    elif graph_type == "Bar Chart (Decadal Averages)":
        if 'Year' in data.columns:
            data['Decade'] = (data['Year'] // 10) * 10
            data['Decade_Str'] = data['Decade'].astype(str) + "s"
            decadal_df = data.groupby('Decade_Str')[val_col].mean().reset_index()
            sns.barplot(data=decadal_df, x='Decade_Str', y=val_col, ax=ax, palette="Blues_d")
            ax.set_xlabel("Decade")
            ax.set_ylabel("Mean Temperature Change (°C)")
            plt.xticks(rotation=0)
        else:
            ax.text(0.5, 0.5, "Decadal bar chart requires 'Year' column", ha='center', va='center')

    # 6. Seasonal / Month Comparison
    elif graph_type == "Seasonal / Month Comparison":
        if 'Months' in data.columns:
            sns.barplot(data=data, x='Months', y=val_col, ax=ax, palette="viridis")
            ax.set_xlabel("Month / Period")
            ax.set_ylabel("Temperature Change (°C)")
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, "Seasonal comparison requires 'Months' column in dataset", ha='center', va='center')

    title_str = f"{graph_type}\n{country_name} | Period: {month_filter} ({start_year}-{end_year})"
    ax.set_title(title_str, fontsize=11, fontweight='bold', pad=10)
    fig.tight_layout()
    return fig


class VisualizationPage(ttk.Frame):
    """
    Tkinter interface frame for Tanishka's Visualization Module.
    Can be initialized inside main.py notebooks or frames.
    """
    def __init__(self, parent, data_manager=None):
        super().__init__(parent, padding=10)
        self.data_manager = data_manager
        self.current_fig = None
        
        self._build_ui()

    def _build_ui(self):
        # Header / Context Banner
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Visual Analytics & Climate Trends", font=("Helvetica", 14, "bold")).pack(side=tk.LEFT)
        
        self.context_lbl = ttk.Label(header_frame, text="Active Country: None Selected", font=("Helvetica", 10, "italic"), foreground="navy")
        self.context_lbl.pack(side=tk.RIGHT)

        # Main Layout: Controls (Left) | Canvas (Right)
        body_frame = ttk.Frame(self)
        body_frame.pack(fill=tk.BOTH, expand=True)

        # Control Panel Sidebar
        control_frame = ttk.LabelFrame(body_frame, text=" Controls & Filters ", padding=12)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Graph Type Dropdown
        ttk.Label(control_frame, text="Select Graph Type:").pack(anchor=tk.W, pady=(0, 2))
        self.graph_type_cb = ttk.Combobox(control_frame, values=[
            "Line Chart (YEAR vs Temp Change)",
            "Histogram",
            "Box Plot",
            "Scatter Plot",
            "Bar Chart (Decadal Averages)",
            "Seasonal / Month Comparison"
        ], state="readonly", width=28)
        self.graph_type_cb.set("Line Chart (YEAR vs Temp Change)")
        self.graph_type_cb.pack(fill=tk.X, pady=(0, 12))

        # Moving Average Option
        self.moving_avg_var = tk.BooleanVar(value=True)
        self.ma_chk = ttk.Checkbutton(control_frame, text="Include 5-Yr Moving Average", variable=self.moving_avg_var)
        self.ma_chk.pack(anchor=tk.W, pady=(0, 12))

        # Month Filter Dropdown
        ttk.Label(control_frame, text="Select Month/Period:").pack(anchor=tk.W, pady=(0, 2))
        self.month_cb = ttk.Combobox(control_frame, values=["All"], state="readonly")
        self.month_cb.set("All")
        self.month_cb.pack(fill=tk.X, pady=(0, 12))

        # Year Range Selection
        ttk.Label(control_frame, text="Start Year:").pack(anchor=tk.W)
        self.start_year_spin = ttk.Spinbox(control_frame, from_=1961, to=2019, increment=1)
        self.start_year_spin.set(1961)
        self.start_year_spin.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(control_frame, text="End Year:").pack(anchor=tk.W)
        self.end_year_spin = ttk.Spinbox(control_frame, from_=1961, to=2019, increment=1)
        self.end_year_spin.set(2019)
        self.end_year_spin.pack(fill=tk.X, pady=(0, 15))

        # Buttons
        ttk.Button(control_frame, text="Generate / Update Graph", command=self.update_graph).pack(fill=tk.X, pady=4)
        ttk.Button(control_frame, text="Save Graph as PNG", command=self.save_png).pack(fill=tk.X, pady=4)
        ttk.Button(control_frame, text="Refresh Data Source", command=self.load_data_from_manager).pack(fill=tk.X, pady=(15, 0))

        # Display Frame for Matplotlib Plot
        self.canvas_frame = ttk.Frame(body_frame, relief=tk.SUNKEN, borderwidth=1)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initial plot attempt
        self.load_data_from_manager()

    def load_data_from_manager(self):
        """Fetches active dataset and country context from shared DataManager."""
        df = None
        country_name = "Selected Country"

        if self.data_manager is not None:
            # Check for shared data manager interfaces
            if hasattr(self.data_manager, 'get_processed_data'):
                df = self.data_manager.get_processed_data()
            elif hasattr(self.data_manager, 'processed_df'):
                df = self.data_manager.processed_df

            if hasattr(self.data_manager, 'get_selected_country'):
                country_name = self.data_manager.get_selected_country()
            elif hasattr(self.data_manager, 'selected_country'):
                country_name = self.data_manager.selected_country

        self.context_lbl.config(text=f"Active Country: {country_name}")

        # Update Month Dropdown options if Months column exists in dataset
        if df is not None and 'Months' in df.columns:
            unique_months = ["All"] + sorted(df['Months'].dropna().unique().tolist())
            self.month_cb['values'] = unique_months

        self.update_graph(df_override=df, country_override=country_name)

    def update_graph(self, df_override=None, country_override=None):
        """Renders chart inside the Tkinter canvas frame."""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Resolve Data Source
        df = df_override
        if df is None and self.data_manager is not None:
            df = getattr(self.data_manager, 'get_processed_data', lambda: None)()

        country_name = country_override or "Selected Country"
        if self.data_manager and hasattr(self.data_manager, 'selected_country'):
            country_name = self.data_manager.selected_country

        # Fetch Form inputs
        graph_type = self.graph_type_cb.get()
        month_filter = self.month_cb.get()
        show_ma = self.moving_avg_var.get()

        try:
            start_yr = int(self.start_year_spin.get())
            end_yr = int(self.end_year_spin.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Start and End years must be numeric integers.")
            return

        # Generate Matplotlib Figure
        self.current_fig = generate_matplotlib_figure(
            df=df,
            graph_type=graph_type,
            country_name=country_name,
            month_filter=month_filter,
            start_year=start_yr,
            end_year=end_yr,
            show_moving_avg=show_ma
        )

        # Draw on Tkinter Canvas
        canvas = FigureCanvasTkAgg(self.current_fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_png(self):
        """Export current chart to disk as PNG image."""
        if self.current_fig is None:
            messagebox.showwarning("Warning", "No active graph to export!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            title="Save Graph As"
        )
        if filepath:
            self.current_fig.savefig(filepath, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Export Successful", f"Chart saved successfully to:\n{filepath}")


# Testing harness for independent branch verification
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Climate Analytics System - Visualization Module")
    root.geometry("1050x650")

    # Mock DataManager for local standalone execution
    class DummyDataManager:
        def __init__(self):
            self.selected_country = "India"
            years = np.tile(np.arange(1961, 2020), 12)
            months = np.repeat(["Meteorological Year", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November"], 59)
            
            self.processed_df = pd.DataFrame({
                "Year": years,
                "Months": months,
                "Temperature_Change": 0.2 + 0.02 * (years - 1961) + np.random.normal(0, 0.3, len(years))
            })

        def get_processed_data(self):
            return self.processed_df

        def get_selected_country(self):
            return self.selected_country

    dummy_dm = DummyDataManager()
    app = VisualizationPage(root, data_manager=dummy_dm)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()