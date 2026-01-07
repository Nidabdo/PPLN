import flet as ft
import json
import os

def main(page: ft.Page):
    page.title = "Patching pour les Noobs"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 700

    # Fichier de sauvegarde
    SAVE_FILE = "roadmap_data.json"

    # Fonction pour sauvegarder les tâches
    def save_tasks():
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            print(f">>> Données sauvegardées dans {SAVE_FILE}")
        except Exception as e:
            print(f">>> Erreur lors de la sauvegarde: {e}")

    # Fonction pour charger les tâches
    def load_tasks():
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    print(f">>> Données chargées depuis {SAVE_FILE}")
                    return loaded
            except Exception as e:
                print(f">>> Erreur lors du chargement: {e}")
                return {"test": [], "pilote": [], "prod": []}
        return {"test": [], "pilote": [], "prod": []}
    
    # Fonction pour migrer l'ancien format (liste plate) vers le nouveau (liste de colonnes)
    def migrate_to_columns(tasks_dict):
        """Convertit les tâches plates en colonnes si nécessaire"""
        for env in ["test", "pilote", "prod"]:
            if env in tasks_dict and len(tasks_dict[env]) > 0:
                # Vérifier si c'est déjà au nouveau format (liste de listes)
                first_item = tasks_dict[env][0]
                if not isinstance(first_item, list):
                    # Migration : convertir chaque tâche en une colonne avec une seule tâche
                    print(f">>> Migration de {env} vers le format colonnes")
                    tasks_dict[env] = [[task] for task in tasks_dict[env]]
        return tasks_dict

    # Stockage des tâches par environnement (chargement depuis le fichier)
    tasks = migrate_to_columns(load_tasks())
    
    # État de verrouillage global (pour persister entre les recharges)
    lock_states = {"test": True, "pilote": True, "prod": True}

    def reset_app():
        # Réinitialiser toutes les tâches
        for env in ["test", "pilote", "prod"]:
            tasks[env] = []
        save_tasks()
        go_to_home()

    def go_to_home():
        page.clean()
        
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Patching pour les Noobs", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Choisissez un changement", size=18),
                    ft.Divider(),
                    ft.ElevatedButton(
                        "Test",
                        on_click=lambda _: go_to_roadmap("test"),
                        width=200
                    ),
                    ft.ElevatedButton(
                        "Pilote",
                        on_click=lambda _: go_to_roadmap("pilote"),
                        width=200
                    ),
                    ft.ElevatedButton(
                        "Prod",
                        on_click=lambda _: go_to_roadmap("prod"),
                        width=200
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                alignment=ft.Alignment(0, 0),
                expand=True
            )
        )
        page.update()

    def go_to_roadmap(env_name):
        page.clean()
        
        # Container pour les tâches en mode flowchart horizontal
        tasks_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=0, alignment=ft.MainAxisAlignment.START)
        
        def toggle_lock():
            lock_states[env_name] = not lock_states[env_name]
            print(f">>> Mode verrouillé pour {env_name}: {lock_states[env_name]}")
            # Recréer la page pour mettre à jour l'icône du cadenas
            go_to_roadmap(env_name)
        
        task_name_input = ft.TextField(
            label="Nom de la tâche *",
            hint_text="Ex: Déployer sur serveur"
        )
        
        task_desc_input = ft.TextField(
            label="Description (optionnel)",
            multiline=True,
            min_lines=2,
            max_lines=3,
            hint_text="Détails de la tâche..."
        )
        
        priority_dropdown = ft.Dropdown(
            label="Priorité",
            value="Moyenne",
            width=200,
            options=[
                ft.dropdown.Option("Haute"),
                ft.dropdown.Option("Moyenne"),
                ft.dropdown.Option("Basse")
            ]
        )
        
        add_form_container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Nouvelle tâche", size=18, weight=ft.FontWeight.BOLD),
                        task_name_input,
                        task_desc_input,
                        priority_dropdown,
                        ft.Row([
                            ft.ElevatedButton(
                                "Annuler",
                                on_click=lambda e: toggle_add_form(False)
                            ),
                            ft.ElevatedButton(
                                "Ajouter",
                                on_click=lambda e: save_new_task()
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ]),
                    padding=20
                )
            ),
            visible=False
        )
        
        # Formulaire d'édition
        edit_task_name_input = ft.TextField(
            label="Nom de la tâche *",
            hint_text="Ex: Déployer sur serveur"
        )
        
        edit_task_desc_input = ft.TextField(
            label="Description (optionnel)",
            multiline=True,
            min_lines=2,
            max_lines=3,
            hint_text="Détails de la tâche..."
        )
        
        edit_priority_dropdown = ft.Dropdown(
            label="Priorité",
            value="Moyenne",
            width=200,
            options=[
                ft.dropdown.Option("Haute"),
                ft.dropdown.Option("Moyenne"),
                ft.dropdown.Option("Basse")
            ]
        )
        
        edit_form_container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Modifier la tâche", size=18, weight=ft.FontWeight.BOLD),
                        edit_task_name_input,
                        edit_task_desc_input,
                        edit_priority_dropdown,
                        ft.Row([
                            ft.ElevatedButton(
                                "Annuler",
                                on_click=lambda e: toggle_edit_form(False)
                            ),
                            ft.ElevatedButton(
                                "Enregistrer",
                                on_click=lambda e: save_edited_task()
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ]),
                    padding=20
                )
            ),
            visible=False,
            data=None
        )
        
        def show_instructions_popup(task_data, col_index, task_index_in_col):
            """Affiche un popup avec les instructions de la tâche"""
            print(f">>> Ouverture popup instructions pour: {task_data['text']}")
            
            instructions_field = ft.TextField(
                value=task_data.get("instructions", ""),
                multiline=True,
                min_lines=8,
                max_lines=15,
                hint_text="Ajoutez des instructions détaillées ici...",
                read_only=True,
                border_color=ft.Colors.BLUE_400,
                expand=True
            )
            
            def toggle_edit(e):
                instructions_field.read_only = not instructions_field.read_only
                edit_btn.icon = ft.Icons.SAVE if not instructions_field.read_only else ft.Icons.EDIT
                edit_btn.tooltip = "Sauvegarder" if not instructions_field.read_only else "Éditer"
                page.update()
            
            def close_overlay(e):
                # Sauvegarder si en mode édition
                if not instructions_field.read_only:
                    tasks[env_name][col_index][task_index_in_col]["instructions"] = instructions_field.value
                    save_tasks()
                    print(f">>> Instructions sauvegardées")
                overlay_container.visible = False
                page.update()
            
            edit_btn = ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Éditer",
                on_click=toggle_edit,
                icon_color=ft.Colors.BLUE_400
            )
            
            # Créer un overlay personnalisé
            overlay_container = ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"📝 Instructions - {task_data['text']}", 
                                       size=20, 
                                       weight=ft.FontWeight.BOLD,
                                       expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=close_overlay,
                                    tooltip="Fermer"
                                )
                            ]),
                            ft.Divider(),
                            instructions_field,
                            ft.Divider(),
                            ft.Row([
                                edit_btn,
                                ft.ElevatedButton("Fermer", on_click=close_overlay)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ], tight=True),
                        padding=20,
                        width=600,
                        height=400
                    ),
                    elevation=10
                ),
                bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                alignment=ft.Alignment(0, 0),
                expand=True,
                visible=True
            )
            
            # Ajouter à page.overlay
            page.overlay.append(overlay_container)
            page.update()
            print(f">>> Overlay affiché")
        
        def create_task_node_in_column(task, col_index, task_index_in_col):
            """Crée un nœud visuel pour une tâche dans une colonne"""
            priority_color = {
                "Haute": ft.Colors.RED,
                "Moyenne": ft.Colors.ORANGE,
                "Basse": ft.Colors.GREEN
            }.get(task.get("priority", "Moyenne"), ft.Colors.ORANGE)
            
            def on_checkbox_change(e):
                tasks[env_name][col_index][task_index_in_col]["done"] = e.control.value
                save_tasks()
                page.update()
            
            def delete_task(e):
                print(f">>> Suppression de la tâche colonne={col_index}, index={task_index_in_col}")
                tasks[env_name][col_index].pop(task_index_in_col)
                # Si la colonne est vide, la supprimer
                if len(tasks[env_name][col_index]) == 0:
                    tasks[env_name].pop(col_index)
                save_tasks()
                refresh_tasks()
            
            def edit_task(e):
                print(f">>> Édition de la tâche colonne={col_index}, index={task_index_in_col}")
                edit_task_name_input.value = tasks[env_name][col_index][task_index_in_col]["text"]
                edit_task_desc_input.value = tasks[env_name][col_index][task_index_in_col].get("description", "")
                edit_priority_dropdown.value = tasks[env_name][col_index][task_index_in_col].get("priority", "Moyenne")
                # Stocker les deux indices
                edit_form_container.data = (col_index, task_index_in_col)
                toggle_edit_form(True)
            
            return ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Checkbox(
                                    value=task["done"],
                                    on_change=on_checkbox_change
                                ),
                                ft.Text(
                                    task["text"],
                                    size=16,
                                    weight=ft.FontWeight.BOLD if not task["done"] else ft.FontWeight.NORMAL,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.INFO_OUTLINE,
                                    icon_color=ft.Colors.CYAN_400,
                                    icon_size=20,
                                    tooltip="Instructions",
                                    on_click=lambda e, t=task, ci=col_index, ti=task_index_in_col: show_instructions_popup(t, ci, ti)
                                )
                            ], spacing=5),
                            ft.Text(
                                task.get("description", ""),
                                size=12,
                                color=ft.Colors.GREY_400,
                                max_lines=3,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                visible=bool(task.get("description"))
                            ),
                            ft.Container(
                                content=ft.Text(
                                    task.get("priority", "Moyenne"),
                                    size=10,
                                    color=ft.Colors.WHITE
                                ),
                                bgcolor=priority_color,
                                padding=5,
                                border_radius=5,
                                alignment=ft.Alignment(0, 0)
                            ),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=ft.Colors.BLUE_400,
                                    icon_size=18,
                                    tooltip="Modifier",
                                    on_click=edit_task,
                                    disabled=lock_states[env_name]
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=18,
                                    tooltip="Supprimer",
                                    on_click=delete_task,
                                    disabled=lock_states[env_name]
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5, visible=not lock_states[env_name])
                        ], spacing=10, tight=True),
                        padding=15,
                        width=250
                    ),
                    elevation=3
                ),
                margin=ft.margin.only(top=5, bottom=5)
            )
        
        def create_connector():
            """Crée une ligne de connexion entre deux nœuds"""
            return ft.Container(
                bgcolor=ft.Colors.BLUE_400,
                width=20,
                height=2
            )
        
        def create_add_button_horizontal(insert_at_col_index):
            """Crée un bouton + horizontal pour ajouter une nouvelle colonne"""
            def add_new_column(e):
                # Stocker l'index de colonne
                add_form_container.data = ("new_column", insert_at_col_index)
                toggle_add_form(True)
            
            return ft.Container(
                content=ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    bgcolor=ft.Colors.BLUE_400,
                    on_click=add_new_column,
                    mini=True,
                    tooltip="Nouvelle étape"
                ),
                margin=ft.margin.only(top=70, left=10, right=10)
            )
        
        def add_task_to_column(col_index):
            """Ouvre le formulaire pour ajouter une tâche dans une colonne existante"""
            add_form_container.data = ("same_column", col_index)
            toggle_add_form(True)
        
        def refresh_tasks():
            tasks_row.controls.clear()
            
            # Chaque élément de tasks[env_name] est maintenant une colonne (liste de tâches)
            for col_index, column in enumerate(tasks[env_name]):
                # Vérifier si ce n'est pas la dernière colonne (pour ajouter les lignes)
                is_last_column = col_index == len(tasks[env_name]) - 1
                
                # Créer une colonne verticale de tâches (sans le bouton +)
                column_tasks = []
                
                for task_index_in_col, task in enumerate(column):
                    # Créer le nœud de tâche
                    task_node = create_task_node_in_column(task, col_index, task_index_in_col)
                    column_tasks.append(task_node)
                    
                
                # Ajouter bouton + vertical en bas de la colonne
                if not lock_states[env_name]:
                    column_tasks.append(
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.ADD,
                                icon_color=ft.Colors.GREEN_400,
                                icon_size=20,
                                tooltip="Ajouter tâche parallèle",
                                on_click=lambda e, ci=col_index: add_task_to_column(ci)
                            ),
                            margin=ft.margin.only(top=10),
                            alignment=ft.Alignment(0, 0)
                        )
                    )
                
                # Créer le container de la colonne (sans lignes verticales/horizontales)
                column_container = ft.Container(
                    content=ft.Column(column_tasks, spacing=10, tight=True),
                    margin=ft.margin.only(left=20 if col_index == 0 else 0, top=20, bottom=20)
                )
                
                # Ajouter la colonne au row
                tasks_row.controls.append(column_container)
                
                # Ajouter connecteur et bouton + horizontal
                if col_index < len(tasks[env_name]) - 1 or len(tasks[env_name]) > 0:
                    tasks_row.controls.append(create_connector())
                    if not lock_states[env_name]:
                        tasks_row.controls.append(create_add_button_horizontal(col_index + 1))
            
            # Si aucune tâche, ajouter un bouton + pour commencer
            if len(tasks[env_name]) == 0 and not lock_states[env_name]:
                tasks_row.controls.append(
                    ft.Container(
                        content=create_add_button_horizontal(0),
                        margin=ft.margin.only(left=50)
                    )
                )
            
            page.update()
        
        def toggle_add_form(show):
            print(f">>> toggle_add_form: {show}")
            add_form_container.visible = show
            page.update()
        
        def save_new_task():
            print(">>> save_new_task appelé")
            if task_name_input.value and task_name_input.value.strip():
                task_data = {
                    "text": task_name_input.value.strip(),
                    "description": task_desc_input.value.strip() if task_desc_input.value else "",
                    "priority": priority_dropdown.value,
                    "done": False
                }
                
                # Interpréter add_form_container.data
                data = add_form_container.data
                
                if data is None or (isinstance(data, tuple) and data[0] == "new_column"):
                    # Nouvelle colonne
                    insert_index = data[1] if (isinstance(data, tuple) and len(data) > 1) else len(tasks[env_name])
                    tasks[env_name].insert(insert_index, [task_data])
                    print(f">>> Nouvelle colonne créée à l'index {insert_index}")
                elif isinstance(data, tuple) and data[0] == "same_column":
                    # Ajouter dans une colonne existante
                    col_index = data[1]
                    tasks[env_name][col_index].append(task_data)
                    print(f">>> Tâche ajoutée à la colonne {col_index}")
                
                save_tasks()
                
                # Réinitialiser le formulaire
                task_name_input.value = ""
                task_desc_input.value = ""
                priority_dropdown.value = "Moyenne"
                add_form_container.data = None
                
                toggle_add_form(False)
                refresh_tasks()
        
        def toggle_edit_form(show):
            print(f">>> toggle_edit_form: {show}")
            edit_form_container.visible = show
            if not show:
                edit_form_container.data = None  # Réinitialiser l'index
            page.update()
        
        def save_edited_task():
            print(">>> save_edited_task appelé")
            if edit_task_name_input.value and edit_task_name_input.value.strip():
                indices = edit_form_container.data
                if indices is not None and isinstance(indices, tuple):
                    col_index, task_index_in_col = indices
                    tasks[env_name][col_index][task_index_in_col]["text"] = edit_task_name_input.value.strip()
                    tasks[env_name][col_index][task_index_in_col]["description"] = edit_task_desc_input.value.strip() if edit_task_desc_input.value else ""
                    tasks[env_name][col_index][task_index_in_col]["priority"] = edit_priority_dropdown.value
                    print(f">>> Tâche col={col_index}, index={task_index_in_col} modifiée")
                    save_tasks()
                    
                    # Réinitialiser le formulaire
                    edit_task_name_input.value = ""
                    edit_task_desc_input.value = ""
                    edit_priority_dropdown.value = "Moyenne"
                    
                    toggle_edit_form(False)
                    refresh_tasks()
        
        # Affichage initial des tâches
        refresh_tasks()
        
        page.add(
            ft.Column([
                ft.AppBar(
                    title=ft.Text(f"Roadmap - {env_name.capitalize()}"),
                    bgcolor="surfaceVariant",
                    leading=ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        on_click=lambda _: go_to_home()
                    ),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.LOCK if lock_states[env_name] else ft.Icons.LOCK_OPEN,
                            icon_color=ft.Colors.RED_400 if lock_states[env_name] else ft.Colors.GREEN_400,
                            tooltip="Déverrouiller" if lock_states[env_name] else "Verrouiller",
                            on_click=lambda _: toggle_lock()
                        )
                    ]
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Tâches - {env_name.capitalize()}", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        add_form_container,
                        edit_form_container,
                        ft.Container(
                            content=tasks_row,
                            expand=True,
                            padding=10
                        )
                    ]),
                    padding=20,
                    expand=True
                )
            ], expand=True)
        )
        page.update()

    # Afficher la page d'accueil au démarrage
    go_to_home()

if __name__ == "__main__":
    ft.app(target=main)
