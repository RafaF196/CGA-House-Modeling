import bpy, bmesh
import random
import math
import mathutils
import time
 
### CONFIGURATION ###

# Path to the folder
path = ""

# Special prefabs
interior_prefabs = ["window", "window2", "window3", "window4", "window5", "window6", "door"]
roof_prefabs = ["roof1", "roof2", "roof3", "roof4"]

# Daytime = True | Nighttime = False
daytime = False

# Number of houses and layers
num_houses = 3
num_layers = 2


### INPUT ###

def prod_rules(block):
    obj = bpy.data.objects[block.id]
    tag = block.tag
    
    # Edit this to generate the rules
    # if tag -> return Succesor
    # Operations available: "extrude_face", "subdivide", "add_prefab"
    
    ##############################################
    
    # House 1
    if layer == 1:
        if tag == 'L':
            return extrude_face(obj, 4, [2.5, 3.0], 'B')
        if tag == 'B':
            add_prefab(obj, "fence", 1, 0, 'N', "bricks")
            add_prefab(obj, "fence", 1, 1, 'N', "bricks")
            add_prefab(obj, "fence", 1, 3, 'N', "bricks")
            rng = random.uniform(0.0, 1.0)
            if rng < 0.3:
                return subdivide(obj, 0, [['R', 2], [0.5, 0.7], ['R', 1]], ['F', 'C', 'EF'], "marble")
            elif rng < 0.6:
                return subdivide(obj, 0, [['R', 1], ['R', 2], [0.5, 0.7]], ['EF', 'F', 'C'], "marble")
            else:
                return subdivide(obj, 0, [['R', 1], [0.5, 0.7], ['R', 2]], ['EF', 'C', 'F'], "marble")
        if tag == 'EF':
            return extrude_face(obj, 2, [1.5, 2.0], 'F')
        if tag == 'C':
            return add_prefab(obj, "chimeney", 1, 2, 'N', "bricks")
        if tag == 'F':
            return subdivide(obj, 2, [[1.2, 1.5], ['R', 1]], ['FL', 'FL'], "marble")
        if tag == 'FL':
            rng = random.uniform(0.0, 1.0)
            if rng < 0.5:
                return subdivide(obj, 0, [['R', 0.5], ['R', 0.6], ['R', 0.5]], ['W','W','W'], "marble")
            else:
                return subdivide(obj, 0, [['R', 0.5], ['R', 0.6], ['R', 0.5]], ['W2','W2','W2'], "marble")
        if tag == 'W':
            return add_prefab(obj, "window", 0.5, 2, 'N', "wood")
        if tag == 'W2':
            return add_prefab(obj, "window2", 0.5, 2, 'N', "wood")
    
    if layer == 2:
        if tag == 'B':
            return subdivide(obj, 2, [['R', 1], [0.15, 0.2], ['R', 1]], ['CB', 'CO', 'N'], "marble")
        if tag == 'CB':
            return subdivide(obj, 0, [[0.15, 0.2], ['R', 1], [0.15, 0.2]], ['CO', 'N', 'CO'], "marble")
        if tag == 'CO':
            return extrude_face(obj, 2, [1.5, 1.6], 'N')
    
    ##############################################
    
    return [] # tag N



### GLOBALS ###

blocks = []
layer = 1
prefab_num = 1
camera_zangle = 0


### CLASSES ###

class Block:
    def __init__(self, id, tag, layer):
        self.id = id
        self.tag = tag
        self.layer = layer
        self.hidden = False
        
    def hide(self):
        self.hidden = True
        
    def show(self):
        self.hidden = False


### SELECTORS ###

def xpos(obj, face):
    return face.normal[0] > 0.9
 
def xneg(obj, face):
    return face.normal[0] < -0.9

def ypos(obj, face):
    return face.normal[1] > 0.9
 
def yneg(obj, face):
    return face.normal[1] < -0.9

def zpos(obj, face):
    return face.normal[2] > 0.9
 
def zneg(obj, face):
    return face.normal[2] < -0.9


### EXTRUSION ###

