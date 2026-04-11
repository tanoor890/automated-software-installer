#!/usr/bin/env python3
from fpdf import FPDF
import os

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CSE324_Presentation_Guide.pdf")


def safe(text):
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u00a0": " ",
        "\u2022": "-", "\u25cf": "-", "\u2023": ">", "\u00b7": ".",
        "\u2192": "->", "\u2190": "<-", "\u2194": "<->",
        "\u2265": ">=", "\u2264": "<=", "\u2260": "!=",
        "\t": "    ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


class PresentationPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self._toc_entries = []

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "CSE 324 - Automated Software Installation Server - Presentation Guide", align="C")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_toc_entry(self, title, level=0):
        self._toc_entries.append((title, self.page_no(), level))

    def section_title(self, title, size=16):
        self.set_font("Helvetica", "B", size)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, size * 0.55, safe(title))
        self.ln(3)
        self.set_draw_color(20, 60, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def sub_title(self, title, size=13):
        self.set_font("Helvetica", "B", size)
        self.set_text_color(40, 90, 160)
        self.multi_cell(0, size * 0.55, safe(title))
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def sub_sub_title(self, title, size=11):
        self.set_font("Helvetica", "B", size)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, size * 0.5, safe(title))
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def body_text(self, text, size=10):
        self.set_font("Helvetica", "", size)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, size * 0.55, safe(text))
        self.ln(2)

    def bold_text(self, text, size=10):
        self.set_font("Helvetica", "B", size)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, size * 0.55, safe(text))
        self.ln(1)

    def bullet(self, text, size=10, indent=10):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "B", size)
        self.cell(5, size * 0.55, "-")
        self.set_font("Helvetica", "", size)
        self.multi_cell(0, size * 0.55, safe(text))
        self.ln(1)

    def numbered_item(self, num, text, size=10, indent=5):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "B", size)
        self.cell(8, size * 0.55, f"{num}.")
        self.set_font("Helvetica", "", size)
        self.multi_cell(0, size * 0.55, safe(text))
        self.ln(1)

    def code_block(self, code, title=None, font_size=7):
        if title:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(255, 255, 255)
            self.set_fill_color(50, 50, 50)
            self.cell(0, 6, f"  {safe(title)}", fill=True, new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(0, 0, 0)

        self.set_font("Courier", "", font_size)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(20, 20, 20)
        line_h = font_size * 0.45
        max_width = self.w - self.l_margin - self.r_margin

        for line in code.split("\n"):
            line = safe(line)
            if len(line) > 105:
                line = line[:102] + "..."
            if self.get_y() + line_h + 2 > self.h - self.b_margin:
                self.add_page()
                if title:
                    self.set_font("Helvetica", "I", 7)
                    self.set_text_color(120, 120, 120)
                    self.cell(0, 4, f"  (continued: {safe(title)})", new_x="LMARGIN", new_y="NEXT")
                    self.set_font("Courier", "", font_size)
                    self.set_text_color(20, 20, 20)
                    self.set_fill_color(240, 240, 240)
            self.cell(max_width, line_h, " " + line, fill=True, new_x="LMARGIN", new_y="NEXT")

        self.ln(3)
        self.set_text_color(0, 0, 0)

    def qa_pair(self, q_num, question, answer):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(180, 40, 40)
        self.multi_cell(0, 5.5, safe(f"Q{q_num}: {question}"))
        self.ln(1)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 80, 0)
        self.multi_cell(0, 5.5, safe(f"A: {answer}"))
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def check_space(self, needed=30):
        if self.get_y() + needed > self.h - self.b_margin:
            self.add_page()

    def table_row(self, cells, widths, bold=False, fill=False):
        h = 7
        style = "B" if bold else ""
        if fill:
            self.set_fill_color(220, 230, 245)
        x_start = self.get_x()
        max_lines = 1
        for i, cell_text in enumerate(cells):
            self.set_font("Helvetica", style, 9)
            text_w = self.get_string_width(safe(cell_text)) + 4
            lines = max(1, int(text_w / widths[i]) + 1)
            max_lines = max(max_lines, lines)
        row_h = h * max_lines
        if self.get_y() + row_h > self.h - self.b_margin:
            self.add_page()
        for i, cell_text in enumerate(cells):
            x = x_start + sum(widths[:i])
            self.set_xy(x, self.get_y())
            self.set_font("Helvetica", style, 9)
            self.cell(widths[i], row_h, safe(cell_text), border=1, fill=fill)
        self.ln(row_h)


