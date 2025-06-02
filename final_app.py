import os
from shiny import App, ui, render, reactive
import ftplib
import tempfile
import base64
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import shutil
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Fungsi untuk mengambil file dari FTP server
def download_from_ftp(area, selected_date):
    date_str = selected_date.strftime("%Y%m%d")
    ftp_url = os.getenv("FTP_URL", "isisendiri")
    username = os.getenv("FTP_USERNAME", "isisendiri")
    password = os.getenv("FTP_PASSWORD", "isisendiri")
    base_path = "/sidik/dpi_oto/dpi_ops_peta/2025"
    peta_filename = f"peta_dpi_{area}_{date_str}.png"
    tabel_filename = f"tabel_dpi_{area}_{date_str}.png"
    peta_path = f"{base_path}/{peta_filename}"
    tabel_path = f"{base_path}/{tabel_filename}"
    logger.debug(f"Mengunduh peta dari: ftp://{ftp_url}{peta_path}")
    logger.debug(f"Mengunduh tabel dari: ftp://{ftp_url}{tabel_path}")
    
    temp_dir = os.path.join(tempfile.gettempdir(), "dpi_images")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
      
    local_peta_path = os.path.join(temp_dir, peta_filename)
    local_tabel_path = os.path.join(temp_dir, tabel_filename)
      
    try:
        with ftplib.FTP(ftp_url, username, password, timeout=60) as ftp:
            ftp.set_pasv(False)
            with open(local_peta_path, "wb") as f:
                ftp.retrbinary(f"RETR {peta_path}", f.write)
            logger.debug(f"Peta berhasil diunduh ke: {local_peta_path}")
            with open(local_tabel_path, "wb") as f:
                ftp.retrbinary(f"RETR {tabel_path}", f.write)
            logger.debug(f"Tabel berhasil diunduh ke: {local_tabel_path}")
        return {"peta": local_peta_path, "tabel": local_tabel_path, "error": None}
    except Exception as e:
        logger.error(f"Error saat mengunduh file: {str(e)}")
        return {"peta": None, "tabel": None, "error": f"Error downloading files: {str(e)}"}


