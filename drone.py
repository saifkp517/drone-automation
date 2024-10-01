from mavsdk import System
import keyboard
import threading
import serial
from mavsdk.mission import MissionItem, MissionPlan
import asyncio

manual_control_active = False

def serial_listener(serial_port):
    global manual_control_active
    while True:
        if serial_port.in_waiting > 0:
            command = serial_port.read().decode('utf-8')
            if command == 'm':
                manual_control_active = not manual_control_active
                print(f"Manual Control active!")

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    curr_pos = await drone.telemetry.position()
    print(f"Current Position- Lat: {curr_pos.latitude_deg}, long: {curr_pos.longitude_deg}")

    delta = 0.0001 #move one metre

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

    serial_port = serial.Serial('/dev/pts/3', baudrate=9600, timeout=1)
    threading.Thread(target=serial_listener, args=(serial_port,), daemon=True).start()

    # Wait for the mission to complete
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")

        if manual_control_active:
            print("Manual is control is active!")
            await asyncio.sleep(1)
            manual_control_active = not manual_control_active
        else:
            if mission_progress.current == mission_progress.total:
                print("Mission completed!")
                break


    await drone.action.return_to_launch()

    print("Returning to launch...")
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())
