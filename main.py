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
    result_text = ft.Text("", color=ft.Colors.GREEN)
    
    async def build_map(e):
        addresses = [line.strip() for line in input_field.value.split('\n') if line.strip()]
        if not addresses:
            result_text.value = "⚠️ Введите адреса!"
            result_text.color = ft.Colors.ORANGE
            page.update()  # ✅ Обычный update() работает в async
            return

        btn.disabled = True
        progress_ring.visible = True
        result_text.value = "⏳ Ищем координаты..."
        result_text.color = ft.Colors.BLUE
        page.update()

        map_points = []
        for addr in addresses:
            coords = get_coords(addr)
            if coords:
                map_points.append({"address": addr, "lat": coords[0], "lon": coords[1]})
        
        if not map_points:
            result_text.value = "❌ Адреса не найдены"
            result_text.color = ft.Colors.RED
            btn.disabled = False
            progress_ring.visible = False
            page.update()
            return

        m = folium.Map(location=[map_points[0]['lat'], map_points[0]['lon']], zoom_start=12, tiles="CartoDB dark_matter")
        
        for i, point in enumerate(map_points, 1):
            folium.Marker(
                [point['lat'], point['lon']],
                popup=f"<b>{i}. {point['address']}</b>",
                tooltip=f"Точка {i}",
                icon=folium.DivIcon(html=f"""
                    <div style="background-color:#ffcc00;color:black;border-radius:50%;width:30px;height:30px;display:flex;justify-content:center;align-items:center;font-weight:bold;border:2px solid white;box-shadow:0 0 5px rgba(0,0,0,0.5)">{i}</div>
                """)
            ).add_to(m)
            
            if i > 1:
                folium.PolyLine(
                    locations=[[map_points[i-2]['lat'], map_points[i-2]['lon']], [point['lat'], point['lon']]],
                    color="#ffcc00", weight=3, opacity=0.8
                ).add_to(m)

                try:
            # Сохраняем карту
            map_path = os.path.join(os.getcwd(), "route_map.html")
            m.save(map_path)
            
            result_text.value = "✅ Карта готова!"
            result_text.color = ft.Colors.GREEN
            page.update()
            
            # 🔧 Правильный способ для Android 7.0+
            try:
                # Пробуем открыть через UrlLauncher с правильным URI
                from pathlib import Path
                file_uri = f"content://com.flet.fletproject.fileprovider/files/{os.path.abspath(map_path)}"
                await ft.UrlLauncher().launch_url(file_uri)
            except:
                # Если не вышло — показываем инструкцию
                result_text.value = "📁 Карта сохранена как route_map.html\nОткройте её через файловый менеджер"
                result_text.color = ft.Colors.ORANGE
                page.update()
                
        except Exception as ex:
            result_text.value = f"⚠️ Ошибка: {str(ex)[:50]}..."
            result_text.color = ft.Colors.RED
        finally:
            btn.disabled = False
            progress_ring.visible = False
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
