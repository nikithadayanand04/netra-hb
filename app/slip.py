from __future__ import annotations

from datetime import datetime

from fpdf import FPDF

import ui

FONTS = ui.APP_DIR / "fonts"
INK, SLATE, LINE, HAEM, CLEAR = (27, 35, 64), (91, 100, 117), (211, 216, 224), (179, 18, 58), (31, 122, 109)


def _rgb(hex_: str) -> tuple[int, int, int]:
    return tuple(int(hex_[i:i + 2], 16) for i in (1, 3, 5))


def _pdf() -> FPDF:
    pdf = FPDF(format=(148, 210))
    pdf.set_margins(14, 14, 14)
    pdf.set_auto_page_break(False)
    pdf.add_font("Atkinson", "", FONTS / "AtkinsonHyperlegible-Regular.ttf")
    pdf.add_font("Atkinson", "B", FONTS / "AtkinsonHyperlegible-Bold.ttf")
    pdf.add_font("Bricolage", "B", FONTS / "BricolageGrotesque-VF.ttf", variations={"wght": 700, "opsz": 28})
    for name, file in (("NotoKannada", "NotoSansKannada-VF.ttf"), ("NotoDevanagari", "NotoSansDevanagari-VF.ttf")):
        pdf.add_font(name, "", FONTS / file, variations={"wght": 400})
        pdf.add_font(name, "B", FONTS / file, variations={"wght": 700})
    pdf.set_fallback_fonts(["NotoKannada", "NotoDevanagari"])
    pdf.set_text_shaping(True)
    pdf.add_page()
    return pdf


def _strip(pdf: FPDF, x: float, y: float, w: float, h: float, position: float, cutoff: float,
           swatch: tuple[int, int, int]) -> None:
    stops = [_rgb(c) for c in ui.STRIP_STOPS]
    n = 120
    for i in range(n):
        f = i / (n - 1) * (len(stops) - 1)
        a, b = stops[int(f)], stops[min(int(f) + 1, len(stops) - 1)]
        t = f - int(f)
        pdf.set_fill_color(*(round(a[k] + (b[k] - a[k]) * t) for k in range(3)))
        pdf.rect(x + w * i / n, y, w / n + 0.05, h, style="F")
    pdf.set_draw_color(*INK)
    pdf.set_line_width(0.5)
    cx = x + w * ui._hb_frac(cutoff)
    pdf.line(cx, y - 2, cx, y + h + 2)
    pdf.set_font("Atkinson", "", 7.5)
    pdf.set_text_color(*SLATE)
    for v in range(int(ui.HB_MIN), int(ui.HB_MAX) + 1):
        tx = x + w * ui._hb_frac(v)
        pdf.set_xy(tx - 4, y + h + 1.2)
        pdf.cell(8, 3, f"{v}", align="C")
    pdf.set_font("Atkinson", "B", 7.5)
    pdf.set_text_color(*INK)
    pdf.set_xy(cx - 25, y + h + 4.5)
    pdf.cell(50, 3.5, f"{ui.t('cutoff')} {cutoff:g} g/dL", align="C")
    sx = x + w * ui._hb_frac(position)
    pdf.set_fill_color(*swatch)
    pdf.set_draw_color(255, 255, 255)
    pdf.set_line_width(0.8)
    pdf.rect(sx - 3.5, y - 9, 7, 7, style="DF", round_corners=True, corner_radius=1.2)
    pdf.set_draw_color(*INK)
    pdf.set_line_width(0.3)
    pdf.line(sx, y - 2, sx, y)


def _row(pdf: FPDF, label: str, value: str, bold: bool = False, colour=INK) -> None:
    pdf.set_x(14)
    pdf.set_font("Atkinson", "", 9)
    pdf.set_text_color(*SLATE)
    pdf.cell(34, 6, label)
    pdf.set_font("Atkinson", "B" if bold else "", 10.5)
    pdf.set_text_color(*colour)
    pdf.multi_cell(0, 6, value, align="L")
    pdf.ln(0.8)


def referral_slip(visit: dict) -> bytes:
    """visit: name, age_key, cutoff, refer, results (list of site results), combined (or None), time (datetime)."""
    pdf = _pdf()
    when: datetime = visit["time"]
    # brand
    for i, c in enumerate(ui.STRIP_STOPS):
        pdf.set_fill_color(*_rgb(c))
        pdf.rect(14 + i * 1.6, 15.5, 1.7, 3.2, style="F")
    pdf.set_xy(24, 14)
    pdf.set_font("Bricolage", "B", 12)
    pdf.set_text_color(*INK)
    pdf.cell(0, 6, "Netra-Hb")
    pdf.set_xy(14, 24)
    pdf.set_font("Bricolage", "B", 22)
    pdf.cell(0, 10, ui.t("slip_title"))
    pdf.set_xy(14, 36)
    _row(pdf, ui.t("slip_patient"), f"{visit['name'] or ui.t('slip_unnamed')}, {ui.t(visit['age_key'])}")
    _row(pdf, ui.t("slip_date"), when.strftime("%d/%m/%Y, %H:%M"))
    _row(pdf, ui.t("slip_sites"), ", ".join(ui.t(f"site_{r['site']}") for r in visit["results"]))
    refer = visit["refer"]   # any site that refers; the experimental combined estimate never cancels a referral
    final = min(visit["results"], key=lambda r: r["position"])
    _row(pdf, ui.t("slip_result"), ui.t("refer" if refer else "normal"), bold=True, colour=HAEM if refer else CLEAR)
    lines = [ui.t("site_result", site=ui.t(f"site_{r['site']}"),
                  word=ui.t("anaemic_word" if r["refer"] else "not_anaemic_word"), p=round(r["p"] * 100))
             for r in visit["results"]]
    if visit["combined"]:
        lines.append(f"{ui.t('combined')}: {round(visit['combined']['p'] * 100)}%")
    _row(pdf, "", "\n".join(lines))
    if visit.get("low_conf"):
        _row(pdf, ui.t("slip_conf"), ui.t("low_conf") + ": " + " ".join(ui.t(k) for k in dict.fromkeys(visit["low_conf"])))

    y = pdf.get_y() + 12
    _strip(pdf, 16, y, 116, 6, final["position"], visit["cutoff"], final["swatch"])

    y += 18
    pdf.set_fill_color(*(HAEM if refer else CLEAR))
    pdf.rect(14, y, 1.6, 20, style="F")
    pdf.set_xy(19, y + 1)
    pdf.set_font("Atkinson", "", 9)
    pdf.set_text_color(*SLATE)
    pdf.cell(0, 5, ui.t("slip_next"))
    pdf.set_xy(19, y + 6.5)
    pdf.set_font("Atkinson", "B", 11.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(110, 6, ui.t("next_step") if refer else ui.t("no_referral"), align="L")

    pdf.set_xy(14, y + 30)
    pdf.set_font("Atkinson", "", 9.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 6, ui.t("slip_phc"), align="L")

    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.3)
    pdf.line(14, 186, 134, 186)
    pdf.set_xy(14, 188)
    pdf.set_font("Atkinson", "", 8.5)
    pdf.set_text_color(*SLATE)
    pdf.multi_cell(0, 4.5, ui.t("footer"), align="L")
    return bytes(pdf.output())