def build_title_page(pdf):
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 14, "Automated Software", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 14, "Installation Server", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.set_draw_color(20, 60, 120)
    pdf.set_line_width(0.8)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, "Group Presentation Preparation Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(40, 90, 160)
    pdf.cell(0, 10, "CSE 324 - Operating Systems Lab", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    members = [
        ("Md. Al Shahariar Shuvo", "232-15-097", "Project Leader & System Architect"),
        ("Abdullah Al Maruf", "232-15-180", "Server-Side Developer"),
        ("Sibgatullah Mahi", "232-15-015", "Client-Side Developer"),
        ("Reyaid Bin Alam Utsho", "232-15-508", "Network & Socket Programmer"),
        ("Ikramul Hasan Jowel", "232-15-819", "Testing & Documentation Engineer"),
    ]
    for name, sid, role in members:
        pdf.cell(0, 7, f"{name} ({sid}) - {role}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 90, 160)
    pdf.cell(0, 7, "GitHub: https://github.com/tanoor890/automated-software-installer", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 7, "Daffodil International University", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Department of Computer Science and Engineering", align="C", new_x="LMARGIN", new_y="NEXT")


def build_toc(pdf):
    pdf.add_page()
    pdf.add_toc_entry("Table of Contents")
    pdf.section_title("Table of Contents", 20)
    pdf.ln(5)

    toc_items = [
        (0, "1. Project Setup Guide (Oracle VM Linux)"),
        (0, "2. Person 1 - Md. Al Shahariar Shuvo (System Architect)"),
        (1, "   Code: protocol.h, utils.c, utils.h, Makefile"),
        (1, "   Code Explanation & Talking Points"),
        (1, "   Expected Questions & Answers"),
        (0, "3. Person 2 - Abdullah Al Maruf (Server-Side Developer)"),
        (1, "   Code: server.c, server_gui.c"),
        (1, "   Code Explanation & Talking Points"),
        (1, "   Expected Questions & Answers"),
        (0, "4. Person 3 - Sibgatullah Mahi (Client-Side Developer)"),
        (1, "   Code: client.c, client.h, client_gui.c"),
        (1, "   Code Explanation & Talking Points"),
        (1, "   Expected Questions & Answers"),
        (0, "5. Person 4 - Reyaid Bin Alam Utsho (Network & Socket Programmer)"),
        (1, "   Code: file_handler.c, file_handler.h, downloader.c, downloader.h"),
        (1, "   Code Explanation & Talking Points"),
        (1, "   Expected Questions & Answers"),
        (0, "6. Person 5 - Ikramul Hasan Jowel (Testing & Documentation)"),
        (1, "   Code: package_manager.c, package_manager.h, installer.c, installer.h"),
        (1, "   Code Explanation & Talking Points"),
        (1, "   Expected Questions & Answers"),
    ]

    for level, text in toc_items:
        if level == 0:
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(20, 60, 120)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 8, safe(text), new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(0, 0, 0)


def build_setup_guide(pdf):
    pdf.add_page()
    pdf.add_toc_entry("Section 1: Project Setup Guide")
    pdf.section_title("Section 1: Project Setup Guide (Oracle VM Linux)")

    pdf.body_text(
        "This section provides a complete, step-by-step guide to setting up the project environment "
        "from scratch using Oracle VirtualBox with Ubuntu Linux. Follow each step carefully to ensure "
        "all dependencies are installed and the project compiles and runs correctly."
    )

    pdf.sub_title("Step 1: Download and Install Oracle VM VirtualBox")
    pdf.body_text(
        "Oracle VM VirtualBox is a free, open-source virtualization tool that lets you run Linux "
        "inside your Windows or Mac machine."
    )
    pdf.numbered_item(1, 'Go to https://www.virtualbox.org/wiki/Downloads')
    pdf.numbered_item(2, 'Download the installer for your host OS (Windows, macOS, or Linux)')
    pdf.numbered_item(3, 'Run the installer and follow the default prompts')
    pdf.numbered_item(4, 'Accept the license agreement and complete installation')
    pdf.numbered_item(5, 'Launch VirtualBox after installation completes')
    pdf.ln(3)

    pdf.sub_title("Step 2: Download Ubuntu 22.04 LTS ISO")
    pdf.body_text(
        "Ubuntu 22.04 LTS (Jammy Jellyfish) is a stable long-term-support release ideal for development."
    )
    pdf.numbered_item(1, 'Go to https://ubuntu.com/download/desktop')
    pdf.numbered_item(2, 'Download the Ubuntu 22.04.x LTS ISO file (approximately 4.5 GB)')
    pdf.numbered_item(3, 'Save the ISO file in a known location on your computer')
    pdf.ln(3)

    pdf.sub_title("Step 3: Create a New Virtual Machine")
    pdf.body_text("Configure the VM with enough resources to run GTK applications smoothly:")
    pdf.numbered_item(1, 'In VirtualBox, click "New" to create a new VM')
    pdf.numbered_item(2, 'Name: "CSE324-OS-Lab", Type: Linux, Version: Ubuntu (64-bit)')
    pdf.numbered_item(3, 'Memory: Allocate at least 4096 MB (4 GB) RAM')
    pdf.numbered_item(4, 'Hard Disk: Create a virtual hard disk now, VDI format, dynamically allocated')
    pdf.numbered_item(5, 'Disk Size: At least 25 GB (recommended 30 GB for comfort)')
    pdf.numbered_item(6, 'Go to Settings -> System -> Processor: assign at least 2 CPU cores')
    pdf.numbered_item(7, 'Go to Settings -> Display -> Video Memory: set to 128 MB, enable 3D Acceleration')
    pdf.numbered_item(8, 'Go to Settings -> Storage: attach the Ubuntu ISO to the optical drive')
    pdf.ln(3)

    pdf.sub_title("Step 4: Install Ubuntu on the Virtual Machine")
    pdf.numbered_item(1, 'Start the VM - it will boot from the Ubuntu ISO')
    pdf.numbered_item(2, 'Select "Install Ubuntu" (not "Try Ubuntu")')
    pdf.numbered_item(3, 'Choose your keyboard layout and click Continue')
    pdf.numbered_item(4, 'Select "Normal Installation" and check "Download updates while installing"')
    pdf.numbered_item(5, 'Choose "Erase disk and install Ubuntu" (this only affects the virtual disk)')
    pdf.numbered_item(6, 'Set your timezone, create a username and password')
    pdf.numbered_item(7, 'Wait for installation to complete, then restart the VM when prompted')
    pdf.numbered_item(8, 'After reboot, log in with your credentials')
    pdf.numbered_item(9, '(Optional) Install VirtualBox Guest Additions for better resolution and shared clipboard:')
    pdf.body_text(
        '   In VM menu: Devices -> Insert Guest Additions CD, then open a terminal and run:\n'
        '   sudo apt install -y build-essential dkms linux-headers-$(uname -r)\n'
        '   sudo /media/$USER/VBox_GAs*/VBoxLinuxAdditions.run\n'
        '   Then reboot the VM.'
    )
    pdf.ln(3)

    pdf.sub_title("Step 5: Install Required Dependencies")
    pdf.body_text(
        "Open a terminal in Ubuntu (Ctrl+Alt+T) and run the following commands to install all "
        "required build tools and libraries:"
    )
    pdf.code_block(
        "# Update package lists\n"
        "sudo apt update\n"
        "\n"
        "# Install all required packages in one command\n"
        "sudo apt install -y git build-essential libgtk-3-dev pkg-config\n"
        "\n"
        "# Verify installations\n"
        "gcc --version        # Should show GCC version\n"
        "pkg-config --cflags gtk+-3.0   # Should show GTK flags\n"
        "git --version        # Should show git version",
        title="Terminal Commands"
    )
    pdf.body_text("What each package provides:")
    pdf.bullet("git - Version control to clone the repository")
    pdf.bullet("build-essential - GCC compiler, make, and standard C libraries")
    pdf.bullet("libgtk-3-dev - GTK 3 development headers and libraries for the GUI")
    pdf.bullet("pkg-config - Helper tool that provides correct compiler/linker flags for GTK")
    pdf.ln(3)

    pdf.sub_title("Step 6: Clone the Project Repository")
    pdf.code_block(
        "# Clone the repository from GitHub\n"
        "git clone https://github.com/tanoor890/automated-software-installer.git\n"
        "\n"
        "# Navigate into the project directory\n"
        "cd automated-software-installer\n"
        "\n"
        "# Verify the project structure\n"
        "ls -la",
        title="Terminal Commands"
    )
    pdf.body_text(
        "You should see directories: common/, server/, client/, and a Makefile in the root. "
        "The common/ directory contains shared protocol definitions and utility functions. "
        "The server/ directory has server logic, GUI, package management, and file handler. "
        "The client/ directory has client logic, GUI, downloader, and installer."
    )
    pdf.ln(3)

    pdf.sub_title("Step 7: Build the Project")
    pdf.code_block(
        "# Build both server and client applications\n"
        "make all\n"
        "\n"
        "# This creates two executables:\n"
        "#   server_app - The server application\n"
        "#   client_app - The client application\n"
        "\n"
        "# If you want to build individually:\n"
        "make server   # Build only the server\n"
        "make client   # Build only the client",
        title="Terminal Commands"
    )
    pdf.body_text(
        "The Makefile compiles all source files with GTK 3 flags and pthread support. "
        "If the build succeeds without errors, you will see server_app and client_app in the project root."
    )
    pdf.ln(3)

    pdf.sub_title("Step 8: Prepare the Software Packages")
    pdf.body_text(
        "Before running the server, ensure the packages directory and packages.txt file exist:"
    )
    pdf.code_block(
        "# Create the packages directory if it doesn't exist\n"
        "mkdir -p server/software_packages\n"
        "\n"
        "# Create a sample packages.txt file\n"
        'echo "1|Sample Package|sample.deb|1048576" > server/software_packages/packages.txt\n'
        "\n"
        "# Place actual .deb, .sh, or other files in server/software_packages/\n"
        "# The format of packages.txt is: id|name|filename|size_in_bytes",
        title="Terminal Commands"
    )
    pdf.ln(3)

    pdf.sub_title("Step 9: Run the Server")
    pdf.code_block(
        "# In Terminal 1 - Start the server\n"
        "./server_app\n"
        "\n"
        "# The GTK server GUI will open\n"
        "# Click 'Start Server' to begin listening on port 8080\n"
        "# The log panel will show: Server started on port 8080\n"
        "# The server is now ready to accept client connections",
        title="Terminal 1 - Server"
    )
    pdf.ln(3)

    pdf.sub_title("Step 10: Run the Client and Test")
    pdf.code_block(
        "# In Terminal 2 - Start the client\n"
        "./client_app\n"
        "\n"
        "# The GTK client GUI will open\n"
        "# Steps to test:\n"
        "#   1. Enter server IP: 127.0.0.1 (localhost) and port: 8080\n"
        "#   2. Click 'Connect' - status should show Connected\n"
        "#   3. Click 'Refresh List' - available packages appear\n"
        "#   4. Select a package and click 'Download'\n"
        "#   5. Watch the progress bar fill up\n"
        "#   6. After download, click 'Install' to auto-install\n"
        "#   7. Check the activity log for status messages",
        title="Terminal 2 - Client"
    )
    pdf.ln(3)

    pdf.sub_title("Common Errors and Solutions")
    pdf.ln(2)
    widths = [60, 130]
    pdf.table_row(["Error", "Solution"], widths, bold=True, fill=True)
    errors = [
        ("gtk+-3.0 not found", "Run: sudo apt install libgtk-3-dev pkg-config"),
        ("make: gcc: not found", "Run: sudo apt install build-essential"),
        ("Connection refused", "Ensure server_app is running and 'Start Server' was clicked"),
        ("Permission denied", "Run: chmod +x server_app client_app"),
        ("Port already in use", "Kill existing process: sudo kill -9 $(lsof -t -i:8080)"),
        ("Cannot open packages file", "Create server/software_packages/packages.txt"),
        ("Display error (Wayland)", "Run: export GDK_BACKEND=x11 before launching"),
        ("Segmentation fault", "Check that all files exist; rebuild with: make clean && make all"),
    ]
    for err, sol in errors:
        pdf.table_row([err, sol], widths)

    pdf.ln(5)
    pdf.sub_title("Tips for the Presentation Demo")
    pdf.bullet("Run both server and client on the same VM using 127.0.0.1 (localhost)")
    pdf.bullet("Have the packages.txt pre-populated with 3-5 sample packages for variety")
    pdf.bullet("Use the server GUI log to show real-time client connections to the teacher")
    pdf.bullet("If possible, use two VMs on the same network to show true network communication")
    pdf.bullet("Practice the full flow (connect -> browse -> download -> install) before the presentation")


def build_person1(pdf):
    pdf.add_page()
    pdf.add_toc_entry("Person 1 - Shuvo (System Architect)")
    pdf.section_title("Person 1: Md. Al Shahariar Shuvo (232-15-097)")
    pdf.sub_title("Role: Project Leader & System Architect")
    pdf.body_text(
        "Shuvo designed the overall architecture of the system, defining the shared communication "
        "protocol, data structures, and utility functions that every other module depends on. He "
        "also created the Makefile build system that compiles both the server and client applications "
        "with the correct GTK and pthread flags. His work forms the foundation upon which the entire "
        "project is built."
    )
    pdf.ln(3)

    pdf.sub_title("Files Responsible For:")
    pdf.bullet("common/protocol.h - Shared protocol constants and data structures")
    pdf.bullet("common/utils.h - Utility function declarations")
    pdf.bullet("common/utils.c - Utility function implementations")
    pdf.bullet("Makefile - Build system for the entire project")
    pdf.ln(3)

    pdf.sub_title("Code: common/protocol.h")
    pdf.code_block(
        '#ifndef PROTOCOL_H\n'
        '#define PROTOCOL_H\n'
        '\n'
        '#include <stddef.h>\n'
        '\n'
        '#define DEFAULT_PORT      8080\n'
        '#define BUFFER_SIZE       4096\n'
        '#define MAX_FILENAME      256\n'
        '#define MAX_PACKAGES      100\n'
        '#define MAX_CLIENTS       50\n'
        '#define MAX_PATH_LEN      512\n'
        '#define MAX_LINE_LEN      1024\n'
        '\n'
        '#define CMD_LIST          "LIST"\n'
        '#define CMD_DOWNLOAD      "DOWNLOAD"\n'
        '#define CMD_BYE           "BYE"\n'
        '\n'
        '#define RESP_OK           "RESPONSE: OK"\n'
        '#define RESP_ERROR        "RESPONSE: ERROR"\n'
        '\n'
        '#define PACKAGES_FILE     "server/software_packages/packages.txt"\n'
        '#define PACKAGES_DIR      "server/software_packages/"\n'
        '#define DOWNLOADS_DIR     "downloads/"\n'
        '\n'
        'typedef struct {\n'
        '    int    id;\n'
        '    char   name[MAX_FILENAME];\n'
        '    char   filename[MAX_FILENAME];\n'
        '    long   size;\n'
        '} Package;\n'
        '\n'
        'typedef void (*progress_callback)(long received, long total,\n'
        '                                  void *user_data);\n'
        'typedef void (*log_callback)(const char *message,\n'
        '                             void *user_data);\n'
        '\n'
        '#endif',
        title="common/protocol.h"
    )

    pdf.sub_title("Code: common/utils.h")
    pdf.code_block(
        '#ifndef UTILS_H\n'
        '#define UTILS_H\n'
        '\n'
        '#include <stddef.h>\n'
        '\n'
        'void format_size(long bytes, char *buf, size_t buf_size);\n'
        'void trim_newline(char *str);\n'
        'void get_timestamp(char *buf, size_t buf_size);\n'
        'void log_message(const char *format, ...);\n'
        '\n'
        '#endif',
        title="common/utils.h"
    )

    pdf.sub_title("Code: common/utils.c")
    pdf.code_block(
        '#include "utils.h"\n'
        '#include <stdio.h>\n'
        '#include <string.h>\n'
        '#include <stdarg.h>\n'
        '#include <time.h>\n'
        '\n'
        'void format_size(long bytes, char *buf, size_t buf_size) {\n'
        '    if (bytes >= 1073741824)\n'
        '        snprintf(buf, buf_size, "%.2f GB", bytes / 1073741824.0);\n'
        '    else if (bytes >= 1048576)\n'
        '        snprintf(buf, buf_size, "%.2f MB", bytes / 1048576.0);\n'
        '    else if (bytes >= 1024)\n'
        '        snprintf(buf, buf_size, "%.2f KB", bytes / 1024.0);\n'
        '    else\n'
        '        snprintf(buf, buf_size, "%ld B", bytes);\n'
        '}\n'
        '\n'
        'void trim_newline(char *str) {\n'
        '    if (!str) return;\n'
        '    size_t len = strlen(str);\n'
        '    while (len > 0 && (str[len-1] == \'\\n\' || str[len-1] == \'\\r\'))\n'
        '        str[--len] = \'\\0\';\n'
        '}\n'
        '\n'
        'void get_timestamp(char *buf, size_t buf_size) {\n'
        '    time_t now = time(NULL);\n'
        '    struct tm *t = localtime(&now);\n'
        '    strftime(buf, buf_size, "%Y-%m-%d %H:%M:%S", t);\n'
        '}\n'
        '\n'
        'void log_message(const char *format, ...) {\n'
        '    char timestamp[64];\n'
        '    get_timestamp(timestamp, sizeof(timestamp));\n'
        '    fprintf(stdout, "[%s] ", timestamp);\n'
        '    va_list args;\n'
        '    va_start(args, format);\n'
        '    vfprintf(stdout, format, args);\n'
        '    va_end(args);\n'
        '    fprintf(stdout, "\\n");\n'
        '    fflush(stdout);\n'
        '}',
        title="common/utils.c"
    )

    pdf.sub_title("Code: Makefile")
    pdf.code_block(
        'CC = gcc\n'
        'CFLAGS = -Wall -Wextra -g\n'
        'GTK_CFLAGS = $(shell pkg-config --cflags gtk+-3.0)\n'
        'GTK_LIBS = $(shell pkg-config --libs gtk+-3.0)\n'
        'PTHREAD = -lpthread\n'
        '\n'
        'COMMON_SRC = common/utils.c\n'
        'SERVER_SRC = server/server.c server/server_gui.c \\\n'
        '             server/package_manager.c server/file_handler.c\n'
        'CLIENT_SRC = client/client.c client/client_gui.c \\\n'
        '             client/downloader.c client/installer.c\n'
        '\n'
        'SERVER_BIN = server_app\n'
        'CLIENT_BIN = client_app\n'
        '\n'
        '.PHONY: all server client clean dirs\n'
        '\n'
        'all: dirs server client\n'
        '\n'
        'dirs:\n'
        '\t@mkdir -p server/software_packages\n'
        '\t@mkdir -p downloads\n'
        '\n'
        'server: dirs $(SERVER_SRC) $(COMMON_SRC)\n'
        '\t$(CC) $(CFLAGS) $(GTK_CFLAGS) -o $(SERVER_BIN) \\\n'
        '\t  $(SERVER_SRC) $(COMMON_SRC) $(GTK_LIBS) $(PTHREAD)\n'
        '\n'
        'client: dirs $(CLIENT_SRC) $(COMMON_SRC)\n'
        '\t$(CC) $(CFLAGS) $(GTK_CFLAGS) -o $(CLIENT_BIN) \\\n'
        '\t  $(CLIENT_SRC) $(COMMON_SRC) $(GTK_LIBS) $(PTHREAD)\n'
        '\n'
        'clean:\n'
        '\trm -f $(SERVER_BIN) $(CLIENT_BIN)',
        title="Makefile"
    )

    pdf.add_page()
    pdf.sub_title("Detailed Code Explanation")

    pdf.sub_sub_title("protocol.h - The Shared Contract")
    pdf.body_text(
        "This header file is the most critical piece of the architecture because every single module "
        "in the project includes it. It serves as the contract between server and client."
    )
    pdf.body_text(
        "Constants: DEFAULT_PORT (8080) sets the TCP port both server and client use. BUFFER_SIZE "
        "(4096) defines the chunk size for network I/O and file reading - chosen as a standard page "
        "size for efficient memory-aligned transfers. MAX_FILENAME (256) matches the Linux filesystem "
        "limit. MAX_PACKAGES (100) and MAX_CLIENTS (50) set upper bounds for static arrays."
    )
    pdf.body_text(
        "Command Protocol: CMD_LIST, CMD_DOWNLOAD, CMD_BYE define a simple text-based command protocol. "
        "The client sends these string commands over TCP, and the server parses and responds accordingly. "
        "RESP_OK and RESP_ERROR are the server's response prefixes for success and failure."
    )
    pdf.body_text(
        "Path Constants: PACKAGES_FILE, PACKAGES_DIR, and DOWNLOADS_DIR define the filesystem layout so "
        "all modules reference the same paths."
    )
    pdf.body_text(
        "Package Struct: The Package struct holds an id (integer identifier), name (display name), "
        "filename (actual file on disk), and size (in bytes). This struct is used by both the server "
        "(to manage the catalog) and the client (to display and request packages)."
    )
    pdf.body_text(
        "Callback Typedefs: progress_callback and log_callback define function pointer types that enable "
        "loose coupling - the file transfer modules can report progress without knowing about GTK, and "
        "the GUI modules register their update functions as callbacks."
    )

    pdf.sub_sub_title("utils.h and utils.c - Shared Utilities")
    pdf.body_text(
        "format_size() converts raw byte counts into human-readable strings (B, KB, MB, GB) using "
        "standard power-of-1024 thresholds. This is used in both the server and client GUIs to display "
        "file sizes."
    )
    pdf.body_text(
        "trim_newline() strips trailing newline and carriage return characters from strings. This is "
        "essential when parsing network data or text files, as fgets() and recv() often leave trailing "
        "newlines that would break string comparisons."
    )
    pdf.body_text(
        "get_timestamp() uses time() and localtime() to produce a formatted timestamp string. "
        "log_message() uses variadic arguments (va_list) to provide printf-style logging with automatic "
        "timestamps and newlines. The fflush(stdout) call ensures logs appear immediately even when "
        "output is buffered (important for debugging)."
    )

    pdf.sub_sub_title("Makefile - Build System")
    pdf.body_text(
        "The Makefile uses pkg-config to dynamically get the correct GTK 3 compile and link flags, "
        "making it portable across different GTK installations. The -Wall -Wextra flags enable "
        "comprehensive warnings, and -g includes debug symbols for GDB. The -lpthread flag links "
        "the POSIX threads library needed by the server. The 'dirs' target creates necessary "
        "directories before compilation. The .PHONY declaration ensures these targets always run "
        "regardless of file timestamps."
    )

    pdf.sub_title("How This Part Connects to the Whole System")
    pdf.body_text(
        "Every single file in the project includes protocol.h, making it the architectural backbone. "
        "When the server sends a file and the client receives it, both use the same BUFFER_SIZE. "
        "When the client sends 'LIST' and the server checks for it, both use CMD_LIST from protocol.h. "
        "The Package struct is serialized for network transfer and deserialized on the other end. "
        "The utility functions are linked into both the server and client binaries (as seen in the "
        "Makefile's COMMON_SRC variable). Without these shared definitions, the server and client "
        "would be unable to communicate correctly."
    )

    pdf.sub_title("Presentation Talking Points")
    pdf.bullet("I designed the system architecture following a modular approach - shared protocol, "
               "server module, and client module - ensuring clean separation of concerns.")
    pdf.bullet("The text-based command protocol (LIST/DOWNLOAD/BYE) was chosen for simplicity and "
               "debuggability - you can even test it with telnet or netcat.")
    pdf.bullet("Callback typedefs enable loose coupling: the file transfer code doesn't need to know "
               "about GTK, making the modules independently testable.")
    pdf.bullet("The Makefile uses pkg-config for portability and compiles with -Wall -Wextra to catch "
               "potential bugs at compile time.")
    pdf.bullet("I coordinated with all team members to ensure the protocol definitions met everyone's "
               "needs - this required iterating on buffer sizes, struct fields, and command formats.")

    pdf.add_page()
    pdf.sub_title("Expected Teacher Questions & Model Answers")

    pdf.qa_pair(1,
        "Why did you choose port 8080 as the default?",
        "Port 8080 is a common alternative HTTP port that doesn't require root/sudo privileges "
        "(ports below 1024 are privileged on Linux). It's widely recognized, unlikely to conflict "
        "with other services during development, and easy to remember."
    )
    pdf.qa_pair(2,
        "Why is BUFFER_SIZE set to 4096?",
        "4096 bytes (4 KB) matches the default memory page size on most Linux systems. This makes "
        "memory allocation and I/O operations efficient because the OS handles data in page-sized "
        "chunks. It's also large enough for reasonable throughput but small enough to avoid excessive "
        "memory usage per client connection."
    )
    pdf.qa_pair(3,
        "What is the purpose of the #ifndef PROTOCOL_H include guard?",
        "The include guard prevents multiple inclusion of the header file. If protocol.h is included "
        "by multiple files that are compiled together, without the guard the compiler would see "
        "duplicate definitions of structs, constants, and typedefs, causing compilation errors. "
        "The preprocessor checks if PROTOCOL_H is already defined; if so, it skips the entire file."
    )
    pdf.qa_pair(4,
        "Why use typedef for function pointers instead of writing them directly?",
        "Typedefs for function pointers (progress_callback, log_callback) improve code readability "
        "significantly. Without them, function signatures would contain complex pointer syntax that's "
        "hard to read. They also create a single point of change - if the callback signature needs to "
        "change, we update the typedef in one place rather than every function that uses it."
    )
    pdf.qa_pair(5,
        "Why does log_message use variadic arguments?",
        "Variadic arguments (using va_list, va_start, va_end) allow log_message to accept printf-style "
        "format strings with a variable number of arguments, like log_message('Client %d connected on "
        "port %d', client_id, port). This makes logging flexible and natural for C programmers. "
        "The function wraps vfprintf which handles the format string processing."
    )
    pdf.qa_pair(6,
        "What would happen if you removed fflush(stdout) from log_message?",
        "stdout is typically line-buffered when connected to a terminal and fully-buffered when "
        "redirected. Without fflush(), log messages might be delayed in the buffer and only appear "
        "much later, or not at all if the program crashes. In a real-time server monitoring scenario, "
        "delayed logs would make debugging nearly impossible."
    )
    pdf.qa_pair(7,
        "Why did you use static arrays instead of dynamic memory allocation?",
        "Static arrays (like MAX_PACKAGES = 100, MAX_CLIENTS = 50) simplify memory management and "
        "avoid the complexity of malloc/free and potential memory leaks. For a lab project of this "
        "scale, the fixed limits are more than sufficient. In a production system, you might use "
        "dynamic arrays or linked lists, but that adds complexity without benefit here."
    )
    pdf.qa_pair(8,
        "Explain the Makefile: what does $(shell pkg-config --cflags gtk+-3.0) do?",
        "The $(shell ...) directive executes a shell command during Makefile evaluation. pkg-config "
        "--cflags gtk+-3.0 outputs the compiler flags needed for GTK 3, typically something like "
        "'-I/usr/include/gtk-3.0 -I/usr/include/glib-2.0 ...' - the include paths for all GTK "
        "headers. This makes the build system portable because the actual paths differ across "
        "Linux distributions, and pkg-config resolves them automatically."
    )
    pdf.qa_pair(9,
        "What is the difference between a header file (.h) and a source file (.c)?",
        "Header files (.h) contain declarations - function prototypes, struct definitions, macros, "
        "and type definitions. They tell other modules WHAT functions exist and WHAT types look like. "
        "Source files (.c) contain the actual implementations - the function bodies with real code. "
        "This separation enables modular compilation: you can change the implementation in a .c file "
        "without recompiling modules that only depend on the .h interface."
    )
    pdf.qa_pair(10,
        "How does the Package struct get shared between server and client if they're separate programs?",
        "Both the server and client source files #include protocol.h at compile time. The struct "
        "definition is literally copied into each program's compilation. When the server serializes "
        "package data as pipe-delimited text (e.g., '1|Firefox|firefox.deb|5242880') and sends it "
        "over the network, the client parses this text back into the same Package struct. The struct "
        "is never sent in binary form - text serialization ensures compatibility."
    )


def build_person2(pdf):
    pdf.add_page()
    pdf.add_toc_entry("Person 2 - Maruf (Server-Side Developer)")
    pdf.section_title("Person 2: Abdullah Al Maruf (232-15-180)")
    pdf.sub_title("Role: Server-Side Developer")
    pdf.body_text(
        "Maruf implemented the core server application, which is responsible for listening on a TCP socket, "
        "accepting incoming client connections, spawning threads to handle each client concurrently, and "
        "processing commands (LIST, DOWNLOAD, BYE). He also built the GTK 3 graphical management interface "
        "for the server, providing real-time monitoring of connected clients, server logs, and package management."
    )
    pdf.ln(3)

    pdf.sub_title("Files Responsible For:")
    pdf.bullet("server/server.c - Core server: socket setup, threading, command processing")
    pdf.bullet("server/server_gui.c - GTK 3 server management interface")
    pdf.ln(3)

    pdf.sub_title("Code: server/server.c")
    pdf.code_block(
        '#include <stdio.h>\n'
        '#include <stdlib.h>\n'
        '#include <string.h>\n'
        '#include <unistd.h>\n'
        '#include <arpa/inet.h>\n'
        '#include <sys/socket.h>\n'
        '#include <pthread.h>\n'
        '#include "../common/protocol.h"\n'
        '#include "../common/utils.h"\n'
        '#include "package_manager.h"\n'
        '#include "file_handler.h"\n'
        '\n'
        'static int server_fd = -1;\n'
        'static int running = 0;\n'
        'static Package packages[MAX_PACKAGES];\n'
        'static int package_count = 0;\n'
        'static pthread_mutex_t clients_mutex = PTHREAD_MUTEX_INITIALIZER;\n'
        'static log_callback gui_log_cb = NULL;\n'
        'static void *gui_log_data = NULL;\n'
        '\n'
        'typedef struct {\n'
        '    int sockfd;\n'
        '    struct sockaddr_in addr;\n'
        '    int active;\n'
        '} ClientInfo;\n'
        '\n'
        'static ClientInfo clients[MAX_CLIENTS];\n'
        'static int client_count = 0;\n'
        '\n'
        'void server_set_log_callback(log_callback cb, void *data) {\n'
        '    gui_log_cb = cb;\n'
        '    gui_log_data = data;\n'
        '}\n'
        '\n'
        'static void server_log(const char *msg) {\n'
        '    log_message("%s", msg);\n'
        '    if (gui_log_cb)\n'
        '        gui_log_cb(msg, gui_log_data);\n'
        '}\n'
        '\n'
        'static void add_client(int sockfd, struct sockaddr_in addr) {\n'
        '    pthread_mutex_lock(&clients_mutex);\n'
        '    if (client_count < MAX_CLIENTS) {\n'
        '        clients[client_count].sockfd = sockfd;\n'
        '        clients[client_count].addr = addr;\n'
        '        clients[client_count].active = 1;\n'
        '        client_count++;\n'
        '    }\n'
        '    pthread_mutex_unlock(&clients_mutex);\n'
        '}\n'
        '\n'
        'static void remove_client(int sockfd) {\n'
        '    pthread_mutex_lock(&clients_mutex);\n'
        '    for (int i = 0; i < client_count; i++) {\n'
        '        if (clients[i].sockfd == sockfd) {\n'
        '            clients[i] = clients[client_count - 1];\n'
        '            client_count--;\n'
        '            break;\n'
        '        }\n'
        '    }\n'
        '    pthread_mutex_unlock(&clients_mutex);\n'
        '}\n'
        '\n'
        'static void *handle_client(void *arg) {\n'
        '    int sockfd = *(int *)arg;\n'
        '    free(arg);\n'
        '    char buffer[BUFFER_SIZE];\n'
        '    char msg[MAX_LINE_LEN];\n'
        '\n'
        '    snprintf(msg, sizeof(msg), "Client connected: fd=%d", sockfd);\n'
        '    server_log(msg);\n'
        '\n'
        '    while (running) {\n'
        '        memset(buffer, 0, BUFFER_SIZE);\n'
        '        ssize_t n = recv(sockfd, buffer, BUFFER_SIZE - 1, 0);\n'
        '        if (n <= 0) break;\n'
        '        trim_newline(buffer);\n'
        '\n'
        '        if (strcmp(buffer, CMD_LIST) == 0) {\n'
        '            char list_buf[BUFFER_SIZE * 4];\n'
        '            list_packages(packages, package_count,\n'
        '                          list_buf, sizeof(list_buf));\n'
        '            send(sockfd, list_buf, strlen(list_buf), 0);\n'
        '            server_log("Sent package list to client");\n'
        '\n'
        '        } else if (strncmp(buffer, CMD_DOWNLOAD,\n'
        '                           strlen(CMD_DOWNLOAD)) == 0) {\n'
        '            int pkg_id = atoi(buffer + strlen(CMD_DOWNLOAD) + 1);\n'
        '            Package *pkg = find_package(packages,\n'
        '                                        package_count, pkg_id);\n'
        '            if (pkg) {\n'
        '                char filepath[MAX_PATH_LEN];\n'
        '                snprintf(filepath, sizeof(filepath),\n'
        '                         "%s%s", PACKAGES_DIR, pkg->filename);\n'
        '                char resp[BUFFER_SIZE];\n'
        '                snprintf(resp, sizeof(resp),\n'
        '                         "%s %ld", RESP_OK, pkg->size);\n'
        '                send(sockfd, resp, strlen(resp), 0);\n'
        '                usleep(100000);\n'
        '                send_file(sockfd, filepath, NULL, NULL);\n'
        '                snprintf(msg, sizeof(msg),\n'
        '                         "Sent file: %s", pkg->filename);\n'
        '                server_log(msg);\n'
        '            } else {\n'
        '                send(sockfd, RESP_ERROR,\n'
        '                     strlen(RESP_ERROR), 0);\n'
        '            }\n'
        '\n'
        '        } else if (strcmp(buffer, CMD_BYE) == 0) {\n'
        '            server_log("Client disconnected gracefully");\n'
        '            break;\n'
        '        }\n'
        '    }\n'
        '    close(sockfd);\n'
        '    remove_client(sockfd);\n'
        '    return NULL;\n'
        '}\n'
        '\n'
        'int start_server(int port) {\n'
        '    server_fd = socket(AF_INET, SOCK_STREAM, 0);\n'
        '    if (server_fd < 0) return -1;\n'
        '\n'
        '    int opt = 1;\n'
        '    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR,\n'
        '               &opt, sizeof(opt));\n'
        '\n'
        '    struct sockaddr_in addr;\n'
        '    addr.sin_family = AF_INET;\n'
        '    addr.sin_addr.s_addr = INADDR_ANY;\n'
        '    addr.sin_port = htons(port);\n'
        '\n'
        '    if (bind(server_fd, (struct sockaddr *)&addr,\n'
        '             sizeof(addr)) < 0) {\n'
        '        close(server_fd);\n'
        '        return -1;\n'
        '    }\n'
        '\n'
        '    if (listen(server_fd, MAX_CLIENTS) < 0) {\n'
        '        close(server_fd);\n'
        '        return -1;\n'
        '    }\n'
        '\n'
        '    package_count = load_packages(PACKAGES_FILE,\n'
        '                                  packages, MAX_PACKAGES);\n'
        '    running = 1;\n'
        '    char msg[256];\n'
        '    snprintf(msg, sizeof(msg),\n'
        '             "Server started on port %d", port);\n'
        '    server_log(msg);\n'
        '\n'
        '    while (running) {\n'
        '        struct sockaddr_in client_addr;\n'
        '        socklen_t addr_len = sizeof(client_addr);\n'
        '        int *client_fd = malloc(sizeof(int));\n'
        '        *client_fd = accept(server_fd,\n'
        '            (struct sockaddr *)&client_addr, &addr_len);\n'
        '        if (*client_fd < 0) {\n'
        '            free(client_fd);\n'
        '            if (!running) break;\n'
        '            continue;\n'
        '        }\n'
        '        add_client(*client_fd, client_addr);\n'
        '        pthread_t tid;\n'
        '        pthread_create(&tid, NULL,\n'
        '                       handle_client, client_fd);\n'
        '        pthread_detach(tid);\n'
        '    }\n'
        '    return 0;\n'
        '}\n'
        '\n'
        'void stop_server(void) {\n'
        '    running = 0;\n'
        '    if (server_fd >= 0) {\n'
        '        close(server_fd);\n'
        '        server_fd = -1;\n'
        '    }\n'
        '    server_log("Server stopped");\n'
        '}',
        title="server/server.c"
    )

    pdf.sub_title("Code: server/server_gui.c")
    pdf.code_block(
        '#include <gtk/gtk.h>\n'
        '#include <pthread.h>\n'
        '#include "../common/protocol.h"\n'
        '#include "../common/utils.h"\n'
        '\n'
        'extern int start_server(int port);\n'
        'extern void stop_server(void);\n'
        'extern void server_set_log_callback(\n'
        '    void (*cb)(const char *, void *), void *data);\n'
        '\n'
        'static GtkWidget *log_view;\n'
        'static GtkTextBuffer *log_buffer;\n'
        'static GtkWidget *start_btn, *stop_btn;\n'
        'static GtkWidget *port_entry;\n'
        'static GtkWidget *status_label;\n'
        'static pthread_t server_thread;\n'
        '\n'
        'static gboolean append_log_idle(gpointer data) {\n'
        '    char *msg = (char *)data;\n'
        '    GtkTextIter end;\n'
        '    gtk_text_buffer_get_end_iter(log_buffer, &end);\n'
        '    char timestamped[1024];\n'
        '    char ts[64];\n'
        '    get_timestamp(ts, sizeof(ts));\n'
        '    snprintf(timestamped, sizeof(timestamped),\n'
        '             "[%s] %s\\n", ts, msg);\n'
        '    gtk_text_buffer_insert(log_buffer,\n'
        '                           &end, timestamped, -1);\n'
        '    GtkTextMark *mark = gtk_text_buffer_get_mark(\n'
        '        log_buffer, "end");\n'
        '    if (!mark)\n'
        '        mark = gtk_text_buffer_create_mark(\n'
        '            log_buffer, "end", &end, FALSE);\n'
        '    else\n'
        '        gtk_text_buffer_move_mark(\n'
        '            log_buffer, mark, &end);\n'
        '    gtk_text_view_scroll_mark_onscreen(\n'
        '        GTK_TEXT_VIEW(log_view), mark);\n'
        '    free(msg);\n'
        '    return FALSE;\n'
        '}\n'
        '\n'
        'static void gui_log_callback(const char *msg,\n'
        '                             void *data) {\n'
        '    (void)data;\n'
        '    g_idle_add(append_log_idle, g_strdup(msg));\n'
        '}\n'
        '\n'
        'static void *server_thread_func(void *arg) {\n'
        '    int port = *(int *)arg;\n'
        '    free(arg);\n'
        '    start_server(port);\n'
        '    return NULL;\n'
        '}\n'
        '\n'
        'static void on_start_clicked(GtkWidget *w, gpointer d) {\n'
        '    (void)w; (void)d;\n'
        '    const char *port_str = gtk_entry_get_text(\n'
        '        GTK_ENTRY(port_entry));\n'
        '    int *port = malloc(sizeof(int));\n'
        '    *port = atoi(port_str);\n'
        '    if (*port <= 0) *port = DEFAULT_PORT;\n'
        '    server_set_log_callback(gui_log_callback, NULL);\n'
        '    pthread_create(&server_thread, NULL,\n'
        '                   server_thread_func, port);\n'
        '    gtk_widget_set_sensitive(start_btn, FALSE);\n'
        '    gtk_widget_set_sensitive(stop_btn, TRUE);\n'
        '    gtk_label_set_text(GTK_LABEL(status_label),\n'
        '                       "Status: Running");\n'
        '}\n'
        '\n'
        'static void on_stop_clicked(GtkWidget *w, gpointer d) {\n'
        '    (void)w; (void)d;\n'
        '    stop_server();\n'
        '    gtk_widget_set_sensitive(start_btn, TRUE);\n'
        '    gtk_widget_set_sensitive(stop_btn, FALSE);\n'
        '    gtk_label_set_text(GTK_LABEL(status_label),\n'
        '                       "Status: Stopped");\n'
        '}\n'
        '\n'
        'int main(int argc, char *argv[]) {\n'
        '    gtk_init(&argc, &argv);\n'
        '    GtkWidget *window = gtk_window_new(\n'
        '        GTK_WINDOW_TOPLEVEL);\n'
        '    gtk_window_set_title(GTK_WINDOW(window),\n'
        '        "Software Server - Management Console");\n'
        '    gtk_window_set_default_size(\n'
        '        GTK_WINDOW(window), 700, 500);\n'
        '    g_signal_connect(window, "destroy",\n'
        '                     G_CALLBACK(gtk_main_quit), NULL);\n'
        '\n'
        '    GtkWidget *vbox = gtk_box_new(\n'
        '        GTK_ORIENTATION_VERTICAL, 5);\n'
        '    gtk_container_set_border_width(\n'
        '        GTK_CONTAINER(vbox), 10);\n'
        '    gtk_container_add(GTK_CONTAINER(window), vbox);\n'
        '\n'
        '    /* Control bar */\n'
        '    GtkWidget *hbox = gtk_box_new(\n'
        '        GTK_ORIENTATION_HORIZONTAL, 5);\n'
        '    gtk_box_pack_start(GTK_BOX(vbox),\n'
        '                       hbox, FALSE, FALSE, 5);\n'
        '\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '        gtk_label_new("Port:"), FALSE, FALSE, 5);\n'
        '    port_entry = gtk_entry_new();\n'
        '    gtk_entry_set_text(GTK_ENTRY(port_entry), "8080");\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '                       port_entry, FALSE, FALSE, 5);\n'
        '\n'
        '    start_btn = gtk_button_new_with_label("Start");\n'
        '    stop_btn = gtk_button_new_with_label("Stop");\n'
        '    gtk_widget_set_sensitive(stop_btn, FALSE);\n'
        '    g_signal_connect(start_btn, "clicked",\n'
        '        G_CALLBACK(on_start_clicked), NULL);\n'
        '    g_signal_connect(stop_btn, "clicked",\n'
        '        G_CALLBACK(on_stop_clicked), NULL);\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '                       start_btn, FALSE, FALSE, 5);\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '                       stop_btn, FALSE, FALSE, 5);\n'
        '\n'
        '    status_label = gtk_label_new("Status: Stopped");\n'
        '    gtk_box_pack_end(GTK_BOX(hbox),\n'
        '                     status_label, FALSE, FALSE, 5);\n'
        '\n'
        '    /* Log view */\n'
        '    GtkWidget *scroll = gtk_scrolled_window_new(\n'
        '        NULL, NULL);\n'
        '    gtk_scrolled_window_set_policy(\n'
        '        GTK_SCROLLED_WINDOW(scroll),\n'
        '        GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);\n'
        '    gtk_box_pack_start(GTK_BOX(vbox),\n'
        '                       scroll, TRUE, TRUE, 5);\n'
        '\n'
        '    log_view = gtk_text_view_new();\n'
        '    gtk_text_view_set_editable(\n'
        '        GTK_TEXT_VIEW(log_view), FALSE);\n'
        '    log_buffer = gtk_text_view_get_buffer(\n'
        '        GTK_TEXT_VIEW(log_view));\n'
        '    gtk_container_add(GTK_CONTAINER(scroll), log_view);\n'
        '\n'
        '    gtk_widget_show_all(window);\n'
        '    gtk_main();\n'
        '    stop_server();\n'
        '    return 0;\n'
        '}',
        title="server/server_gui.c"
    )

    pdf.add_page()
    pdf.sub_title("Detailed Code Explanation")

    pdf.sub_sub_title("server.c - Server Core Logic")
    pdf.body_text(
        "Global State: The server uses static global variables to maintain state - server_fd holds "
        "the listening socket descriptor, running is a flag to control the accept loop, packages[] "
        "stores the loaded package catalog, and clients[] tracks connected clients. The "
        "clients_mutex (PTHREAD_MUTEX_INITIALIZER) protects the clients array from race conditions "
        "when multiple threads add or remove clients simultaneously."
    )
    pdf.body_text(
        "ClientInfo Struct: Each connected client is tracked with its socket descriptor (sockfd), "
        "address (struct sockaddr_in for IP/port info), and an active flag. This allows the server "
        "GUI to display currently connected clients."
    )
    pdf.body_text(
        "start_server(): This function follows the standard POSIX TCP server setup:\n"
        "1. socket(AF_INET, SOCK_STREAM, 0) creates a TCP socket\n"
        "2. setsockopt with SO_REUSEADDR allows reusing the port immediately after restart\n"
        "3. bind() associates the socket with the specified port on all interfaces (INADDR_ANY)\n"
        "4. listen() marks the socket as passive, ready to accept connections\n"
        "5. The accept loop runs while running==1, blocking on accept() for new connections\n"
        "6. For each new connection, it creates a new thread with pthread_create()"
    )
    pdf.body_text(
        "handle_client(): Each client gets its own thread running this function. It loops reading "
        "commands from the client socket. For CMD_LIST, it serializes the package array and sends it. "
        "For CMD_DOWNLOAD, it parses the package ID, looks it up, sends the file size as a response "
        "header, waits 100ms (usleep) for the client to prepare, then calls send_file() to stream "
        "the binary data. For CMD_BYE, it logs the disconnect and breaks the loop. When the thread "
        "exits, it closes the socket and removes the client from the tracking array."
    )
    pdf.body_text(
        "Thread Management: pthread_detach(tid) is called after creating each thread, meaning the "
        "thread's resources are automatically freed when it exits - no need for pthread_join(). "
        "The client socket fd is allocated on the heap (malloc) and passed to the thread to avoid "
        "race conditions with stack variables."
    )

    pdf.sub_sub_title("server_gui.c - GTK 3 Server Interface")
    pdf.body_text(
        "Thread-Safe GUI Updates: GTK is not thread-safe, so the server thread cannot directly modify "
        "GUI widgets. The gui_log_callback() uses g_idle_add() to schedule append_log_idle() on the "
        "GTK main thread's event loop. This is a critical pattern: g_idle_add() is one of the few "
        "GTK functions safe to call from any thread."
    )
    pdf.body_text(
        "The main() function initializes GTK, creates the window with a vertical box layout containing "
        "a control bar (port entry, start/stop buttons, status label) and a scrollable text view for "
        "logs. The start button spawns the server in a new thread so the GUI remains responsive. "
        "The stop button calls stop_server() which sets running=0 and closes the listening socket, "
        "causing accept() to fail and the server thread to exit."
    )

    pdf.sub_title("How This Part Connects to the Whole System")
    pdf.body_text(
        "The server is the central hub of the system. It uses protocol.h constants for all network "
        "communication. It calls load_packages() and find_package() from package_manager.c (Jowel's "
        "code) to manage the software catalog. It calls send_file() from file_handler.c (Utsho's "
        "code) to transfer files. The GUI uses the log_callback typedef from protocol.h to receive "
        "log messages from the server thread. The server responds to commands that the client "
        "(Mahi's code) sends."
    )

    pdf.sub_title("Presentation Talking Points")
    pdf.bullet("The server uses a multi-threaded architecture with one thread per client, enabling "
               "simultaneous connections without blocking.")
    pdf.bullet("I used mutex locks to protect shared data (the clients array) from race conditions "
               "when threads add or remove clients concurrently.")
    pdf.bullet("The GTK GUI runs on the main thread while the server runs on a separate thread - "
               "g_idle_add() bridges the thread boundary safely for GUI updates.")
    pdf.bullet("SO_REUSEADDR is essential for development - without it, restarting the server would "
               "fail with 'Address already in use' until the OS releases the port.")
    pdf.bullet("The text-based command protocol makes the server easy to test with tools like "
               "netcat: echo 'LIST' | nc localhost 8080")

    pdf.add_page()
    pdf.sub_title("Expected Teacher Questions & Model Answers")

    pdf.qa_pair(1,
        "Why did you use one thread per client instead of select() or poll()?",
        "One-thread-per-client is simpler to implement and understand for a lab project. Each "
        "thread has its own stack and can block on recv() independently. For our scale (up to 50 "
        "clients), the thread overhead is negligible. select()/poll()/epoll would be more "
        "efficient for thousands of concurrent connections but add significant complexity."
    )
    pdf.qa_pair(2,
        "What is the purpose of the mutex in the clients array operations?",
        "The pthread_mutex_t protects the shared clients[] array and client_count variable. Without "
        "the mutex, if two client threads try to add_client or remove_client simultaneously, they "
        "could corrupt the array - for example, both reading client_count as 5, then both writing "
        "to index 5, losing one entry. The mutex ensures only one thread modifies the array at a time."
    )
    pdf.qa_pair(3,
        "Explain the socket setup steps: socket(), bind(), listen(), accept().",
        "socket() creates the socket descriptor. bind() associates it with a specific IP and port. "
        "listen() marks it as a passive socket that waits for connections, with MAX_CLIENTS as the "
        "backlog queue size. accept() blocks until a client connects, then returns a NEW socket "
        "descriptor specifically for that client while the original continues listening."
    )
    pdf.qa_pair(4,
        "Why is the client socket fd allocated with malloc before passing to the thread?",
        "If we passed the address of a local variable, by the time the thread reads it, the accept "
        "loop may have already overwritten it with a new connection's fd. Allocating on the heap "
        "gives each thread its own copy. The thread is responsible for freeing it."
    )
    pdf.qa_pair(5,
        "Why do you use pthread_detach instead of pthread_join?",
        "pthread_detach() tells the system to automatically reclaim the thread's resources when it "
        "exits. We don't need to wait for client threads to finish - they should clean up "
        "independently. Using pthread_join() would require the accept loop to block until each "
        "client disconnects, which defeats the purpose of multi-threading."
    )
    pdf.qa_pair(6,
        "What does SO_REUSEADDR do and why is it needed?",
        "When a TCP connection closes, the port enters a TIME_WAIT state for 2-4 minutes to handle "
        "delayed packets. SO_REUSEADDR tells the OS to allow bind() on a port in TIME_WAIT. Without "
        "it, restarting the server quickly would fail with 'Address already in use' error."
    )
    pdf.qa_pair(7,
        "Why is g_idle_add() necessary for updating the GUI from the server thread?",
        "GTK uses a single-threaded event loop. Calling GTK functions from other threads causes "
        "undefined behavior - crashes, freezes, or corrupted display. g_idle_add() queues a "
        "function to run on the main GTK thread during idle time, ensuring thread safety. "
        "It's the standard GTK pattern for cross-thread GUI updates."
    )
    pdf.qa_pair(8,
        "What happens if a client disconnects unexpectedly (crashes)?",
        "When the client process dies, the OS closes its socket. The server's recv() call in "
        "handle_client() will return 0 (clean close) or -1 (error), causing the while loop to "
        "break. The thread then closes its end of the socket and calls remove_client() to clean "
        "up. No special crash handling is needed - the server continues running normally."
    )
    pdf.qa_pair(9,
        "Why is there a usleep(100000) between sending the response header and the file data?",
        "The 100ms delay gives the client time to read and parse the OK response (which contains "
        "the file size) before the binary file data starts arriving. Without this delay, the "
        "response header and file data could arrive in the same recv() buffer, making it difficult "
        "for the client to separate the text response from binary content. This is a simple "
        "synchronization mechanism."
    )
    pdf.qa_pair(10,
        "How does stop_server() cause the accept loop to exit?",
        "stop_server() sets running = 0, then closes server_fd. The accept() call that was "
        "blocking returns with an error (because the socket was closed underneath it). The loop "
        "checks 'if (!running) break;' and exits cleanly. Any existing client threads continue "
        "until their clients disconnect."
    )


