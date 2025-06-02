library(shiny)
library(shinydashboard)
library(lubridate)
library(RCurl)
library(httr)
library(curl)
library(rvest)
library(dplyr)
library(shinyWidgets)
library(DT)
library(shinyjs)
library(base64enc)

# Fungsi untuk mengambil file dari FTP server
downloadFromFTP <- function(area, selected_date) {
  date_str <- format(selected_date, "%Y%m%d")
  ftp_url <- "isisendiri"
  username <- "isisendiri"
  password <- "isisendiri"
  base_path <- "/sidik/dpi_oto/dpi_ops_peta/2025"
  peta_filename <- paste0("peta_dpi_", area, "_", date_str, ".png")
  tabel_filename <- paste0("tabel_dpi_", area, "_", date_str, ".png")
  peta_path <- paste0(base_path, "/", peta_filename)
  tabel_path <- paste0(base_path, "/", tabel_filename)
  peta_url <- paste0(ftp_url, peta_path)
  tabel_url <- paste0(ftp_url, tabel_path)
  cat("Mengunduh peta dari:", peta_url, "\n")
  cat("Mengunduh tabel dari:", tabel_url, "\n")
  temp_dir <- file.path(tempdir(), "dpi_images")
  if (dir.exists(temp_dir)) {
    unlink(temp_dir, recursive = TRUE)
  }
  dir.create(temp_dir, recursive = TRUE)
  local_peta_path <- file.path(temp_dir, peta_filename)
  local_tabel_path <- file.path(temp_dir, tabel_filename)
  tryCatch({
    curl_download(
      url = peta_url,
      destfile = local_peta_path,
      handle = new_handle(
        username = username,
        password = password,
        ftp_use_epsv = FALSE,
        connecttimeout = 30,
        timeout = 60
      )
    )
    cat("Peta berhasil diunduh ke:", local_peta_path, "\n")
    curl_download(
      url = tabel_url,
      destfile = local_tabel_path,
      handle = new_handle(
        username = username,
        password = password,
        ftp_use_epsv = FALSE,
        connecttimeout = 30,
        timeout = 60
      )
    )
    cat("Tabel berhasil diunduh ke:", local_tabel_path, "\n")
    return(list(
      peta = local_peta_path,
      tabel = local_tabel_path
    ))
  }, error = function(e) {
    cat("Error saat mengunduh file:", e$message, "\n")
    return(list(
      peta = NULL,
      tabel = NULL,
      error = paste("Error downloading files:", e$message)
    ))
  })
}