def extrude(obj, face_selector, value):
    bpy.context.scene.objects.active = obj

    # Go to edit mode, face selection mode and select all faces
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.select_mode( type = 'FACE' )
    bpy.ops.mesh.select_all( action = 'SELECT' )

    # Create Bmesh
    bm = bmesh.new()
    bm = bmesh.from_edit_mesh( bpy.context.object.data )

    selected_faces = []
    for f in bm.faces:
        if face_selector(obj, f):
            selected_faces.append(f)

    normal = selected_faces[0].normal

    if len(bm.faces) > 1:
        for vert in selected_faces[0].verts:
            vert.co = vert.co + normal*value
        
    else:
        r = bmesh.ops.extrude_face_region(bm, geom=selected_faces)
        verts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
        TranslateDirection = normal * -value # Extrude Strength/Length
        bmesh.ops.translate(bm, vec = TranslateDirection, verts = verts)
        
        # Update & Destroy Bmesh
        bmesh.update_edit_mesh(bpy.context.object.data)
        bm.free()

    # Flip normals
    bpy.ops.mesh.select_all( action = 'SELECT' )
    bpy.ops.mesh.flip_normals()

    # At end recalculate UV
    bpy.ops.mesh.select_all( action = 'SELECT' )
    bpy.ops.uv.smart_project()

    # Switch back to Object at end
    bpy.ops.object.mode_set( mode = 'OBJECT' )

    # Origin to center
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')


def extrude_face(obj, dir, value, tag):
    extrude(obj, zpos, 0)
    
    if len(value) > 1:
        value = random.uniform(value[0], value[1])
    else:
        value = value[0]
    
    if (dir == 0):
        extrude(obj, xpos, value)
    if (dir == 1):
        extrude(obj, xneg, value)
    if (dir == 2):
        extrude(obj, ypos, value)
    if (dir == 3):
        extrude(obj, yneg, value)
    if (dir == 4):
        extrude(obj, zpos, value)
    if (dir == 5):
        extrude(obj, zneg, value)
    
    succesor = []
    succesor.append( Block(obj.name, tag, layer) )

    succesor[0].show()
    return succesor
 
 
### SUBDIVISION ###

def divide_cube(obj, parent, number, coord, value, length):
    bpy.context.scene.objects.active = obj
    
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    new_obj.animation_data_clear()
    new_obj.name = parent + str(layer) + str(number)
    bpy.context.scene.objects.link(new_obj)
    
    for v in obj.data.vertices:
        if v.co[coord] > value:
            v.co[coord] = value
            
    for v in new_obj.data.vertices:
        if v.co[coord] < value:
            v.co[coord] = value
            
    return new_obj


def getvalueofR(values, length):
    r_amount = 0
    total = 0
    r_val = 0
    
    for value in values:
        if value[0] == 'R':
            r_amount = r_amount + value[1]
        else:
            if len(value) == 1:
                aux = value[0]
            else:
                aux = random.uniform(value[0], value[1])
                value[0] = aux
            total = total + aux
    
    if r_amount > 0:
        r_val = (length - total) / r_amount
    
    return r_val, values


def convert_values(values, length, min, max):
    new_values = []
    last_break = min

    r_val, values = getvalueofR(values, length)
    
    for value in values:
        if value[0] == 'R':
            value = r_val*value[1]
        else:
            value = value[0] # Random value is already calculated at this point
            
        last_break = last_break + value
        new_value = last_break
        new_values.append(new_value)
    
    return new_values


def subdivide(obj, coord, values, tags, mat):
    number = 0
    
    # Get min, max and length
    min = 1000; max = -1000
    for v in obj.data.vertices:
        if v.co[coord] < min:
            min = v.co[coord]
        if v.co[coord] > max:
            max = v.co[coord]
    length = max - min
    
    norm_values = convert_values(values, length, min, max)

    # Generate copy to mantain original
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    new_obj.animation_data_clear()
    new_obj.name = obj.name + str(layer) + str(number)
    bpy.context.scene.objects.link(new_obj)
    number = number + 1
    
    hide_block(obj.name)
    
    parent = obj.name
    obj = new_obj
    
    add_material(obj, mat)
    
    succesors = []
    succesors.append( Block(obj.name, tags[0], layer) )
    if layer > 1:
        succesors[len(succesors) - 1].hide()
    
    for value in norm_values[:-1]: # Last division is useless
        new_obj = divide_cube(obj, parent, number, coord, value, length)
        number = number + 1
        obj = new_obj
        succesors.append( Block(obj.name, tags[number - 1], layer) )
        add_material(obj, mat)
        
        bpy.context.scene.objects.active = obj
        unwrap_text(5,5,1)
        
    return succesors


### TEXTURING ###

