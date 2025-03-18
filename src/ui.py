import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"

def main(page: ft.Page):
    page.title = "AI-Powered Code Assistant"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8F9FA"
    page.padding = 20

    primary_color = "#FFB6C1"  #pibk one
    secondary_color = "#87CEFA"  # blue one
    card_bg = "white"

    languages = ["Python", "JavaScript", "C++", "Java", "C#", "Go", "Swift", "Kotlin"]

    # --- MAIN CONTENT CONTAINER ---
    content_container = ft.Column()

    # --- CODE GENERATION SECTION ---
    gen_description = ft.TextField(label="Enter Code Description", multiline=True, width=500)
    gen_language = ft.Dropdown(label="Select Language", options=[ft.dropdown.Option(lang) for lang in languages])
    gen_output = ft.TextField(label="Generated Code", multiline=True, width=500, height=200, read_only=True)

    def generate_code(e):
        response = requests.post(f"{API_URL}/generate_code", json={"description": gen_description.value, "language": gen_language.value})
        data = response.json()
        gen_output.value = data.get("generated_code", "Error generating code.")
        page.update()

    def clear_generation(e):
        gen_description.value = ""
        gen_output.value = ""
        page.update()

    code_generation_section = ft.Column([
        ft.Text("Code Generation", size=20, weight="bold"),
        gen_description,
        gen_language,
        ft.Row([
            ft.ElevatedButton(text="Generate Code", on_click=generate_code, bgcolor=primary_color),
            ft.ElevatedButton(text="Clear", on_click=clear_generation, bgcolor="#DDDDDD"),
        ], spacing=10),
        gen_output,
    ], spacing=10)

    # --- CODE EXPLANATION SECTION ---
    exp_input = ft.TextField(label="Paste Code to Explain", multiline=True, width=500)
    exp_output = ft.TextField(label="Explanation", multiline=True, width=500, height=200, read_only=True)

    def explain_code(e):
        response = requests.post(f"{API_URL}/explain_code", json={"code": exp_input.value})
        data = response.json()
        exp_output.value = data.get("explanation", "Error explaining code.")
        page.update()

    def clear_explanation(e):
        exp_input.value = ""
        exp_output.value = ""
        page.update()

    code_explanation_section = ft.Column([
        ft.Text("Code Explanation", size=20, weight="bold"),
        exp_input,
        ft.Row([
            ft.ElevatedButton(text="Explain Code", on_click=explain_code, bgcolor=secondary_color),
            ft.ElevatedButton(text="Clear", on_click=clear_explanation, bgcolor="#DDDDDD"),
        ], spacing=10),
        exp_output,
    ], spacing=10)

    # --- CODE TRANSLATION SECTION ---
    trans_input = ft.TextField(label="Paste Code to Translate", multiline=True, width=500)
    trans_target_lang = ft.Dropdown(label="Target Language", options=[ft.dropdown.Option(lang) for lang in languages])
    trans_output = ft.TextField(label="Translated Code", multiline=True, width=500, height=200, read_only=True)
    trans_lang_info = ft.Text("", size=14, italic=True)

    def translate_code(e):
        response = requests.post(f"{API_URL}/translate_code", json={"code": trans_input.value, "target_language": trans_target_lang.value})
        data = response.json()
        trans_lang_info.value = f"Input Language: {data.get('input_language', 'Unknown')}"
        trans_output.value = data.get("translated_code", "Error translating code.")
        page.update()

    def clear_translation(e):
        trans_input.value = ""
        trans_output.value = ""
        trans_lang_info.value = ""
        page.update()

    code_translation_section = ft.Column([
        ft.Text(" Code Translation", size=20, weight="bold"),
        trans_input,
        trans_target_lang,
        ft.Row([
            ft.ElevatedButton(text="Translate Code", on_click=translate_code, bgcolor=primary_color),
            ft.ElevatedButton(text="Clear", on_click=clear_translation, bgcolor="#DDDDDD"),
        ], spacing=10),
        trans_lang_info,
        trans_output,
    ], spacing=10)

    # --- SETTINGS SECTION ---
    indent_option = ft.Dropdown(label="Code Indentation", options=[ft.dropdown.Option("2"), ft.dropdown.Option("4")])
    naming_convention = ft.Dropdown(label="Naming Convention", options=[ft.dropdown.Option("snake_case"), ft.dropdown.Option("camelCase"), ft.dropdown.Option("PascalCase")])

    def save_preferences(e):
        preferences = {"indentation": indent_option.value, "naming_convention": naming_convention.value}
        requests.post(f"{API_URL}/style_preferences", json=preferences)
        page.snack_bar = ft.SnackBar(ft.Text("Preferences saved!"), bgcolor="#32CD32")
        page.snack_bar.open = True
        page.update()

    settings_section = ft.Column([
        ft.Text(" Settings", size=20, weight="bold"),
        indent_option,
        naming_convention,
        ft.ElevatedButton(text="Save Preferences", on_click=save_preferences, bgcolor=secondary_color),
    ], spacing=10)

    # --- FUNCTION TO SWITCH CONTENT ---
    def switch_page(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            content_container.controls = [code_generation_section]
        elif selected_index == 1:
            content_container.controls = [code_explanation_section]
        elif selected_index == 2:
            content_container.controls = [code_translation_section]
        elif selected_index == 3:
            content_container.controls = [settings_section]
        page.drawer.open = False  # Close drawer after selection
        page.update()

    # --- NAVIGATION DRAWER ---
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Text("🔹 Menu", size=24, weight="bold", color=primary_color),
            ft.NavigationDrawerDestination(icon=ft.icons.CODE, label="Code Generation"),
            ft.NavigationDrawerDestination(icon=ft.icons.BOOK, label="Code Explanation"),
            ft.NavigationDrawerDestination(icon=ft.icons.TRANSLATE, label="Code Translation"),
            ft.NavigationDrawerDestination(icon=ft.icons.SETTINGS, label="Settings"),
        ],
        selected_index=0,  # Default selection
        on_change=switch_page  # Detects changes and switches page
    )

    # --- TOP APP BAR ---
    page.appbar = ft.AppBar(
        title=ft.Text("AI Code Assistant"),
        bgcolor=primary_color,
        leading=ft.IconButton(icon=ft.icons.MENU, on_click=lambda e: setattr(page.drawer, "open", True) or page.update()),
    )

    content_container.controls = [code_generation_section]
    page.add(content_container)


if __name__ == "__main__":
    ft.app(target=main)



