import json
from mavsdk import System
from mavsdk.mission import (MissionPlan, MissionItem)

async def load_mission_from_file(file_path):
    """ Loads a mission from a QGC plan file and returns a list of MissionItems """
    with open(file_path, 'r') as f:
        qgc_plan = json.load(f)
    
    mission_items = []
    for wp in qgc_plan['mission']['items']:
        # Convert each waypoint into a MissionItem
        mission_item = MissionItem(
            latitude=wp['coordinate'][0],
            longitude=wp['coordinate'][1],
            relative_altitude=float(wp['coordinate'][2]),
            speed=float(wp.get('speed', 5.0)),  # Default speed to 5 m/s if not specified
            is_fly_through=bool(wp.get('flyThrough', True)),
            gimbal_pitch=float(wp.get('gimbalPitch', 0.0)),
            gimbal_yaw=float(wp.get('gimbalYaw', 0.0)),
            camera_action=MissionItem.CameraAction.NONE
        )
        mission_items.append(mission_item)
    return mission_items

async def upload_and_start_mission(drone, mission_items):
    """ Uploads and starts a mission """
    mission_plan = MissionPlan(mission_items)
    await drone.mission.upload_mission(mission_plan)
    print("Mission uploaded!")

    await drone.mission.start_mission()
    print("Mission started!")

async def run():
    """ Main function to connect to the drone and run the mission """
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone is connected!")
            break

    # Load mission from file
    mission_items = await load_mission_from_file('../Downloads/flightplan.plan')

    # Upload and start the mission
    await upload_and_start_mission(drone, mission_items)

    # Optionally, monitor mission progress
    async for mission_progress in drone.mission.mission_progress():
        print(f"Current waypoint: {mission_progress.current}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
