import flet as ft
import folium
import requests
import os
import platform

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
            # 📁 Сохраняем в ПРИБАВКУ ПРИЛОЖЕНИЯ (всегда есть доступ!)
            app_dir = os.getcwd()  # Папка приложения: /data/user/0/com.flet.scooter_app/files/flet/app/
            map_path = os.path.join(app_dir, "route_map.html")
            m.save(map_path)
            
            result_text.value = "✅ Карта создана!"
            result_text.color = ft.Colors.GREEN
            page.update()
            
            # 🚀 Пробуем открыть файл
            try:
                # Пытаемся открыть через UrlLauncher
                launcher = ft.UrlLauncher()
                await launcher.launch_url(f"file://{map_path}")
            except Exception as launch_err:
                # Если не удалось — показываем что файл сохранён
                result_text.value = "✅ Карта сохранена!\n\n📂 Файл: route_map.html\n\n📱 Чтобы открыть:\n1. Подключите телефон к ПК\n2. Найдите папку приложения\n3. Скопируйте route_map.html\n4. Откройте на телефоне\n\nИли откройте через файловый менеджер внутри папки приложения"
                result_text.color = ft.Colors.ORANGE
                page.update()
                
        except Exception as ex:
            result_text.value = f"⚠️ Ошибка: {str(ex)[:50]}"
            result_text.color = ft.Colors.RED
            page.update()
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
