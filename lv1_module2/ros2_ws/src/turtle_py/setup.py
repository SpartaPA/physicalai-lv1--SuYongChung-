from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'turtle_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pa24',
    maintainer_email='affluentmind12@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': ['pytest'],
    },
        entry_points={
        'console_scripts': [
            'distance_publisher = turtle_py.distance_publisher:main',
            'distance_subscriber = turtle_py.distance_subscriber:main',
            'square_driver = turtle_py.square_driver:main',
            'tf_broadcaster = turtle_py.tf_broadcaster:main',
            'waypoint_marker = turtle_py.waypoint_marker:main',
            'ex05_builtin_service_client = turtle_py.ex05_builtin_service_client:main',
            'ex05_rotate_absolute_client = turtle_py.ex05_rotate_absolute_client:main',
            'ex05_toggle_servers = turtle_py.ex05_toggle_servers:main',
            'ex06_polygon_action_server = turtle_py.ex06_polygon_action_server:main',
            'ex06_waypoint_publisher = turtle_py.ex06_waypoint_publisher:main',
            'ex07_qos_sensor_publisher = turtle_py.ex07_qos_sensor_publisher:main',
            'ex07_qos_subscriber = turtle_py.ex07_qos_subscriber:main',
        ],
    },
)