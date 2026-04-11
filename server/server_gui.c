#include <gtk/gtk.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <arpa/inet.h>

#include "../common/protocol.h"
#include "../common/utils.h"
#include "package_manager.h"
#include "file_handler.h"

#if !GLIB_CHECK_VERSION(2, 74, 0)
#define G_APPLICATION_DEFAULT_FLAGS G_APPLICATION_FLAGS_NONE
#endif

typedef struct {
    char   ip[INET_ADDRSTRLEN];
    int    port;
    time_t connected_at;
} ClientInfo;

extern int  start_server(int port);
extern void stop_server(void);
extern int  is_server_running(void);
extern void server_set_log_callback(log_callback cb, void *data);
extern void server_set_client_update_callback(void (*cb)(void));
extern int  get_client_count(void);
extern int  get_package_count(void);
extern void server_reload_packages(void);
extern void get_connected_clients_copy(ClientInfo *out, int *count);

static GtkWidget *window;
static GtkWidget *port_entry;
static GtkWidget *start_button;
static GtkWidget *stop_button;
static GtkWidget *status_label;
static GtkWidget *client_count_label;
static GtkWidget *log_view;
static GtkTextBuffer *log_buffer;
static GtkWidget *client_tree;
static GtkListStore *client_store;
static GtkWidget *pkg_tree;
static GtkListStore *pkg_store;

typedef struct {
    char message[MAX_LINE_LEN];
} LogData;

static gboolean append_log_idle(gpointer data) {
    LogData *ld = (LogData *)data;
    GtkTextIter end;
    char timestamp[64];
    get_timestamp(timestamp, sizeof(timestamp));

    char full_msg[MAX_LINE_LEN + 80];
    snprintf(full_msg, sizeof(full_msg), "[%s] %s\n", timestamp, ld->message);

    gtk_text_buffer_get_end_iter(log_buffer, &end);
    gtk_text_buffer_insert(log_buffer, &end, full_msg, -1);

    GtkTextMark *mark = gtk_text_buffer_get_mark(log_buffer, "end");
    if (!mark)
        mark = gtk_text_buffer_create_mark(log_buffer, "end", &end, FALSE);
    else
        gtk_text_buffer_move_mark(log_buffer, mark, &end);

    gtk_text_view_scroll_mark_onscreen(GTK_TEXT_VIEW(log_view), mark);

    free(ld);
    return FALSE;
}

static void gui_log_callback(const char *message, void *user_data) {
    (void)user_data;
    LogData *ld = malloc(sizeof(LogData));
    if (ld) {
        strncpy(ld->message, message, sizeof(ld->message) - 1);
        ld->message[sizeof(ld->message) - 1] = '\0';
        g_idle_add(append_log_idle, ld);
    }
}

static gboolean update_client_tree_idle(gpointer data) {
    (void)data;
    gtk_list_store_clear(client_store);

    ClientInfo clients[MAX_CLIENTS];
    int count = 0;
    get_connected_clients_copy(clients, &count);

    for (int i = 0; i < count; i++) {
        char time_str[64];
        struct tm *t = localtime(&clients[i].connected_at);
        strftime(time_str, sizeof(time_str), "%H:%M:%S", t);

        char addr_str[80];
        snprintf(addr_str, sizeof(addr_str), "%s:%d", clients[i].ip, clients[i].port);

        GtkTreeIter iter;
        gtk_list_store_append(client_store, &iter);
        gtk_list_store_set(client_store, &iter,
                           0, addr_str,
                           1, time_str,
                           -1);
    }

    return FALSE;
}

static gboolean update_status_idle(gpointer data) {
    (void)data;
    if (is_server_running()) {
        gtk_label_set_text(GTK_LABEL(status_label), "Status: RUNNING");
        gtk_widget_set_sensitive(start_button, FALSE);
        gtk_widget_set_sensitive(stop_button, TRUE);
        gtk_widget_set_sensitive(port_entry, FALSE);
    } else {
        gtk_label_set_text(GTK_LABEL(status_label), "Status: STOPPED");
        gtk_widget_set_sensitive(start_button, TRUE);
        gtk_widget_set_sensitive(stop_button, FALSE);
        gtk_widget_set_sensitive(port_entry, TRUE);
    }

    char count_str[64];
    snprintf(count_str, sizeof(count_str), "Connected Clients: %d", get_client_count());
    gtk_label_set_text(GTK_LABEL(client_count_label), count_str);

    return FALSE;
}

