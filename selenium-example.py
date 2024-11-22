import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import matplotlib.pyplot as plt
import mplcursors

options = Options()
options.headless = True

# Run Selenium WebDriver
driver = webdriver.Chrome(options=options)
driver.get("file:///C:/ddp/echarts-example.html")

# Wait for the graph
driver.implicitly_wait(5)

# Find the canvas element containing the graph
canvas = driver.find_element(By.CSS_SELECTOR, '#chart0 canvas')

# Executes dataZoom on graph
def simulate_zoom_in(newStart: int, newEnd: int):
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
    driver.execute_script(script)

# Get the WebDriver Chrome process and its children
def get_chrome_process(driver):
    parent_pid = driver.service.process.pid  # Get the PID of WebDriver process
    try:
        parent_process = psutil.Process(parent_pid)
        children = parent_process.children(recursive=True)  # Get all child processes
        return [parent_process] + children  # Include parent and its children
    except psutil.NoSuchProcess:
        return []

# Track CPU usage
def track_cpu_usage_during_zoom(chrome_processes, iters):
    cpu_usage_during_zoom = []
    for i in range(iters):
        for _ in range(10):
            cpu_usage = psutil.cpu_percent(interval=0.0)
            cpu_usage_during_zoom.append(cpu_usage)
        if i < iters/2:
            simulate_zoom_in(5, 5)
        else:
            simulate_zoom_in(-5, -5)
        time.sleep(0.1)  # Pause between zooming steps
    return cpu_usage_during_zoom

# Get Chrome processes
chrome_processes = get_chrome_process(driver)
if not chrome_processes:
    print("Chrome process not found.")
    driver.quit()
    exit()

# Measure CPU usage
cpu_usage_during_zoom = track_cpu_usage_during_zoom(chrome_processes, 18)

# Kill WebDriver
driver.quit()

# Plot the results
plt.figure(figsize=(10, 6))
line, = plt.plot(cpu_usage_during_zoom, label="CPU Usage (%)", color="orange")
plt.title("CPU Usage During Zooming", fontsize=14)
plt.xlabel("Time (0.01s intervals)", fontsize=12)
plt.ylabel("CPU Usage (%)", fontsize=12)
plt.legend()
plt.grid(True)

# Add interactive tooltips
cursor = mplcursors.cursor(line, hover=True)
cursor.connect("add", lambda sel: sel.annotation.set_text(f"Time: {sel.index * 0.01:.2f}s\nCPU: {sel.target[1]:.2f}%"))

plt.show()