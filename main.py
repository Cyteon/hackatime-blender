import bpy
import sys
import time
import requests

last_scene = None

bl_info = {
    "name": "Hackatime Wakatime",
    "blender": (4, 3, 2),
    "category": "Development",
    "author": "Cyteon"
}

print("Starting Hackatime")

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

    #requests.post("https://waka.hackclub.com/users/current/heartbeats", json=data, headers={
    #    "Content-Type": "application/json",
    #})
