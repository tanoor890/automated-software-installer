#include <gtk/gtk.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <pthread.h>
#include <unistd.h>

#include "../common/protocol.h"
#include "../common/utils.h"
#include "client.h"
#include "installer.h"

#if !GLIB_CHECK_VERSION(2, 74, 0)
#define G_APPLICATION_DEFAULT_FLAGS G_APPLICATION_FLAGS_NONE
#endif

/* ── State ───────────────────────────────────────────────── */

static int sockfd = -1;
static int is_connected = 0;
static int is_downloading = 0;

/* ── GUI widgets ─────────────────────────────────────────── */

static GtkWidget *window;
static GtkWidget *ip_entry;
static GtkWidget *port_entry;
static GtkWidget *connect_button;
static GtkWidget *disconnect_button;
static GtkWidget *connection_status;

static GtkWidget *pkg_tree;
static GtkListStore *pkg_store;
static GtkWidget *refresh_button;
static GtkWidget *download_button;

static GtkWidget *progress_bar;
static GtkWidget *progress_label;

static GtkWidget *log_view;
static GtkTextBuffer *log_buffer;

static GtkWidget *status_bar;

static Package gui_packages[MAX_PACKAGES];
static int gui_package_count = 0;

/* ── Logging ─────────────────────────────────────────────── */

typedef struct {
    char message[MAX_LINE_LEN];
} LogMsg;

static gboolean append_log_idle(gpointer data) {
    LogMsg *msg = (LogMsg *)data;
    GtkTextIter end;
    char timestamp[64];
    get_timestamp(timestamp, sizeof(timestamp));

    char full[MAX_LINE_LEN + 80];
    snprintf(full, sizeof(full), "[%s] %s\n", timestamp, msg->message);

    gtk_text_buffer_get_end_iter(log_buffer, &end);
    gtk_text_buffer_insert(log_buffer, &end, full, -1);

    GtkTextMark *mark = gtk_text_buffer_get_mark(log_buffer, "end");
    if (!mark)
        mark = gtk_text_buffer_create_mark(log_buffer, "end", &end, FALSE);
    else
        gtk_text_buffer_move_mark(log_buffer, mark, &end);
    gtk_text_view_scroll_mark_onscreen(GTK_TEXT_VIEW(log_view), mark);

    free(msg);
    return FALSE;
}

static void gui_log(const char *fmt, ...) {
    LogMsg *msg = malloc(sizeof(LogMsg));
    if (!msg) return;

    va_list args;
    va_start(args, fmt);
    vsnprintf(msg->message, sizeof(msg->message), fmt, args);
    va_end(args);

    g_idle_add(append_log_idle, msg);
}

/* ── Progress update ─────────────────────────────────────── */

typedef struct {
    double fraction;
    char   text[128];
} ProgressData;

static gboolean update_progress_idle(gpointer data) {
    ProgressData *pd = (ProgressData *)data;
    gtk_progress_bar_set_fraction(GTK_PROGRESS_BAR(progress_bar), pd->fraction);
    gtk_progress_bar_set_text(GTK_PROGRESS_BAR(progress_bar), pd->text);
    gtk_label_set_text(GTK_LABEL(progress_label), pd->text);
    free(pd);
    return FALSE;
}

static void download_progress_cb(long received, long total, void *user_data) {
    (void)user_data;
    ProgressData *pd = malloc(sizeof(ProgressData));
    if (!pd) return;

    pd->fraction = (double)received / (double)total;

    char recv_str[64], total_str[64];
    format_size(received, recv_str, sizeof(recv_str));
    format_size(total, total_str, sizeof(total_str));
    snprintf(pd->text, sizeof(pd->text), "%s / %s (%.1f%%)",
             recv_str, total_str, pd->fraction * 100.0);

    g_idle_add(update_progress_idle, pd);
}

/* ── UI state helpers ────────────────────────────────────── */

typedef struct {
    int connected;
    int downloading;
} UIState;