# CSS dan JavaScript dari kode R
css_styles = """
body {
    background-color: #f5f5f5;
    font-family: Arial, sans-serif;
}
.header {
    background-color: white;
    padding: 10px;
    border-bottom: 1px solid #ddd;
    display: flex;
    align-items: center;
}
.logo {
    height: 80px;
    margin-right: 15px;
}
.header-title {
    font-size: 22px;
    font-weight: bold;
    margin: 0;
    flex-grow: 1;
}
.input-area {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin: 10px 0;
}
.input-label {
    font-weight: normal;
    margin-bottom: 5px;
    font-size: 14px;
}
.input-box {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
.calendar-container {
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    width: 100%;
}
.calendar-month {
    min-width: auto;
    width: fit-content;
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow-x: auto;
}
.calendar-slider {
    display: flex;
    width: 100%;
    justify-content: center;
    flex-wrap: nowrap;
    gap: 5px;
    overflow-x: auto;
}
.date-display {
    text-align: center;
    font-weight: bold;
    margin-bottom: 10px;
}
.calendar-btn {
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px 10px;
    cursor: pointer;
    font-size: 16px;
    flex-shrink: 0;
}
.calendar-btn#prev-month {
    margin-right: 5px;
}
.calendar-btn#next-month {
    margin-left: 5px;
}
.calendar-date {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 30px;
    height: 30px;
    margin: 4px;
    cursor: pointer;
    border-radius: 50%;
    box-sizing: border-box;
}
.calendar-date:hover {
    background-color: #e0e0e0;
}
.calendar-date.selected {
    background-color: #3c8dbc;
    color: white;
}
.calendar-date.today {
    border: 1px solid #3c8dbc;
}
.calendar-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}
.calendar-title {
    text-align: center;
    font-weight: bold;
    flex-grow: 1;
}
.calendar-weekdays {
    display: flex;
    justify-content: space-around;
    margin-bottom: 5px;
}
.calendar-weekday {
    width: 30px;
    text-align: center;
    font-weight: bold;
}
.calendar-dates {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    white-space: nowrap;
    width: 100%;
    padding: 0 40px;
    padding-bottom: 10px;
    scrollbar-width: thin;
}
.calendar-dates::-webkit-scrollbar {
    height: 8px;
}
.calendar-dates::-webkit-scrollbar-track {
    background: #f1f1f1;
}
.calendar-dates::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}
.calendar-dates::-webkit-scrollbar-thumb:hover {
    background: #555;
}
.calendar-row {
    display: flex;
    width: 100%;
    justify-content: space-around;
}
.content-box {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin: 10px 0;
    min-height: 250px;
    position: relative;
}
.content-title {
    font-size: 16px;
    font-weight: normal;
    margin-top: 0;
    margin-bottom: 15px;
}
.unduh-btn {
    background-color: #3c8dbc;
    color: white;
    border: none;
    padding: 5px 12px;
    border-radius: 4px;
    position: absolute;
    top: 15px;
    right: 15px;
    display: flex;
    align-items: center;
    font-size: 14px;
}
.unduh-icon {
    margin-right: 5px;
}
.expand-btn {
    position: absolute;
    top: 15px;
    right: 100px;
    background: none;
    border: none;
    color: #3c8dbc;
    font-size: 18px;
    cursor: pointer;
    z-index: 10;
}
.expand-btn:hover {
    color: #2a6496;
}
.placeholder-text {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding-top: 80px;
    color: #666;
    width: 100%;
}
.placeholder-text p {
    margin: 0;
    text-align: center;
    width: 100%;
}
.footer {
    background-color: #7fa9c8;
    color: white;
    padding: 15px;
    margin-top: 20px;
}
.footer-logo {
    height: 30px;
    margin-right: 10px;
}
.footer-title {
    font-size: 18px;
    font-weight: bold;
}
.footer-info {
    font-size: 12px;
    margin: 5px 0;
}
.footer-social {
    text-align: right;
}
.footer-social-icon {
    display: inline-block;
    width: 30px;
    height: 30px;
    background-color: #333;
    border-radius: 50%;
    margin-left: 5px;
    text-align: center;
    line-height: 30px;
    color: white;
}
.copyright {
    text-align: center;
    font-size: 12px;
    margin-top: 10px;
}
.loading-spinner {
    text-align: center;
    padding: 20px;
    color: #3c8dbc;
}
.date-picker {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    width: 100%;
}
.modal-dialog {
    z-index: 1050;
}
.download-count {
    position: absolute;
    top: 50px;
    right: 15px;
    font-size: 12px;
    color: #666;
}
.d-none {
    display: none !important;
}
@media (max-width: 576px) {
    .calendar-slider {
        flex-direction: column;
        gap: 5px;
        overflow-x: hidden;
    }
    .calendar-month {
        margin-bottom: 10px;
    }
    .calendar-btn {
        position: static;
        width: 100%;
        margin: 5px 0;
        top: auto;
        transform: none;
    }
    .calendar-btn#prev-month {
        order: -1;
    }
    .calendar-btn#next-month {
        order: 1;
    }
    .calendar-date {
        width: 25px;
        height: 25px;
        margin: 2px;
    }
    .calendar-dates {
        padding: 0 30px;
        padding-bottom: 5px;
    }
}
@media (min-width: 577px) and (max-width: 768px) {
    .calendar-date {
        width: 28px;
        height: 28px;
        margin: 3px;
    }
    .calendar-dates {
        padding: 0 35px;
        padding-bottom: 8px;
    }
    .calendar-slider {
        gap: 3px;
    }
}
@media (min-width: 769px) {
    .calendar-date {
        width: 30px;
        height: 30px;
        margin: 4px;
    }
    .calendar-dates {
        padding: 0 40px;
        padding-bottom: 12px;
    }
    .calendar-slider {
        gap: 5px;
    }
}
"""