def unwrap_text(sc1, sc2, sc3):
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.editmode_toggle()
    tex = bpy.context.object.active_material.texture_slots[0]
    tex.mapping_x = 'Y'
    tex.mapping_y = 'X'
    tex.scale[0] = sc1
    tex.scale[1] = sc2
    tex.scale[2] = sc3
    
    
def unwrap_text_offset(sc1, sc2, sc3, off):
    unwrap_text(sc1, sc2, sc3)
    tex = bpy.context.object.active_material.texture_slots[0]
    tex.offset[0] = off
    
    
def add_material(ob, matname):
    mat = bpy.data.materials.get(matname)
    if mat is None:
        img = bpy.data.images.load(path + "textures\\" + matname + ".jpg")
        tex = bpy.data.textures.new("imgtex", "IMAGE")
        tex.image = img
        mat = bpy.data.materials.new(name=matname)
        mat.active_texture = tex

    # Assign material to object
    if ob.data.materials:
        if matname[0] == "a" and not daytime:
            mat.emit = 0.7
        else:
            mat.emit = 0
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)


### PREFAB ADDITION ###

def add_prefab(obj, objname, scale, dir, tag, mat):
    bpy.context.scene.objects.active = obj
    house = obj.name[0]
    rotX = 90
    rotZ = 0
    Vector=(0,0,0)
    offset = mathutils.Vector(Vector) 
      
    if (dir == 0):
        face_selector = xneg
        rotZ = 0
        offset[0] = 0.5
    if (dir == 1):
        face_selector = xpos
        rotZ = 180
        offset[0] = -0.5
    if (dir == 2):
        face_selector = yneg
        rotZ = 90
        offset[1] = 0.5
    if (dir == 3):
        face_selector = ypos
        rotZ = 270
        offset[1] = -0.5
    if (dir == 4):
        face_selector = zneg
    if (dir == 5):
        face_selector = zpos
        
    rotX = rotX/360 * (2*math.pi)
    rotZ = rotZ/360 * (2*math.pi)
        
    # Go to edit mode, face selection mode and select all faces
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.select_mode( type = 'FACE' )
    bpy.ops.mesh.select_all( action = 'SELECT' )
    
    bm = bmesh.new()
    bm = bmesh.from_edit_mesh( bpy.context.object.data )
    
    selected_faces = []
    for f in bm.faces:
        if face_selector(obj, f):
            selected_faces.append(f)
    
    translation = selected_faces[0].calc_center_median()
    
    dimx = selected_faces[0].edges[0].calc_length()
    dimy = selected_faces[0].edges[1].calc_length()
    
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    interior_obj = False
    if objname in interior_prefabs:
        newobj, newobj2 = load_interior_obj(objname, house, mat)
        interior_obj = True
    else:
        newobj = load_obj(objname, house, mat)
    
    translation = obj.matrix_world * translation # translation
    
    bpy.context.scene.objects.active = newobj
    
    unwrap_text(1,2,1)
    newobj.rotation_euler = (rotX, 0, rotZ)
    newobj.scale = (scale, dimy/2, dimx/2)
    
    if objname in roof_prefabs: # Roof prefabs only
        newobj.scale = (dimy/2, scale, dimx/2)
        
    newobj.location += translation
    
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.mesh.faces_shade_flat()
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    succesor = []
    succesor.append( Block(newobj.name, tag, layer) )
    
    if interior_obj == True: # Modify the interior part of the prefab if it exists
        bpy.context.scene.objects.active = newobj2
        
        offset_tex = camera_zangle / (1.5*(2*math.pi)) + 0.15
        unwrap_text_offset(0.25, 0.6, 1, offset_tex)
        newobj2.rotation_euler = (rotX, 0, rotZ)
        newobj2.scale = (scale, dimy/2, dimx/2)
        newobj2.location += translation
        
        if not daytime:
            light_pos = translation + offset
            add_light(light_pos[0], light_pos[1], light_pos[2])
        
        succesor.append( Block(newobj2.name, 'N', layer) )

    bpy.ops.object.select_all(action='DESELECT')
    
    return succesor


def load_obj(objname, house, mat):
    global prefab_num
    file_loc = path + "prefabs\\" + objname + ".obj"    

    imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
    obj = bpy.context.selected_objects[0]
    obj.name = str(house) + objname + "_" + str(prefab_num)
    
    prefab_num = prefab_num + 1
    
    add_material(obj, mat)
    
    return obj


