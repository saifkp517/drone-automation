from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
import asyncio

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    mission_items = []
    mission_item = MissionItem(
        latitude_deg=47.39803986,
        longitude_deg=8.54557254,
        relative_altitude_m=10,
        speed_m_s=5,
        is_fly_through=False,
        gimbal_pitch_deg=float('nan'),
        gimbal_yaw_deg=0.0,
        camera_action=MissionItem.CameraAction.NONE,
        loiter_time_s=5,
        acceptance_radius_m=1,
        yaw_deg=float('nan'),
        camera_photo_interval_s=float('nan'),
        camera_photo_distance_m=float('nan'),
        vehicle_action=MissionItem.VehicleAction.NONE
    )
    mission_items.append(mission_item)

    mission_plan = MissionPlan(mission_items)

    print("Uploading mission...")
    await drone.mission.upload_mission(mission_plan)
    print("Mission uploaded successfully!")

    print("Drone taking off...")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)

    print("Starting mission...")
    await drone.mission.start_mission()
    print("Mission started...")

    # Wait for the mission to complete
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("Mission completed!")
            break

    await drone.action.return_to_launch()

    print("Returning to launch...")
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())