def build_person3(pdf):
    pdf.add_page()
    pdf.add_toc_entry("Person 3 - Mahi (Client-Side Developer)")
    pdf.section_title("Person 3: Sibgatullah Mahi (232-15-015)")
    pdf.sub_title("Role: Client-Side Developer")
    pdf.body_text(
        "Mahi developed the client-side application, including the networking functions that connect "
        "to the server, request the package list, and initiate downloads, as well as the GTK 3 "
        "graphical interface that provides users with a friendly way to browse packages, monitor "
        "download progress, and trigger installations. His code is the user-facing half of the system."
    )
    pdf.ln(3)

    pdf.sub_title("Files Responsible For:")
    pdf.bullet("client/client.h - Client networking function declarations")
    pdf.bullet("client/client.c - Client networking implementations")
    pdf.bullet("client/client_gui.c - GTK 3 client user interface")
    pdf.ln(3)

    pdf.sub_title("Code: client/client.h")
    pdf.code_block(
        '#ifndef CLIENT_H\n'
        '#define CLIENT_H\n'
        '\n'
        '#include "../common/protocol.h"\n'
        '\n'
        'int  connect_to_server(const char *ip, int port);\n'
        'int  request_list(int sockfd, char *buf, size_t buf_size);\n'
        'int  request_download(int sockfd, int package_id,\n'
        '                      long *file_size);\n'
        'void disconnect(int sockfd);\n'
        'int  parse_package_list(const char *data,\n'
        '                        Package *pkgs, int max);\n'
        '\n'
        '#endif',
        title="client/client.h"
    )

    pdf.sub_title("Code: client/client.c")
    pdf.code_block(
        '#include "client.h"\n'
        '#include "../common/utils.h"\n'
        '#include <stdio.h>\n'
        '#include <stdlib.h>\n'
        '#include <string.h>\n'
        '#include <unistd.h>\n'
        '#include <arpa/inet.h>\n'
        '#include <sys/socket.h>\n'
        '\n'
        'int connect_to_server(const char *ip, int port) {\n'
        '    int sockfd = socket(AF_INET, SOCK_STREAM, 0);\n'
        '    if (sockfd < 0) return -1;\n'
        '\n'
        '    struct sockaddr_in addr;\n'
        '    addr.sin_family = AF_INET;\n'
        '    addr.sin_port = htons(port);\n'
        '    if (inet_pton(AF_INET, ip, &addr.sin_addr) <= 0) {\n'
        '        close(sockfd);\n'
        '        return -1;\n'
        '    }\n'
        '    if (connect(sockfd, (struct sockaddr *)&addr,\n'
        '                sizeof(addr)) < 0) {\n'
        '        close(sockfd);\n'
        '        return -1;\n'
        '    }\n'
        '    log_message("Connected to %s:%d", ip, port);\n'
        '    return sockfd;\n'
        '}\n'
        '\n'
        'int request_list(int sockfd, char *buf,\n'
        '                 size_t buf_size) {\n'
        '    send(sockfd, CMD_LIST, strlen(CMD_LIST), 0);\n'
        '    memset(buf, 0, buf_size);\n'
        '    ssize_t n = recv(sockfd, buf, buf_size - 1, 0);\n'
        '    if (n <= 0) return -1;\n'
        '    buf[n] = \'\\0\';\n'
        '    return 0;\n'
        '}\n'
        '\n'
        'int request_download(int sockfd, int package_id,\n'
        '                     long *file_size) {\n'
        '    char cmd[BUFFER_SIZE];\n'
        '    snprintf(cmd, sizeof(cmd), "%s %d",\n'
        '             CMD_DOWNLOAD, package_id);\n'
        '    send(sockfd, cmd, strlen(cmd), 0);\n'
        '\n'
        '    char resp[BUFFER_SIZE];\n'
        '    memset(resp, 0, sizeof(resp));\n'
        '    ssize_t n = recv(sockfd, resp, sizeof(resp)-1, 0);\n'
        '    if (n <= 0) return -1;\n'
        '    resp[n] = \'\\0\';\n'
        '\n'
        '    if (strncmp(resp, RESP_OK, strlen(RESP_OK)) == 0) {\n'
        '        *file_size = atol(resp + strlen(RESP_OK) + 1);\n'
        '        return 0;\n'
        '    }\n'
        '    return -1;\n'
        '}\n'
        '\n'
        'void disconnect(int sockfd) {\n'
        '    send(sockfd, CMD_BYE, strlen(CMD_BYE), 0);\n'
        '    close(sockfd);\n'
        '    log_message("Disconnected from server");\n'
        '}\n'
        '\n'
        'int parse_package_list(const char *data,\n'
        '                       Package *pkgs, int max) {\n'
        '    int count = 0;\n'
        '    char *copy = strdup(data);\n'
        '    char *line = strtok(copy, "\\n");\n'
        '    while (line && count < max) {\n'
        '        int id; char name[MAX_FILENAME];\n'
        '        char fname[MAX_FILENAME]; long sz;\n'
        '        if (sscanf(line, "%d|%[^|]|%[^|]|%ld",\n'
        '                   &id, name, fname, &sz) == 4) {\n'
        '            pkgs[count].id = id;\n'
        '            strncpy(pkgs[count].name,\n'
        '                    name, MAX_FILENAME-1);\n'
        '            strncpy(pkgs[count].filename,\n'
        '                    fname, MAX_FILENAME-1);\n'
        '            pkgs[count].size = sz;\n'
        '            count++;\n'
        '        }\n'
        '        line = strtok(NULL, "\\n");\n'
        '    }\n'
        '    free(copy);\n'
        '    return count;\n'
        '}',
        title="client/client.c"
    )

    pdf.sub_title("Code: client/client_gui.c")
    pdf.code_block(
        '#include <gtk/gtk.h>\n'
        '#include <pthread.h>\n'
        '#include "../common/protocol.h"\n'
        '#include "../common/utils.h"\n'
        '#include "client.h"\n'
        '#include "downloader.h"\n'
        '#include "installer.h"\n'
        '\n'
        'static int sockfd = -1;\n'
        'static Package packages[MAX_PACKAGES];\n'
        'static int pkg_count = 0;\n'
        '\n'
        'static GtkWidget *ip_entry, *port_entry;\n'
        'static GtkWidget *connect_btn, *disconnect_btn;\n'
        'static GtkWidget *refresh_btn, *download_btn, *install_btn;\n'
        'static GtkWidget *pkg_tree_view;\n'
        'static GtkListStore *pkg_store;\n'
        'static GtkWidget *progress_bar;\n'
        'static GtkWidget *log_view;\n'
        'static GtkTextBuffer *log_buf;\n'
        'static GtkWidget *status_label;\n'
        '\n'
        'static void gui_log(const char *msg) {\n'
        '    GtkTextIter end;\n'
        '    gtk_text_buffer_get_end_iter(log_buf, &end);\n'
        '    char ts[64], line[1024];\n'
        '    get_timestamp(ts, sizeof(ts));\n'
        '    snprintf(line, sizeof(line), "[%s] %s\\n", ts, msg);\n'
        '    gtk_text_buffer_insert(log_buf, &end, line, -1);\n'
        '}\n'
        '\n'
        'typedef struct {\n'
        '    double fraction;\n'
        '    char text[128];\n'
        '} ProgressData;\n'
        '\n'
        'static gboolean update_progress_idle(gpointer data) {\n'
        '    ProgressData *pd = (ProgressData *)data;\n'
        '    gtk_progress_bar_set_fraction(\n'
        '        GTK_PROGRESS_BAR(progress_bar), pd->fraction);\n'
        '    gtk_progress_bar_set_text(\n'
        '        GTK_PROGRESS_BAR(progress_bar), pd->text);\n'
        '    free(pd);\n'
        '    return FALSE;\n'
        '}\n'
        '\n'
        'static void download_progress(long recv, long total,\n'
        '                              void *ud) {\n'
        '    (void)ud;\n'
        '    ProgressData *pd = malloc(sizeof(ProgressData));\n'
        '    pd->fraction = (double)recv / total;\n'
        '    snprintf(pd->text, sizeof(pd->text),\n'
        '             "%ld / %ld bytes (%.0f%%)",\n'
        '             recv, total, pd->fraction * 100);\n'
        '    g_idle_add(update_progress_idle, pd);\n'
        '}\n'
        '\n'
        'static void on_connect(GtkWidget *w, gpointer d) {\n'
        '    (void)w; (void)d;\n'
        '    const char *ip = gtk_entry_get_text(\n'
        '        GTK_ENTRY(ip_entry));\n'
        '    int port = atoi(gtk_entry_get_text(\n'
        '        GTK_ENTRY(port_entry)));\n'
        '    sockfd = connect_to_server(ip, port);\n'
        '    if (sockfd >= 0) {\n'
        '        gui_log("Connected to server");\n'
        '        gtk_label_set_text(GTK_LABEL(status_label),\n'
        '                           "Connected");\n'
        '        gtk_widget_set_sensitive(connect_btn, FALSE);\n'
        '        gtk_widget_set_sensitive(disconnect_btn, TRUE);\n'
        '        gtk_widget_set_sensitive(refresh_btn, TRUE);\n'
        '    } else {\n'
        '        gui_log("Connection failed!");\n'
        '    }\n'
        '}\n'
        '\n'
        'static void on_disconnect(GtkWidget *w, gpointer d) {\n'
        '    (void)w; (void)d;\n'
        '    if (sockfd >= 0) {\n'
        '        disconnect(sockfd);\n'
        '        sockfd = -1;\n'
        '    }\n'
        '    gui_log("Disconnected");\n'
        '    gtk_label_set_text(GTK_LABEL(status_label),\n'
        '                       "Disconnected");\n'
        '    gtk_widget_set_sensitive(connect_btn, TRUE);\n'
        '    gtk_widget_set_sensitive(disconnect_btn, FALSE);\n'
        '    gtk_widget_set_sensitive(refresh_btn, FALSE);\n'
        '    gtk_widget_set_sensitive(download_btn, FALSE);\n'
        '}\n'
        '\n'
        'static void on_refresh(GtkWidget *w, gpointer d) {\n'
        '    (void)w; (void)d;\n'
        '    char buf[BUFFER_SIZE * 4];\n'
        '    if (request_list(sockfd, buf, sizeof(buf)) == 0) {\n'
        '        pkg_count = parse_package_list(\n'
        '            buf, packages, MAX_PACKAGES);\n'
        '        gtk_list_store_clear(pkg_store);\n'
        '        for (int i = 0; i < pkg_count; i++) {\n'
        '            char sz[64];\n'
        '            format_size(packages[i].size, sz, 64);\n'
        '            GtkTreeIter iter;\n'
        '            gtk_list_store_append(pkg_store, &iter);\n'
        '            gtk_list_store_set(pkg_store, &iter,\n'
        '                0, packages[i].id,\n'
        '                1, packages[i].name,\n'
        '                2, packages[i].filename,\n'
        '                3, sz, -1);\n'
        '        }\n'
        '        gui_log("Package list refreshed");\n'
        '        gtk_widget_set_sensitive(download_btn, TRUE);\n'
        '    }\n'
        '}\n'
        '\n'
        'static void *download_thread_func(void *arg) {\n'
        '    int pkg_id = *(int *)arg;\n'
        '    free(arg);\n'
        '    Package *pkg = NULL;\n'
        '    for (int i = 0; i < pkg_count; i++)\n'
        '        if (packages[i].id == pkg_id)\n'
        '            { pkg = &packages[i]; break; }\n'
        '    if (!pkg) return NULL;\n'
        '\n'
        '    long file_size;\n'
        '    if (request_download(sockfd, pkg_id,\n'
        '                         &file_size) == 0) {\n'
        '        char path[MAX_PATH_LEN];\n'
        '        snprintf(path, sizeof(path), "%s%s",\n'
        '                 DOWNLOADS_DIR, pkg->filename);\n'
        '        receive_file(sockfd, path, file_size,\n'
        '                     download_progress, NULL);\n'
        '    }\n'
        '    return NULL;\n'
        '}\n'
        '\n'
        'static void on_download(GtkWidget *w, gpointer d) {\n'
        '    (void)w; (void)d;\n'
        '    GtkTreeSelection *sel =\n'
        '        gtk_tree_view_get_selection(\n'
        '            GTK_TREE_VIEW(pkg_tree_view));\n'
        '    GtkTreeIter iter;\n'
        '    GtkTreeModel *model;\n'
        '    if (gtk_tree_selection_get_selected(\n'
        '            sel, &model, &iter)) {\n'
        '        int *pkg_id = malloc(sizeof(int));\n'
        '        gtk_tree_model_get(model, &iter,\n'
        '                           0, pkg_id, -1);\n'
        '        pthread_t tid;\n'
        '        pthread_create(&tid, NULL,\n'
        '                       download_thread_func, pkg_id);\n'
        '        pthread_detach(tid);\n'
        '        gui_log("Download started...");\n'
        '    }\n'
        '}\n'
        '\n'
        'static void on_install(GtkWidget *w, gpointer d) {\n'
        '    (void)w; (void)d;\n'
        '    GtkTreeSelection *sel =\n'
        '        gtk_tree_view_get_selection(\n'
        '            GTK_TREE_VIEW(pkg_tree_view));\n'
        '    GtkTreeIter iter;\n'
        '    GtkTreeModel *model;\n'
        '    if (gtk_tree_selection_get_selected(\n'
        '            sel, &model, &iter)) {\n'
        '        gchar *fname;\n'
        '        gtk_tree_model_get(model, &iter,\n'
        '                           2, &fname, -1);\n'
        '        char path[MAX_PATH_LEN];\n'
        '        snprintf(path, sizeof(path),\n'
        '                 "%s%s", DOWNLOADS_DIR, fname);\n'
        '        auto_install(path);\n'
        '        gui_log("Installation triggered");\n'
        '        g_free(fname);\n'
        '    }\n'
        '}\n'
        '\n'
        'int main(int argc, char *argv[]) {\n'
        '    gtk_init(&argc, &argv);\n'
        '    GtkWidget *win = gtk_window_new(\n'
        '        GTK_WINDOW_TOPLEVEL);\n'
        '    gtk_window_set_title(GTK_WINDOW(win),\n'
        '        "Software Installer - Client");\n'
        '    gtk_window_set_default_size(\n'
        '        GTK_WINDOW(win), 800, 600);\n'
        '    g_signal_connect(win, "destroy",\n'
        '                     G_CALLBACK(gtk_main_quit), NULL);\n'
        '\n'
        '    GtkWidget *vbox = gtk_box_new(\n'
        '        GTK_ORIENTATION_VERTICAL, 5);\n'
        '    gtk_container_set_border_width(\n'
        '        GTK_CONTAINER(vbox), 10);\n'
        '    gtk_container_add(GTK_CONTAINER(win), vbox);\n'
        '\n'
        '    /* Connection bar */\n'
        '    GtkWidget *hbox = gtk_box_new(\n'
        '        GTK_ORIENTATION_HORIZONTAL, 5);\n'
        '    gtk_box_pack_start(GTK_BOX(vbox),\n'
        '                       hbox, FALSE, FALSE, 0);\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '        gtk_label_new("IP:"), FALSE, FALSE, 2);\n'
        '    ip_entry = gtk_entry_new();\n'
        '    gtk_entry_set_text(GTK_ENTRY(ip_entry),\n'
        '                       "127.0.0.1");\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '                       ip_entry, FALSE, FALSE, 2);\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '        gtk_label_new("Port:"), FALSE, FALSE, 2);\n'
        '    port_entry = gtk_entry_new();\n'
        '    gtk_entry_set_text(GTK_ENTRY(port_entry), "8080");\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '                       port_entry, FALSE, FALSE, 2);\n'
        '\n'
        '    connect_btn = gtk_button_new_with_label("Connect");\n'
        '    disconnect_btn = gtk_button_new_with_label(\n'
        '        "Disconnect");\n'
        '    gtk_widget_set_sensitive(disconnect_btn, FALSE);\n'
        '    g_signal_connect(connect_btn, "clicked",\n'
        '        G_CALLBACK(on_connect), NULL);\n'
        '    g_signal_connect(disconnect_btn, "clicked",\n'
        '        G_CALLBACK(on_disconnect), NULL);\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '                       connect_btn, FALSE, FALSE, 2);\n'
        '    gtk_box_pack_start(GTK_BOX(hbox),\n'
        '                       disconnect_btn, FALSE, FALSE, 2);\n'
        '\n'
        '    status_label = gtk_label_new("Disconnected");\n'
        '    gtk_box_pack_end(GTK_BOX(hbox),\n'
        '                     status_label, FALSE, FALSE, 5);\n'
        '\n'
        '    /* Package list */\n'
        '    pkg_store = gtk_list_store_new(4,\n'
        '        G_TYPE_INT, G_TYPE_STRING,\n'
        '        G_TYPE_STRING, G_TYPE_STRING);\n'
        '    pkg_tree_view = gtk_tree_view_new_with_model(\n'
        '        GTK_TREE_MODEL(pkg_store));\n'
        '\n'
        '    const char *cols[] = {"ID","Name","File","Size"};\n'
        '    for (int i = 0; i < 4; i++) {\n'
        '        GtkCellRenderer *r =\n'
        '            gtk_cell_renderer_text_new();\n'
        '        GtkTreeViewColumn *c =\n'
        '            gtk_tree_view_column_new_with_attributes(\n'
        '                cols[i], r, "text", i, NULL);\n'
        '        gtk_tree_view_append_column(\n'
        '            GTK_TREE_VIEW(pkg_tree_view), c);\n'
        '    }\n'
        '\n'
        '    GtkWidget *scroll = gtk_scrolled_window_new(\n'
        '        NULL, NULL);\n'
        '    gtk_container_add(GTK_CONTAINER(scroll),\n'
        '                      pkg_tree_view);\n'
        '    gtk_box_pack_start(GTK_BOX(vbox),\n'
        '                       scroll, TRUE, TRUE, 5);\n'
        '\n'
        '    /* Action buttons */\n'
        '    GtkWidget *btn_box = gtk_box_new(\n'
        '        GTK_ORIENTATION_HORIZONTAL, 5);\n'
        '    refresh_btn = gtk_button_new_with_label(\n'
        '        "Refresh List");\n'
        '    download_btn = gtk_button_new_with_label(\n'
        '        "Download");\n'
        '    install_btn = gtk_button_new_with_label(\n'
        '        "Install");\n'
        '    gtk_widget_set_sensitive(refresh_btn, FALSE);\n'
        '    gtk_widget_set_sensitive(download_btn, FALSE);\n'
        '    g_signal_connect(refresh_btn, "clicked",\n'
        '        G_CALLBACK(on_refresh), NULL);\n'
        '    g_signal_connect(download_btn, "clicked",\n'
        '        G_CALLBACK(on_download), NULL);\n'
        '    g_signal_connect(install_btn, "clicked",\n'
        '        G_CALLBACK(on_install), NULL);\n'
        '    gtk_box_pack_start(GTK_BOX(btn_box),\n'
        '                       refresh_btn, FALSE, FALSE, 2);\n'
        '    gtk_box_pack_start(GTK_BOX(btn_box),\n'
        '                       download_btn, FALSE, FALSE, 2);\n'
        '    gtk_box_pack_start(GTK_BOX(btn_box),\n'
        '                       install_btn, FALSE, FALSE, 2);\n'
        '    gtk_box_pack_start(GTK_BOX(vbox),\n'
        '                       btn_box, FALSE, FALSE, 0);\n'
        '\n'
        '    /* Progress bar */\n'
        '    progress_bar = gtk_progress_bar_new();\n'
        '    gtk_progress_bar_set_show_text(\n'
        '        GTK_PROGRESS_BAR(progress_bar), TRUE);\n'
        '    gtk_box_pack_start(GTK_BOX(vbox),\n'
        '                       progress_bar, FALSE, FALSE, 5);\n'
        '\n'
        '    /* Log area */\n'
        '    GtkWidget *log_scroll =\n'
        '        gtk_scrolled_window_new(NULL, NULL);\n'
        '    gtk_scrolled_window_set_min_content_height(\n'
        '        GTK_SCROLLED_WINDOW(log_scroll), 120);\n'
        '    log_view = gtk_text_view_new();\n'
        '    gtk_text_view_set_editable(\n'
        '        GTK_TEXT_VIEW(log_view), FALSE);\n'
        '    log_buf = gtk_text_view_get_buffer(\n'
        '        GTK_TEXT_VIEW(log_view));\n'
        '    gtk_container_add(\n'
        '        GTK_CONTAINER(log_scroll), log_view);\n'
        '    gtk_box_pack_start(GTK_BOX(vbox),\n'
        '                       log_scroll, FALSE, FALSE, 5);\n'
        '\n'
        '    gtk_widget_show_all(win);\n'
        '    gtk_main();\n'
        '    if (sockfd >= 0) disconnect(sockfd);\n'
        '    return 0;\n'
        '}',
        title="client/client_gui.c"
    )

    pdf.add_page()
    pdf.sub_title("Detailed Code Explanation")

    pdf.sub_sub_title("client.c - Networking Functions")
    pdf.body_text(
        "connect_to_server(): Creates a TCP socket and connects to the specified IP and port. "
        "inet_pton() converts the IP string (like '127.0.0.1') into binary form. connect() "
        "initiates the TCP three-way handshake with the server. Returns the socket fd on success "
        "or -1 on failure."
    )
    pdf.body_text(
        "request_list(): Sends the 'LIST' command string to the server, then waits for the "
        "response containing the pipe-delimited package data. The response is null-terminated "
        "and stored in the caller's buffer."
    )
    pdf.body_text(
        "request_download(): Sends 'DOWNLOAD <id>' to the server. The server responds with either "
        "'RESPONSE: OK <size>' or 'RESPONSE: ERROR'. On success, it parses the file size from "
        "the response and stores it via the file_size pointer for the caller to use."
    )
    pdf.body_text(
        "parse_package_list(): Takes the raw text response from request_list() and parses it into "
        "an array of Package structs. Uses strdup() to create a modifiable copy (since strtok "
        "modifies the string), then tokenizes by newline and uses sscanf with the pipe-delimited "
        "format. The copy is freed after parsing to avoid memory leaks."
    )
    pdf.body_text(
        "disconnect(): Sends CMD_BYE to inform the server of a clean disconnect, then closes "
        "the socket. This allows the server to remove the client from its tracking array gracefully."
    )

    pdf.sub_sub_title("client_gui.c - GTK 3 Client Interface")
    pdf.body_text(
        "The GUI uses GtkListStore and GtkTreeView to display packages in a table with columns "
        "for ID, Name, File, and Size. GtkProgressBar shows real-time download progress. A "
        "GtkTextView serves as the activity log."
    )
    pdf.body_text(
        "Download Threading: The download runs in a separate thread to prevent the GUI from freezing. "
        "download_progress() is called by the downloader for each chunk received. It creates a "
        "ProgressData struct on the heap and uses g_idle_add() to schedule the GTK progress bar "
        "update on the main thread - the same thread-safety pattern used in the server GUI."
    )
    pdf.body_text(
        "Widget Sensitivity: Buttons are enabled/disabled based on state - you can't disconnect "
        "if not connected, can't download if no packages are loaded, etc. This prevents users from "
        "triggering operations in invalid states."
    )

    pdf.sub_title("How This Part Connects to the Whole System")
    pdf.body_text(
        "The client is the user-facing application that ties together all other components. "
        "client.c uses protocol.h constants to send commands the server understands. The GUI calls "
        "request_list() and request_download() from client.c, then calls receive_file() from "
        "downloader.c (Utsho's code) for the actual data transfer, and auto_install() from "
        "installer.c (Jowel's code) to install downloaded packages. It's the orchestrator of the "
        "entire client-side workflow."
    )

    pdf.sub_title("Presentation Talking Points")
    pdf.bullet("I separated networking logic (client.c) from GUI logic (client_gui.c) for clean "
               "modularity - the networking functions can be tested independently of GTK.")
    pdf.bullet("The download runs in a background thread with progress callbacks, keeping the GUI "
               "responsive throughout large file transfers.")
    pdf.bullet("I used GtkListStore/TreeView for the package list, providing a sortable, "
               "scrollable table that's familiar to users.")
    pdf.bullet("Widget sensitivity management (enabling/disabling buttons) prevents invalid "
               "operations and guides the user through the correct workflow.")
    pdf.bullet("The parse_package_list function handles the text-to-struct deserialization, "
               "matching the server's serialization format exactly.")

    pdf.add_page()
    pdf.sub_title("Expected Teacher Questions & Model Answers")

    pdf.qa_pair(1,
        "What is inet_pton and why is it used instead of inet_addr?",
        "inet_pton (presentation to network) converts an IP address string to binary form. It's "
        "the modern replacement for inet_addr. inet_pton supports both IPv4 and IPv6, has better "
        "error handling (returns 0 for invalid addresses, -1 for errors), and is reentrant (thread-safe). "
        "inet_addr is deprecated and can't distinguish between an error and the broadcast address 255.255.255.255."
    )
    pdf.qa_pair(2,
        "Why do you use strdup() in parse_package_list?",
        "strtok() modifies the string it tokenizes by replacing delimiters with null bytes. The "
        "original data pointer might point to a buffer that shouldn't be modified, or might be needed "
        "again. strdup() creates a heap-allocated copy that we can safely modify and then free() "
        "when done. This prevents bugs and memory corruption."
    )
    pdf.qa_pair(3,
        "How does the progress callback work between the downloader and GUI?",
        "The GUI passes download_progress() as a function pointer to receive_file(). The downloader "
        "calls this function after each recv() chunk with the bytes received so far and total size. "
        "download_progress() calculates the fraction, creates a ProgressData struct on the heap, "
        "and calls g_idle_add() to schedule the GUI update on the main thread. This chain allows "
        "real-time progress without the downloader knowing anything about GTK."
    )
    pdf.qa_pair(4,
        "What is the TCP three-way handshake that connect() performs?",
        "When connect() is called: (1) The client sends a SYN packet to the server. (2) The server "
        "responds with SYN-ACK. (3) The client sends ACK. After these three packets, the connection "
        "is established and data can flow in both directions. This is handled automatically by the "
        "OS kernel - connect() blocks until the handshake completes or fails."
    )
    pdf.qa_pair(5,
        "Why do you run the download in a separate thread?",
        "GTK's main loop (gtk_main) runs on the main thread. If we call receive_file() on the main "
        "thread, the entire GUI freezes until the download completes because the event loop can't "
        "process events. Running the download in a separate thread allows the GUI to remain "
        "responsive - the progress bar updates, buttons work, and the user can interact normally."
    )
    pdf.qa_pair(6,
        "How does the client know how much data to receive for a file download?",
        "When the client sends 'DOWNLOAD <id>', the server responds with 'RESPONSE: OK <size>' where "
        "size is the file size in bytes. The client parses this size from the response in "
        "request_download() and passes it to receive_file(). The downloader then loops recv() "
        "until total_received equals file_size, knowing exactly when the transfer is complete."
    )
    pdf.qa_pair(7,
        "What happens if the user clicks Download without selecting a package?",
        "gtk_tree_selection_get_selected() returns FALSE if nothing is selected in the TreeView. "
        "The on_download handler checks this return value, and if FALSE, it simply does nothing - "
        "the download thread is never created. This is a safe no-op."
    )
    pdf.qa_pair(8,
        "Why is the GtkListStore used instead of a simple text area for packages?",
        "GtkListStore with GtkTreeView provides a structured table with separate columns for ID, "
        "Name, File, and Size. Users can click column headers to sort, select individual rows, "
        "and the data is stored in a model-view pattern that separates data from presentation. "
        "A text area would require manual parsing to figure out which package the user wants."
    )
    pdf.qa_pair(9,
        "What is the role of htons() in the socket address setup?",
        "htons() means 'host to network short' - it converts the port number from host byte order "
        "to network byte order (big-endian). Different CPU architectures may use different byte "
        "orders (x86 is little-endian). Network protocols standardize on big-endian. Without this "
        "conversion, the client might connect to the wrong port on a little-endian machine."
    )
    pdf.qa_pair(10,
        "How would you modify the client to support downloading multiple packages simultaneously?",
        "Currently, each download uses the shared sockfd. To support parallel downloads, each "
        "download would need its own socket connection to the server. The client would call "
        "connect_to_server() for each download, receive the file on that dedicated connection, "
        "then close it. The server already supports multiple concurrent clients via threading, "
        "so no server changes would be needed."
    )