static gboolean update_ui_state_idle(gpointer data) {
    UIState *state = (UIState *)data;

    if (state->connected) {
        gtk_label_set_text(GTK_LABEL(connection_status), "Connected");
        gtk_widget_set_sensitive(connect_button, FALSE);
        gtk_widget_set_sensitive(disconnect_button, TRUE);
        gtk_widget_set_sensitive(ip_entry, FALSE);
        gtk_widget_set_sensitive(port_entry, FALSE);
        gtk_widget_set_sensitive(refresh_button, TRUE);
        gtk_widget_set_sensitive(download_button, !state->downloading);
    } else {
        gtk_label_set_text(GTK_LABEL(connection_status), "Disconnected");
        gtk_widget_set_sensitive(connect_button, TRUE);
        gtk_widget_set_sensitive(disconnect_button, FALSE);
        gtk_widget_set_sensitive(ip_entry, TRUE);
        gtk_widget_set_sensitive(port_entry, TRUE);
        gtk_widget_set_sensitive(refresh_button, FALSE);
        gtk_widget_set_sensitive(download_button, FALSE);
    }

    free(state);
    return FALSE;
}

static void update_ui_state(void) {
    UIState *state = malloc(sizeof(UIState));
    if (!state) return;
    state->connected = is_connected;
    state->downloading = is_downloading;
    g_idle_add(update_ui_state_idle, state);
}

/* ── Package list update ─────────────────────────────────── */

typedef struct {
    Package packages[MAX_PACKAGES];
    int count;
} PkgListData;

static gboolean update_pkg_list_idle(gpointer data) {
    PkgListData *pld = (PkgListData *)data;

    gtk_list_store_clear(pkg_store);

    for (int i = 0; i < pld->count; i++) {
        char size_str[64];
        format_size(pld->packages[i].size, size_str, sizeof(size_str));

        GtkTreeIter iter;
        gtk_list_store_append(pkg_store, &iter);
        gtk_list_store_set(pkg_store, &iter,
                           0, pld->packages[i].id,
                           1, pld->packages[i].name,
                           2, size_str,
                           -1);
    }

    free(pld);
    return FALSE;
}

/* ── Connect thread ──────────────────────────────────────── */

typedef struct {
    char ip[64];
    int  port;
} ConnectArgs;

static void *connect_thread(void *arg) {
    ConnectArgs *ca = (ConnectArgs *)arg;

    gui_log("Connecting to %s:%d...", ca->ip, ca->port);
    sockfd = connect_to_server(ca->ip, ca->port);

    if (sockfd >= 0) {
        is_connected = 1;
        gui_log("Connected to %s:%d", ca->ip, ca->port);
    } else {
        gui_log("Failed to connect to %s:%d", ca->ip, ca->port);
    }

    update_ui_state();
    free(ca);
    return NULL;
}

static void on_connect_clicked(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;

    ConnectArgs *ca = malloc(sizeof(ConnectArgs));
    if (!ca) return;

    strncpy(ca->ip, gtk_entry_get_text(GTK_ENTRY(ip_entry)), sizeof(ca->ip) - 1);
    ca->port = atoi(gtk_entry_get_text(GTK_ENTRY(port_entry)));
    if (ca->port <= 0 || ca->port > 65535) ca->port = DEFAULT_PORT;

    pthread_t tid;
    pthread_create(&tid, NULL, connect_thread, ca);
    pthread_detach(tid);
}

/* ── Disconnect ──────────────────────────────────────────── */

static void on_disconnect_clicked(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;

    if (is_connected && sockfd >= 0) {
        disconnect(sockfd);
        sockfd = -1;
        is_connected = 0;
        gui_log("Disconnected from server");
        update_ui_state();

        gtk_list_store_clear(pkg_store);
        gui_package_count = 0;
    }
}

/* ── Refresh packages thread ─────────────────────────────── */

static void *refresh_thread(void *arg) {
    (void)arg;

    gui_log("Requesting package list...");

    char list_buf[BUFFER_SIZE * 4];
    if (request_list(sockfd, list_buf, sizeof(list_buf)) == 0) {
        gui_package_count = parse_package_list(list_buf, gui_packages, MAX_PACKAGES);
        gui_log("Received %d packages", gui_package_count);

        PkgListData *pld = malloc(sizeof(PkgListData));
        if (pld) {
            memcpy(pld->packages, gui_packages, sizeof(gui_packages));
            pld->count = gui_package_count;
            g_idle_add(update_pkg_list_idle, pld);
        }
    } else {
        gui_log("Failed to get package list");
    }

    return NULL;
}

