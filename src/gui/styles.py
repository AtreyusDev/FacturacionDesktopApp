APP_GLOBAL_STYLES = """
* {
    font-family: 'Segoe UI';
    font-size:14px;
    color: black;
}
QWidget {
    background-color: #F0F0F0;
}
QLabel[class="main-text"]{
    font-size: 18px;
    font-weight: bold;
}
QPushButton {
    background-color: #FBEEAF;
    color: black;
    border-radius: 5px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #DEC135;
}
QPushButton:pressed{
    background-color: #FFD700;
}
QPushButton:checked {
    background-color: #FFD700;
}
QListWidget {
    background-color: #C4CCDE;
    color: black;
    padding: 5px;
}
QListWidget::item {
    padding: 6px;
    border: none;
    color: #333;
}
QListWidget::item:hover {
    background-color: #f0f0f0;
    color: #000;
}
QListWidget::item:selected {
    background-color: #FBEEAF;
    color: black;
    font-weight: bold;
}
QSlider::groove:horizontal {
    border: 1px solid #bbb;
    height: 6px;
    background: white; /* color base del groove */
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #FBEEAF; /* parte izquierda (marcada) */
    border: 1px solid #aaa;
    height: 6px;
    border-radius: 3px;
}

QSlider::add-page:horizontal {
    background: white; /* parte derecha (restante) */
    border: 1px solid #aaa;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #DEC135;
    border: 1px solid #aaa;
    width: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QScrollBar:vertical {
    background: #C4CCDE;
    width: 12px;
    margin: 0px;
    border: none;
}

QScrollBar::handle:vertical {
    background: #FBEEAF;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: white;
}
QRadioButton {
    spacing: 8px;
    font-size: 11pt;
    color: #333;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 15px;
    border: 2px solid #666;
    background-color: white;
}

QRadioButton::indicator:checked {
    background-color: #FBEEAF;
    border: 2px solid #DEC135;
}
"""