def load_interior_obj(objname, house, mat):
    global prefab_num
    file_loc = path + "prefabs\\" + objname + ".obj"  

    imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
    
    obj = bpy.context.selected_objects[-1]
    obj2 = bpy.context.selected_objects[0]
    
    if obj.name[0] == 'I' or obj.name[0] == 'i': #interior
        aux = obj
        obj = obj2
        obj2 = aux
    
    obj.name = str(house) + objname + "_" + str(prefab_num)
    obj2.name = str(house) + "interior" + str(prefab_num)
    
    prefab_num = prefab_num + 1
    
    add_material(obj, mat)
    
    int_number = random.randint(1, 10) # random interior
    add_material(obj2, "ang_interior" + str(int_number))
    
    return obj, obj2
        

### OBJECT SELECTION ###

def select_all_mesh_objs():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select = True
        else:
            obj.select = False
            
            
def select_all_point_lights():
    for obj in bpy.context.scene.objects:
        if obj.type == 'LAMP' and obj.name != "Lamp":
            obj.select = True
   
    
### OBJECT MERGING ###

def merge_objs():
    select_all_mesh_objs()
    bpy.ops.object.join()
    obj = bpy.context.scene.objects.active
    obj.name = "House"
    
    
def merge_objs_by_layer(layers, houses):
    for current_layer in range(1, layers + 1):
        for current_house in range(0, houses):

            bpy.ops.object.select_all(action='DESELECT')
            
            for block in blocks:
                if block.layer == current_layer:
                    if block.id[0] == str(current_house):
                        obj = bpy.data.objects[block.id]
                        obj.select = True
                    
                        bpy.context.scene.objects.active = obj

            bpy.ops.object.join()
            obj = bpy.context.scene.objects.active
            obj.name = str(current_house) + "Layer" + str(current_layer)
        
        
def merge_layers(layers, houses):
    for current_house in range(0, houses):
        bpy.ops.object.select_all(action='DESELECT')
        for current_layer in range(1, layers):
            layer1 = str(current_house) + "Layer" + str(current_layer)
            layer2 = str(current_house) + "Layer" + str(current_layer + 1)
            
            if bpy.data.objects.get(layer2) is None:
                continue
            
            obj2 = bpy.data.objects[layer2]
            
            if bpy.data.objects.get(layer1) is None:
                continue
            
            obj = bpy.data.objects[layer1]
            
            obj.select = True
            obj2.select = True
            bpy.context.scene.objects.active = obj2
            
            # Small offset to avoid coplanar planes and Z-fighting
            bpy.context.object.scale[0] = 1 - 0.001 * current_layer
            bpy.context.object.scale[1] = 1 - 0.001 * current_layer
            bpy.context.object.scale[2] = 1 - 0.001 * current_layer
            
            bpy.ops.object.join()
        
        if obj2 is not None:
            obj2.name = "House" + str(current_house + 1)
        

### OBJECT HIDING ###

def show_block(name):
    for block in blocks:
        if block.id == name:
            block.show()
            return


def hide_block(name):
    for block in blocks:
        if block.id == name:
            block.hide()
            return
    
    
def hide_objs():
    for block in blocks:
        if block.hidden == True:
            obj = bpy.data.objects[block.id]
            obj.hide = True
            obj.hide_render = True


### PRODUCTION OF RULES ###

def add_block(current_block):
    i = 0
    for block in blocks:
        if blocks[i].id == current_block.id:
            blocks[i] = current_block
            return
        i = i + 1
    
    blocks.append(current_block)
    

def production(lots, numlayers):
    queue = []
    while len(lots) > 0:
        queue.append(lots[0])
        lots.pop(0)
        
    global layer
    while len(queue) > 0:
        current_block = queue[0]
        queue.pop(0)
        
        add_block(current_block)
        
        total_succesors = []
        for i in range(1, numlayers + 1):
            layer = i
            succesors = prod_rules(current_block)
            total_succesors = total_succesors + succesors
        
        for block in total_succesors:
            queue.append(block)


### ENVIRONMENT ELEMENTS ###

def generate_lot(name, size, loc):
    bpy.ops.mesh.primitive_plane_add(radius=size, calc_uvs=False, view_align=False,
     enter_editmode=False, location=loc, rotation=(0, 0, 0))
    
    obj = bpy.data.objects["Plane"]
    obj.name = name
    
    return obj