static void on_refresh_clicked(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;

    if (!is_connected) return;

    pthread_t tid;
    pthread_create(&tid, NULL, refresh_thread, NULL);
    pthread_detach(tid);
}

/* ── Download & install thread ───────────────────────────── */

typedef struct {
    int package_id;
    char package_name[MAX_FILENAME];
} DownloadArgs;

static gboolean download_finished_idle(gpointer data) {
    char *filepath = (char *)data;

    is_downloading = 0;
    update_ui_state();

    if (filepath) {
        GtkWidget *dialog = gtk_message_dialog_new(
            GTK_WINDOW(window),
            GTK_DIALOG_DESTROY_WITH_PARENT,
            GTK_MESSAGE_QUESTION,
            GTK_BUTTONS_YES_NO,
            "Download complete!\n\nFile: %s\n\nDo you want to install it now?",
            filepath);

        if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_YES) {
            gui_log("Starting installation of %s...", filepath);
            int ret = auto_install(filepath);
            if (ret == 0)
                gui_log("Installation successful: %s", filepath);
            else
                gui_log("Installation failed (code %d): %s", ret, filepath);
        }

        gtk_widget_destroy(dialog);
        free(filepath);
    }

    return FALSE;
}

static void *download_thread(void *arg) {
    DownloadArgs *da = (DownloadArgs *)arg;

    gui_log("Requesting download of package %d (%s)...", da->package_id, da->package_name);

    char filename[MAX_FILENAME] = {0};
    if (request_download(sockfd, da->package_id, DOWNLOADS_DIR,
                         filename, sizeof(filename),
                         download_progress_cb, NULL) == 0) {

        char *filepath = malloc(MAX_PATH_LEN);
        if (filepath) {
            snprintf(filepath, MAX_PATH_LEN, "%s%s", DOWNLOADS_DIR, filename);
            gui_log("Download complete: %s", filepath);
            g_idle_add(download_finished_idle, filepath);
        }
    } else {
        gui_log("Download failed for package %d", da->package_id);
        is_downloading = 0;
        update_ui_state();
    }

    free(da);
    return NULL;
}

static void on_download_clicked(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;

    if (!is_connected || is_downloading) return;

    GtkTreeSelection *sel = gtk_tree_view_get_selection(GTK_TREE_VIEW(pkg_tree));
    GtkTreeModel *model;
    GtkTreeIter iter;

    if (!gtk_tree_selection_get_selected(sel, &model, &iter)) {
        GtkWidget *dialog = gtk_message_dialog_new(
            GTK_WINDOW(window), GTK_DIALOG_DESTROY_WITH_PARENT,
            GTK_MESSAGE_WARNING, GTK_BUTTONS_OK,
            "Please select a package to download.");
        gtk_dialog_run(GTK_DIALOG(dialog));
        gtk_widget_destroy(dialog);
        return;
    }

    int pkg_id;
    char *pkg_name;
    gtk_tree_model_get(model, &iter, 0, &pkg_id, 1, &pkg_name, -1);

    DownloadArgs *da = malloc(sizeof(DownloadArgs));
    if (!da) { g_free(pkg_name); return; }

    da->package_id = pkg_id;
    strncpy(da->package_name, pkg_name, MAX_FILENAME - 1);
    g_free(pkg_name);

    is_downloading = 1;
    update_ui_state();

    /* Reset progress bar */
    ProgressData *pd = malloc(sizeof(ProgressData));
    if (pd) {
        pd->fraction = 0.0;
        snprintf(pd->text, sizeof(pd->text), "Starting download...");
        g_idle_add(update_progress_idle, pd);
    }

    pthread_t tid;
    pthread_create(&tid, NULL, download_thread, da);
    pthread_detach(tid);
}

/* ── Build GUI ───────────────────────────────────────────── */

