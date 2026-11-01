import asyncio
import subprocess
import platform
import re
import flet as ft

def ping_host(host: str):
    """
    执行一次 Ping 并返回耗时 (ms) 和状态
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    
    try:
        output = subprocess.run(command, capture_output=True, text=True, timeout=3)
        if output.returncode == 0:
            res = output.stdout
            match = re.search(r"(?:time|时间)[<=](\d+ms|\d+\.\d+ms)", res, re.IGNORECASE)
            if not match:
                match = re.search(r"(?:time|时间)[<=]\s*(\d+)", res, re.IGNORECASE)
            
            if match:
                val = match.group(1)
                if not val.endswith("ms"):
                    val += "ms"
                return True, val
            return True, "<1ms"
        else:
            return False, "超时"
    except Exception as e:
        return False, "错误"

def main(page: ft.Page):
    page.title = "OKX Network Ping Studio"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#0B0E14"  # 欧易/暗黑专业交易应用背景色
    page.padding = 24
    page.window.width = 950
    page.window.height = 750
    page.window.resizable = True

    # 状态存储
    target_hosts = [
        {"name": "主节点 (Cloudflare)", "host": "1.1.1.1", "status": "检测中...", "latency": "-"},
        {"name": "备用节点 (Google)", "host": "8.8.8.8", "status": "检测中...", "latency": "-"},
        {"name": "国内高速 (百度)", "host": "www.baidu.com", "status": "检测中...", "latency": "-"},
        {"name": "香港节点", "host": "8.210.0.1", "status": "检测中...", "latency": "-"},
    ]

    # UI 控件引用列表
    node_cards = []

    # 顶栏标题
    header = ft.Row(
        [
            ft.Row([
                ft.Container(
                    bgcolor="#0052FF",
                    width=10,
                    height=24,
                    border_radius=2
                ),
                ft.Text("OKX NETWORK STUDIO", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ], spacing=10),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=10, color=ft.Colors.GREEN_ACCENT),
                    ft.Text("实时网络引擎就绪", size=12, color=ft.Colors.GREEN_ACCENT),
                ], spacing=6),
                bgcolor="#151A21",
                padding=8,
                border_radius=20,
                border=ft.Border(
                    top=ft.BorderSide(1, "#222D3D"),
                    bottom=ft.BorderSide(1, "#222D3D"),
                    left=ft.BorderSide(1, "#222D3D"),
                    right=ft.BorderSide(1, "#222D3D"),
                )
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 自定义输入框
    input_host = ft.TextField(
        label="输入自定义主机/IP",
        label_style=ft.TextStyle(color="#848E9C", size=12),
        border_color="#222D3D",
        focused_border_color="#0052FF",
        color=ft.Colors.WHITE,
        bgcolor="#151A21",
        text_size=14,
        height=48,
        expand=True,
    )

    # 可滚动卡片容器（支持无限添加节点滚动浏览）
    cards_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)

    def build_cards():
        cards_column.controls.clear()
        node_cards.clear()
        
        for item in target_hosts:
            status_badge = ft.Container(
                content=ft.Text(item["status"], size=11, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                bgcolor="#222D3D",
                padding=6,
                border_radius=4,
            )
            
            latency_text = ft.Text(item["latency"], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            
            card_content = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.DNS_OUTLINED, color="#0052FF", size=20),
                            bgcolor="#1E2633",
                            padding=10,
                            border_radius=8,
                        ),
                        ft.Column([
                            ft.Text(item["name"], size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(item["host"], size=12, color="#848E9C"),
                        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=12),
                    ft.Row([
                        ft.Column([
                            latency_text,
                            ft.Text("响应延迟", size=10, color="#848E9C"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0),
                        ft.Container(width=15),
                        status_badge,
                    ], alignment=ft.MainAxisAlignment.END)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#151A21",
                padding=16,
                border_radius=12,
                border=ft.Border(
                    top=ft.BorderSide(1, "#222D3D"),
                    bottom=ft.BorderSide(1, "#222D3D"),
                    left=ft.BorderSide(1, "#222D3D"),
                    right=ft.BorderSide(1, "#222D3D"),
                ),
            )
            
            node_cards.append({
                "data": item,
                "card": card_content,
                "latency_text": latency_text,
                "status_badge": status_badge
            })
            cards_column.controls.append(card_content)

    build_cards()

    # 异步巡检任务
    is_running = False

    async def start_ping_loop(e):
        nonlocal is_running
        if is_running:
            return
        is_running = True
        btn_start.content.controls[1].value = "检测中..."
        btn_start.bgcolor = "#1E2633"
        btn_start.update()

        try:
            while is_running:
                for nc in node_cards:
                    host = nc["data"]["host"]
                    success, val = await asyncio.to_thread(ping_host, host)
                    
                    if success:
                        nc["data"]["status"] = "正常"
                        nc["data"]["latency"] = val
                        nc["status_badge"].bgcolor = "#00B42A22"
                        nc["status_badge"].content.color = "#00B42A"
                        nc["card"].border = ft.Border(
                            top=ft.BorderSide(1, "#00B42A55"),
                            bottom=ft.BorderSide(1, "#00B42A55"),
                            left=ft.BorderSide(1, "#00B42A55"),
                            right=ft.BorderSide(1, "#00B42A55"),
                        )
                        
                        num_val = float(re.sub(r"[^\d.]", "", val) or 0)
                        if num_val < 50:
                            nc["latency_text"].color = "#00B42A"
                        elif num_val < 150:
                            nc["latency_text"].color = "#FF7D00"
                        else:
                            nc["latency_text"].color = "#F53F3F"
                    else:
                        nc["data"]["status"] = "超时"
                        nc["data"]["latency"] = "-"
                        nc["status_badge"].bgcolor = "#F53F3F22"
                        nc["status_badge"].content.color = "#F53F3F"
                        nc["card"].border = ft.Border(
                            top=ft.BorderSide(1, "#F53F3F55"),
                            bottom=ft.BorderSide(1, "#F53F3F55"),
                            left=ft.BorderSide(1, "#F53F3F55"),
                            right=ft.BorderSide(1, "#F53F3F55"),
                        )
                        nc["latency_text"].color = "#F53F3F"
                        
                    nc["latency_text"].value = nc["data"]["latency"]
                    nc["status_badge"].content.value = nc["data"]["status"]
                    nc["card"].update()
                
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass
        finally:
            is_running = False
            btn_start.content.controls[1].value = "开始实时检测"
            btn_start.bgcolor = "#0052FF"
            btn_start.update()

    def stop_ping_loop(e):
        nonlocal is_running
        is_running = False
        btn_start.content.controls[1].value = "开始实时检测"
        btn_start.bgcolor = "#0052FF"
        btn_start.update()

    def add_custom_host(e):
        h = input_host.value.strip()
        if not h:
            return
        target_hosts.append({
            "name": f"自定义节点 #{len(target_hosts) - 3}",
            "host": h,
            "status": "等待检测",
            "latency": "-",
        })
        input_host.value = ""
        input_host.update()
        build_cards()
        cards_column.update()

    # 控制按钮
    btn_start = ft.FilledButton(
        content=ft.Row([
            ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=ft.Colors.WHITE, size=18),
            ft.Text("开始实时检测", color=ft.Colors.WHITE)
        ], spacing=6),
        bgcolor="#0052FF",
        on_click=start_ping_loop
    )

    btn_stop = ft.FilledButton(
        content=ft.Row([
            ft.Icon(ft.Icons.STOP_ROUNDED, color="#848E9C", size=18),
            ft.Text("停止", color="#848E9C")
        ], spacing=6),
        bgcolor="#1E2633",
        on_click=stop_ping_loop
    )

    btn_add = ft.FilledButton(
        content=ft.Row([
            ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=18),
            ft.Text("添加节点", color=ft.Colors.WHITE)
        ], spacing=6),
        bgcolor="#1E2633",
        on_click=add_custom_host
    )

    controls_row = ft.Row([
        input_host,
        btn_add,
        btn_start,
        btn_stop,
    ], spacing=12)

    # 主布局组合（用 Container 包裹列表，设置 expand=True 并支持内部滚动）
    page.add(
        ft.Column([
            header,
            ft.Divider(height=24, color="#222D3D"),
            controls_row,
            ft.Container(height=10),
            ft.Row([
                ft.Text("节点延迟监控矩阵", size=14, weight=ft.FontWeight.BOLD, color="#848E9C"),
                ft.Text("支持无限添加并自动循环监控", size=11, color="#556277"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Container(
                content=cards_column,
                expand=True,
            )
        ], spacing=10, expand=True)
    )

if __name__ == "__main__":
    ft.run(main)
