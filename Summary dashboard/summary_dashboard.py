"""
================================================================================
 summary_dashboard.py
================================================================================
 Purpose:
    This module defines a `SummaryDashboard` class that provides a
    comprehensive, scrollable, and exportable summary of the Weather
    Analytics project.

    It is designed to be launched from the main `WeatherApp` (inside
    `analysis.py`) after the user has already uploaded a dataset and
    (optionally) calculated statistics.

 Key Features:
    1. Displays a dashboard window with sections:
        - Dataset Overview
        - Analysis Configuration
        - Statistical Results
        - Correlation Matrix
        - Key Findings (auto-generated interpretation)
        - Conclusion (narrative summary)
    2. Allows the user to export the entire summary as a well-formatted
       PDF document using the `reportlab` library.

 Dependencies:
    - tkinter  (built-in, for GUI)
    - pandas   (for handling tabular data)
    - os       (for path/filename operations)
    - datetime (for timestamping the PDF)
    - reportlab (OPTIONAL — required only for PDF export)
================================================================================
"""

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------
import tkinter as tk                      # Core GUI toolkit
from tkinter import ttk, messagebox, filedialog  # ttk widgets & dialogs
import pandas as pd                       # DataFrame operations
import os                                 # File system helpers
from datetime import datetime             # Timestamp generation