# UI untuk aplikasi
ui <- fluidPage(
  useShinyjs(),
  tags$head(
    tags$style(HTML("
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
        text-align: center;
        padding-top: 80px;
        color: #666;
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
      @media (max-width: 576px) {
        .calendar-slider {
          flex-direction: column;
          gap: 5;
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
          gap: rehab5px;
        }
      }
    "))
  ),
  div(class = "header",
      tags$img(src = "kkp_atas.png", class = "logo"),
      h1("Peta Prakiraan Daerah Penangkapan Ikan Nasional - PPDPI NASIONAL", class = "header-title")
  ),
  div(class = "input-area",
      fluidRow(
        column(width = 3,
               div(class = "form-group",
                   tags$label("Pilih Area WPP NRI", class = "input-label"),
                   selectInput("area", NULL, 
                              choices = c("571", "572", "573", "711", "712", "713", "714", "715", "716", "717", "718"), 
                              selected = "712",
                              width = "100%")
               )
        ),
        column(width = 9,
               div(class = "form-group",
                   tags$label("Pilih Tanggal", class = "input-label"),
                   div(class = "date-picker",
                       uiOutput("dateSlider")
                   )
               )
        )
      )
  ),
  div(class = "content-box",
      h3("Peta DPI", class = "content-title"),
      tags$button(icon("expand"), class = "expand-btn", id = "expand_peta"),
      downloadButton("unduh_peta", "Unduh", class = "unduh-btn"),
      div(class = "download-count", textOutput("peta_download_count")),
      div(id = "peta_container",
          div(id = "peta_loading", class = "loading-spinner", 
              tags$i(class = "fa fa-spinner fa-spin fa-3x"),
              tags$p("Memuat data...")
          ),
          uiOutput("petaOutput")
      )
  ),
  div(class = "content-box",
      h3("Tabel DPI", class = "content-title"),
      tags$button(icon("expand"), class = "expand-btn", id = "expand_tabel"),
      downloadButton("unduh_tabel", "Unduh", class = "unduh-btn"),
      div(class = "download-count", textOutput("tabel_download_count")),
      div(id = "tabel_container",
          div(id = "tabel_loading", class = "loading-spinner", 
              tags$i(class = "fa fa-spinner fa-spin fa-3x"),
              tags$p("Memuat data...")
          ),
          uiOutput("tabelOutput")
      )
  ),
  div(class = "footer",
      fluidRow(
        column(width = 8,
               div(style = "display: flex; align-items: center;",
                   tags$img(src = "kkp_bawah.png", class = "footer-logo"),
                   span("Peta PDPI", class = "footer-title")
               ),
               p("Kementerian Kelautan dan Perikanan", class = "footer-info"),
               p("Sekretariat Jenderal", class = "footer-info"),
               p("Pusat Data, Statistik, dan Informasi", class = "footer-info"),
               p("Jl. Medan Merdeka Timur No. 16, Jakarta Pusat", class = "footer-info"),
               p("Telp. (021) 3519070 Ext. 7438 – Fax. (021) 3864293", class = "footer-info"),
               p("Email: humas.kkp@kkp.go.id", class = "footer-info"),
               p("Call Center KKP: 141", class = "footer-info")
        ),
        column(width = 4,
               div(class = "footer-social",
                   h4("Hubungi Kami"),
                   div(
                     tags$a(href = "#", icon("circle"), class = "footer-social-icon"),
                     tags$a(href = "#", icon("facebook-f"), class = "footer-social-icon"),
                     tags$a(href = "#", icon("instagram"), class = "footer-social-icon"),
                     tags$a(href = "#", icon("youtube"), class = "footer-social-icon")
                   )
               )
        )
      ),
      div(class = "copyright",
          p(paste("© Copyright", format(Sys.Date(), "%Y"), "Kementerian Kelautan dan Perikanan Republik Indonesia"))
      )
  )
)

# Server logic
server <- function(input, output, session) {
  selected_date <- reactiveVal(Sys.Date())
  current_month <- reactiveVal(5)
  current_year <- reactiveVal(2025)
  images <- reactiveVal(NULL)
  
  # Variabel reaktif untuk menyimpan jumlah unduhan per kombinasi area dan tanggal
  download_counts <- reactiveVal(list(peta = list(), tabel = list()))
  
  fetchImages <- reactive({
    req(input$area)
    req(selected_date())
    shinyjs::hide(" прослушать petaOutput")
    shinyjs::hide("tabelOutput")
    shinyjs::show("peta_loading")
    shinyjs::show("tabel_loading")
    result <- downloadFromFTP(input$area, selected_date())
    shinyjs::hide("peta_loading")
    shinyjs::hide("tabel_loading")
    shinyjs::show("petaOutput")
    shinyjs::show("tabelOutput")
    return(result)
  })
  
  output$dateSlider <- renderUI({
    month1 <- current_month()
    year1 <- current_year()
    if (month1 == 12) {
      month2 <- 1
      year2 <- year1 + 1
    } else {
      month2 <- month1 + 1
      year2 <- year1
    }
    month_names <- c("Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember")
    first_day_month1 <- as.Date(paste(year1, month1, "01", sep = "-"))
    last_day_month1 <- ceiling_date(first_day_month1, "month") - days(1)
    weekday_start_month1 <- as.numeric(format(first_day_month1, "%u"))
    days_in_month1 <- as.numeric(format(last_day_month1, "%d"))
    first_day_month2 <- as.Date(paste(year2, month2, "01", sep = "-"))
    last_day_month2 <- ceiling_date(first_day_month2, "month") - days(1)
    weekday_start_month2 <- as.numeric(format(first_day_month2, "%u"))
    days_in_month2 <- as.numeric(format(last_day_month2, "%d"))
    month1_dates <- lapply(1:days_in_month1, function(day) {
      date <- as.Date(paste(year1, month1, day, sep = "-"))
      is_today <- date == Sys.Date()
      is_selected <- date == selected_date()
      classes <- "calendar-date"
      if (is_selected) {
        classes <- paste(classes, "selected")
      }
      if (is_today) {
        classes <- paste(classes, "today")
      }
      onclick_js <- sprintf(
        "Shiny.setInputValue('select_date', '%s', {priority: 'event'});",
        format(date, "%Y-%m-%d")
      )
      tags$div(
        class = classes,
        onclick = onclick_js,
        day
      )
    })
    month1_dates <- c(
      lapply(1:(weekday_start_month1 - 1), function(x) {
        tags$div(class = "calendar-date", "")
      }),
      month1_dates
    )
    month2_dates <- lapply(1:days_in_month2, function(day) {
      date <- as.Date(paste(year2, month2, day, sep = "-"))
      is_today <- date == Sys.Date()
      is_selected <- date == selected_date()
      classes <- "calendar-date"
      if (is_selected) {
        classes <- paste(classes, "selected")
      }
      if (is_today) {
        classes <- paste(classes, "today")
      }
      onclick_js <- sprintf(
        "Shiny.setInputValue('select_date', '%s', {priority: 'event'});",
        format(date, "%Y-%m-%d")
      )
      tags$div(
        class = classes,
        onclick = onclick_js,
        day
      )
    })
    month2_dates <- c(
      lapply(1:(weekday_start_month2 - 1), function(x) {
        tags$div(class = "calendar-date", "")
      }),
      month2_dates
    )
    tagList(
      div(class = "calendar-container",
          tags$button(icon("chevron-left"), id = "prev-month", class = "calendar-btn",
                    onclick = "Shiny.setInputValue('prev_month', true, {priority: 'event'})"),
          div(id = "calendar-slider", class = "calendar-slider",
              div(class = "calendar-month", id = paste0("month-", month1, "-", year1),
                  tags$div(class = "calendar-title", paste(month_names[month1], year1)),
                  tags$div(class = "calendar-dates", id = paste0("dates-", month1, "-", year1),
                           month1_dates
                  )
              ),
              div(class = "calendar-month", id = paste0("month-", month2, "-", year2),
                  tags$div(class = "calendar-title", paste(month_names[month2], year2)),
                  tags$div(class = "calendar-dates", id = paste0("dates-", month2, "-", year2),
                           month2_dates
                  )
              )
          ),
          tags$button(icon("chevron-right"), id = "next-month", class = "calendar-btn",
                    onclick = "Shiny.setInputValue('next_month', true, {priority: 'event'})")
      )
    )
  })
  
  observeEvent(input$prev_month, {
    month <- current_month()
    year <- current_year()
    if (month == 1) {
      current_month(12)
      current_year(year - 1)
    } else {
      current_month(month - 1)
    }
  })
  
  observeEvent(input$next_month, {
    month <- current_month()
    year <- current_year()
    if (month == 12) {
      current_month(1)
      current_year(year + 1)
    } else {
      current_month(month + 1)
    }
  })
  
  observeEvent(input$select_date, {
    selected_date(as.Date(input$select_date))
    images(fetchImages())
    shinyjs::runjs(sprintf("
      document.querySelectorAll('.calendar-date.selected').forEach(function(el) {
        el.classList.remove('selected');
      });
      document.querySelectorAll('.calendar-date').forEach(function(el) {
        if (el.onclick && el.onclick.toString().includes('%s')) {
          el.classList.add('selected');
        }
      });
    ", input$select_date))
  })
  
  observeEvent(input$area, {
    images(fetchImages())
  })
  
  output$petaOutput <- renderUI({
    req(images())
    if (!is.null(images()$peta) && file.exists(images()$peta)) {
      img_base64 <- base64encode(images()$peta)
      div(
        style = "width:100%; text-align:center;",
        tags$img(
          src = paste0("data:image/png;base64,", img_base64),
          style = "max-width:100%; max-height:600px;"
        )
      )
    } else {
      error_message <- if (!is.null(images()$error)) images()$error else NULL
      tagList(
        div(
          class = "placeholder-text",
          p(paste0("Nama file: peta_dpi_", input$area, "_", format(selected_date(), "%Y%m%d"), ".png")),
          p("File tidak ditemukan atau terjadi kesalahan dalam mengambil file.")
        ),
        if (!is.null(error_message)) div(p(error_message))
      )
    }
  })
  
  output$tabelOutput <- renderUI({
    req(images())
    if (!is.null(images()$tabel) && file.exists(images()$tabel)) {
      img_base64 <- base64encode(images()$tabel)
      div(
        style = "width:100%; text-align:center;",
        tags$img(
          src = paste0("data:image/png;base64,", img_base64),
          style = "max-width:100%; max-height:600px;"
        )
      )
    } else {
      error_message <- if (!is.null(images()$error)) images()$error else NULL
      tagList(
        div(
          class = "placeholder-text",
          p(paste0("Nama file: tabel_dpi_", input$area, "_", format(selected_date(), "%Y%m%d"), ".png")),
          p("File tidak ditemukan atau terjadi kesalahan dalam mengambil file.")
        ),
        if (!is.null(error_message)) div(p(error_message))
      )
    }
  })
  
  output$unduh_peta <- downloadHandler(
    filename = function() {
      paste0("peta_dpi_", input$area, "_", format(selected_date(), "%Y%m%d"), ".png")
    },
    content = function(file) {
      if (!is.null(images()$peta) && file.exists(images()$peta)) {
        file.copy(images()$peta, file)
        # Perbarui jumlah unduhan untuk kombinasi area dan tanggal
        key <- paste0(input$area, "_", format(selected_date(), "%Y%m%d"))
        counts <- download_counts()
        counts$peta[[key]] <- if (is.null(counts$peta[[key]])) 1 else counts$peta[[key]] + 1
        download_counts(counts)
      } else {
        showNotification("File tidak ditemukan", type = "error")
      }
    }
  )
  
  output$unduh_tabel <- downloadHandler(
    filename = function() {
      paste0("tabel_dpi_", input$area, "_", format(selected_date(), "%Y%m%d"), ".png")
    },
    content = function(file) {
      if (!is.null(images()$tabel) && file.exists(images()$tabel)) {
        file.copy(images()$tabel, file)
        # Perbarui jumlah unduhan untuk kombinasi area dan tanggal
        key <- paste0(input$area, "_", format(selected_date(), "%Y%m%d"))
        counts <- download_counts()
        counts$tabel[[key]] <- if (is.null(counts$tabel[[key]])) 1 else counts$tabel[[key]] + 1
        download_counts(counts)
      } else {
        showNotification("File tidak ditemukan", type = "error")
      }
    }
  )
  
  output$peta_download_count <- renderText({
    key <- paste0(input$area, "_", format(selected_date(), "%Y%m%d"))
    count <- download_counts()$peta[[key]]
    paste("Jumlah Unduhan:", ifelse(is.null(count), 0, count))
  })
  
  output$tabel_download_count <- renderText({
    key <- paste0(input$area, "_", format(selected_date(), "%Y%m%d"))
    count <- download_counts()$tabel[[key]]
    paste("Jumlah Unduhan:", ifelse(is.null(count), 0, count))
  })
  
  observe({
    shinyjs::runjs("
      $('#expand_peta').on('click', function() {
        Shiny.setInputValue('expand_peta', true, {priority: 'event'});
      });
      $('#expand_tabel').on('click', function() {
        Shiny.setInputValue('expand_tabel', true, {priority: 'event'});
      });
    ")
  })
  
  observeEvent(input$expand_peta, {
    peta_status <- if (!is.null(images()$peta)) images()$peta else "NULL"
    peta_exists <- if (!is.null(images()$peta)) file.exists(images()$peta) else FALSE
    cat("Tombol expand peta diklik\n")
    cat("Status images()$peta:", peta_status, "\n")
    cat("File exists:", peta_exists, "\n")
    showModal(modalDialog(
      title = "Peta DPI (Diperbesar)",
      if (!is.null(images()$peta) && file.exists(images()$peta)) {
        img_base64 <- base64encode(images()$peta)
        div(
          style = "width:100%; text-align:center;",
          tags$img(
            src = paste0("data:image/png;base64,", img_base64),
            style = "max-width:100%; max-height:700px;"
          )
        )
      } else {
        div(
          class = "placeholder-text",
          p("File peta tidak ditemukan"),
          p("Pastikan file tersedia di server FTP atau periksa koneksi.")
        )
      },
      size = "l",
      easyClose = TRUE
    ))
    shinyjs::runjs("
      setTimeout(function() {
        var buttons = document.querySelectorAll('button[data-dismiss=\"modal\"], button[data-bs-dismiss=\"modal\"]');
        buttons.forEach(function(btn) {
          if (btn.textContent.trim() === 'Dismiss') {
            btn.textContent = 'Keluar';
          }
        });
      }, 100);
    ")
  })
  
  observeEvent(input$expand_tabel, {
    tabel_status <- if (!is.null(images()$tabel)) images()$tabel else "NULL"
    tabel_exists <- if (!is.null(images()$tabel)) file.exists(images()$tabel) else FALSE
    cat("Tombol expand tabel diklik\n")
    cat("Status images()$tabel:", tabel_status, "\n")
    cat("File exists:", tabel_exists, "\n")
    showModal(modalDialog(
      title = "Tabel DPI (Diperbesar)",
      if (!is.null(images()$tabel) && file.exists(images()$tabel)) {
        img_base64 <- base64encode(images()$tabel)
        div(
          style = "width:100%; text-align:center;",
          tags$img(
            src = paste0("data:image/png;base64,", img_base64),
            style = "max-width:100%; max-height:700px;"
          )
        )
      } else {
        div(
          class = "placeholder-text",
          p("File tabel tidak ditemukan"),
          p("Pastikan file tersedia di server FTP atau periksa koneksi.")
        )
      },
      size = "l",
      easyClose = TRUE
    ))
    shinyjs::runjs("
      setTimeout(function() {
        var buttons = document.querySelectorAll('button[data-dismiss=\"modal\"], button[data-bs-dismiss=\"modal\"]');
        buttons.forEach(function(btn) {
          if (btn.textContent.trim() === 'Dismiss') {
            btn.textContent = 'Keluar';
          }
        });
      }, 100);
    ")
  })
  
  observe({
    shinyjs::hide("peta_loading")
    shinyjs::hide("tabel_loading")
    images(fetchImages())
  })
}

# Run the application
shinyApp(ui = ui, server = server)