# -*- coding: utf-8 -*-
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "screenshots"
OUT = ROOT / "BOAR-prezentaciya.pptx"

# Brand
PINE = RGBColor(0x1C, 0x3D, 0x38)
PINE_DARK = RGBColor(0x0F, 0x28, 0x24)
COPPER = RGBColor(0x9A, 0x6B, 0x3D)
PAPER = RGBColor(0xF3, 0xEE, 0xE4)
SHEET = RGBColor(0xFA, 0xF7, 0xF1)
INK = RGBColor(0x17, 0x24, 0x1F)
MUTED = RGBColor(0x66, 0x75, 0x6E)
WHITE = RGBColor(0xFF, 0xFC, 0xF7)
BAD = RGBColor(0x8A, 0x3A, 0x2A)
OK = RGBColor(0x2B, 0x5C, 0x45)


def set_run(run, size=18, bold=False, color=INK, font="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_textbox(slide, left, top, width, height, text, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color, font=font)
    return box


def fill_shape(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def add_bg(slide, color=PAPER):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    fill_shape(shape, color)
    # send to back
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def add_footer(slide, page, total=12, light=True):
    color = RGBColor(0x8A, 0xA1, 0x99) if not light else MUTED
    add_textbox(slide, Inches(0.5), Inches(7.05), Inches(8), Inches(0.3), "БОАР · новый сайт общества", size=11, color=color)
    add_textbox(slide, Inches(11.2), Inches(7.05), Inches(1.6), Inches(0.3), f"{page} / {total}", size=11, color=color, align=PP_ALIGN.RIGHT)


def fit_image(slide, path, left, top, max_w, max_h):
    if not path.exists():
        return None
    pic = slide.shapes.add_picture(str(path), left, top)
    w, h = pic.width, pic.height
    scale = min(max_w / w, max_h / h)
    pic.width = int(w * scale)
    pic.height = int(h * scale)
    return pic


def add_screenshot_slide(prs, blank, eyebrow, title, image_path, url, page, total):
    """Screenshot on dark mat inside a browser-like frame — no blend with cream site bg."""
    s = prs.slides.add_slide(blank)
    add_bg(s, PINE_DARK)

    add_textbox(s, Inches(0.55), Inches(0.28), Inches(12), Inches(0.28), eyebrow, size=12, bold=True, color=COPPER)
    add_textbox(s, Inches(0.55), Inches(0.55), Inches(12), Inches(0.45), title, size=22, bold=True, color=WHITE, font="Georgia")

    # Outer mat / window
    frame_left = Inches(0.55)
    frame_top = Inches(1.15)
    frame_w = Inches(12.2)
    frame_h = Inches(5.55)
    frame = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, frame_left, frame_top, frame_w, frame_h)
    fill_shape(frame, RGBColor(0x18, 0x2E, 0x2A))
    frame.line.color.rgb = RGBColor(0x2F, 0x4A, 0x44)
    frame.adjustments[0] = 0.04

    # Chrome bar
    chrome_h = Inches(0.42)
    chrome = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, frame_left, frame_top, frame_w, chrome_h)
    fill_shape(chrome, RGBColor(0x24, 0x3C, 0x37))
    chrome.line.fill.background()

    # Traffic lights
    for i, color in enumerate([RGBColor(0xC7, 0x6B, 0x5A), RGBColor(0xC9, 0xA0, 0x5C), RGBColor(0x5E, 0x9A, 0x72)]):
        dot = s.shapes.add_shape(
            MSO_SHAPE.OVAL,
            frame_left + Inches(0.18 + i * 0.28),
            frame_top + Inches(0.13),
            Inches(0.16),
            Inches(0.16),
        )
        fill_shape(dot, color)

    # URL pill
    url_left = frame_left + Inches(1.3)
    url_w = frame_w - Inches(1.6)
    url_bar = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        url_left,
        frame_top + Inches(0.08),
        url_w,
        Inches(0.26),
    )
    fill_shape(url_bar, RGBColor(0x12, 0x22, 0x1F))
    url_bar.line.fill.background()
    url_bar.adjustments[0] = 0.5
    add_textbox(
        s,
        url_left + Inches(0.15),
        frame_top + Inches(0.08),
        url_w - Inches(0.2),
        Inches(0.26),
        url,
        size=10,
        color=RGBColor(0xA8, 0xB9, 0xB3),
    )

    # Image area inside frame
    pad = Inches(0.12)
    img_left = frame_left + pad
    img_top = frame_top + chrome_h + pad
    max_w = frame_w - pad * 2
    max_h = frame_h - chrome_h - pad * 2

    pic = fit_image(s, image_path, img_left, img_top, max_w, max_h)
    if pic is not None:
        # center horizontally in the frame content area
        pic.left = int(img_left + (max_w - pic.width) / 2)
        pic.top = int(img_top)

        # thin border rectangle matching image size
        border = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, pic.left, pic.top, pic.width, pic.height)
        border.fill.background()
        border.line.color.rgb = RGBColor(0x3A, 0x55, 0x4E)
        border.line.width = Pt(1.25)

    add_footer(s, page, total, light=False)
    return s


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    total = 12

    # 1 Title
    s = prs.slides.add_slide(blank)
    add_bg(s, PINE_DARK)
    add_textbox(s, Inches(0.7), Inches(1.6), Inches(11), Inches(0.4), "ПРЕЗЕНТАЦИЯ ДЛЯ РУКОВОДСТВА ОБЩЕСТВА", size=14, bold=True, color=COPPER)
    add_textbox(s, Inches(0.7), Inches(2.2), Inches(11.5), Inches(2), "Новый сайт БОАР\nкак рабочий инструмент врача", size=40, bold=True, color=WHITE, font="Georgia")
    add_textbox(s, Inches(0.7), Inches(4.6), Inches(10), Inches(1), "Заседания, документы, обучение, вступление и кабинет члена —\nв одном современном продукте.", size=18, color=RGBColor(0xC5, 0xD4, 0xCE))
    add_textbox(s, Inches(0.7), Inches(6.5), Inches(10), Inches(0.4), "Сентябрь 2026 · макет для согласования", size=12, color=MUTED)

    # 2 Why
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_textbox(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.3), "ЗАЧЕМ МЕНЯТЬ", size=12, bold=True, color=COPPER)
    add_textbox(s, Inches(0.6), Inches(0.7), Inches(12), Inches(0.8), "Что нужно профессору и практикующему врачу", size=28, bold=True, color=INK, font="Georgia")
    items = [
        ("01", "Быстро найти заседание", "Дата, зал, программа — без поиска по ленте новостей."),
        ("02", "Открыть нужный документ", "Протокол, санэпид, ФАР — по разделам."),
        ("03", "Показать общество коллегам", "Сайт, который не стыдно открыть на лекции и съезде."),
        ("04", "Принять нового члена", "Понятный путь заявки вместо письма «куда-нибудь»."),
    ]
    for i, (num, title, text) in enumerate(items):
        x = Inches(0.6 + (i % 2) * 6.2)
        y = Inches(1.8 + (i // 2) * 2.3)
        card = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(5.9), Inches(2.0))
        fill_shape(card, SHEET)
        card.line.color.rgb = RGBColor(0xD8, 0xD0, 0xC4)
        add_textbox(s, x + Inches(0.25), y + Inches(0.25), Inches(5.3), Inches(0.3), num, size=14, bold=True, color=COPPER)
        add_textbox(s, x + Inches(0.25), y + Inches(0.6), Inches(5.3), Inches(0.4), title, size=18, bold=True, color=INK, font="Georgia")
        add_textbox(s, x + Inches(0.25), y + Inches(1.1), Inches(5.3), Inches(0.7), text, size=14, color=MUTED)
    add_footer(s, 2, total)

    # 3–10 screenshot slides with framed windows
    add_screenshot_slide(
        prs, blank, "ГЛАВНАЯ",
        "Ближайшее заседание — сразу в первом экране",
        SHOTS / "01-home.png",
        "leshahker.github.io/bsaer-mockup/",
        3, total,
    )

    # 4 Old vs new
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_textbox(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.3), "СРАВНЕНИЕ", size=12, bold=True, color=COPPER)
    add_textbox(s, Inches(0.6), Inches(0.7), Inches(12), Inches(0.6), "Старый сайт → новый продукт", size=28, bold=True, color=INK, font="Georgia")
    left = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.6), Inches(5.8), Inches(5.0))
    fill_shape(left, SHEET)
    left.line.color.rgb = BAD
    right = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.8), Inches(5.0))
    fill_shape(right, SHEET)
    right.line.color.rgb = OK
    add_textbox(s, Inches(0.85), Inches(1.8), Inches(5.2), Inches(0.4), "Было (bsaer.org)", size=18, bold=True, color=BAD, font="Georgia")
    add_textbox(s, Inches(7.15), Inches(1.8), Inches(5.2), Inches(0.4), "Стало (новый макет)", size=18, bold=True, color=OK, font="Georgia")
    old = "• Новостная лента как главный экран\n• Документы «где-то в разделах»\n• Съезды и заседания вперемешку\n• Вступление через почту\n• Устаревший визуальный язык\n• Слабая мобильная читаемость"
    new = "• Действие и заседание сразу\n• Каталог с 6 понятными разделами\n• Календарь + архив без путаницы\n• Форма членства и понятные шаги\n• Сдержанный медицинский дизайн\n• Адаптив под телефон и проектор"
    add_textbox(s, Inches(0.85), Inches(2.4), Inches(5.2), Inches(3.8), old, size=15, color=INK)
    add_textbox(s, Inches(7.15), Inches(2.4), Inches(5.2), Inches(3.8), new, size=15, color=INK)
    add_footer(s, 4, total)

    protocols = SHOTS / "08-library-protocols.png"
    if not protocols.exists():
        protocols = SHOTS / "02-library.png"

    add_screenshot_slide(
        prs, blank, "БИБЛИОТЕКА",
        "Шесть разделов: книги, протоколы, санэпид, статьи, ФАР, видео",
        SHOTS / "02-library.png",
        "leshahker.github.io/bsaer-mockup/library.html",
        5, total,
    )
    add_screenshot_slide(
        prs, blank, "ПРОТОКОЛЫ И САНЭПИД",
        "Документы разложены так, как ими пользуются врачи",
        protocols,
        "leshahker.github.io/bsaer-mockup/library.html#protocols",
        6, total,
    )
    add_screenshot_slide(
        prs, blank, "СОБЫТИЯ",
        "Календарь ближайших заседаний и архив съездов",
        SHOTS / "03-events.png",
        "leshahker.github.io/bsaer-mockup/events.html",
        7, total,
    )
    add_screenshot_slide(
        prs, blank, "ВСТУПЛЕНИЕ",
        "Путь в членство: статус → заявка → взнос",
        SHOTS / "05-join.png",
        "leshahker.github.io/bsaer-mockup/join.html",
        8, total,
    )
    add_screenshot_slide(
        prs, blank, "ПАЦИЕНТАМ",
        "Спокойные ответы без ложных обещаний",
        SHOTS / "04-patients.png",
        "leshahker.github.io/bsaer-mockup/patients.html",
        9, total,
    )
    add_screenshot_slide(
        prs, blank, "КАБИНЕТ ЧЛЕНА",
        "Демо личного кабинета — задел под закрытую зону и чат",
        SHOTS / "06-cabinet.png",
        "leshahker.github.io/bsaer-mockup/cabinet/",
        10, total,
    )

    # 11 Advantages
    s = prs.slides.add_slide(blank)
    add_bg(s)
    add_textbox(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.3), "ПРЕИМУЩЕСТВА ПРОДУКТА", size=12, bold=True, color=COPPER)
    add_textbox(s, Inches(0.6), Inches(0.7), Inches(12), Inches(0.8), "Почему это лучше «просто обновить WordPress»", size=26, bold=True, color=INK, font="Georgia")
    adv = [
        ("I", "Архитектура под задачи службы АиР, а не под шаблон блога."),
        ("II", "Контент заказчика уже разложен: протоколы и санэпид из рабочих перечней."),
        ("III", "Готовность к хостингу общества: статика сейчас, сервер чата — следующим этапом."),
        ("IV", "Можно согласовывать по экранам: каждый раздел читается отдельно."),
    ]
    for i, (num, text) in enumerate(adv):
        y = Inches(1.8 + i * 1.15)
        add_textbox(s, Inches(0.7), y, Inches(1), Inches(0.5), num, size=22, bold=True, color=COPPER, font="Georgia")
        add_textbox(s, Inches(1.7), y, Inches(10.5), Inches(0.8), text, size=18, color=INK)
    add_footer(s, 11, total)

    # 12 CTA
    s = prs.slides.add_slide(blank)
    add_bg(s, PINE_DARK)
    add_textbox(s, Inches(0.7), Inches(1.5), Inches(12), Inches(0.3), "ПРЕДЛОЖЕНИЕ", size=14, bold=True, color=COPPER)
    add_textbox(s, Inches(0.7), Inches(2.1), Inches(11.5), Inches(1.8), "Согласовать макет\nи перенести на хостинг общества", size=34, bold=True, color=WHITE, font="Georgia")
    add_textbox(s, Inches(0.7), Inches(4.3), Inches(11), Inches(1.2), "Живой сайт для показа:\nhttps://leshahker.github.io/bsaer-mockup/\n\nКабинет: /cabinet/  ·  демо-вход admin / admin", size=16, color=RGBColor(0xC5, 0xD4, 0xCE))
    add_textbox(s, Inches(0.7), Inches(6.5), Inches(11), Inches(0.4), "Спасибо · БОАР · сентябрь 2026", size=12, color=MUTED)

    prs.save(OUT)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