# UI untuk aplikasi
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
        ),
        ui.tags.style(css_styles),
        ui.tags.script("""
            $(document).ready(function() {
                console.log('Document ready');
                $('#expand_peta').on('click', function() {
                    console.log('Expand peta clicked');
                    Shiny.setInputValue('expand_peta', true, {priority: 'event'});
                });
                $('#expand_tabel').on('click', function() {
                    console.log('Expand tabel clicked');
                    Shiny.setInputValue('expand_tabel', true, {priority: 'event'});
                });
                $(document).on('click', '#prev-month', function() {
                    console.log('Prev month clicked');
                    Shiny.setInputValue('prev_month', Date.now(), {priority: 'event'});
                });
                $(document).on('click', '#next-month', function() {
                    console.log('Next month clicked');
                    Shiny.setInputValue('next_month', Date.now(), {priority: 'event'});
                });
                $(document).on('shown.bs.modal', function() {
                    setTimeout(function() {
                        var buttons = document.querySelectorAll('button[data-dismiss="modal"], button[data-bs-dismiss="modal"]');
                        buttons.forEach(function(btn) {
                            if (btn.textContent.trim() === 'Dismiss') {
                                btn.textContent = 'Keluar';
                            }
                        });
                    }, 100);
                });
                Shiny.addCustomMessageHandler('update_visibility', function(message) {
                    console.log('Update visibility:', message);
                    if (message.element_id && message.show !== undefined) {
                        var element = document.getElementById(message.element_id);
                        if (element) {
                            if (message.show) {
                                element.classList.remove('d-none');
                            } else {
                                element.classList.add('d-none');
                            }
                        }
                    }
                });
                Shiny.addCustomMessageHandler('update_calendar', function(message) {
                    console.log('Update calendar:', message);
                    document.querySelectorAll('.calendar-date.selected').forEach(function(el) {
                        el.classList.remove('selected');
                    });
                    document.querySelectorAll('.calendar-date').forEach(function(el) {
                        if (el.onclick && el.onclick.toString().includes(message.selected_date)) {
                            el.classList.add('selected');
                        }
                    });
                });
            });
        """)
    ),
    ui.div(
        {"class": "header"},
        ui.tags.img(src="/kkp_atas.png", class_="logo", onerror="this.src='https://via.placeholder.com/80x80?text=Logo+Atas';"),
        ui.h1("Peta Prakiraan Daerah Penangkapan Ikan Nasional - PPDPI NASIONAL", class_="header-title")
    ),
    ui.div(
        {"class": "input-area"},
        ui.row(
            ui.column(
                3,
                ui.div(
                    {"class": "form-group"},
                    ui.tags.label("Pilih Area WPP NRI", class_="input-label"),
                    ui.input_select(
                        "area",
                        None,
                        choices=["571", "572", "573", "711", "712", "713", "714", "715", "716", "717", "718"],
                        selected="712",
                        width="100%"
                    )
                )
            ),
            ui.column(
                9,
                ui.div(
                    {"class": "form-group"},
                    ui.tags.label("Pilih Tanggal", class_="input-label"),
                    ui.div(
                        {"class": "date-picker"},
                        ui.output_ui("date_slider")
                    )
                )
            )
        )
    ),
    ui.div(
        {"class": "content-box"},
        ui.h3("Peta DPI", class_="content-title"),
        ui.tags.button(ui.tags.i(class_="fa fa-expand"), id="expand_peta", class_="expand-btn"),
        ui.download_button("unduh_peta", "Unduh", class_="unduh-btn"),
        ui.div({"class": "download-count"}, ui.output_text("peta_download_count")),
        ui.div(
            {"id": "peta_container"},
            # spinner
            ui.div({"id": "peta_loading", "class": "loading-spinner"}, ui.tags.i(class_="fa fa-spinner fa-spin"), " Memuat Peta..."), # Perbaikan: Tambahkan ikon spinner
            ui.div({"id": "peta_output"}, ui.output_ui("peta_content"))
        )
    ),
    ui.div(
        {"class": "content-box"},
        ui.h3("Tabel DPI", class_="content-title"),
        ui.tags.button(ui.tags.i(class_="fa fa-expand"), id="expand_tabel", class_="expand-btn"),
        ui.download_button("unduh_tabel", "Unduh", class_="unduh-btn"),
        ui.div({"class": "download-count"}, ui.output_text("tabel_download_count")),
        ui.div(
            {"id": "tabel_container"},
            # spinner
            ui.div({"id": "tabel_loading", "class": "loading-spinner"}, ui.tags.i(class_="fa fa-spinner fa-spin"), " Memuat Tabel..."), # Perbaikan: Tambahkan ikon spinner
            ui.div({"id": "tabel_output"}, ui.output_ui("tabel_content"))
        )
    ),
    ui.div(
        {"class": "footer"},
        ui.row(
            ui.column(
                8,
                ui.div(
                    {"style": "display: flex; align-items: center;"},
                    ui.tags.img(src="/kkp_bawah.png", class_="footer-logo", onerror="this.src='https://via.placeholder.com/30x30?text=Logo+Bawah';"),
                    ui.span("Peta PDPI", class_="footer-title")
                ),
                ui.p("Kementerian Kelautan dan Perikanan", class_="footer-info"),
                ui.p("Sekretariat Jenderal", class_="footer-info"),
                ui.p("Pusat Data, Statistik, dan Informasi", class_="footer-info"),
                ui.p("Jl. Medan Merdeka Timur No. 16, Jakarta Pusat", class_="footer-info"),
                ui.p("Telp. (021) 3519070 Ext. 7438 – Fax. (021) 3864293", class_="footer-info"),
                ui.p("Email: humas.kkp@kkp.go.id", class_="footer-info"),
                ui.p("Call Center KKP: 141", class_="footer-info")
            ),
            ui.column(
                4,
                ui.div(
                    {"class": "footer-social"},
                    ui.h4("Hubungi Kami"),
                    ui.div(
                        ui.tags.a(
                            ui.tags.i(class_="fa fa-circle"),
                            href="#",
                            class_="footer-social-icon"
                        ),
                        ui.tags.a(
                            ui.tags.i(class_="fa fa-facebook-f"),
                            href="#",
                            class_="footer-social-icon"
                        ),
                        ui.tags.a(
                            ui.tags.i(class_="fa fa-instagram"),
                            href="#",
                            class_="footer-social-icon"
                        ),
                        ui.tags.a(
                            ui.tags.i(class_="fa fa-youtube"),
                            href="#",
                            class_="footer-social-icon"
                        )
                    )
                )
            )
        ),
        ui.div(
            {"class": "copyright"},
            ui.p(f"© Copyright {datetime.now().year} Kementerian Kelautan dan Perikanan Republik Indonesia")
        )
    )
)

