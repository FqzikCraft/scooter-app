import flet as ft
import folium
import requests
import os

def get_coords(address):
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}&limit=1"
        headers = {'User-Agent': 'ScooterApp/1.0'}
        response = requests.get(url, headers=headers).json()
        if response:
            return float(response[0]['lat']), float(response[0]['lon'])
    except Exception:
        return None
    return None

async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Маршрут самокатов"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    title = ft.Text("🛴 Миссия: Перезарядка", size=24, weight=ft.FontWeight.BOLD)
    input_field = ft.TextField(
        label="Вставь адреса (каждый с новой строки)", 
        multiline=True, min_lines=5, max_lines=10,
        border_radius=15,
        hint_text="Тихая улица, 18с2\nТаганрогская улица, 27..."
    )
    
    progress_ring = ft.ProgressRing(visible=False)
    result_text = ft.Text("", color=ft.Colors.GREEN, size=14)
    
    async def build_map(e):
        addresses = [line.strip() for line in input_field.value.split('\n') if line.strip()]
        if not addresses:
            result_text.value = "⚠️ Введите адреса!"
            result_text.color = ft.Colors.ORANGE
            page.update()
            return

        btn.disabled = True
        progress_ring.visible = True
        result_text.value = "⏳ Ищем координаты..."
        result_text.color = ft.Colors.BLUE
        page.update()

        map_points = []
        for addr in addresses:
            coords = get_coords(addr)            if coords:
                map_points.append({"address": addr, "lat": coords[0], "lon": coords[1]})
        
        if not map_points:
            result_text.value = "❌ Адреса не найдены"
            result_text.color = ft.Colors.RED
            btn.disabled = False
            progress_ring.visible = False
            page.update()
            return

        # 🗺️ СВЕТЛАЯ КАРТА (как Яндекс.Карты)
        m = folium.Map(
            location=[map_points[0]['lat'], map_points[0]['lon']], 
            zoom_start=12, 
            tiles="CartoDB voyager"
        )
        
        for i, point in enumerate(map_points, 1):
            folium.Marker(
                [point['lat'], point['lon']],
                popup=f"<b>{i}. {point['address']}</b>",
                tooltip=f"Точка {i}",
                icon=folium.DivIcon(html=f"""
                    <div style="
                        background-color: #FF0000; 
                        color: white; 
                        border-radius: 50%; 
                        width: 30px; 
                        height: 30px; 
                        display: flex; 
                        justify-content: center; 
                        align-items: center; 
                        font-weight: bold;
                        border: 2px solid white;
                        box-shadow: 0 0 5px rgba(0,0,0,0.3);
                        font-size: 14px;
                    ">{i}</div>
                """)
            ).add_to(m)
            
            if i > 1:
                folium.PolyLine(
                    locations=[[map_points[i-2]['lat'], map_points[i-2]['lon']], [point['lat'], point['lon']]],
                    color="#FF0000", weight=3, opacity=0.9
                ).add_to(m)

        try:
            # 📁 Пробуем сохранить в Documents
            if os.path.exists('/storage/emulated/0'):                save_dir = "/storage/emulated/0/Documents"
            else:
                save_dir = os.path.join(os.path.expanduser("~"), "Documents")
                
            os.makedirs(save_dir, exist_ok=True)
            map_path = os.path.join(save_dir, "route_map.html")
            m.save(map_path)
            folder_name = "Documents"
            
        except Exception:
            # Если доступ заблокирован → сохраняем в папку приложения (гарантированно работает)
            save_dir = os.getcwd()
            map_path = os.path.join(save_dir, "route_map.html")
            m.save(map_path)
            folder_name = "папку приложения"

        result_text.value = "✅ Карта сохранена!"
        result_text.color = ft.Colors.GREEN
        page.update()
        
        # 📱 Показываем понятное окно с путём
        page.dialog = ft.AlertDialog(
            title=ft.Text("🗺️ Карта готова!", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"📂 Файл сохранён в:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"{folder_name}/route_map.html", size=16, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD, selectable=True),
                ft.Divider(),
                ft.Text("📱 Как открыть:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("1. Откройте 'Мои файлы' / 'Файловый менеджер'", size=13),
                ft.Text("2. Перейдите в папку 'Documents' (Документы)", size=13),
                ft.Text("3. Найдите 'route_map.html'", size=13),
                ft.Text("4. Нажмите на файл → 'Открыть через Chrome'", size=13),
                ft.Divider(),
                ft.Text("💡 Карта работает только с интернетом!", size=12, color=ft.Colors.ORANGE)
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.ElevatedButton("Понятно, закрыть", on_click=lambda _: close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        def close_dialog():
            page.dialog.open = False
            page.update()
        
        page.dialog.open = True
        page.update()
            
        finally:
            btn.disabled = False            progress_ring.visible = False
            page.update()

    btn = ft.Button(
        "Построить маршрут 🗺️", 
        icon="map",
        style=ft.ButtonStyle(padding=20, shape=ft.RoundedRectangleBorder(radius=15)),
        on_click=build_map
    )

    page.add(
        ft.Column(
            [title, ft.Container(height=20), input_field, ft.Container(height=10), 
             ft.Row([progress_ring, result_text], alignment=ft.MainAxisAlignment.CENTER), btn],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    )

ft.run(main)
