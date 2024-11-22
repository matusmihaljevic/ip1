import psutil
import matplotlib.pyplot as plt
from playwright.sync_api import sync_playwright, Page
import time
import mplcursors

# Executes dataZoom on graph
def simulate_zoom_in(page: Page, newStart: int, newEnd: int):
    script = f"""
    var chart = echarts.getInstanceByDom(document.getElementById('chart0'));
    var currentOption = chart.getOption();
    var dataZoom = currentOption.dataZoom[0];
    var newStart = dataZoom.start + {newStart};
    var newEnd = dataZoom.end - {newEnd};
    chart.setOption({{
        dataZoom: [{{
            start: newStart,
            end: newEnd
        }}]
    }}); 
    """
    page.evaluate(script)

def track_cpu_usage_during_zoom(page, iters):
    cpu_usage_during_zoom = []
    for i in range(iters):
        for _ in range(10):
            cpu_usage = psutil.cpu_percent(interval=0.0)
            cpu_usage_during_zoom.append(cpu_usage)
        if i < iters // 2:
            simulate_zoom_in(page, 5, 5)
        else:
            simulate_zoom_in(page, -5, -5)
        time.sleep(0.1)
    return cpu_usage_during_zoom

# Main script
with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("file:///C:/ddp/echarts-example.html")
    page.wait_for_selector("#chart0 canvas")

    cpu_usage_during_zoom = track_cpu_usage_during_zoom(page, 18)
    
    browser.close()

# Plot the results
plt.figure(figsize=(10, 6))
line, = plt.plot(cpu_usage_during_zoom, label="CPU Usage (%)", color="orange")
plt.title("CPU Usage During Zooming", fontsize=14)
plt.xlabel("Time (0.01s intervals)", fontsize=12)
plt.ylabel("CPU Usage (%)", fontsize=12)
plt.legend()
plt.grid(True)

cursor = mplcursors.cursor(line, hover=True)
cursor.connect("add", lambda sel: sel.annotation.set_text(f"Time: {sel.index * 0.01:.2f}s\nCPU: {sel.target[1]:.2f}%"))

plt.show()
