import bpy
import sys
import os
import time
import requests
import configparser

last_scene = ""
api_key = ""
coding_time_this_session = 0

if "win" in sys.platform:
    config = configparser.ConfigParser()
    config.read("C:/Users/%s/.wakatime.cfg" % os.getlogin())
    api_key = config["settings"]["api_key"]

elif "darwin" in sys.platform or "linux" in sys.platform:
    config = configparser.ConfigParser()
    home_dir = os.path.expanduser("~")
    config.read(home_dir + "/.wakatime.cfg")
    api_key = config["settings"]["api_key"]

bl_info = {
    "name": "Hackatime Wakatime",
    "blender": (4, 3, 2),
    "category": "Development",
    "author": "Cyteon"
}

print("Starting Hackatime")
print("API Key: %s" % api_key)

def get_os():
    if "darwin" in sys.platform:
        return "Mac"
    elif "win" in sys.platform:
        return "Windows"
    elif "linux" in sys.platform:
        return "Linux"
    return "none"

print("Running on " + get_os())

def encode_scene_as_string():
    scene = bpy.context.scene
    scene_string = ""
    for key in scene.objects.keys():
        obj = scene.objects[key]
        scene_string += "%s-%s_(%s)(%s)(%s)" % (key, obj, obj.location, obj.rotation_euler, obj.scale)
        if (obj.data):
            scene_string += "-%s" % obj.data
            if ("vertices" in dir(obj.data)):
                scene_string += "-%s_%s\n" % (obj.data.vertices, ",".join([str(x.co) for x in obj.data.vertices]))
    return scene_string

def send_heartbeat():
    print("Sending heartbeat")

    path = bpy.context.blend_data.filepath
    project = ""

    if path != "":
        project = bpy.context.blend_data.filepath.split("/")[-2]
    else:
        path = "Untitled"
        project = "Untitled"

    data = {
        "entity": path,
        "project": project,
        "type": "file",
        "category": "Modelling",
        "language": "Blender",
        "time": int(time.time()),
        "lines": len(bpy.context.scene.objects.keys()),

        "editor": "Blender",
        "machine": "%s: %s (%s)" % (get_os(), bpy.app.version_string, bpy.app.build_platform),
        "operating_system": get_os(),
        "user_agent": "wakatime/unset (Blender-%s) cyteon/blender-hackatime" % bpy.app.version_string,

        "is_write": False,
        "lineno": 1,
        "cursorpos": 1,
    }

    print(data)

    res = requests.post("https://waka.hackclub.com/api/users/current/heartbeats", json=data, headers={
        "Content-Type": "application/json",
        "Authorization": "Basic %s" % api_key
    })

    print("Response: " + str(res.status_code), " | ", res.text)

def update_coding_time():
    global coding_time_this_session
    res = requests.get("https://waka.hackclub.com/api/compat/wakatime/v1/users/current/summaries?range=today", headers={
        "Content-Type": "application/json",
        "Authorization": "Basic %s" % api_key
    })

    if res.status_code == 200:
        data = res.json()
        coding_time_this_session = data["data"][0]["grand_total"]["total_seconds"]
        print("Coding time today: %s" % time.strftime("%H:%M:%S", time.gmtime(coding_time_this_session)))
    else:
        print("Failed to get coding time")
        print("Response: " + str(res.status_code), " | ", res.text)

@bpy.app.handlers.persistent
def timer_fired():
    global last_scene

    print("Timer fired")

    if encode_scene_as_string() != last_scene:
        send_heartbeat()
        last_scene = encode_scene_as_string()
    
    update_coding_time()

    return 120

bpy.app.timers.register(timer_fired, first_interval=120, persistent=True)

def draw_info(self, context):
    layout = self.layout
    layout.label(text="Hackatime Today: %s" % time.strftime("%H:%M:%S", time.gmtime(coding_time_this_session)))

def unregister():
    try:
        bpy.types.STATUSBAR_HT_header.remove(draw_info)
    except:
        pass

def register():
    unregister()

    bpy.types.STATUSBAR_HT_header.append(draw_info)

register()
update_coding_time()