static void on_client_update(void) {
    g_idle_add(update_status_idle, NULL);
    g_idle_add(update_client_tree_idle, NULL);
}

static void on_start_clicked(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;
    const char *port_str = gtk_entry_get_text(GTK_ENTRY(port_entry));
    int port = atoi(port_str);
    if (port <= 0 || port > 65535) port = DEFAULT_PORT;

    if (start_server(port) == 0) {
        g_idle_add(update_status_idle, NULL);
    }
}

static void on_stop_clicked(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;
    stop_server();
    g_idle_add(update_status_idle, NULL);
}

static void refresh_package_list(void) {
    gtk_list_store_clear(pkg_store);

    Package pkgs[MAX_PACKAGES];
    int count = load_packages(PACKAGES_FILE, pkgs, MAX_PACKAGES);

    for (int i = 0; i < count; i++) {
        char size_str[64];
        format_size(pkgs[i].size, size_str, sizeof(size_str));

        GtkTreeIter iter;
        gtk_list_store_append(pkg_store, &iter);
        gtk_list_store_set(pkg_store, &iter,
                           0, pkgs[i].id,
                           1, pkgs[i].name,
                           2, pkgs[i].filename,
                           3, size_str,
                           -1);
    }
}

static void on_refresh_packages(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;
    server_reload_packages();
    refresh_package_list();
}

static void on_add_package(GtkWidget *widget, gpointer data) {
    (void)widget; (void)data;

    GtkWidget *dialog = gtk_file_chooser_dialog_new(
        "Select Software Package",
        GTK_WINDOW(window),
        GTK_FILE_CHOOSER_ACTION_OPEN,
        "_Cancel", GTK_RESPONSE_CANCEL,
        "_Add", GTK_RESPONSE_ACCEPT,
        NULL);

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
        char *filepath = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));
        if (filepath) {
            char *basename = strrchr(filepath, '/');
            basename = basename ? basename + 1 : filepath;

            long fsize = get_file_size(filepath);

            char dest[MAX_PATH_LEN];
            snprintf(dest, sizeof(dest), "%s%s", PACKAGES_DIR, basename);

            FILE *src_fp = fopen(filepath, "rb");
            FILE *dst_fp = fopen(dest, "wb");
            if (src_fp && dst_fp) {
                char buf[BUFFER_SIZE];
                size_t n;
                while ((n = fread(buf, 1, sizeof(buf), src_fp)) > 0)
                    fwrite(buf, 1, n, dst_fp);
                fclose(src_fp);
                fclose(dst_fp);

                GtkWidget *name_dialog = gtk_dialog_new_with_buttons(
                    "Package Name",
                    GTK_WINDOW(window),
                    GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
                    "_OK", GTK_RESPONSE_ACCEPT,
                    NULL);

                GtkWidget *content = gtk_dialog_get_content_area(GTK_DIALOG(name_dialog));
                GtkWidget *label = gtk_label_new("Enter display name for the package:");
                GtkWidget *name_entry = gtk_entry_new();
                gtk_entry_set_text(GTK_ENTRY(name_entry), basename);

                gtk_box_pack_start(GTK_BOX(content), label, FALSE, FALSE, 5);
                gtk_box_pack_start(GTK_BOX(content), name_entry, FALSE, FALSE, 5);
                gtk_widget_show_all(name_dialog);

                if (gtk_dialog_run(GTK_DIALOG(name_dialog)) == GTK_RESPONSE_ACCEPT) {
                    const char *pkg_name = gtk_entry_get_text(GTK_ENTRY(name_entry));
                    add_package(PACKAGES_FILE, pkg_name, basename, fsize);
                    server_reload_packages();
                    refresh_package_list();
                    gui_log_callback("Package added successfully", NULL);
                }

                gtk_widget_destroy(name_dialog);
            } else {
                if (src_fp) fclose(src_fp);
                if (dst_fp) fclose(dst_fp);
                gui_log_callback("Failed to copy package file", NULL);
            }

            g_free(filepath);
        }
    }

    gtk_widget_destroy(dialog);
}