# --------------------------------------------------------------------------
# PDF EXPORT DEPENDENCY (ReportLab)
# --------------------------------------------------------------------------
# ReportLab is a third-party library. We wrap its imports in a try/except
# so the entire module still works (for viewing the dashboard) even if
# ReportLab is not installed. PDF export will simply be disabled.
# --------------------------------------------------------------------------
try:
    from reportlab.lib.pagesizes import A4       # Standard A4 page size
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch          # 1 inch = 72 points
    from reportlab.lib import colors              # Named color constants
    from reportlab.platypus import (              # Layout building blocks
        SimpleDocTemplate,   # High-level PDF document builder
        Paragraph,           # Formatted text block
        Spacer,              # Vertical whitespace
        Table,               # Tabular data
        TableStyle,          # Table formatting
        PageBreak            # Force a new page
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT   # Text alignment
    REPORTLAB_AVAILABLE = True                    # Flag used later in the UI
except ImportError:
    # If ReportLab is missing, we still allow the app to run.
    REPORTLAB_AVAILABLE = False


# ==========================================================================
# CLASS: SummaryDashboard
# ==========================================================================
class SummaryDashboard:
    """
    A dashboard window that consolidates and displays the entire summary
    of the Weather Analytics project.

    The class is instantiated with a reference to the parent Tk widget
    (typically `self.root` from WeatherApp) plus all the data needed to
    build the summary.

    Attributes
    ----------
    parent : tk.Widget
        The widget that owns this dashboard (usually the Tk root).
    df : pd.DataFrame
        The loaded weather dataset.
    current_filename : str
        The file name of the currently loaded CSV.
    statistics : dict
        Dictionary of statistics (Mean, Median, etc.) calculated in
        the analysis page. May be empty.
    selected_data : pd.Series or None
        The series of yearly values that were used to compute statistics.
    area, element, period : str
        Currently selected filter values.
    analysis_results : dict
        Additional results, e.g. {"correlation_text": "..."}.
    window : tk.Toplevel or tk.Widget
        The actual Tk window/frame used to render the dashboard.
    """

    # ----------------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------------
    def __init__(self, parent, df, current_filename,
                 statistics=None, selected_data=None,
                 area=None, element=None, period=None,
                 analysis_results=None):
        """
        Initialise the dashboard.

        All parameters except `parent`, `df`, and `current_filename` are
        optional so the dashboard can still be shown even if the user
        hasn't run the analysis yet.
        """

        # ----- Save references to incoming data -----
        self.parent = parent
        self.df = df
        self.current_filename = current_filename

        # `statistics` is a dict; if None is passed, use an empty dict
        # to avoid None-checks everywhere.
        self.statistics = statistics or {}

        # `selected_data` is a pandas Series (yearly temperature values).
        self.selected_data = selected_data

        # Filter selections from the analysis page.
        self.area = area
        self.element = element
        self.period = period

        # Extra results such as correlation matrix text.
        self.analysis_results = analysis_results or {}

        # ----- Build the actual GUI -----
        self._build_ui()


    # ======================================================================
    # UI CONSTRUCTION
    # ======================================================================
    # ======================================================================
# UI CONSTRUCTION (FIXED VERSION)
# ======================================================================
    def _build_ui(self):
        """
        Create the entire user interface of the dashboard:

            ┌────────────────────────────────────────┐
            │  Header (blue bar with title)          │  ← packed FIRST (top)
            ├────────────────────────────────────────┤
            │  Scrollable body with 6 sections       │  ← packed SECOND (fills)
            │                                        │
            ├────────────────────────────────────────┤
            │  Bottom button bar (PDF, Refresh, X)   │  ← packed THIRD (bottom)
            └────────────────────────────────────────┘

        IMPORTANT (Tkinter pack rule):
            Widgets packed with `side="bottom"` or `side="top"` must be
            packed BEFORE widgets using `fill="both", expand=True`.
            Otherwise the expanding widget consumes the entire window and
            the button bar becomes invisible (pushed off-screen).

            Correct order:
                1. Header          (side="top")
                2. Button bar      (side="bottom")   ← MUST COME EARLY
                3. Body container  (fill="both", expand=True)
        """

        # ------------------------------------------------------------------
        # STEP 1: Create the top-level window.
        # ------------------------------------------------------------------
        if isinstance(self.parent, tk.Tk):
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = self.parent

        self.window.title("Project Summary Dashboard")
        self.window.geometry("1050x750")
        self.window.configure(bg="#f0f4f8")

        # Try to make it modal-ish.
        try:
            self.window.transient(self.parent)
            self.window.grab_set()
        except Exception:
            pass

        # ------------------------------------------------------------------
        # STEP 2: HEADER — packed FIRST at the top.
        # ------------------------------------------------------------------
        header = tk.Frame(self.window, bg="#2b6cb0", height=80)
        header.pack(fill="x", side="top")     # Explicitly side="top"
        header.pack_propagate(False)           # Lock height to 80px

        tk.Label(
            header,
            text="📊 Project Summary Dashboard",
            font=("Arial", 22, "bold"),
            bg="#2b6cb0",
            fg="white"
        ).pack(pady=20)

        # ------------------------------------------------------------------
        # STEP 3: BOTTOM BUTTON BAR — packed SECOND, BEFORE the body.
        #
        # >>> THIS IS THE CRITICAL FIX <<<
        # If this frame is packed after the body_container, the body will
        # claim the entire window and the button bar will be pushed off.
        # ------------------------------------------------------------------
        btn_bar = tk.Frame(self.window, bg="#e2e8f0", height=70)
        btn_bar.pack(fill="x", side="bottom")   # Reserve bottom strip FIRST
        btn_bar.pack_propagate(False)           # Lock height to 70px

        # ----- Download PDF button -----
        self.btn_pdf = tk.Button(
            btn_bar,
            text="📄 Download Summary as PDF",
            font=("Arial", 12, "bold"),
            bg="#38a169",
            fg="white",
            activebackground="#2f855a",
            activeforeground="white",
            padx=20, pady=10,
            cursor="hand2",
            command=self.export_pdf
        )
        self.btn_pdf.pack(side="left", padx=20, pady=15)

        # ----- Refresh button -----
        tk.Button(
            btn_bar,
            text="🔄 Refresh",
            font=("Arial", 11, "bold"),
            bg="#3182ce",
            fg="white",
            activebackground="#2c5282",
            activeforeground="white",
            padx=15, pady=10,
            cursor="hand2",
            command=self._refresh
        ).pack(side="left", padx=5, pady=15)

        # ----- Close button -----
        tk.Button(
            btn_bar,
            text="✖ Close",
            font=("Arial", 11, "bold"),
            bg="#e53e3e",
            fg="white",
            activebackground="#c53030",
            activeforeground="white",
            padx=15, pady=10,
            cursor="hand2",
            command=self._close
        ).pack(side="right", padx=20, pady=15)

        # ----- Optional warning if ReportLab missing -----
        if not REPORTLAB_AVAILABLE:
            tk.Label(
                btn_bar,
                text="⚠ Install 'reportlab' to enable PDF export",
                font=("Arial", 10, "italic"),
                bg="#e2e8f0",
                fg="#c53030"
            ).pack(side="right", padx=10)

        # ------------------------------------------------------------------
        # STEP 4: BODY (scrollable area) — packed LAST so it fills whatever
        # space remains between the header (top) and button bar (bottom).
        # ------------------------------------------------------------------
        body_container = tk.Frame(self.window, bg="#f0f4f8")
        body_container.pack(fill="both", expand=True)

        # ---- Canvas + Scrollbar + inner Frame pattern ----
        canvas = tk.Canvas(
            body_container,
            bg="#f0f4f8",
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            body_container,
            orient="vertical",
            command=canvas.yview
        )

        self.scroll_frame = tk.Frame(canvas, bg="#f0f4f8")

        # Keep canvas scrollregion in sync with content size.
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # Place inner frame inside canvas.
        canvas.create_window(
            (0, 0),
            window=self.scroll_frame,
            anchor="nw"
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas (expand) and scrollbar (right).
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse-wheel scrolling.
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            )
        )

        # ------------------------------------------------------------------
        # STEP 5: Populate the six content sections.
        # ------------------------------------------------------------------
        self._section_dataset_overview()
        self._section_analysis_config()
        self._section_statistics()
        self._section_correlation()
        self._section_key_findings()
        self._section_conclusion()


    # ======================================================================
    # HELPER WIDGET BUILDERS
    # ======================================================================

    def _section_title(self, text):
        """
        Render a section heading (e.g. "1. Dataset Overview").

        Parameters
        ----------
        text : str
            The heading text.
        """
        tk.Label(
            self.scroll_frame,
            text=text,
            font=("Arial", 14, "bold"),
            bg="#f0f4f8",
            fg="#2b6cb0",
            anchor="w"               # Left-align text
        ).pack(fill="x", padx=30, pady=(20, 5))


    def _card(self, parent=None):
        """
        Create a white "card" frame that visually groups section content.

        Parameters
        ----------
        parent : tk.Widget or None
            If None, defaults to `self.scroll_frame`.

        Returns
        -------
        frame : tk.Frame
            The newly created card frame.
        """
        frame = tk.Frame(
            parent or self.scroll_frame,
            bg="white",                       # White background
            bd=1,                             # 1px border width
            relief="solid",                   # Solid border style
            highlightbackground="#cbd5e0"     # Light grey border colour
        )
        frame.pack(fill="x", padx=30, pady=5)
        return frame


    # ======================================================================
    # SECTION 1: DATASET OVERVIEW
    # ======================================================================
    def _section_dataset_overview(self):
        """
        Render a table of basic dataset facts:
            - File name
            - Number of rows & columns
            - Number of year-columns (columns starting with 'Y')
            - Number of unique Areas / Elements / Month types
        """
        self._section_title("1. Dataset Overview")
        card = self._card()

        # Build a list of (label, value) pairs so we can iterate cleanly.
        # Conditional expressions handle the possibility that certain
        # columns are missing (defensive programming).
        rows = [
            ("File Name:", self.current_filename or "—"),
            ("Total Rows:", f"{self.df.shape[0]:,}"),
            ("Total Columns:", f"{self.df.shape[1]}"),
            (
                "Year Columns:",
                str(len([c for c in self.df.columns if c.startswith("Y")]))
            ),
            (
                "Unique Areas:",
                str(self.df["Area"].nunique())
                if "Area" in self.df.columns else "—"
            ),
            (
                "Unique Elements:",
                str(self.df["Element"].nunique())
                if "Element" in self.df.columns else "—"
            ),
            (
                "Unique Month Types:",
                str(self.df["Months"].nunique())
                if "Months" in self.df.columns else "—"
            ),
        ]

        # Grid layout: column 0 = bold labels, column 1 = plain values.
        for i, (label, value) in enumerate(rows):
            tk.Label(
                card, text=label,
                font=("Arial", 11, "bold"),
                bg="white", fg="#4a5568",
                anchor="w", width=22
            ).grid(row=i, column=0, sticky="w", padx=15, pady=4)

            tk.Label(
                card, text=value,
                font=("Arial", 11),
                bg="white", fg="#1a202c",
                anchor="w"
            ).grid(row=i, column=1, sticky="w", padx=5, pady=4)


    # ======================================================================
    # SECTION 2: ANALYSIS CONFIGURATION
    # ======================================================================
    def _section_analysis_config(self):
        """
        Show the filters that were chosen on the analysis page:
            - Area, Element, Period
            - How many yearly observations were used
        """
        self._section_title("2. Analysis Configuration")
        card = self._card()

        rows = [
            ("Selected Area:", self.area or "—"),
            ("Selected Element:", self.element or "—"),
            ("Selected Period:", self.period or "—"),
            (
                "Observations Used:",
                str(len(self.selected_data))
                if self.selected_data is not None else "—"
            ),
        ]

        # Same grid pattern as Section 1.
        for i, (label, value) in enumerate(rows):
            tk.Label(
                card, text=label,
                font=("Arial", 11, "bold"),
                bg="white", fg="#4a5568",
                anchor="w", width=22
            ).grid(row=i, column=0, sticky="w", padx=15, pady=4)

            tk.Label(
                card, text=value,
                font=("Arial", 11),
                bg="white", fg="#1a202c",
                anchor="w"
            ).grid(row=i, column=1, sticky="w", padx=5, pady=4)


    # ======================================================================
    # SECTION 3: STATISTICAL RESULTS
    # ======================================================================
    def _section_statistics(self):
        """
        Render every key/value pair from `self.statistics` as a table.
        If no statistics exist yet, show an italic placeholder message.
        """
        self._section_title("3. Statistical Results")
        card = self._card()

        # ---- Guard clause: no stats computed yet ----
        if not self.statistics:
            tk.Label(
                card,
                text="No statistics calculated yet. "
                     "Please run 'Calculate Statistics' on the Analysis page.",
                font=("Arial", 11, "italic"),
                bg="white", fg="#718096",
                padx=15, pady=15
            ).pack(anchor="w")
            return

        # ---- Render each statistic as a two-column grid row ----
        for i, (key, value) in enumerate(self.statistics.items()):
            tk.Label(
                card, text=f"{key}:",
                font=("Arial", 11, "bold"),
                bg="white", fg="#4a5568",
                anchor="w", width=22
            ).grid(row=i, column=0, sticky="w", padx=15, pady=4)

            # Values may be numeric OR string (e.g. "No mode").
            if isinstance(value, str):
                display = value
            else:
                display = f"{value:.4f}"   # 4 decimal places

            tk.Label(
                card, text=display,
                font=("Arial", 11),
                bg="white", fg="#1a202c",
                anchor="w"
            ).grid(row=i, column=1, sticky="w", padx=5, pady=4)


    # ======================================================================
    # SECTION 4: CORRELATION MATRIX
    # ======================================================================
    def _section_correlation(self):
        """
        Display the correlation matrix text (if available). The text was
        produced in `analysis.py`'s `calculate_correlation` method and
        passed in via `analysis_results["correlation_text"]`.
        """
        self._section_title("4. Correlation Matrix")
        card = self._card()

        # Retrieve correlation text safely.
        corr_text = self.analysis_results.get("correlation_text", "")

        # ---- Guard clause: no correlation text available ----
        if not corr_text.strip():
            tk.Label(
                card,
                text="Correlation matrix not available. "
                     "Ensure analysis has been run.",
                font=("Arial", 11, "italic"),
                bg="white", fg="#718096",
                padx=15, pady=15
            ).pack(anchor="w")
            return

        # ---- Display text in a read-only Text widget with monospace ----
        # Monospace is important because correlation matrices are aligned
        # using spaces; a proportional font would break the alignment.
        txt = tk.Text(
            card,
            height=8,
            font=("Courier New", 10),
            bg="white", fg="#1a202c",
            bd=0,
            wrap="none"                # Preserve original spacing
        )
        txt.insert("1.0", corr_text)   # Insert at the beginning
        txt.config(state="disabled")   # Prevent editing
        txt.pack(fill="x", padx=15, pady=12)


    # ======================================================================
    # SECTION 5: KEY FINDINGS
    # ======================================================================
    def _section_key_findings(self):
        """
        Render a bulleted list of automatically generated findings.
        The findings come from `self._generate_findings()`.
        """
        self._section_title("5. Key Findings & Interpretation")
        card = self._card()

        findings = self._generate_findings()

        for bullet in findings:
            tk.Label(
                card,
                text=f"•  {bullet}",
                font=("Arial", 11),
                bg="white", fg="#2d3748",
                anchor="w", justify="left",
                wraplength=900    # Wrap long lines within card width
            ).pack(anchor="w", padx=15, pady=4)


    # ======================================================================
    # SECTION 6: CONCLUSION
    # ======================================================================
    def _section_conclusion(self):
        """
        Render a narrative conclusion paragraph. Text is generated by
        `self._generate_conclusion()`.
        """
        self._section_title("6. Conclusion")
        card = self._card()

        text = self._generate_conclusion()

        tk.Label(
            card,
            text=text,
            font=("Arial", 11),
            bg="white", fg="#2d3748",
            anchor="w", justify="left",
            wraplength=900
        ).pack(anchor="w", padx=15, pady=15)


    # ======================================================================
    # TEXT GENERATORS
    # ======================================================================

    def _generate_findings(self):
        """
        Produce a list of human-readable interpretation bullets based on
        the computed statistics.

        Returns
        -------
        findings : list[str]
        """
        findings = []

        # ---- If no statistics, return a single informative bullet ----
        if not self.statistics:
            findings.append(
                "Statistics have not been computed yet."
            )
            return findings

        # ---- Safely extract numeric statistics ----
        # Some values might be strings (e.g. "No mode"), so we wrap the
        # conversion in try/except to avoid crashing.
        try:
            mean_val   = float(self.statistics.get("Mean", 0))
            median_val = float(self.statistics.get("Median", 0))
            min_val    = float(self.statistics.get("Minimum", 0))
            max_val    = float(self.statistics.get("Maximum", 0))
            std_val    = float(self.statistics.get("Standard Deviation", 0))
            rng_val    = float(self.statistics.get("Range", 0))
        except (ValueError, TypeError):
            findings.append(
                "Some statistical values could not be parsed."
            )
            return findings

        # ---- Bullet 1: Mean ----
        findings.append(
            f"The average (mean) value for {self.area or 'the selected area'} "
            f"during the {self.period or 'selected period'} is {mean_val:.2f} °C."
        )

        # ---- Bullet 2: Median and skewness interpretation ----
        if median_val > mean_val:
            skew_text = (
                "is higher than the mean, suggesting a slight "
                "negative skew in the distribution."
            )
        elif median_val < mean_val:
            skew_text = (
                "is lower than the mean, suggesting a slight "
                "positive skew in the distribution."
            )
        else:
            skew_text = (
                "is approximately equal to the mean, indicating "
                "a fairly symmetric distribution."
            )

        findings.append(
            f"The median value is {median_val:.2f} °C, which {skew_text}"
        )

        # ---- Bullet 3: Range and extremes ----
        findings.append(
            f"Values range from a minimum of {min_val:.2f} °C "
            f"to a maximum of {max_val:.2f} °C, giving a total "
            f"range of {rng_val:.2f} °C."
        )

        # ---- Bullet 4: Variability based on standard deviation ----
        if std_val > 5:
            variability = "high variability in the data across the observed years."
        elif std_val > 2:
            variability = "moderate variability in the data across the observed years."
        else:
            variability = (
                "low variability, meaning temperatures are "
                "relatively stable across the observed years."
            )

        findings.append(
            f"The standard deviation is {std_val:.2f}, indicating {variability}"
        )

        # ---- Bullet 5: Trend from first to last observation ----
        # Only computed if we have the underlying yearly series.
        if self.selected_data is not None and len(self.selected_data) > 1:
            try:
                first_val = float(self.selected_data.iloc[0])
                last_val  = float(self.selected_data.iloc[-1])
                trend = last_val - first_val

                # Threshold of 0.1 °C avoids reporting negligible changes.
                if abs(trend) < 0.1:
                    findings.append(
                        "The overall trend across the years appears "
                        "relatively flat / stable."
                    )
                elif trend > 0:
                    findings.append(
                        f"A warming trend of approximately {trend:.2f} °C "
                        f"is observed between the first and last recorded years."
                    )
                else:
                    findings.append(
                        f"A cooling trend of approximately {abs(trend):.2f} °C "
                        f"is observed between the first and last recorded years."
                    )
            except Exception:
                # Silently ignore if the series cannot be interpreted.
                pass

        return findings


    def _generate_conclusion(self):
        """
        Build a narrative paragraph summarising the entire analysis.

        Returns
        -------
        conclusion : str
        """
        # ---- If we have no stats, return a short fallback message ----
        if not self.statistics:
            return ("Insufficient data to generate a conclusion. "
                    "Please run the statistical analysis first.")

        # ---- Extract numeric statistics safely ----
        try:
            mean_val = float(self.statistics.get("Mean", 0))
            std_val  = float(self.statistics.get("Standard Deviation", 0))
        except (ValueError, TypeError):
            mean_val = 0
            std_val  = 0

        # ---- Compose the conclusion paragraph ----
        return (
            f"This report summarised the temperature records for "
            f"the area '{self.area or 'N/A'}' for the element "
            f"'{self.element or 'N/A'}' during the '{self.period or 'N/A'}' "
            f"period. The analysis was performed on "
            f"{len(self.selected_data) if self.selected_data is not None else 0} "
            f"yearly observations extracted from the dataset "
            f"'{self.current_filename}'. "
            f"The mean temperature was {mean_val:.2f} °C with a standard "
            f"deviation of {std_val:.2f} °C. "
            f"The computed statistics and correlation matrix provide a "
            f"quantitative foundation for understanding historical climate "
            f"behaviour and can support further predictive modelling."
        )


    # ======================================================================
    # PDF EXPORT
    # ======================================================================
    def export_pdf(self):
        """
        Ask the user for a save location and export the summary as a PDF.

        If ReportLab is not installed, an error message is shown instead.
        """
        # ---- Guard: ReportLab must be installed ----
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "ReportLab is not installed.\n\n"
                "Install it using:\n    pip install reportlab"
            )
            return

        # ---- Ask user where to save the PDF ----
        file_path = filedialog.asksaveasfilename(
            title="Save Summary as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            # Pre-fill the filename with a timestamp so exports don't clash.
            initialfile=f"weather_summary_"
                        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        # User cancelled the dialog.
        if not file_path:
            return

        # ---- Try to generate the PDF, catch any runtime errors ----
        try:
            self._write_pdf(file_path)
            messagebox.showinfo(
                "Export Successful",
                f"Summary PDF saved successfully:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "PDF Export Error",
                f"An error occurred while generating the PDF:\n\n{e}"
            )


    def _write_pdf(self, file_path):
        """
        Actually build the PDF document using ReportLab's Platypus
        (Page Layout Using Typesetting And Scripting) framework.

        Parameters
        ----------
        file_path : str
            Full path where the PDF will be written.
        """

        # ------------------------------------------------------------------
        # Create the document template. This defines page size and margins.
        # ------------------------------------------------------------------
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            leftMargin=0.7 * inch,
            rightMargin=0.7 * inch,
            topMargin=0.7 * inch,
            bottomMargin=0.7 * inch,
            title="Weather Analytics Project Summary"
        )

        # ------------------------------------------------------------------
        # Get the default style sheet (body, headings, code, etc.)
        # ------------------------------------------------------------------
        styles = getSampleStyleSheet()

        # ------------------------------------------------------------------
        # Define custom paragraph styles for our PDF.
        # ------------------------------------------------------------------

        # Main title (large, blue, centred).
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=20,
            textColor=colors.HexColor("#2b6cb0"),
            alignment=TA_CENTER,
            spaceAfter=6
        )

        # Subtitle (smaller, grey, centred) — used for the timestamp.
        subtitle_style = ParagraphStyle(
            "SubtitleStyle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#4a5568"),
            alignment=TA_CENTER,
            spaceAfter=18
        )

        # Section heading (blue, slightly spaced above).
        h2_style = ParagraphStyle(
            "H2Style",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#2b6cb0"),
            spaceBefore=12,
            spaceAfter=6
        )

        # Body text (readable line height).
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=10.5,
            leading=15,
            alignment=TA_LEFT
        )

        # Bullet-point style (indented).
        bullet_style = ParagraphStyle(
            "BulletStyle",
            parent=body_style,
            leftIndent=14,
            bulletIndent=4,
            spaceAfter=4
        )

        # Monospace style for the correlation matrix (with a light box).
        mono_style = ParagraphStyle(
            "MonoStyle",
            parent=styles["Code"],
            fontSize=9,
            textColor=colors.HexColor("#1a202c"),
            backColor=colors.HexColor("#f7fafc"),
            borderColor=colors.HexColor("#cbd5e0"),
            borderWidth=0.5,
            borderPadding=6
        )

        # ------------------------------------------------------------------
        # `story` is the list of "flowables" (elements) that make up the PDF.
        # Each item is added to the story in order, and ReportLab handles
        # pagination automatically.
        # ------------------------------------------------------------------
        story = []

        # ----------- TITLE & TIMESTAMP -----------
        story.append(Paragraph(
            "Weather Analytics Project — Summary Report",
            title_style
        ))
        story.append(Paragraph(
            f"Generated on "
            f"{datetime.now().strftime('%d %B %Y, %H:%M')}",
            subtitle_style
        ))

        # ----------- SECTION 1: DATASET OVERVIEW -----------
        story.append(Paragraph("1. Dataset Overview", h2_style))
        story.append(self._kv_table([
            ["File Name", self.current_filename or "—"],
            ["Total Rows", f"{self.df.shape[0]:,}"],
            ["Total Columns", f"{self.df.shape[1]}"],
            ["Year Columns",
             str(len([c for c in self.df.columns if c.startswith("Y")]))],
            ["Unique Areas",
             str(self.df["Area"].nunique())
             if "Area" in self.df.columns else "—"],
            ["Unique Elements",
             str(self.df["Element"].nunique())
             if "Element" in self.df.columns else "—"],
            ["Unique Month Types",
             str(self.df["Months"].nunique())
             if "Months" in self.df.columns else "—"],
        ]))

        # ----------- SECTION 2: ANALYSIS CONFIGURATION -----------
        story.append(Paragraph("2. Analysis Configuration", h2_style))
        story.append(self._kv_table([
            ["Selected Area", self.area or "—"],
            ["Selected Element", self.element or "—"],
            ["Selected Period", self.period or "—"],
            ["Observations Used",
             str(len(self.selected_data))
             if self.selected_data is not None else "—"],
        ]))

        # ----------- SECTION 3: STATISTICAL RESULTS -----------
        story.append(Paragraph("3. Statistical Results", h2_style))
        if self.statistics:
            # Convert dict to a list of [key, value] pairs for the table.
            rows = []
            for k, v in self.statistics.items():
                rows.append([
                    str(k),
                    v if isinstance(v, str) else f"{v:.4f}"
                ])
            story.append(self._kv_table(rows))
        else:
            story.append(Paragraph(
                "No statistics available.", body_style
            ))

        # ----------- SECTION 4: CORRELATION MATRIX -----------
        story.append(Paragraph("4. Correlation Matrix", h2_style))
        corr_text = self.analysis_results.get("correlation_text", "")
        if corr_text.strip():
            # ReportLab collapses multiple spaces in Paragraph, so we
            # replace leading spaces with &nbsp; (non-breaking space) to
            # preserve column alignment.
            for line in corr_text.splitlines():
                if line.strip():
                    story.append(Paragraph(
                        line.replace(" ", "&nbsp;"),
                        mono_style
                    ))
        else:
            story.append(Paragraph(
                "Correlation matrix not available.", body_style
            ))

        # ----------- FORCE NEW PAGE FOR FINDINGS + CONCLUSION -----------
        # Keeps the numeric tables on page 1 and qualitative text on page 2.
        story.append(PageBreak())

        # ----------- SECTION 5: KEY FINDINGS -----------
        story.append(Paragraph(
            "5. Key Findings & Interpretation", h2_style
        ))
        for bullet in self._generate_findings():
            story.append(Paragraph(
                f"• {bullet}", bullet_style
            ))

        # ----------- SECTION 6: CONCLUSION -----------
        story.append(Paragraph("6. Conclusion", h2_style))
        story.append(Paragraph(
            self._generate_conclusion(), body_style
        ))

        '''# ----------- FOOTER NOTE -----------
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "<i>This report was automatically generated by the "
            "Weather Analytics Tool.</i>",
            subtitle_style
        ))'''

        # ------------------------------------------------------------------
        # Finally, build the PDF. ReportLab walks through the story and
        # writes each flowable onto pages, breaking as needed.
        # ------------------------------------------------------------------
        doc.build(story)


    def _kv_table(self, rows):
        """
        Helper: create a styled two-column key/value table for the PDF.

        Parameters
        ----------
        rows : list[tuple[str, str]]
            List of (key, value) pairs.

        Returns
        -------
        table : reportlab.platypus.Table
            A table ready to be appended to the story.
        """
        # Convert each row into two Paragraph objects (so long values wrap).
        data = [
            [
                Paragraph(f"<b>{k}</b>", getSampleStyleSheet()["Normal"]),
                Paragraph(str(v), getSampleStyleSheet()["Normal"])
            ]
            for k, v in rows
        ]

        # Column widths: 2.2" for keys, 4.3" for values.
        tbl = Table(data, colWidths=[2.2 * inch, 4.3 * inch])

        # Apply visual styling: light grey key column, thin grid lines,
        # and padded cells.
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1),
             colors.HexColor("#edf2f7")),           # Key column background
            ("BOX", (0, 0), (-1, -1), 0.5,
             colors.HexColor("#cbd5e0")),           # Outer border
            ("INNERGRID", (0, 0), (-1, -1), 0.25,
             colors.HexColor("#e2e8f0")),           # Grid between cells
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), # Vertical centring
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return tbl


    # ======================================================================
    # REFRESH / CLOSE HELPERS
    # ======================================================================

    def _refresh(self):
        """
        Rebuild all six content sections in the scroll frame.
        Useful if statistics or filters have changed since the dashboard
        was opened.
        """
        # Delete existing content from the scroll frame.
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Recreate the six sections in order.
        self._section_dataset_overview()
        self._section_analysis_config()
        self._section_statistics()
        self._section_correlation()
        self._section_key_findings()
        self._section_conclusion()


    def _close(self):
        """
        Safely close the dashboard:
            1. Release the modal grab (if any).
            2. Destroy the Toplevel window (only if we created one).
        """
        try:
            self.window.grab_release()
        except Exception:
            pass

        # Only destroy the window if it is our own Toplevel — not if the
        # dashboard was rendered into an existing frame.
        if isinstance(self.parent, tk.Tk):
            self.window.destroy()
