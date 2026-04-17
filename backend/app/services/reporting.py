from fpdf import FPDF
from fpdf.errors import FPDFException
import os
import re
from datetime import datetime
from app.utils.vercel import get_storage_path


class ReportingService:
    def __init__(self):
        self.reports_dir = get_storage_path("reports")

    def _sanitize_pdf_text(self, value):
        """
        Make text safe for FPDF:
        - handle None
        - normalize unicode punctuation
        - remove hidden characters
        - add break opportunities for long URLs/paths/tokens
        - force latin-1-safe output for built-in fonts like Helvetica
        """
        if value is None:
            return "N/A"

        text = str(value)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove hidden/problematic whitespace chars
        text = text.replace("\u00a0", " ")   # non-breaking space
        text = text.replace("\u200b", "")    # zero-width space
        text = text.replace("\ufeff", "")    # BOM

        # Replace unicode punctuation with safer ASCII
        replacements = {
            "—": "-",
            "–": "-",
            "•": "*",
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "…": "...",
            "✓": "[OK]",
            "⚠": "[!]",
            "✅": "[OK]",
            "❌": "[X]",
            "🔒": "[LOCK]",
            "🔗": "[LINK]",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Add wrapping opportunities around separators often found in URLs/paths/tokens
        separators = ["/", "\\", "?", "&", "=", ".", "_", "-", ":", "@", "#"]
        for sep in separators:
            text = text.replace(sep, sep + " ")

        # Break any extremely long token with no spaces
        def break_long_token(match):
            token = match.group(0)
            chunk_size = 20
            return " ".join(token[i:i + chunk_size] for i in range(0, len(token), chunk_size))

        text = re.sub(r"\S{35,}", break_long_token, text)

        # Final encoding fallback for Helvetica/core fonts
        text = text.encode("latin-1", errors="replace").decode("latin-1")

        return text

    def _safe_multicell(self, pdf, width, height, text, label="unknown"):
        """
        Safely render multicell text and print useful debug info if it fails.
        """
        clean = self._sanitize_pdf_text(text)

        try:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(width, height, clean)
        except FPDFException as e:
            print(f"[PDF ERROR] Section: {label}")
            print(f"[PDF ERROR] Width: {width}, Height: {height}")
            print(f"[PDF ERROR] Text preview: {repr(clean[:500])}")

            # Last-resort fallback: aggressively break remaining text
            fallback = re.sub(
                r"(\S)",
                r"\1 ",
                clean[:2000]
            )
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(width, height, fallback)

    def _safe_cell(self, pdf, width, height, text="", **kwargs):
        clean = self._sanitize_pdf_text(text)
        pdf.set_x(pdf.l_margin)
        pdf.cell(width, height, clean, **kwargs)

    def generate_threat_report(self, analysis_result: dict):
        pdf = FPDF()
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        body_w = pdf.w - pdf.l_margin - pdf.r_margin

        # Header background
        pdf.set_fill_color(17, 20, 27)
        pdf.rect(0, 0, pdf.w, 40, "F")

        # Header title
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(pdf.l_margin, 12)
        pdf.cell(body_w, 15, "ZenShield AI Audit", align="C", new_x="LMARGIN", new_y="NEXT")

        # Header subtitle
        pdf.set_font("Helvetica", size=10)
        pdf.set_x(pdf.l_margin)
        pdf.cell(
            body_w,
            10,
            self._sanitize_pdf_text(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_text_color(0, 0, 0)
        pdf.set_y(50)

        # Risk Summary
        risk_score = analysis_result.get("risk_score", 0)
        status = str(analysis_result.get("severity", "SAFE")).upper()

        pdf.set_font("Helvetica", "B", 16)
        self._safe_cell(
            pdf,
            body_w,
            10,
            f"Status: {status} ({risk_score}%)",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(2)

        # Analyzed content preview
        pdf.set_font("Helvetica", "B", 11)
        self._safe_cell(
            pdf,
            body_w,
            10,
            "ANALYZED CONTENT PREVIEW:",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font("Helvetica", size=9)
        self._safe_multicell(
            pdf,
            body_w,
            5,
            analysis_result.get("text_preview", "N/A"),
            label="text_preview",
        )
        pdf.ln(5)

        # Executive summary
        pdf.set_font("Helvetica", "B", 11)
        self._safe_cell(
            pdf,
            body_w,
            10,
            "EXECUTIVE SUMMARY:",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font("Helvetica", size=9)
        self._safe_multicell(
            pdf,
            body_w,
            5,
            analysis_result.get("plain_explanation", "No explanation available."),
            label="plain_explanation",
        )
        pdf.ln(5)

        # Intelligence breakdown
        pdf.set_font("Helvetica", "B", 11)
        self._safe_cell(
            pdf,
            body_w,
            10,
            "INTELLIGENCE BREAKDOWN:",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font("Helvetica", size=9)
        breakdown = analysis_result.get("breakdown", {})

        if isinstance(breakdown, dict) and breakdown:
            for key, val in breakdown.items():
                title = str(key).replace("_", " ").title()

                if isinstance(val, dict):
                    self._safe_multicell(
                        pdf,
                        body_w,
                        6,
                        f"- {title}:",
                        label=f"breakdown_{key}",
                    )
                    for sub_key, sub_val in val.items():
                        sub_title = str(sub_key).replace("_", " ").title()
                        self._safe_multicell(
                            pdf,
                            body_w,
                            6,
                            f"  - {sub_title}: {sub_val}",
                            label=f"breakdown_{key}_{sub_key}",
                        )
                else:
                    self._safe_multicell(
                        pdf,
                        body_w,
                        6,
                        f"- {title}: {val}",
                        label=f"breakdown_{key}",
                    )
        else:
            self._safe_multicell(
                pdf,
                body_w,
                6,
                "No detailed breakdown available.",
                label="breakdown_empty",
            )

        pdf.ln(5)

        # Risk signals
        pdf.set_font("Helvetica", "B", 11)
        self._safe_cell(
            pdf,
            body_w,
            10,
            "RISK SIGNALS DETECTED:",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font("Helvetica", size=9)
        signals = analysis_result.get("signals", [])

        if isinstance(signals, list) and signals:
            for idx, sig in enumerate(signals):
                msg = sig.get("message", sig) if isinstance(sig, dict) else sig
                self._safe_multicell(
                    pdf,
                    body_w,
                    6,
                    f"[!] {msg}",
                    label=f"signal_{idx}",
                )
        else:
            self._safe_multicell(
                pdf,
                body_w,
                6,
                "No major risk signals detected.",
                label="signals_empty",
            )

        pdf.ln(5)

        # Recommendations header
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_x(pdf.l_margin)
        pdf.cell(
            body_w,
            10,
            self._sanitize_pdf_text("ACTIONABLE RECOMMENDATIONS:"),
            fill=True,
            new_x="LMARGIN",
            new_y="NEXT",
        )

        # Recommendations body
        pdf.set_font("Helvetica", size=9)
        recommendations = analysis_result.get("recommendations", [])

        if isinstance(recommendations, list) and recommendations:
            for idx, rec in enumerate(recommendations):
                self._safe_multicell(
                    pdf,
                    body_w,
                    6,
                    f"* {rec}",
                    label=f"recommendation_{idx}",
                )
        else:
            self._safe_multicell(
                pdf,
                body_w,
                6,
                analysis_result.get("suggested_action", "Monitoring recommended."),
                label="suggested_action",
            )

        # Footer
        pdf.set_y(-25)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(150, 150, 150)
        pdf.set_x(pdf.l_margin)
        pdf.cell(
            body_w,
            10,
            self._sanitize_pdf_text("AMD ROCm Optimized Audit Report | Confidential"),
            align="C",
        )

        report_filename = f"audit_{int(datetime.now().timestamp())}.pdf"
        report_path = os.path.join(self.reports_dir, report_filename)
        pdf.output(report_path)

        return report_filename, report_path

    def generate_awareness_summary(self, stats: dict):
        pdf = FPDF()
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        body_w = 180

        # Header - Safe drawing
        pdf.set_fill_color(17, 20, 27)
        pdf.rect(0, 0, 210, 50, 'F')
        
        pdf.set_font("Helvetica", 'B', 24)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 15)
        pdf.cell(body_w, 20, "ZenShield AI - Security Awareness Report", align='C', ln=1)
        
        pdf.set_font("Helvetica", size=10)
        pdf.set_x(15)
        pdf.cell(body_w, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", align='C', ln=1)
        
        pdf.ln(25)
        pdf.set_text_color(0, 0, 0)

        # Core Metrics
        pdf.set_font("Helvetica", 'B', 16)
        pdf.set_x(15)
        pdf.cell(body_w, 10, "Executive Security Summary", ln=1)
        pdf.ln(5)

        # Score Box
        current_score = stats.get('current_score', 0)
        pdf.set_fill_color(240, 245, 255)
        pdf.rect(15, 80, 180, 40, 'F')
        
        pdf.set_font("Helvetica", 'B', 12)
        pdf.set_xy(25, 85)
        pdf.cell(body_w, 10, "Your Cyber Awareness Score:", ln=1)
        
        pdf.set_font("Helvetica", 'B', 32)
        pdf.set_text_color(59, 130, 246)
        pdf.set_x(25)
        pdf.cell(body_w, 15, f"{current_score}%", ln=1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(130)
        
        # Risk Distribution
        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_x(15)
        pdf.cell(0, 10, "Intelligence Findings Breakdown", ln=1)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", size=10)
        counts = stats.get('risk_counts', {})
        pdf.set_x(15)
        pdf.cell(0, 8, f"- High Risk Threats Detected: {counts.get('high', 0)}", ln=1)
        pdf.set_x(15)
        pdf.cell(0, 8, f"- Medium Risk Encounters: {counts.get('medium', 0)}", ln=1)
        pdf.set_x(15)
        pdf.cell(0, 8, f"- Safe Scans Verified: {counts.get('low', 0)}", ln=1)
        
        pdf.ln(10)

        # Guidance
        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_x(15)
        pdf.cell(0, 10, "AI Governance & Recommendations", ln=1)
        pdf.set_font("Helvetica", size=10)
        
        advice = [
            "1. Consistently audit suspicious emails in 'Phishing Analysis' before clicking links.",
            "2. High-risk code patterns found in scripts must be isolated in a secure container.",
            "3. Your awareness score depends on how successfully you identify threats across all modules."
        ]
        for line in advice:
            pdf.set_x(15)
            pdf.multi_cell(body_w, 8, line)

        # Footer
        pdf.set_y(-25)
        pdf.set_font("Helvetica", 'I', 7)
        pdf.set_text_color(180, 180, 180)
        pdf.set_x(15)
        pdf.cell(0, 10, "AMD ROCm NPU Optimized Generative Audit Report | Confidential", align='C')

        report_filename = f"zen_audit_report_{int(datetime.now().timestamp())}.pdf"
        report_path = os.path.join(self.reports_dir, report_filename)
        pdf.output(report_path)
        
        return report_filename, report_path