static void build_server_gui(GtkApplication *app) {
    window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Automated Software Installation Server");
    gtk_window_set_default_size(GTK_WINDOW(window), 900, 700);

    GtkWidget *main_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_set_border_width(GTK_CONTAINER(main_box), 10);
    gtk_container_add(GTK_CONTAINER(window), main_box);

    GtkWidget *header_label = gtk_label_new(NULL);
    gtk_label_set_markup(GTK_LABEL(header_label),
        "<span size='x-large' weight='bold'>Automated Software Installation Server</span>");
    gtk_box_pack_start(GTK_BOX(main_box), header_label, FALSE, FALSE, 5);

    GtkWidget *separator1 = gtk_separator_new(GTK_ORIENTATION_HORIZONTAL);
    gtk_box_pack_start(GTK_BOX(main_box), separator1, FALSE, FALSE, 2);

    GtkWidget *ctrl_frame = gtk_frame_new("Server Controls");
    gtk_box_pack_start(GTK_BOX(main_box), ctrl_frame, FALSE, FALSE, 5);

    GtkWidget *ctrl_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 10);
    gtk_container_set_border_width(GTK_CONTAINER(ctrl_box), 8);
    gtk_container_add(GTK_CONTAINER(ctrl_frame), ctrl_box);

    GtkWidget *port_label = gtk_label_new("Port:");
    gtk_box_pack_start(GTK_BOX(ctrl_box), port_label, FALSE, FALSE, 0);

    port_entry = gtk_entry_new();
    gtk_entry_set_text(GTK_ENTRY(port_entry), "8080");
    gtk_entry_set_width_chars(GTK_ENTRY(port_entry), 8);
    gtk_box_pack_start(GTK_BOX(ctrl_box), port_entry, FALSE, FALSE, 0);

    start_button = gtk_button_new_with_label("Start Server");
    gtk_box_pack_start(GTK_BOX(ctrl_box), start_button, FALSE, FALSE, 0);
    g_signal_connect(start_button, "clicked", G_CALLBACK(on_start_clicked), NULL);

    stop_button = gtk_button_new_with_label("Stop Server");
    gtk_widget_set_sensitive(stop_button, FALSE);
    gtk_box_pack_start(GTK_BOX(ctrl_box), stop_button, FALSE, FALSE, 0);
    g_signal_connect(stop_button, "clicked", G_CALLBACK(on_stop_clicked), NULL);

    status_label = gtk_label_new("Status: STOPPED");
    gtk_box_pack_start(GTK_BOX(ctrl_box), status_label, FALSE, FALSE, 10);

    client_count_label = gtk_label_new("Connected Clients: 0");
    gtk_box_pack_end(GTK_BOX(ctrl_box), client_count_label, FALSE, FALSE, 10);

    GtkWidget *paned = gtk_paned_new(GTK_ORIENTATION_VERTICAL);
    gtk_paned_set_position(GTK_PANED(paned), 300);
    gtk_box_pack_start(GTK_BOX(main_box), paned, TRUE, TRUE, 0);

    GtkWidget *top_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);

    GtkWidget *pkg_frame = gtk_frame_new("Available Packages");
    gtk_box_pack_start(GTK_BOX(top_box), pkg_frame, TRUE, TRUE, 0);

    GtkWidget *pkg_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_set_border_width(GTK_CONTAINER(pkg_box), 5);
    gtk_container_add(GTK_CONTAINER(pkg_frame), pkg_box);

    pkg_store = gtk_list_store_new(4, G_TYPE_INT, G_TYPE_STRING, G_TYPE_STRING, G_TYPE_STRING);
    pkg_tree = gtk_tree_view_new_with_model(GTK_TREE_MODEL(pkg_store));
    g_object_unref(pkg_store);

    GtkCellRenderer *renderer;
    GtkTreeViewColumn *col;

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("ID", renderer, "text", 0, NULL);
    gtk_tree_view_column_set_min_width(col, 40);
    gtk_tree_view_append_column(GTK_TREE_VIEW(pkg_tree), col);

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("Name", renderer, "text", 1, NULL);
    gtk_tree_view_column_set_expand(col, TRUE);
    gtk_tree_view_append_column(GTK_TREE_VIEW(pkg_tree), col);

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("Filename", renderer, "text", 2, NULL);
    gtk_tree_view_column_set_expand(col, TRUE);
    gtk_tree_view_append_column(GTK_TREE_VIEW(pkg_tree), col);

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("Size", renderer, "text", 3, NULL);
    gtk_tree_view_column_set_min_width(col, 100);
    gtk_tree_view_append_column(GTK_TREE_VIEW(pkg_tree), col);

    GtkWidget *pkg_scroll = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(pkg_scroll),
                                   GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_container_add(GTK_CONTAINER(pkg_scroll), pkg_tree);
    gtk_box_pack_start(GTK_BOX(pkg_box), pkg_scroll, TRUE, TRUE, 0);

    GtkWidget *pkg_btn_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
    gtk_box_pack_start(GTK_BOX(pkg_box), pkg_btn_box, FALSE, FALSE, 0);

    GtkWidget *add_pkg_btn = gtk_button_new_with_label("Add Package");
    g_signal_connect(add_pkg_btn, "clicked", G_CALLBACK(on_add_package), NULL);
    gtk_box_pack_start(GTK_BOX(pkg_btn_box), add_pkg_btn, FALSE, FALSE, 0);

    GtkWidget *refresh_pkg_btn = gtk_button_new_with_label("Refresh");
    g_signal_connect(refresh_pkg_btn, "clicked", G_CALLBACK(on_refresh_packages), NULL);
    gtk_box_pack_start(GTK_BOX(pkg_btn_box), refresh_pkg_btn, FALSE, FALSE, 0);

    GtkWidget *client_frame = gtk_frame_new("Connected Clients");
    gtk_widget_set_size_request(client_frame, 280, -1);
    gtk_box_pack_start(GTK_BOX(top_box), client_frame, FALSE, FALSE, 0);

    client_store = gtk_list_store_new(2, G_TYPE_STRING, G_TYPE_STRING);
    client_tree = gtk_tree_view_new_with_model(GTK_TREE_MODEL(client_store));
    g_object_unref(client_store);

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("Client Address", renderer, "text", 0, NULL);
    gtk_tree_view_column_set_expand(col, TRUE);
    gtk_tree_view_append_column(GTK_TREE_VIEW(client_tree), col);

    renderer = gtk_cell_renderer_text_new();
    col = gtk_tree_view_column_new_with_attributes("Connected At", renderer, "text", 1, NULL);
    gtk_tree_view_column_set_expand(col, TRUE);
    gtk_tree_view_append_column(GTK_TREE_VIEW(client_tree), col);

    GtkWidget *client_scroll = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(client_scroll),
                                   GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_container_add(GTK_CONTAINER(client_scroll), client_tree);
    gtk_container_add(GTK_CONTAINER(client_frame), client_scroll);

    gtk_paned_add1(GTK_PANED(paned), top_box);

    GtkWidget *log_frame = gtk_frame_new("Server Log");

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
    gtk_container_add(GTK_CONTAINER(log_scroll), log_view);
    gtk_container_add(GTK_CONTAINER(log_frame), log_scroll);

    gtk_paned_add2(GTK_PANED(paned), log_frame);

    GtkWidget *statusbar = gtk_statusbar_new();
    gtk_statusbar_push(GTK_STATUSBAR(statusbar), 0,
                       "Automated Software Installation Server — CSE 324 OS Lab Project");
    gtk_box_pack_end(GTK_BOX(main_box), statusbar, FALSE, FALSE, 0);

    server_set_log_callback(gui_log_callback, NULL);
    server_set_client_update_callback(on_client_update);

    refresh_package_list();

    gtk_widget_show_all(window);
}

static void on_activate(GtkApplication *app, gpointer data) {
    (void)data;
    build_server_gui(app);
}

static void on_shutdown_app(GtkApplication *app, gpointer data) {
    (void)app; (void)data;
    if (is_server_running())
        stop_server();
}

int main(int argc, char *argv[]) {
    GtkApplication *app = gtk_application_new("com.cse324.server",
                                               G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(on_activate), NULL);
    g_signal_connect(app, "shutdown", G_CALLBACK(on_shutdown_app), NULL);

    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}
