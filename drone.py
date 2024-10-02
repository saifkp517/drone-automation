from mavsdk import System
import threading
import serial
from mavsdk.mission import MissionItem, MissionPlan
import asyncio

manual_control_active = False

# Function to move drone based on command
async def move_drone_based_on_command(command, drone):
    print("inside function")
    async for position in drone.telemetry.position():
        lat = position.latitude_deg
        lon = position.longitude_deg
        alt = 20
        break

    if command == 'w':
        print("Forward action triggered (North)")
        await drone.action.goto_location(lat + 0.0001, lon, alt, 0)
    elif command == 's':
        print("Backward action triggered (South)")
        await drone.action.goto_location(lat - 0.0001, lon, alt, 0)
    elif command == 'a':
        print("Left action triggered (West)")
        await drone.action.goto_location(lat, lon - 0.0001, alt, 0)
    elif command == 'd':
        print("Right action triggered (East)")
        await drone.action.goto_location(lat, lon + 0.0001, alt, 0)
    elif command == 'e':
        global manual_control_active
        manual_control_active = False
        print("Exiting manual control.")

        # Return to launch once mission is complete
        await drone.action.return_to_launch()
        print("Returning to launch...")

        # Land the drone
        await drone.action.land()

        await asyncio.sleep(0.1)  # Throttle the async loop

# Function to handle manual control based on serial input
async def handle_manual_control(serial_port, drone, loop):
    global manual_control_active
    while manual_control_active:
        if serial_port.in_waiting > 0:
            print("Inside manual control loop")
            command = serial_port.read().decode('utf-8').strip()

            if loop.is_running():
                await move_drone_based_on_command(command, drone)
                print(f"Executed Command: {command}")


# Threaded function to listen for serial input
async def serial_listener(serial_port, drone, loop):
    global manual_control_active
    while True:
        if serial_port.in_waiting > 0:
            command = serial_port.read().decode('utf-8').strip()
            print(f"Received command: {command}")

            if command == 'm':
                manual_control_active = not manual_control_active
                print(f"Manual Control {'activated' if manual_control_active else 'deactivated'}!")

            if manual_control_active:
                await handle_manual_control(serial_port, drone, loop)

# Main async function to run the drone mission
async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    # Mission items setup
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

    # Upload mission
    print("Uploading mission...")
    await drone.mission.upload_mission(mission_plan)
    print("Mission uploaded successfully!")

    # Takeoff and start the mission
    print("Drone taking off...")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)

    '''
    print("Starting mission...")
    await drone.mission.start_mission()
    print("Mission started...")
    '''

    loop = asyncio.get_event_loop()

    # Start the serial listener in a separate thread
    serial_port = serial.Serial('/dev/pts/3', baudrate=9600, timeout=1)

    await asyncio.gather(
        serial_listener(serial_port, drone, loop),
    )

    # Loop for mission progress
    '''
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")

        if manual_control_active:
            print("Manual control is active!")
        elif mission_progress.current == mission_progress.total:
            print("Mission completed!")
            break
    '''


if __name__ == "__main__":
    asyncio.run(run())