def add_terrain():
    bpy.ops.mesh.primitive_plane_add(radius=3, calc_uvs=False, view_align=False,
     enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
    
    obj = bpy.data.objects["Plane"]
    obj.name = 'Terrain'
    obj.scale = (6, 5, 1)
    
    add_material(obj, "grass")
    unwrap_text(10, 10, 1)
    
    
def add_background():
    bpy.ops.mesh.primitive_plane_add(radius=3, calc_uvs=False, view_align=False,
     enter_editmode=False, location=(0, 4.2, -21), rotation=(0, 0, math.pi/2))
    
    obj = bpy.data.objects["Plane"]
    obj.name = 'Background'
    obj.scale = (2.4, 4.1, 1)
    
    add_material(obj, "background2")
    unwrap_text(1, 1, 1)
    
    obj.parent = bpy.data.objects["Camera"]
    

def add_road(sizex, sizey, posx, posy):
    bpy.ops.mesh.primitive_plane_add(radius=3, calc_uvs=False, view_align=False,
     enter_editmode=False, location=(posx, posy, 0.001), rotation=(0, 0, 0))
    
    obj = bpy.data.objects["Plane"]
    obj.name = 'Terrain'
    obj.scale = (sizex, sizey, 1)
    
    add_material(obj, "asphalt")
    unwrap_text(2, 10, 1)
    
    
def add_light(xpos, ypos, zpos):
    lamp = bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=(xpos, ypos, zpos))
    bpy.context.object.data.color = (0.8, 0.5, 0.1)
    bpy.context.object.data.distance = 3
    bpy.context.object.data.shadow_method = 'RAY_SHADOW'
    

def daymode():
    bpy.context.scene.world.light_settings.environment_energy = 1.0
    bpy.data.objects["Lamp"].hide_render = False


def nightmode():
    bpy.context.scene.world.light_settings.environment_energy = 0.15
    bpy.data.objects["Lamp"].hide_render = True
    

### EXTRA FUNCTIONS ###

def get_camera_zangle():
    cam = bpy.data.objects["Camera"]
    bpy.context.scene.objects.active = cam
    zangle = bpy.context.object.rotation_euler[2]

    return zangle


def delete_objs():
    select_all_mesh_objs()
    select_all_point_lights()
    bpy.ops.object.delete()
    

### MAIN ###

def main():
    time1 = time.time() # Time checkpoint
    bpy.ops.object.mode_set(mode='OBJECT')
    delete_objs() # Delete mesh objects and point lights
    
    time2 = time.time() # Time checkpoint
    obj = generate_lot('0', 3, (0,0,0))
    obj2 = generate_lot('1', 3, (-8.001,0,0))
    obj3 = generate_lot('2', 3, (8.001,0,0))

    lots = [] # Adding the lots to the queue
    lots.append( Block(obj.name, 'L', layer) )
    lots.append( Block(obj2.name, 'L', layer) )
    lots.append( Block(obj3.name, 'L', layer) )
    
    global camera_zangle
    camera_zangle = get_camera_zangle()
    
    time3 = time.time() # Time checkpoint
    production(lots, num_layers)
    
    time4 = time.time() # Time checkpoint
    hide_objs() # Hide objects that were tagged as hidden
    
    # Layer merging
    merge_objs_by_layer(num_layers, num_houses)
    if num_layers > 1:
        merge_layers(num_layers, num_houses)
    
    time5 = time.time() # Time checkpoint
    # Terrain
    add_terrain()
    
    # Road
    add_road(6, 0.6, 0, 9)
    add_road(0.3, 0.8, 1, 4.8)
    add_road(0.3, 0.8, 9, 4.8)
    add_road(0.3, 0.8, -7, 4.8)
    
    # Background
    add_background()
    
    # Lighting
    if daytime:
        daymode()
    else:
        nightmode()
        
    # Add ambient occlusion
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1
        
    time6 = time.time() # Time checkpoint
    
    # Console prompt
    print("- Preparation: %s s -" % round((time2 - time1), 3))
    print("- Lot generation: %s s -" % round((time3 - time2), 3))
    print("- Rules: %s s -" % round((time4 - time3), 3))
    print("- Layer merging: %s s -" % round((time5 - time4), 3))
    print("- Environment: %s s -" % round((time6 - time5), 3))
    

start_time = time.time() # Time checkpoint

# Calling main function
main()

print("- Total: %s s -" % round((time.time() - start_time), 3))