# Server logic
def server(input, output, session):
    selected_date = reactive.Value(datetime.now().date())
    current_month = reactive.Value(5)
    current_year = reactive.Value(2025)
    images = reactive.Value(None)
    download_counts = reactive.Value({"peta": {}, "tabel": {}})
    peta_loading = reactive.Value(True)
    tabel_loading = reactive.Value(True)
    peta_visible = reactive.Value(False)
    tabel_visible = reactive.Value(False)
    
    # Bagian fetch_images()
    @reactive.Effect
    @reactive.event(input.area, selected_date)
    async def fetch_images():
        area = input.area()
        date = selected_date.get()
        if not area or not date:
            logger.debug("Area atau tanggal tidak valid")
            return
        logger.debug(f"Fetching images for area: {area}, date: {date}")
        # Tampilkan loading spinner, sembunyikan output
        peta_loading.set(True)
        tabel_loading.set(True)
        peta_visible.set(False)
        tabel_visible.set(False)
        await session.send_custom_message("update_visibility", {"element_id": "peta_loading", "show": True})
        await session.send_custom_message("update_visibility", {"element_id": "tabel_loading", "show": True})
        await session.send_custom_message("update_visibility", {"element_id": "peta_output", "show": False})
        await session.send_custom_message("update_visibility", {"element_id": "tabel_output", "show": False})
        
        result = download_from_ftp(area, date)
        
        # Sembunyikan loading spinner, tampilkan output
        peta_loading.set(False)
        tabel_loading.set(False)
        peta_visible.set(True)
        tabel_visible.set(True)
        await session.send_custom_message("update_visibility", {"element_id": "peta_loading", "show": False})
        await session.send_custom_message("update_visibility", {"element_id": "tabel_loading", "show": False})
        await session.send_custom_message("update_visibility", {"element_id": "peta_output", "show": True})
        await session.send_custom_message("update_visibility", {"element_id": "tabel_output", "show": True})
        
        images.set(result)
        #logger.debug(f"Images updated: {result}")
    
    @output
    @render.ui
    @reactive.event(current_month, current_year, selected_date)
    def date_slider():
        month1 = current_month.get()
        year1 = current_year.get()
        month2 = 1 if month1 == 12 else month1 + 1
        year2 = year1 + 1 if month1 == 12 else year1
        month_names = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        logger.debug(f"Rendering date slider for month1: {month1}, year1: {year1}, month2: {month2}, year2: {year2}")
        
        # Bulan pertama
        first_day_month1 = datetime(year1, month1, 1)
        last_day_month1 = (first_day_month1 + relativedelta(months=1) - timedelta(days=1))
        weekday_start_month1 = first_day_month1.weekday() + 1
        days_in_month1 = last_day_month1.day
        
        # Bulan kedua
        first_day_month2 = datetime(year2, month2, 1)
        last_day_month2 = (first_day_month2 + relativedelta(months=1) - timedelta(days=1))
        weekday_start_month2 = first_day_month2.weekday() + 1
        days_in_month2 = last_day_month2.day
        
        # Tanggal bulan pertama
        month1_dates = []
        for day in range(1, days_in_month1 + 1):
            date = datetime(year1, month1, day).date()
            is_today = date == datetime.now().date()
            is_selected = date == selected_date.get()
            classes = "calendar-date"
            if is_selected:
                classes += " selected"
            if is_today:
                classes += " today"
            month1_dates.append(
                ui.tags.div(
                    {"class": classes, "onclick": f"Shiny.setInputValue('select_date', '{date.strftime('%Y-%m-%d')}', {{priority: 'event'}});"},
                    str(day)
                )
            )
        month1_dates = [ui.tags.div({"class": "calendar-date", "style": "visibility: hidden;"}) for _ in range(weekday_start_month1 - 1)] + month1_dates
        
        # Tanggal bulan kedua
        month2_dates = []
        for day in range(1, days_in_month2 + 1):
            date = datetime(year2, month2, day).date()
            is_today = date == datetime.now().date()
            is_selected = date == selected_date.get()
            classes = "calendar-date"
            if is_selected:
                classes += " selected"
            if is_today:
                classes += " today"
            month2_dates.append(
                ui.tags.div(
                    {"class": classes, "onclick": f"Shiny.setInputValue('select_date', '{date.strftime('%Y-%m-%d')}', {{priority: 'event'}});"},
                    str(day)
                )
            )
        month2_dates = [ui.tags.div({"class": "calendar-date", "style": "visibility: hidden;"}) for _ in range(weekday_start_month2 - 1)] + month2_dates
        
        return ui.div(
            {"class": "calendar-container"},
            ui.tags.button(
                ui.tags.i({"class": "fa fa-chevron-left"}),
                id="prev-month",
                class_="calendar-btn"
            ),
            ui.div(
                {"id": "calendar-slider", "class": "calendar-slider"},
                ui.div(
                    {"class": "calendar-month", "id": f"month-{month1}-{year1}"},
                    ui.tags.div({"class": "calendar-title"}, f"{month_names[month1-1]} {year1}"),
                    ui.tags.div({"class": "calendar-dates", "id": f"dates-{month1}-{year1}"}, month1_dates)
                ),
                ui.div(
                    {"class": "calendar-month", "id": f"month-{month2}-{year2}"},
                    ui.tags.div({"class": "calendar-title"}, f"{month_names[month2-1]} {year2}"),
                    ui.tags.div({"class": "calendar-dates", "id": f"dates-{month2}-{year2}"}, month2_dates)
                )
            ),
            ui.tags.button(
                ui.tags.i({"class": "fa fa-chevron-right"}),
                id="next-month",
                class_="calendar-btn"
            )
        )
    
    # Bagian tombol prev - next month
    @reactive.Effect
    @reactive.event(input.prev_month)
    async def prev_month():
        logger.debug(f"Tombol prev_month diklik, input.prev_month: {input.prev_month()}")
        month = current_month.get()
        year = current_year.get()
        if month is None or year is None:
            logger.error("Nilai month atau year tidak valid")
            return
        if month == 1:
            current_month.set(12)
            current_year.set(year - 1)
        else:
            current_month.set(month - 1)
        logger.debug(f"Updated to month: {current_month.get()}, year: {current_year.get()}")
        await session.send_custom_message("update_calendar", {
            "selected_date": selected_date.get().strftime("%Y-%m-%d"),
            "month": current_month.get(),
            "year": current_year.get()
        })

    @reactive.Effect
    @reactive.event(input.next_month)
    async def next_month():
        logger.debug(f"Tombol next_month diklik, input.next_month: {input.next_month()}")
        month = current_month.get()
        year = current_year.get()
        if month is None or year is None:
            logger.error("Nilai month atau year tidak valid")
            return
        if month == 12:
            current_month.set(1)
            current_year.set(year + 1)
        else:
            current_month.set(month + 1)
        logger.debug(f"Updated to month: {current_month.get()}, year: {current_year.get()}")
        await session.send_custom_message("update_calendar", {
            "selected_date": selected_date.get().strftime("%Y-%m-%d"),
            "month": current_month.get(),
            "year": current_year.get()
        })
    
    # Bagian update_selected_date()
    @reactive.Effect
    @reactive.event(input.select_date)
    async def update_selected_date():
        logger.debug(f"Tanggal dipilih: {input.select_date()}")
        selected_date.set(datetime.strptime(input.select_date(), "%Y-%m-%d").date())
        await session.send_custom_message("update_calendar", {
            "selected_date": input.select_date()
        })
    
    @output
    @render.ui
    def peta_content():
        img_data = images.get()
        logger.debug(f"Rendering peta_content, img_data['peta']: {img_data['peta'] if img_data else None}")
        if img_data and img_data["peta"] and os.path.exists(img_data["peta"]):
            with open(img_data["peta"], "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode()
            return ui.tags.img(
                {"src": f"data:image/png;base64,{img_base64}", "style": "max-width:100%; max-height:600px; display: block; margin: 0 auto;"}
            )
        else:
            error_message = img_data["error"] if img_data and img_data["error"] else None
            return ui.div(
                {"class": "placeholder-text"},
                ui.p(f"Nama file: peta_dpi_{input.area()}_{selected_date.get().strftime('%Y%m%d')}.png"),
                ui.p("File tidak ditemukan atau terjadi kesalahan dalam mengambil file."),
                ui.p(error_message) if error_message else None
            )
    
    @output
    @render.ui
    def tabel_content():
        img_data = images.get()
        logger.debug(f"Rendering tabel_content, img_data['tabel']: {img_data['tabel'] if img_data else None}")
        if img_data and img_data["tabel"] and os.path.exists(img_data["tabel"]):
            with open(img_data["tabel"], "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode()
            return ui.tags.img(
                {"src": f"data:image/png;base64,{img_base64}", "style": "max-width:100%; max-height:600px; display: block; margin: 0 auto;"}
            )
        else:
            error_message = img_data["error"] if img_data and img_data["error"] else None
            return ui.div(
                {"class": "placeholder-text"},
                ui.p(f"Nama file: tabel_dpi_{input.area()}_{selected_date.get().strftime('%Y%m%d')}.png"),
                ui.p("File tidak ditemukan atau terjadi kesalahan dalam mengambil file."),
                ui.p(error_message) if error_message else None
            )
    
    @output
    @render.download(filename=lambda: f"peta_dpi_{input.area()}_{selected_date.get().strftime('%Y%m%d')}.png")
    def unduh_peta():
        img_data = images.get()
        logger.debug(f"Tombol unduh_peta diklik, img_data['peta']: {img_data['peta'] if img_data else None}")
        if img_data and img_data["peta"] and os.path.exists(img_data["peta"]):
            key = f"{input.area()}_{selected_date.get().strftime('%Y%m%d')}"
            counts = download_counts.get()
            counts["peta"][key] = counts["peta"].get(key, 0) + 1
            download_counts.set(counts)
            logger.debug(f"Jumlah unduhan peta untuk {key}: {counts['peta'][key]}")
            with open(img_data["peta"], "rb") as f:
                yield f.read()
        else:
            ui.notification_show("File peta tidak ditemukan untuk diunduh", type="error")
            logger.error("Gagal mengunduh peta: File tidak ditemukan")
    
    @output
    @render.download(filename=lambda: f"tabel_dpi_{input.area()}_{selected_date.get().strftime('%Y%m%d')}.png")
    def unduh_tabel():
        img_data = images.get()
        logger.debug(f"Tombol unduh_tabel diklik, img_data['tabel']: {img_data['tabel'] if img_data else None}")
        if img_data and img_data["tabel"] and os.path.exists(img_data["tabel"]):
            key = f"{input.area()}_{selected_date.get().strftime('%Y%m%d')}"
            counts = download_counts.get()
            counts["tabel"][key] = counts["tabel"].get(key, 0) + 1
            download_counts.set(counts)
            logger.debug(f"Jumlah unduhan tabel untuk {key}: {counts['tabel'][key]}")
            with open(img_data["tabel"], "rb") as f:
                yield f.read()
        else:
            ui.notification_show("File tabel tidak ditemukan untuk diunduh", type="error")
            logger.error("Gagal mengunduh tabel: File tidak ditemukan")
    
    @output
    @render.text
    def peta_download_count():
        key = f"{input.area()}_{selected_date.get().strftime('%Y%m%d')}"
        count = download_counts.get()["peta"].get(key, 0)
        logger.debug(f"Menampilkan jumlah unduhan peta untuk {key}: {count}")
        return f"Jumlah Unduhan: {count}"
    
    @output
    @render.text
    def tabel_download_count():
        key = f"{input.area()}_{selected_date.get().strftime('%Y%m%d')}"
        count = download_counts.get()["tabel"].get(key, 0)
        logger.debug(f"Menampilkan jumlah unduhan tabel untuk {key}: {count}")
        return f"Jumlah Unduhan: {count}"
    
    
    @reactive.Effect
    @reactive.event(input.expand_peta)
    def expand_peta():
        img_data = images.get()
        
        logger.debug(f"Tombol expand peta diklik, img_data: {img_data}")
        
        # Perbaikan
        has_valid_image = (img_data is not None and 
                        img_data.get("peta") is not None and 
                        os.path.exists(img_data.get("peta", "")))
        
        logger.debug(f"File peta valid: {has_valid_image}")
        
        if has_valid_image:
            try:
                with open(img_data["peta"], 'rb') as f:
                    img_base64 = base64.b64encode(f.read()).decode()
                
                content = ui.div(
                    {"style": "width:100%; text-align:center;"},
                    ui.tags.img(
                        {"src": f"data:image/png;base64,{img_base64}", 
                        "style": "max-width:100%; max-height:700px;"}
                    )
                )
            except Exception as e:
                logger.error(f"Error saat membuka file peta: {str(e)}")
                content = ui.div(
                    {"class": "placeholder-text"},
                    ui.p(f"Terjadi kesalahan saat membuka file peta: {str(e)}"),
                    ui.p("Silakan coba lagi dalam beberapa saat.")
                )
        else:
            content = ui.div(
                {"class": "placeholder-text"},
                ui.p(f"File peta untuk area {input.area()} tanggal {selected_date.get().strftime('%d-%m-%Y')} tidak ditemukan"),
                ui.p("Pastikan file tersedia di server FTP atau periksa koneksi.")
            )
        
        ui.modal_show(
            ui.modal(
                content,
                title="Peta DPI (Diperbesar)",
                size="l",
                easy_close=True
            )
        )

    
    @reactive.Effect
    @reactive.event(input.expand_tabel)
    def expand_tabel():
        img_data = images.get()
        
        logger.debug(f"Tombol expand tabel diklik, img_data: {img_data}")
        
        # Perbaikan
        has_valid_image = (img_data is not None and 
                        img_data.get("tabel") is not None and 
                        os.path.exists(img_data.get("tabel", "")))
        
        logger.debug(f"File tabel valid: {has_valid_image}")
        
        if has_valid_image:
            try:
                with open(img_data["tabel"], 'rb') as f:
                    img_base64 = base64.b64encode(f.read()).decode()
                
                content = ui.div(
                    {"style": "width:100%; text-align:center;"},
                    ui.tags.img(
                        {"src": f"data:image/png;base64,{img_base64}", 
                        "style": "max-width:100%; max-height:700px;"}
                    )
                )
            except Exception as e:
                logger.error(f"Error saat membuka file tabel: {str(e)}")
                content = ui.div(
                    {"class": "placeholder-text"},
                    ui.p(f"Terjadi kesalahan saat membuka file tabel: {str(e)}"),
                    ui.p("Silakan coba lagi dalam beberapa saat.")
                )
        else:
            content = ui.div(
                {"class": "placeholder-text"},
                ui.p(f"File tabel untuk area {input.area()} tanggal {selected_date.get().strftime('%d-%m-%Y')} tidak ditemukan"),
                ui.p("Pastikan file tersedia di server FTP atau periksa koneksi.")
            )
        
        ui.modal_show(
            ui.modal(
                content,
                title="Tabel DPI (Diperbesar)",
                size="l",
                easy_close=True
            )
        )
    
    # Bagian initialize_visibility()
    @reactive.Effect
    async def initialize_visibility():
        logger.debug("Initializing visibility")
        peta_loading.set(True)
        tabel_loading.set(True)
        peta_visible.set(False)
        tabel_visible.set(False)
        await session.send_custom_message("update_visibility", {"element_id": "peta_loading", "show": True})
        await session.send_custom_message("update_visibility", {"element_id": "tabel_loading", "show": True})
        await session.send_custom_message("update_visibility", {"element_id": "peta_output", "show": False})
        await session.send_custom_message("update_visibility", {"element_id": "tabel_output", "show": False})

# Run the application
app = App(app_ui, server, static_assets=os.path.join(os.path.dirname(__file__), "www"))

if __name__ == "__main__":
    logger.debug("Starting application")
    app.run()
