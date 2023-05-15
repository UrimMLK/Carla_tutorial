import sys
import os
import glob, time
import cv2
import numpy as np

try:
    sys.path.append(glob.glob(r'C:\WindowsNoEditor_final\WindowsNoEditor\PythonAPI\carla\dist\carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

actor_list = []

def camera_callback(image, data_dict):
    data_dict['image'] = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))

def control_cam():
    image_w = camera_bp.get_attribute("image_size_x").as_int()
    image_h = camera_bp.get_attribute("image_size_y").as_int()
    camera_data = {'image': np.zeros((image_h, image_w, 4))}
    # Start camera recording
    camera.listen(lambda image: camera_callback(image, camera_data))
    # Game loop
    while True:
        # Imshow renders sensor data to display
        cv2.imshow('Carla Camera', camera_data['image'])

        # Quit if user presses 'q'
        if cv2.waitKey(1) == ord('q'):
            break

    # Close OpenCV window when finished
    cv2.destroyAllWindows()
    cv2.stop()



try:
    client = carla.Client('localhost', 2000)
    """Try to keep a set_timeout to more than 2s"""
    client.set_timeout(10.0)
    world = client.get_world()

    """If you want to load another map"""
    #world = client.load_world('Town01')
    loc = carla.Location(x=-114, y=-12.2, z=0.6)
    rot = carla.Rotation(pitch=0.000000, yaw=162.0, roll=0.000000)

    """Carla library"""
    blueprint_library = world.get_blueprint_library()

    """make pedestrian and spawn actor"""
    spawn_point = carla.Transform(loc, rot)
    walker_bp = blueprint_library.find('walker.pedestrian.0003')
    walker_actor = world.spawn_actor(walker_bp, spawn_point)
    actor_list.append(walker_actor)

    """make car1 and spawn it"""
    vehicle = world.get_blueprint_library().find('vehicle.citroen.c3')
    vehicle.set_attribute('color', '255,0,0')  # set vehicle's color to red
    #model3_spawn_point = np.random.choice(spawn_points)
    location1 = carla.Location(x=-52.30, y=-25, z=0.600000)
    rotation1 = carla.Rotation(pitch=0.000000, yaw=162.0, roll=0.000000)
    transform1 = carla.Transform(location1, rotation1)
    vehicle_actor = world.spawn_actor(vehicle, transform1)

    """Set autopilot"""
    vehicle_actor.set_autopilot(True)
    actor_list.append(vehicle_actor)

    """create the camera1"""
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '810')
    camera_bp.set_attribute('image_size_y', '735')
    camera_init_trans = carla.Transform(carla.Location(z=2))  # Change this to move camera
    camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=vehicle_actor)
    actor_list.append(camera)


    """move the camera next to the spectator"""
    spectator = world.get_spectator()
    transform = carla.Transform(vehicle_actor.get_transform().transform(carla.Location(x=-4, z=2.5)),
                                vehicle_actor.get_transform().rotation)
    spectator.set_transform(transform)

    time.sleep(0.2)
    spectator.set_transform(camera.get_transform())

    """Start the camera"""
    control_cam()


    """Duration of the simulation"""
    time.sleep(20)

    world.tick()


finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
        print('done.')
    sys.exit()