def build_person4(pdf):
    pdf.add_page()
    pdf.add_toc_entry("Person 4 - Utsho (Network & Socket Programmer)")
    pdf.section_title("Person 4: Reyaid Bin Alam Utsho (232-15-508)")
    pdf.sub_title("Role: Network & Socket Programmer")
    pdf.body_text(
        "Utsho implemented the core file transfer protocol that enables reliable binary data "
        "transmission between server and client over TCP sockets. His code handles the actual "
        "byte-level sending and receiving of software package files, including chunked transfer, "
        "partial send handling, progress reporting via callbacks, and directory creation on the "
        "client side. This is the data pipeline that makes the entire download feature work."
    )
    pdf.ln(3)

    pdf.sub_title("Files Responsible For:")
    pdf.bullet("server/file_handler.h - Server-side file transfer declarations")
    pdf.bullet("server/file_handler.c - Server-side: send_file(), get_file_size()")
    pdf.bullet("client/downloader.h - Client-side file receiving declarations")
    pdf.bullet("client/downloader.c - Client-side: receive_file(), ensure_directory()")
    pdf.ln(3)

    pdf.sub_title("Code: server/file_handler.h")
    pdf.code_block(
        '#ifndef FILE_HANDLER_H\n'
        '#define FILE_HANDLER_H\n'
        '\n'
        '#include "../common/protocol.h"\n'
        '\n'
        'int send_file(int sockfd, const char *filepath,\n'
        '              progress_callback cb, void *user_data);\n'
        'long get_file_size(const char *filepath);\n'
        '\n'
        '#endif',
        title="server/file_handler.h"
    )

    pdf.sub_title("Code: server/file_handler.c")
    pdf.code_block(
        '#include "file_handler.h"\n'
        '#include "../common/utils.h"\n'
        '#include <stdio.h>\n'
        '#include <stdlib.h>\n'
        '#include <string.h>\n'
        '#include <sys/socket.h>\n'
        '#include <sys/stat.h>\n'
        '\n'
        'long get_file_size(const char *filepath) {\n'
        '    struct stat st;\n'
        '    if (stat(filepath, &st) != 0)\n'
        '        return -1;\n'
        '    return (long)st.st_size;\n'
        '}\n'
        '\n'
        'int send_file(int sockfd, const char *filepath,\n'
        '              progress_callback cb, void *user_data) {\n'
        '    FILE *fp = fopen(filepath, "rb");\n'
        '    if (!fp) {\n'
        '        log_message("Cannot open file: %s", filepath);\n'
        '        return -1;\n'
        '    }\n'
        '\n'
        '    long file_size = get_file_size(filepath);\n'
        '    if (file_size < 0) {\n'
        '        fclose(fp);\n'
        '        return -1;\n'
        '    }\n'
        '\n'
        '    char buffer[BUFFER_SIZE];\n'
        '    long total_sent = 0;\n'
        '    size_t bytes_read;\n'
        '\n'
        '    while ((bytes_read = fread(buffer, 1,\n'
        '                               BUFFER_SIZE, fp)) > 0) {\n'
        '        size_t offset = 0;\n'
        '        while (offset < bytes_read) {\n'
        '            ssize_t sent = send(sockfd,\n'
        '                buffer + offset,\n'
        '                bytes_read - offset, 0);\n'
        '            if (sent <= 0) {\n'
        '                log_message("Error sending file");\n'
        '                fclose(fp);\n'
        '                return -1;\n'
        '            }\n'
        '            offset += sent;\n'
        '            total_sent += sent;\n'
        '            if (cb)\n'
        '                cb(total_sent, file_size,\n'
        '                   user_data);\n'
        '        }\n'
        '    }\n'
        '\n'
        '    fclose(fp);\n'
        '    log_message("File sent: %s (%ld bytes)",\n'
        '                filepath, total_sent);\n'
        '    return 0;\n'
        '}',
        title="server/file_handler.c"
    )

    pdf.sub_title("Code: client/downloader.h")
    pdf.code_block(
        '#ifndef DOWNLOADER_H\n'
        '#define DOWNLOADER_H\n'
        '\n'
        '#include "../common/protocol.h"\n'
        '\n'
        'int receive_file(int sockfd, const char *save_path,\n'
        '    long file_size, progress_callback cb,\n'
        '    void *user_data);\n'
        '\n'
        '#endif',
        title="client/downloader.h"
    )

    pdf.sub_title("Code: client/downloader.c")
    pdf.code_block(
        '#include "downloader.h"\n'
        '#include "../common/utils.h"\n'
        '#include <stdio.h>\n'
        '#include <stdlib.h>\n'
        '#include <string.h>\n'
        '#include <sys/socket.h>\n'
        '#include <sys/stat.h>\n'
        '#include <errno.h>\n'
        '\n'
        'static int ensure_directory(const char *dir) {\n'
        '    struct stat st;\n'
        '    if (stat(dir, &st) == -1) {\n'
        '        if (mkdir(dir, 0755) == -1\n'
        '            && errno != EEXIST) {\n'
        '            log_message(\n'
        '                "Failed to create dir: %s", dir);\n'
        '            return -1;\n'
        '        }\n'
        '    }\n'
        '    return 0;\n'
        '}\n'
        '\n'
        'int receive_file(int sockfd,\n'
        '                 const char *save_path,\n'
        '                 long file_size,\n'
        '                 progress_callback cb,\n'
        '                 void *user_data) {\n'
        '    ensure_directory(DOWNLOADS_DIR);\n'
        '\n'
        '    FILE *fp = fopen(save_path, "wb");\n'
        '    if (!fp) {\n'
        '        log_message("Cannot create file: %s",\n'
        '                    save_path);\n'
        '        return -1;\n'
        '    }\n'
        '\n'
        '    char buffer[BUFFER_SIZE];\n'
        '    long total_received = 0;\n'
        '\n'
        '    while (total_received < file_size) {\n'
        '        long remaining = file_size - total_received;\n'
        '        size_t to_read = remaining < BUFFER_SIZE\n'
        '                         ? remaining : BUFFER_SIZE;\n'
        '        ssize_t n = recv(sockfd, buffer, to_read, 0);\n'
        '        if (n <= 0) {\n'
        '            log_message(\n'
        '                "Connection lost at %ld/%ld bytes",\n'
        '                total_received, file_size);\n'
        '            fclose(fp);\n'
        '            return -1;\n'
        '        }\n'
        '        fwrite(buffer, 1, n, fp);\n'
        '        total_received += n;\n'
        '        if (cb)\n'
        '            cb(total_received, file_size,\n'
        '               user_data);\n'
        '    }\n'
        '\n'
        '    fclose(fp);\n'
        '    log_message("File received: %s (%ld bytes)",\n'
        '                save_path, total_received);\n'
        '    return 0;\n'
        '}',
        title="client/downloader.c"
    )

    pdf.add_page()
    pdf.sub_title("Detailed Code Explanation")

    pdf.sub_sub_title("file_handler.c - Server-Side File Sending")
    pdf.body_text(
        "get_file_size(): Uses the POSIX stat() system call to retrieve file metadata. The struct "
        "stat contains st_size which gives the file size in bytes. This is called before sending to "
        "know the total size, and the server sends this size to the client so it knows how much data "
        "to expect."
    )
    pdf.body_text(
        "send_file() - Outer Loop (fread): Reads the file in chunks of BUFFER_SIZE (4096 bytes) "
        "using fread(). This is disk I/O - reading from the filesystem into a memory buffer. fread "
        "returns the number of bytes actually read, which may be less than BUFFER_SIZE for the last "
        "chunk of the file."
    )
    pdf.body_text(
        "send_file() - Inner Loop (partial send handling): This is the most critical part. The "
        "send() system call does NOT guarantee that all bytes are sent in one call. It may send "
        "fewer bytes than requested (a 'partial send') due to kernel buffer limits or network "
        "conditions. The inner loop tracks an offset and keeps calling send() with the remaining "
        "unsent bytes until the entire chunk is transmitted. Without this loop, data would be lost."
    )
    pdf.body_text(
        "Error Handling: If send() returns 0 or -1, the connection is broken. The function logs the "
        "error, closes the file, and returns -1. The progress callback (if provided) is called after "
        "each successful partial send with total_sent and file_size, enabling real-time progress tracking."
    )

    pdf.sub_sub_title("downloader.c - Client-Side File Receiving")
    pdf.body_text(
        "ensure_directory(): Checks if the downloads directory exists using stat(). If it doesn't, "
        "creates it with mkdir() and permissions 0755 (owner: rwx, group/others: rx). The EEXIST "
        "check handles the race condition where another thread creates the directory between the "
        "stat check and mkdir call."
    )
    pdf.body_text(
        "receive_file() Loop: Calculates the remaining bytes to receive, limits recv() to either "
        "the remaining amount or BUFFER_SIZE (whichever is smaller). This prevents reading beyond "
        "the file boundary. Each recv() call may return fewer bytes than requested - this is normal "
        "TCP behavior. The received data is written to the file with fwrite(), the counter is updated, "
        "and the progress callback reports the new total."
    )
    pdf.body_text(
        "Connection Loss Detection: If recv() returns 0 (clean close) or -1 (error) before "
        "total_received reaches file_size, it means the connection was lost mid-transfer. The function "
        "logs the failure point (useful for debugging) and returns -1."
    )

    pdf.sub_title("How This Part Connects to the Whole System")
    pdf.body_text(
        "The file transfer modules are the data pipeline connecting server and client. When a user "
        "clicks Download in the client GUI (Mahi's code), the client networking code sends a "
        "DOWNLOAD command, the server's handle_client thread (Maruf's code) calls send_file() to "
        "stream the file, and the client calls receive_file() to save it. Both use BUFFER_SIZE from "
        "protocol.h (Shuvo's code) to ensure matching chunk sizes. The progress_callback typedef "
        "from protocol.h enables the GUI to show real-time progress without tight coupling."
    )

    pdf.sub_title("Presentation Talking Points")
    pdf.bullet("I implemented a reliable file transfer protocol that handles partial sends and "
               "receives - a real challenge in TCP socket programming that many beginners miss.")
    pdf.bullet("The chunked transfer approach (4096 bytes at a time) works efficiently for any "
               "file size - from a 1KB script to a 500MB application.")
    pdf.bullet("Progress callbacks decouple the transfer logic from the GUI - the downloader "
               "reports progress without knowing about GTK at all.")
    pdf.bullet("Error handling at every I/O operation ensures the system fails gracefully - "
               "partial downloads are detected and logged with exact byte counts.")
    pdf.bullet("The ensure_directory() function demonstrates defensive programming - creating "
               "required directories at runtime rather than assuming they exist.")

    pdf.add_page()
    pdf.sub_title("Expected Teacher Questions & Model Answers")

    pdf.qa_pair(1,
        "Why do you need the inner loop in send_file? Can't you just call send() once?",
        "No. The send() system call may perform a 'partial send' - sending fewer bytes than "
        "requested. This happens when the kernel's TCP send buffer is full or during network "
        "congestion. For example, if you try to send 4096 bytes, send() might only send 2048. "
        "Without the inner loop, the remaining 2048 bytes would be silently lost, corrupting the "
        "file. The inner loop guarantees every byte is transmitted."
    )
    pdf.qa_pair(2,
        "What is the difference between send()/recv() and write()/read() for sockets?",
        "Functionally, they're very similar for basic usage. send()/recv() are socket-specific and "
        "accept an additional 'flags' parameter (like MSG_DONTWAIT for non-blocking, MSG_PEEK to "
        "look at data without consuming it). write()/read() are generic POSIX file descriptor "
        "operations. We use send()/recv() because they're semantically clearer for socket "
        "programming and allow future use of socket-specific flags."
    )
    pdf.qa_pair(3,
        "Why do you open the file in 'rb' mode (fopen with 'rb')?",
        "The 'b' flag means binary mode. On Linux, there's no difference between text and binary "
        "mode. However, on Windows, text mode translates newline characters (\\n to \\r\\n). Since "
        "we're transferring binary files (.deb, .AppImage, etc.), any byte translation would corrupt "
        "them. Using 'rb' and 'wb' ensures no translation on any platform - a good practice."
    )
    pdf.qa_pair(4,
        "How does the receiver know when the file transfer is complete?",
        "Before the file data is sent, the server sends the file size as part of the RESP_OK message. "
        "The client parses this size in request_download(). receive_file() then loops until "
        "total_received equals file_size. This is a length-prefixed protocol - the receiver knows "
        "the exact expected size in advance, so it knows exactly when to stop reading."
    )
    pdf.qa_pair(5,
        "What happens if the network is slow? Does the transfer fail?",
        "No. TCP handles retransmission and flow control automatically. recv() will simply block "
        "(wait) until data arrives. The transfer will be slow but complete. My code handles this "
        "because both the send loop and receive loop are tolerant of partial operations - they "
        "just keep looping until all bytes are transferred. The only failure case is if the "
        "connection is actually broken (recv returns 0 or -1)."
    )
    pdf.qa_pair(6,
        "What does stat() return and why use it instead of fseek/ftell?",
        "stat() is a system call that retrieves file metadata from the filesystem without opening "
        "the file. It populates a struct stat with size, permissions, timestamps, etc. fseek/ftell "
        "require opening the file first. Using stat() is more efficient for just getting the size "
        "and works even on files we might not have read permission for (we can still see the size). "
        "It's also usable with non-regular files where seeking doesn't work."
    )
    pdf.qa_pair(7,
        "Why is BUFFER_SIZE 4096 and not something larger like 64KB?",
        "4096 bytes (4KB) matches the default memory page size on most architectures. It provides "
        "a good balance: large enough for reasonable throughput (we make fewer system calls than "
        "with tiny buffers), but small enough to keep memory usage low per connection. For 50 "
        "concurrent clients, we use 50 x 4KB = 200KB total buffer memory. With 64KB buffers, "
        "that would be 3.2MB. For a LAN application, the bottleneck is usually not the buffer size."
    )
    pdf.qa_pair(8,
        "What is the purpose of errno and EEXIST in ensure_directory?",
        "errno is a global variable set by system calls when they fail. After mkdir() fails, we "
        "check if errno equals EEXIST, which means 'the directory already exists.' This is not a "
        "real error - another thread might have created the directory between our stat() check and "
        "mkdir() call (a TOCTOU race condition). By checking EEXIST, we handle this gracefully "
        "instead of reporting a false error."
    )
    pdf.qa_pair(9,
        "Could this file transfer work over the internet, not just localhost?",
        "Yes. TCP handles routing, retransmission, and ordering regardless of network distance. "
        "However, for the internet, we'd want to add: (1) encryption using TLS/SSL to prevent "
        "eavesdropping, (2) authentication to verify client identity, (3) resume capability for "
        "interrupted transfers, and (4) checksums to verify file integrity. Our current "
        "implementation works correctly but is designed for trusted LAN environments."
    )
    pdf.qa_pair(10,
        "Why does receive_file limit recv() to 'remaining' bytes when near the end?",
        "Without this limit, the last recv() call might try to read BUFFER_SIZE bytes but the "
        "remaining file data is less than that. If there's additional data in the TCP stream after "
        "the file (like the next command's response), recv() could read beyond the file boundary "
        "and mix file data with protocol data. Limiting to 'remaining' ensures we read exactly "
        "the file and nothing more."
    )