static void build_client_gui(GtkApplication *app) {
    window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Automated Software Installer — Client");
    gtk_window_set_default_size(GTK_WINDOW(window), 850, 650);

    GtkWidget *main_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_set_border_width(GTK_CONTAINER(main_box), 10);
    gtk_container_add(GTK_CONTAINER(window), main_box);

    /* ── Header ────────────────────────────────────────── */
    GtkWidget *header = gtk_label_new(NULL);
    gtk_label_set_markup(GTK_LABEL(header),
        "<span size='x-large' weight='bold'>Automated Software Installer</span>");
    gtk_box_pack_start(GTK_BOX(main_box), header, FALSE, FALSE, 5);

    gtk_box_pack_start(GTK_BOX(main_box),
        gtk_separator_new(GTK_ORIENTATION_HORIZONTAL), FALSE, FALSE, 2);

    /* ── Connection frame ──────────────────────────────── */
    GtkWidget *conn_frame = gtk_frame_new("Server Connection");
    gtk_box_pack_start(GTK_BOX(main_box), conn_frame, FALSE, FALSE, 5);

    GtkWidget *conn_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_container_set_border_width(GTK_CONTAINER(conn_box), 8);
    gtk_container_add(GTK_CONTAINER(conn_frame), conn_box);

    gtk_box_pack_start(GTK_BOX(conn_box), gtk_label_new("IP:"), FALSE, FALSE, 0);
    ip_entry = gtk_entry_new();
    gtk_entry_set_text(GTK_ENTRY(ip_entry), "127.0.0.1");
    gtk_entry_set_width_chars(GTK_ENTRY(ip_entry), 15);
    gtk_box_pack_start(GTK_BOX(conn_box), ip_entry, FALSE, FALSE, 0);

    gtk_box_pack_start(GTK_BOX(conn_box), gtk_label_new("Port:"), FALSE, FALSE, 0);
    port_entry = gtk_entry_new();
    gtk_entry_set_text(GTK_ENTRY(port_entry), "8080");
    gtk_entry_set_width_chars(GTK_ENTRY(port_entry), 6);
    gtk_box_pack_start(GTK_BOX(conn_box), port_entry, FALSE, FALSE, 0);

    connect_button = gtk_button_new_with_label("Connect");
    g_signal_connect(connect_button, "clicked", G_CALLBACK(on_connect_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(conn_box), connect_button, FALSE, FALSE, 0);

    disconnect_button = gtk_button_new_with_label("Disconnect");
    gtk_widget_set_sensitive(disconnect_button, FALSE);
    g_signal_connect(disconnect_button, "clicked", G_CALLBACK(on_disconnect_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(conn_box), disconnect_button, FALSE, FALSE, 0);

    connection_status = gtk_label_new("Disconnected");
    gtk_box_pack_end(GTK_BOX(conn_box), connection_status, FALSE, FALSE, 10);

    /* ── Package list frame ────────────────────────────── */
    GtkWidget *pkg_frame = gtk_frame_new("Available Software Packages");
    gtk_box_pack_start(GTK_BOX(main_box), pkg_frame, TRUE, TRUE, 5);

    GtkWidget *pkg_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_set_border_width(GTK_CONTAINER(pkg_box), 5);
    gtk_container_add(GTK_CONTAINER(pkg_frame), pkg_box);

    pkg_store = gtk_list_store_new(3, G_TYPE_INT, G_TYPE_STRING, G_TYPE_STRING);
    pkg_tree = gtk_tree_view_new_with_model(GTK_TREE_MODEL(pkg_store));
    g_object_unref(pkg_store);

    GtkCellRenderer *renderer;
    GtkTreeViewColumn *col;

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("ID", renderer, "text", 0, NULL);
    gtk_tree_view_column_set_min_width(col, 50);
    gtk_tree_view_append_column(GTK_TREE_VIEW(pkg_tree), col);

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("Software Name", renderer, "text", 1, NULL);
    gtk_tree_view_column_set_expand(col, TRUE);
    gtk_tree_view_append_column(GTK_TREE_VIEW(pkg_tree), col);

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("Size", renderer, "text", 2, NULL);
    gtk_tree_view_column_set_min_width(col, 120);
    gtk_tree_view_append_column(GTK_TREE_VIEW(pkg_tree), col);

    GtkWidget *pkg_scroll = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(pkg_scroll),
                                   GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_container_add(GTK_CONTAINER(pkg_scroll), pkg_tree);
    gtk_box_pack_start(GTK_BOX(pkg_box), pkg_scroll, TRUE, TRUE, 0);

    GtkWidget *btn_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
    gtk_box_pack_start(GTK_BOX(pkg_box), btn_box, FALSE, FALSE, 0);

    refresh_button = gtk_button_new_with_label("Refresh List");
    gtk_widget_set_sensitive(refresh_button, FALSE);
    g_signal_connect(refresh_button, "clicked", G_CALLBACK(on_refresh_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(btn_box), refresh_button, FALSE, FALSE, 0);

    download_button = gtk_button_new_with_label("Download & Install");
    gtk_widget_set_sensitive(download_button, FALSE);
    g_signal_connect(download_button, "clicked", G_CALLBACK(on_download_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(btn_box), download_button, FALSE, FALSE, 0);

    /* ── Progress section ──────────────────────────────── */
    GtkWidget *prog_frame = gtk_frame_new("Download Progress");
    gtk_box_pack_start(GTK_BOX(main_box), prog_frame, FALSE, FALSE, 5);

    GtkWidget *prog_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 3);
    gtk_container_set_border_width(GTK_CONTAINER(prog_box), 5);
    gtk_container_add(GTK_CONTAINER(prog_frame), prog_box);

    progress_bar = gtk_progress_bar_new();
    gtk_progress_bar_set_show_text(GTK_PROGRESS_BAR(progress_bar), TRUE);
    gtk_progress_bar_set_text(GTK_PROGRESS_BAR(progress_bar), "No active download");
    gtk_box_pack_start(GTK_BOX(prog_box), progress_bar, FALSE, FALSE, 0);

    progress_label = gtk_label_new("");
    gtk_box_pack_start(GTK_BOX(prog_box), progress_label, FALSE, FALSE, 0);

    /* ── Log area ──────────────────────────────────────── */
    GtkWidget *log_frame = gtk_frame_new("Activity Log");
    gtk_box_pack_start(GTK_BOX(main_box), log_frame, TRUE, TRUE, 5);

    log_view = gtk_text_view_new();
    log_buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(log_view));
    gtk_text_view_set_editable(GTK_TEXT_VIEW(log_view), FALSE);
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(log_view), GTK_WRAP_WORD_CHAR);
    gtk_text_view_set_cursor_visible(GTK_TEXT_VIEW(log_view), FALSE);

    gtk_widget_set_name(log_view, "log_text");
    GtkCssProvider *css = gtk_css_provider_new();
    gtk_css_provider_load_from_data(css,
        "#log_text { font-family: Monospace; font-size: 9pt; }", -1, NULL);
    gtk_style_context_add_provider(gtk_widget_get_style_context(log_view),
        GTK_STYLE_PROVIDER(css), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    g_object_unref(css);

    GtkWidget *log_scroll = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(log_scroll),
                                   GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_widget_set_size_request(log_scroll, -1, 150);
    gtk_container_add(GTK_CONTAINER(log_scroll), log_view);
    gtk_container_add(GTK_CONTAINER(log_frame), log_scroll);

    /* ── Status bar ────────────────────────────────────── */
    status_bar = gtk_statusbar_new();
    gtk_statusbar_push(GTK_STATUSBAR(status_bar), 0,
                       "Automated Software Installer — CSE 324 OS Lab Project");
    gtk_box_pack_end(GTK_BOX(main_box), status_bar, FALSE, FALSE, 0);

    gtk_widget_show_all(window);
}

static void on_activate(GtkApplication *app, gpointer data) {
    (void)data;
    build_client_gui(app);
}

static void on_shutdown_app(GtkApplication *app, gpointer data) {
    (void)app; (void)data;
    if (is_connected && sockfd >= 0) {
        disconnect(sockfd);
        sockfd = -1;
        is_connected = 0;
    }
}

int main(int argc, char *argv[]) {
    GtkApplication *app = gtk_application_new("com.cse324.client",
                                               G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(on_activate), NULL);
    g_signal_connect(app, "shutdown", G_CALLBACK(on_shutdown_app), NULL);

    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}