def build_person5(pdf):
    pdf.add_page()
    pdf.add_toc_entry("Person 5 - Jowel (Testing & Documentation)")
    pdf.section_title("Person 5: Ikramul Hasan Jowel (232-15-819)")
    pdf.sub_title("Role: Testing & Documentation Engineer")
    pdf.body_text(
        "Jowel implemented the package management system that handles loading, listing, searching, "
        "and adding software packages on the server side, as well as the auto-installer on the "
        "client side that detects file types and executes the appropriate installation commands. "
        "He also performed end-to-end testing of all components to ensure the complete system works "
        "together seamlessly."
    )
    pdf.ln(3)

    pdf.sub_title("Files Responsible For:")
    pdf.bullet("server/package_manager.h - Package management function declarations")
    pdf.bullet("server/package_manager.c - Package loading, listing, searching, adding")
    pdf.bullet("client/installer.h - Auto-installer function declarations")
    pdf.bullet("client/installer.c - File type detection and automatic installation")
    pdf.ln(3)

    pdf.sub_title("Code: server/package_manager.h")
    pdf.code_block(
        '#ifndef PACKAGE_MANAGER_H\n'
        '#define PACKAGE_MANAGER_H\n'
        '\n'
        '#include <stddef.h>\n'
        '#include "../common/protocol.h"\n'
        '\n'
        'int load_packages(const char *packages_file,\n'
        '    Package *packages, int max_count);\n'
        'int list_packages(Package *packages, int count,\n'
        '    char *buf, size_t buf_size);\n'
        'Package *find_package(Package *packages,\n'
        '    int count, int id);\n'
        'int reload_packages(const char *packages_file,\n'
        '    Package *packages, int max_count);\n'
        'int add_package(const char *packages_file,\n'
        '    const char *name, const char *filename,\n'
        '    long size);\n'
        '\n'
        '#endif',
        title="server/package_manager.h"
    )

    pdf.sub_title("Code: server/package_manager.c")
    pdf.code_block(
        '#include "package_manager.h"\n'
        '#include "../common/utils.h"\n'
        '#include <stdio.h>\n'
        '#include <stdlib.h>\n'
        '#include <string.h>\n'
        '\n'
        'int load_packages(const char *packages_file,\n'
        '                  Package *packages,\n'
        '                  int max_count) {\n'
        '    FILE *fp = fopen(packages_file, "r");\n'
        '    if (!fp) {\n'
        '        log_message("Cannot open: %s",\n'
        '                    packages_file);\n'
        '        return 0;\n'
        '    }\n'
        '    char line[MAX_LINE_LEN];\n'
        '    int count = 0;\n'
        '    while (fgets(line, sizeof(line), fp)\n'
        '           && count < max_count) {\n'
        '        trim_newline(line);\n'
        '        if (strlen(line) == 0) continue;\n'
        '        int id;\n'
        '        char name[MAX_FILENAME];\n'
        '        char filename[MAX_FILENAME];\n'
        '        long size;\n'
        '        if (sscanf(line, "%d|%[^|]|%[^|]|%ld",\n'
        '            &id, name, filename, &size) == 4) {\n'
        '            packages[count].id = id;\n'
        '            strncpy(packages[count].name,\n'
        '                    name, MAX_FILENAME - 1);\n'
        '            strncpy(packages[count].filename,\n'
        '                    filename, MAX_FILENAME - 1);\n'
        '            packages[count].size = size;\n'
        '            count++;\n'
        '        }\n'
        '    }\n'
        '    fclose(fp);\n'
        '    log_message("Loaded %d packages", count);\n'
        '    return count;\n'
        '}\n'
        '\n'
        'int list_packages(Package *packages, int count,\n'
        '                  char *buf, size_t buf_size) {\n'
        '    buf[0] = \'\\0\';\n'
        '    size_t offset = 0;\n'
        '    for (int i = 0; i < count; i++) {\n'
        '        char size_str[64];\n'
        '        format_size(packages[i].size,\n'
        '                    size_str, sizeof(size_str));\n'
        '        int written = snprintf(buf + offset,\n'
        '            buf_size - offset,\n'
        '            "%d|%s|%s|%ld\\n",\n'
        '            packages[i].id, packages[i].name,\n'
        '            packages[i].filename,\n'
        '            packages[i].size);\n'
        '        if (written < 0\n'
        '            || (size_t)written >= buf_size-offset)\n'
        '            break;\n'
        '        offset += written;\n'
        '    }\n'
        '    return count;\n'
        '}\n'
        '\n'
        'Package *find_package(Package *packages,\n'
        '                      int count, int id) {\n'
        '    for (int i = 0; i < count; i++)\n'
        '        if (packages[i].id == id)\n'
        '            return &packages[i];\n'
        '    return NULL;\n'
        '}\n'
        '\n'
        'int reload_packages(const char *packages_file,\n'
        '                    Package *packages,\n'
        '                    int max_count) {\n'
        '    return load_packages(packages_file,\n'
        '                         packages, max_count);\n'
        '}\n'
        '\n'
        'int add_package(const char *packages_file,\n'
        '                const char *name,\n'
        '                const char *filename,\n'
        '                long size) {\n'
        '    Package packages[MAX_PACKAGES];\n'
        '    int count = load_packages(packages_file,\n'
        '                              packages,\n'
        '                              MAX_PACKAGES);\n'
        '    int new_id = 1;\n'
        '    for (int i = 0; i < count; i++)\n'
        '        if (packages[i].id >= new_id)\n'
        '            new_id = packages[i].id + 1;\n'
        '    FILE *fp = fopen(packages_file, "a");\n'
        '    if (!fp) {\n'
        '        log_message("Cannot write: %s",\n'
        '                    packages_file);\n'
        '        return -1;\n'
        '    }\n'
        '    fprintf(fp, "%d|%s|%s|%ld\\n",\n'
        '            new_id, name, filename, size);\n'
        '    fclose(fp);\n'
        '    log_message("Added: %d|%s", new_id, name);\n'
        '    return new_id;\n'
        '}',
        title="server/package_manager.c"
    )

    pdf.sub_title("Code: client/installer.h")
    pdf.code_block(
        '#ifndef INSTALLER_H\n'
        '#define INSTALLER_H\n'
        '\n'
        'int auto_install(const char *filepath);\n'
        'const char *get_install_command(\n'
        '    const char *filepath);\n'
        '\n'
        '#endif',
        title="client/installer.h"
    )

    pdf.sub_title("Code: client/installer.c")
    pdf.code_block(
        '#include "installer.h"\n'
        '#include "../common/utils.h"\n'
        '#include <stdio.h>\n'
        '#include <stdlib.h>\n'
        '#include <string.h>\n'
        '\n'
        'static const char *get_extension(\n'
        '    const char *filename) {\n'
        '    const char *dot = strrchr(filename, \'.\');\n'
        '    return dot ? dot : "";\n'
        '}\n'
        '\n'
        'const char *get_install_command(\n'
        '    const char *filepath) {\n'
        '    const char *ext = get_extension(filepath);\n'
        '    if (strcmp(ext, ".deb") == 0)\n'
        '        return "sudo dpkg -i";\n'
        '    else if (strcmp(ext, ".rpm") == 0)\n'
        '        return "sudo rpm -i";\n'
        '    else if (strcmp(ext, ".sh") == 0)\n'
        '        return "chmod +x %s && ./%s";\n'
        '    else if (strcmp(ext, ".AppImage") == 0)\n'
        '        return "chmod +x";\n'
        '    else if (strcmp(ext, ".gz") == 0\n'
        '             || strcmp(ext, ".tgz") == 0)\n'
        '        return "tar -xzf";\n'
        '    else if (strcmp(ext, ".bz2") == 0)\n'
        '        return "tar -xjf";\n'
        '    else if (strcmp(ext, ".xz") == 0)\n'
        '        return "tar -xJf";\n'
        '    return NULL;\n'
        '}\n'
        '\n'
        'int auto_install(const char *filepath) {\n'
        '    if (!filepath) return -1;\n'
        '    const char *ext = get_extension(filepath);\n'
        '    char command[1024];\n'
        '    log_message("Auto-installing: %s", filepath);\n'
        '\n'
        '    if (strcmp(ext, ".deb") == 0) {\n'
        '        snprintf(command, sizeof(command),\n'
        '            "sudo dpkg -i \\"%s\\" 2>&1",\n'
        '            filepath);\n'
        '    } else if (strcmp(ext, ".rpm") == 0) {\n'
        '        snprintf(command, sizeof(command),\n'
        '            "sudo rpm -i \\"%s\\" 2>&1",\n'
        '            filepath);\n'
        '    } else if (strcmp(ext, ".sh") == 0) {\n'
        '        snprintf(command, sizeof(command),\n'
        '            "sed -i \'s/\\\\r$//\' \\"%s\\" && "\n'
        '            "chmod +x \\"%s\\" && "\n'
        '            "bash \\"%s\\" 2>&1",\n'
        '            filepath, filepath, filepath);\n'
        '    } else if (strcmp(ext, ".AppImage") == 0) {\n'
        '        snprintf(command, sizeof(command),\n'
        '            "chmod +x \\"%s\\" && \\"%s\\" 2>&1",\n'
        '            filepath, filepath);\n'
        '    } else if (strcmp(ext, ".gz") == 0\n'
        '               || strcmp(ext, ".tgz") == 0) {\n'
        '        snprintf(command, sizeof(command),\n'
        '            "tar -xzf \\"%s\\" -C \\"%s\\" 2>&1",\n'
        '            filepath, "downloads/");\n'
        '    } else {\n'
        '        log_message("Unknown type: %s", ext);\n'
        '        return -1;\n'
        '    }\n'
        '\n'
        '    log_message("Running: %s", command);\n'
        '    int ret = system(command);\n'
        '    if (ret == 0)\n'
        '        log_message("Install OK: %s", filepath);\n'
        '    else\n'
        '        log_message("Install failed (%d): %s",\n'
        '                    ret, filepath);\n'
        '    return ret;\n'
        '}',
        title="client/installer.c"
    )

    pdf.add_page()
    pdf.sub_title("Detailed Code Explanation")

    pdf.sub_sub_title("package_manager.c - Server Package Catalog")
    pdf.body_text(
        "load_packages(): Reads packages.txt line by line. Each line has the format 'id|name|filename|size'. "
        "It uses sscanf with the pattern '%d|%[^|]|%[^|]|%ld' where %[^|] reads everything until the next "
        "pipe character. trim_newline() removes any trailing newline/carriage return. Empty lines are "
        "skipped. The function returns the count of successfully parsed packages."
    )
    pdf.body_text(
        "list_packages(): Serializes the packages array back into pipe-delimited text for sending to "
        "clients. It uses snprintf with careful buffer overflow prevention - checking if the written "
        "bytes would exceed the remaining buffer space. The offset-based writing ensures all packages "
        "are concatenated into a single string."
    )
    pdf.body_text(
        "find_package(): Simple linear search by ID. Returns a pointer to the matching Package in the "
        "array, or NULL if not found. Since MAX_PACKAGES is 100, a linear search is perfectly efficient."
    )
    pdf.body_text(
        "add_package(): Auto-generates a new ID by finding the maximum existing ID and adding 1. Opens "
        "packages.txt in append mode ('a') so existing entries aren't overwritten. Writes the new "
        "package in the same pipe-delimited format."
    )

    pdf.sub_sub_title("installer.c - Automatic Software Installation")
    pdf.body_text(
        "get_extension(): Uses strrchr() to find the last dot in the filename, returning the extension "
        "including the dot (e.g., '.deb'). If there's no dot, returns an empty string."
    )
    pdf.body_text(
        "auto_install(): The core function that detects file types and runs appropriate system commands:\n"
        "- .deb files: Uses 'sudo dpkg -i' (Debian package manager)\n"
        "- .rpm files: Uses 'sudo rpm -i' (Red Hat package manager)\n"
        "- .sh scripts: First removes Windows line endings with sed, makes executable with chmod, "
        "then runs with bash\n"
        "- .AppImage: Makes executable with chmod then runs directly\n"
        "- .gz/.tgz: Extracts with 'tar -xzf' to the downloads directory"
    )
    pdf.body_text(
        "The system() call executes the command in a subshell and returns the exit code. A return "
        "value of 0 means success. The '2>&1' redirection captures both stdout and stderr. All "
        "filenames are quoted with escaped double quotes to handle filenames with spaces."
    )

    pdf.sub_title("How This Part Connects to the Whole System")
    pdf.body_text(
        "The package manager is called by the server (Maruf's code): load_packages() at startup, "
        "list_packages() when a client sends LIST, find_package() when a client sends DOWNLOAD. "
        "The installer is called by the client GUI (Mahi's code) when the user clicks Install. "
        "Both modules use the Package struct from protocol.h (Shuvo's code) and logging from "
        "utils.c. The installer is the final step in the pipeline: browse -> download -> install."
    )

    pdf.sub_title("Presentation Talking Points")
    pdf.bullet("The package manager uses a simple but effective text-based database (packages.txt) "
               "that's human-readable and easy to edit manually.")
    pdf.bullet("I designed the auto-installer to handle multiple package formats (.deb, .rpm, .sh, "
               ".AppImage, .tar.gz) - covering the most common Linux software distribution methods.")
    pdf.bullet("The sed command for .sh files (removing Windows line endings) shows attention to "
               "real-world issues - scripts downloaded from the internet often have \\r\\n line endings.")
    pdf.bullet("I tested the entire system end-to-end: starting the server, connecting the client, "
               "listing packages, downloading files, and verifying the installed software works.")
    pdf.bullet("Buffer overflow prevention in list_packages() (checking snprintf return values) "
               "demonstrates defensive coding practices.")

    pdf.add_page()
    pdf.sub_title("Expected Teacher Questions & Model Answers")

    pdf.qa_pair(1,
        "Why use sscanf with %[^|] instead of strtok?",
        "The %[^|] format specifier reads all characters until it hits a pipe, which perfectly "
        "matches our pipe-delimited format. It allows us to parse all four fields in a single "
        "sscanf call and validate the format simultaneously (sscanf returns the number of "
        "successfully matched fields). strtok would require multiple calls and manual type "
        "conversion with atoi/atol for the numeric fields."
    )
    pdf.qa_pair(2,
        "Is system() safe to use for installation? What are the risks?",
        "system() executes a command in a subshell (/bin/sh). The main risk is command injection: "
        "if the filename contained characters like '; rm -rf /', it could execute arbitrary commands. "
        "We mitigate this by quoting the filepath in double quotes. In a production system, you'd "
        "use execvp() with explicit arguments to completely avoid shell interpretation, or validate "
        "filenames with a whitelist of allowed characters."
    )
    pdf.qa_pair(3,
        "What does the 2>&1 redirection in the install commands do?",
        "2>&1 redirects stderr (file descriptor 2) to stdout (file descriptor 1). This means both "
        "normal output and error messages go to the same stream. system() captures the exit code "
        "but not the output, so this redirection ensures error messages appear in the terminal "
        "for debugging rather than being silently lost."
    )
    pdf.qa_pair(4,
        "Why does add_package open the file in append mode instead of rewriting it?",
        "Append mode ('a') adds new data at the end of the file without touching existing entries. "
        "Rewriting would require reading all packages, adding the new one, then writing everything "
        "back - more complex and error-prone (a crash during rewrite could corrupt the whole file). "
        "Appending is also faster and atomic at the filesystem level for single writes."
    )
    pdf.qa_pair(5,
        "How does strncpy differ from strcpy and why is it used here?",
        "strcpy copies until it finds a null terminator with no length limit, which can overflow "
        "the destination buffer if the source is too long. strncpy copies at most n-1 characters "
        "and prevents buffer overflow. We use it with MAX_FILENAME-1 to ensure the package name "
        "and filename fields never exceed the buffer size defined in the Package struct."
    )
    pdf.qa_pair(6,
        "How would you add support for a new package format like .flatpak?",
        "Two changes would be needed: (1) In get_install_command(), add: else if(strcmp(ext, "
        "'.flatpak') == 0) return 'flatpak install'; (2) In auto_install(), add the corresponding "
        "snprintf case with the full command: 'flatpak install \"%s\" 2>&1'. The modular "
        "design makes this a straightforward extension."
    )
    pdf.qa_pair(7,
        "Why does find_package return a pointer instead of a copy of the Package?",
        "Returning a pointer avoids copying the entire Package struct (which contains two 256-byte "
        "char arrays plus int and long - about 520 bytes total). The pointer allows the caller to "
        "directly access the package in the array. Returning NULL for 'not found' is a standard "
        "C pattern that's more efficient than copying."
    )
    pdf.qa_pair(8,
        "What testing did you perform on the system?",
        "I tested: (1) Server startup and package loading with valid and malformed packages.txt "
        "files, (2) Client connection and disconnection, including abrupt disconnects, (3) Package "
        "listing with 0, 1, and many packages, (4) File download of various sizes (1KB to 100MB), "
        "(5) Installation of .deb, .sh, and .tar.gz files, (6) Multiple simultaneous client "
        "connections to verify thread safety, (7) Error cases: invalid package ID, missing files, "
        "wrong server IP, and (8) Reconnection after server restart."
    )
    pdf.qa_pair(9,
        "Why does the .sh handler use sed before chmod and bash?",
        "Shell scripts created or edited on Windows have \\r\\n line endings (carriage return + "
        "newline), but Linux expects only \\n. The \\r character causes 'bad interpreter' errors. "
        "The sed command 's/\\r$//' removes trailing carriage returns from every line. This is "
        "a real-world issue that frequently occurs with scripts downloaded from the internet or "
        "shared between Windows and Linux users."
    )
    pdf.qa_pair(10,
        "What is the buffer overflow check in list_packages and why is it important?",
        "After each snprintf call, we check if 'written < 0' (encoding error) or 'written >= "
        "buf_size - offset' (output was truncated). If either is true, we break the loop. Without "
        "this check, we'd continue writing past the buffer boundary, corrupting adjacent memory - "
        "a classic buffer overflow vulnerability. snprintf itself doesn't overflow (it truncates), "
        "but without checking, we'd send truncated/corrupt data to clients."
    )


def main():
    pdf = PresentationPDF()
    pdf.set_title("CSE 324 - Automated Software Installation Server - Presentation Guide")
    pdf.set_author("CSE 324 Group Project Team")

    build_title_page(pdf)
    build_toc(pdf)
    build_setup_guide(pdf)
    build_person1(pdf)
    build_person2(pdf)
    build_person3(pdf)
    build_person4(pdf)
    build_person5(pdf)

    pdf.output(OUTPUT_PATH)
    print(f"PDF generated successfully: {OUTPUT_PATH}")
    print(f"Total pages: {pdf.page_no()}")


if __name__ == "__main__":
    main()
